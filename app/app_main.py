import os
import sys
import time
import base64
import pickle
import threading
import webbrowser
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Garante que a raiz do projeto está no sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from trackers.ball_tracker import BallTracker
from app.core.homography import HomographyManager
from app.core.game_engine import GameEngine
from app.core.storage import StorageManager

app = FastAPI(title="Top Training — Tennis Analytics")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

storage = StorageManager(data_dir=os.path.join(os.path.dirname(__file__), "data"))
homography = HomographyManager(width_m=8.23, length_m=11.885)
saved_h = storage.load_homography()
if saved_h:
    homography.load_from_dict(saved_h)

game_engine = GameEngine(homography)

MODEL_PATH = os.path.join(ROOT_DIR, "models", "yolov8_best_2.pt")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(ROOT_DIR, "models", "yolov8_best.pt")

_tracker_instance = None
_tracker_lock = threading.Lock()


def get_tracker() -> BallTracker:
    global _tracker_instance
    with _tracker_lock:
        if _tracker_instance is None:
            _tracker_instance = BallTracker(MODEL_PATH)
        return _tracker_instance


def list_input_videos() -> list:
    vid_dir = os.path.join(ROOT_DIR, "src", "input_videos")
    if not os.path.exists(vid_dir):
        return []
    exts = (".mp4", ".mov", ".avi", ".mkv")
    files = [f for f in sorted(os.listdir(vid_dir)) if f.lower().endswith(exts)]

    # Prioriza vídeos que já possuem cache de detecção em stubs/ (ex: quadra_2, quadra_3)
    model_stem = os.path.splitext(os.path.basename(MODEL_PATH))[0]
    stubs_dir = os.path.join(ROOT_DIR, "stubs")

    def sort_key(fname: str):
        stem = os.path.splitext(fname)[0]
        stub_file = os.path.join(stubs_dir, f"{stem}_{model_stem}_detections.pkl")
        has_stub = os.path.exists(stub_file)
        return (0 if has_stub else 1, fname.lower())

    return sorted(files, key=sort_key)


class TrainingState:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        self.active = False
        self.analyzing = False
        self.analysis_done = False
        self.finished = False
        self.status_msg = "Pronto"
        self.player = "Jogador"
        self.level = "basico"
        self.target_zone = 0
        self.source_type = "video"
        self.source_id = ""
        self.current_frame_idx = 0
        self.total_frames = 0
        self.fps = 30.0
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.accuracy = 0.0
        self.events = []
        self.zone_stats = []
        self.most_hits_summary = ""
        self.most_misses_summary = ""
        self.latest_jpeg = None
        self.stop_requested = False
        self.video_paused = False
        self.seek_frame = -1


training_state = TrainingState()


class CalibrateRequest(BaseModel):
    pixel_points: list
    width_m: float = 8.23
    length_m: float = 11.885


class ValidatePointRequest(BaseModel):
    u: float
    v: float
    level: str = "basico"


class StartTrainingRequest(BaseModel):
    player: str
    level: str
    target_zone: int
    source_type: str  # "video" ou "camera"
    source_id: str    # nome do arquivo ou índice "0", "1", "2"


class VideoControlRequest(BaseModel):
    action: str       # "toggle_pause", "restart", "seek"
    frame: int = 0


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/init")
def api_init():
    profiles = storage.load_profiles()
    return {
        "profiles": list(profiles.keys()),
        "videos": list_input_videos(),
        "cameras": [
            {"id": "0", "label": "Câmera 0 (Padrão / Iriun USB-WiFi)"},
            {"id": "1", "label": "Câmera 1 (Secundária / Iriun)"},
            {"id": "2", "label": "Câmera 2 (Externa UVC)"}
        ],
        "homography": homography.to_dict(),
        "zones": {
            "basico": game_engine.get_zones("basico"),
            "medio": game_engine.get_zones("medio"),
            "avancado": game_engine.get_zones("avancado")
        },
        "ranking": storage.get_ranking()
    }


@app.get("/api/frame_snapshot")
def api_frame_snapshot(source_type: str = "video", source_id: str = ""):
    if source_type == "camera":
        cam_idx = int(source_id) if str(source_id).isdigit() else 0
        cap = cv2.VideoCapture(cam_idx)
    else:
        videos = list_input_videos()
        vid_name = source_id if source_id in videos else (videos[0] if videos else "")
        if not vid_name:
            raise HTTPException(status_code=404, detail="Nenhum vídeo encontrado em src/input_videos.")
        vid_path = os.path.join(ROOT_DIR, "src", "input_videos", vid_name)
        cap = cv2.VideoCapture(vid_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total > 15:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 10)

    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        raise HTTPException(status_code=400, detail=f"Não foi possível capturar imagem da fonte ({source_type}:{source_id}).")

    h, w = frame.shape[:2]
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    if not ok:
        raise HTTPException(status_code=500, detail="Erro ao codificar frame JPEG.")

    b64 = base64.b64encode(buf.tobytes()).decode("ascii")
    return {
        "width": w,
        "height": h,
        "image_base64": f"data:image/jpeg;base64,{b64}",
        "homography": homography.to_dict()
    }


@app.post("/api/calibrate")
def api_calibrate(req: CalibrateRequest):
    if len(req.pixel_points) != 4:
        raise HTTPException(status_code=400, detail="Forneça exatamente 4 pontos.")
    cal = homography.calibrate(req.pixel_points, width_m=req.width_m, length_m=req.length_m)
    storage.save_homography(cal)
    return {
        "homography": cal,
        "zones": {
            "basico": game_engine.get_zones("basico"),
            "medio": game_engine.get_zones("medio"),
            "avancado": game_engine.get_zones("avancado")
        }
    }


@app.post("/api/validate_point")
def api_validate_point(req: ValidatePointRequest):
    if not homography.is_calibrated():
        raise HTTPException(status_code=400, detail="Calibre os 4 pontos da quadra primeiro.")
    xm, ym, inside = homography.pixel_to_meters(req.u, req.v)
    zone_id = game_engine.find_zone_for_point(xm, ym, req.level) if inside else -1
    return {
        "u": round(req.u, 1),
        "v": round(req.v, 1),
        "x_m": xm,
        "y_m": ym,
        "inside_court": inside,
        "zone_id": zone_id
    }


def _ensure_default_calibration(w: int, h: int):
    if not homography.is_calibrated():
        default_pts = [
            [round(w * 0.22, 1), round(h * 0.88, 1)],
            [round(w * 0.78, 1), round(h * 0.88, 1)],
            [round(w * 0.68, 1), round(h * 0.25, 1)],
            [round(w * 0.32, 1), round(h * 0.25, 1)],
        ]
        cal = homography.calibrate(default_pts)
        storage.save_homography(cal)


def _run_video_session(req: StartTrainingRequest):
    """
    Analisa o vídeo como um todo (sem carregar todos os frames na RAM de uma vez),
    calcula todos os quiques e estatísticas de zonas, dispara a popup 'Vídeo Analisado'
    e reproduz o vídeo anotado em alta resolução com suporte a Pause/Seek.
    """
    vid_path = os.path.join(ROOT_DIR, "src", "input_videos", req.source_id)
    cap = cv2.VideoCapture(vid_path)
    if not cap.isOpened():
        with training_state.lock:
            training_state.status_msg = "Erro ao abrir vídeo."
            training_state.active = False
            training_state.analyzing = False
            training_state.finished = True
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080

    _ensure_default_calibration(w, h)

    with training_state.lock:
        training_state.fps = fps
        training_state.total_frames = max(1, total_frames)
        training_state.analyzing = True
        training_state.analysis_done = False
        training_state.status_msg = "Verificando detecções do vídeo..."

    os.makedirs(os.path.join(ROOT_DIR, "stubs"), exist_ok=True)
    video_stem = os.path.splitext(os.path.basename(vid_path))[0]
    model_stem = os.path.splitext(os.path.basename(MODEL_PATH))[0]
    stub_path = os.path.join(ROOT_DIR, "stubs", f"{video_stem}_{model_stem}_detections.pkl")

    detections = None
    if os.path.exists(stub_path):
        try:
            with open(stub_path, "rb") as f:
                cached = pickle.load(f)
            if isinstance(cached, list) and len(cached) > 0 and abs(len(cached) - total_frames) <= 5:
                detections = cached
                total_frames = len(detections)
                with training_state.lock:
                    training_state.total_frames = total_frames
                    training_state.current_frame_idx = total_frames
        except Exception:
            detections = None

    # Se não houver stub salvo, analisa frame a frame sem estourar a memória RAM
    if detections is None:
        tracker = get_tracker()
        detections = []
        prev_gray = None
        last_center = None
        last_det_idx = -999
        idx = 0

        while not training_state.stop_requested:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ball_dict = tracker.detect_frame(
                frame,
                curr_gray=curr_gray,
                prev_gray=prev_gray,
                last_center=last_center,
                frames_since_last=(idx - last_det_idx)
            )
            if 1 in ball_dict:
                x1, y1, x2, y2 = ball_dict[1]
                last_center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
                last_det_idx = idx

            detections.append(ball_dict)
            prev_gray = curr_gray
            idx += 1

            pct = min(100, int((idx / max(1, total_frames)) * 100))
            with training_state.lock:
                training_state.current_frame_idx = idx
                training_state.status_msg = f"Analisando vídeo como um todo... {pct}% ({idx}/{total_frames})"

            # A cada 8 frames atualiza um preview leve do progresso
            if idx % 8 == 0:
                small = cv2.resize(frame, (640, 360))
                cv2.putText(
                    small, f"Analisando Video: {pct}%", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 230, 118), 2, cv2.LINE_AA
                )
                ok, buf = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                if ok:
                    with training_state.lock:
                        training_state.latest_jpeg = buf.tobytes()

        if not training_state.stop_requested and detections:
            try:
                with open(stub_path, "wb") as f:
                    pickle.dump(detections, f)
            except Exception:
                pass

    if training_state.stop_requested or not detections:
        cap.release()
        with training_state.lock:
            training_state.active = False
            training_state.analyzing = False
            training_state.finished = True
            training_state.status_msg = "Análise cancelada."
        return

    # Interpola posições e detecta quiques sem carregar o modelo YOLO caso já estivesse em cache
    bt_helper = BallTracker.__new__(BallTracker)
    detections = bt_helper.interpolate_ball_positions(detections, max_gap=12)
    raw_bounces = bt_helper.detect_bounces(detections)

    eval_result = game_engine.evaluate_bounces(
        raw_bounces, fps, req.level, req.target_zone, is_video_mode=True
    )
    all_events = eval_result["events"]

    # Registra a sessão completa no histórico do jogador
    storage.record_session(req.player, {
        "level": req.level,
        "target_zone": req.target_zone,
        "source": f"video:{req.source_id}",
        "score": eval_result["score"],
        "hits": eval_result["hits"],
        "misses": eval_result["misses"],
        "total_shots": eval_result["total_shots"],
        "accuracy": eval_result["accuracy"],
        "events": all_events
    })

    with training_state.lock:
        training_state.analyzing = False
        training_state.analysis_done = True
        training_state.score = eval_result["score"]
        training_state.hits = eval_result["hits"]
        training_state.misses = eval_result["misses"]
        training_state.accuracy = eval_result["accuracy"]
        training_state.events = all_events
        training_state.zone_stats = eval_result["zone_stats"]
        training_state.most_hits_summary = eval_result["most_hits_summary"]
        training_state.most_misses_summary = eval_result["most_misses_summary"]
        training_state.status_msg = "Vídeo Analisado! Reproduzindo visualização de quiques..."

    # Inicia a reprodução contínua do vídeo em alta definição (960x540) mostrando os quiques
    out_w, out_h = 960, 540
    sx, sy = out_w / float(w), out_h / float(h)
    poly_scaled = np.array(
        [[int(p[0] * sx), int(p[1] * sy)] for p in homography.pixel_points],
        dtype=np.int32
    ).reshape((-1, 1, 2))

    # Se o primeiro quique acontece muito à frente (ex: frame 718 em quadra_3), inicia 45 frames antes dele
    start_idx = 0
    if all_events and all_events[0]["frame"] > 60:
        start_idx = max(0, all_events[0]["frame"] - 45)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
    curr_idx = start_idx
    frame_delay = 1.0 / max(fps, 20.0)

    while not training_state.stop_requested:
        with training_state.lock:
            seek_target = training_state.seek_frame
            paused = training_state.video_paused
            if seek_target >= 0:
                training_state.seek_frame = -1

        if seek_target >= 0:
            curr_idx = max(0, min(total_frames - 1, seek_target))
            cap.set(cv2.CAP_PROP_POS_FRAMES, curr_idx)

        if paused and seek_target < 0:
            time.sleep(0.04)
            continue

        t0 = time.time()
        ret, frame = cap.read()
        if not ret or frame is None or curr_idx >= total_frames:
            # Reinicia o loop de visualização
            curr_idx = start_idx
            cap.set(cv2.CAP_PROP_POS_FRAMES, curr_idx)
            continue

        vis = cv2.resize(frame, (out_w, out_h))

        # Desenha polígono da quadra calibrada
        cv2.polylines(vis, [poly_scaled], isClosed=True, color=(255, 200, 40), thickness=2, lineType=cv2.LINE_AA)

        # Desenha rastro recente da bola (últimos 18 frames)
        trail_pts = []
        for t_idx in range(max(0, curr_idx - 18), curr_idx + 1):
            if t_idx < len(detections) and 1 in detections[t_idx]:
                bx1, by1, bx2, by2 = detections[t_idx][1]
                tcx = int(((bx1 + bx2) / 2.0) * sx)
                tcy = int(((by1 + by2) / 2.0) * sy)
                trail_pts.append((tcx, tcy))
        for k in range(1, len(trail_pts)):
            cv2.line(vis, trail_pts[k - 1], trail_pts[k], (0, 230, 255), 2, cv2.LINE_AA)

        # Desenha bola no frame atual
        if curr_idx < len(detections) and 1 in detections[curr_idx]:
            x1, y1, x2, y2 = detections[curr_idx][1]
            cx, cy = int(((x1 + x2) / 2.0) * sx), int(((y1 + y2) / 2.0) * sy)
            cv2.circle(vis, (cx, cy), 7, (0, 255, 110), -1, cv2.LINE_AA)
            cv2.rectangle(
                vis,
                (int(x1 * sx), int(y1 * sy)),
                (int(x2 * sx), int(y2 * sy)),
                (0, 255, 255), 2
            )

        # Desenha todos os quiques no vídeo (destacando com efeito de onda quando o frame passa pelo quique)
        for e in all_events:
            u = int(e["pixel_u"] * sx)
            v = int(e["pixel_v"] * sy)
            is_hit = e["is_hit"]
            color = (118, 230, 0) if is_hit else (60, 60, 255)  # BGR
            diff_f = curr_idx - e["frame"]

            # Mostra todos os quiques suavemente ou destaca os já ocorridos
            if diff_f >= -5:
                cv2.circle(vis, (u, v), 11, color, 2, cv2.LINE_AA)
                cv2.circle(vis, (u, v), 4, color, -1, cv2.LINE_AA)
                label = f"#{e['shot_number']} {'ACERTO' if is_hit else 'ERRO'}"
                cv2.putText(
                    vis, label, (u + 12, v + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA
                )
                cv2.putText(
                    vis, label, (u + 12, v + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1, cv2.LINE_AA
                )

            # Efeito de impacto no momento do quique
            if 0 <= diff_f <= 20:
                ripple_r = 14 + diff_f * 2
                cv2.circle(vis, (u, v), ripple_r, color, 2, cv2.LINE_AA)

        ok, buf = cv2.imencode(".jpg", vis, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
        with training_state.lock:
            training_state.current_frame_idx = curr_idx + 1
            if ok:
                training_state.latest_jpeg = buf.tobytes()

        curr_idx += 1
        elapsed = time.time() - t0
        time.sleep(max(0.002, frame_delay - elapsed))

    cap.release()
    with training_state.lock:
        training_state.active = False
        training_state.finished = True
        training_state.status_msg = "Sessão finalizada!"


def _run_camera_session(req: StartTrainingRequest):
    cam_idx = int(req.source_id) if str(req.source_id).isdigit() else 0
    cap = cv2.VideoCapture(cam_idx)
    if not cap.isOpened():
        with training_state.lock:
            training_state.status_msg = f"Não foi possível abrir a Câmera {cam_idx}."
            training_state.active = False
            training_state.finished = True
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    tracker = get_tracker()
    prev_gray = None
    last_center = None
    last_det_idx = -999
    detections_history = []
    idx = 0

    with training_state.lock:
        training_state.fps = fps
        training_state.analyzing = False
        training_state.analysis_done = False
        training_state.status_msg = f"Capturando ao vivo (Câmera {cam_idx})..."

    while not training_state.stop_requested:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.02)
            continue

        h, w = frame.shape[:2]
        if idx == 0:
            _ensure_default_calibration(w, h)

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ball_dict = tracker.detect_frame(
            frame,
            curr_gray=curr_gray,
            prev_gray=prev_gray,
            last_center=last_center,
            frames_since_last=(idx - last_det_idx)
        )
        if 1 in ball_dict:
            x1, y1, x2, y2 = ball_dict[1]
            last_center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
            last_det_idx = idx

        detections_history.append(ball_dict)
        prev_gray = curr_gray
        idx += 1

        if idx >= 10 and idx % 3 == 0:
            interp = tracker.interpolate_ball_positions(detections_history, max_gap=8)
            raw_bounces = tracker.detect_bounces(interp)
            eval_result = game_engine.evaluate_bounces(raw_bounces, fps, req.level, req.target_zone, is_video_mode=False)
            with training_state.lock:
                training_state.hits = eval_result["hits"]
                training_state.misses = eval_result["misses"]
                training_state.score = eval_result["score"]
                training_state.accuracy = eval_result["accuracy"]
                training_state.events = eval_result["events"]
                training_state.zone_stats = eval_result["zone_stats"]
                training_state.most_hits_summary = eval_result["most_hits_summary"]
                training_state.most_misses_summary = eval_result["most_misses_summary"]

        out_w, out_h = 854, 480
        sx, sy = out_w / float(w), out_h / float(h)
        vis = cv2.resize(frame, (out_w, out_h))
        poly_pts = np.array(
            [[int(p[0] * sx), int(p[1] * sy)] for p in homography.pixel_points],
            dtype=np.int32
        ).reshape((-1, 1, 2))
        cv2.polylines(vis, [poly_pts], isClosed=True, color=(255, 190, 40), thickness=2)
        if 1 in ball_dict:
            x1, y1, x2, y2 = ball_dict[1]
            cv2.circle(vis, (int(((x1 + x2) / 2) * sx), int(((y1 + y2) / 2) * sy)), 7, (0, 255, 100), -1)

        ok, buf = cv2.imencode(".jpg", vis, [int(cv2.IMWRITE_JPEG_QUALITY), 78])
        with training_state.lock:
            training_state.current_frame_idx = idx
            if ok:
                training_state.latest_jpeg = buf.tobytes()

    cap.release()
    with training_state.lock:
        training_state.active = False
        training_state.finished = True
        training_state.status_msg = "Treino encerrado!"
        storage.record_session(req.player, {
            "level": req.level,
            "target_zone": req.target_zone,
            "source": f"camera:{cam_idx}",
            "score": training_state.score,
            "hits": training_state.hits,
            "misses": training_state.misses,
            "total_shots": training_state.hits + training_state.misses,
            "accuracy": training_state.accuracy,
            "events": training_state.events
        })


@app.post("/api/training/start")
def api_training_start(req: StartTrainingRequest):
    with training_state.lock:
        if training_state.active:
            training_state.stop_requested = True

    time.sleep(0.12)
    storage.get_or_create_profile(req.player)

    with training_state.lock:
        training_state.reset()
        training_state.active = True
        training_state.player = req.player.strip() or "Jogador"
        training_state.level = req.level
        training_state.target_zone = req.target_zone
        training_state.source_type = req.source_type
        training_state.source_id = req.source_id

    target_fn = _run_camera_session if req.source_type == "camera" else _run_video_session
    t = threading.Thread(target=target_fn, args=(req,), daemon=True)
    t.start()
    return {"started": True}


@app.post("/api/training/video_control")
def api_video_control(req: VideoControlRequest):
    with training_state.lock:
        if req.action == "toggle_pause":
            training_state.video_paused = not training_state.video_paused
        elif req.action == "restart":
            training_state.seek_frame = 0
            training_state.video_paused = False
        elif req.action == "seek":
            training_state.seek_frame = max(0, req.frame)
        return {"paused": training_state.video_paused}


@app.post("/api/training/stop")
def api_training_stop():
    with training_state.lock:
        training_state.stop_requested = True
    return {"stopping": True}


@app.get("/api/training/status")
def api_training_status():
    with training_state.lock:
        return {
            "active": training_state.active,
            "analyzing": training_state.analyzing,
            "analysis_done": training_state.analysis_done,
            "paused": training_state.video_paused,
            "finished": training_state.finished,
            "status_msg": training_state.status_msg,
            "player": training_state.player,
            "level": training_state.level,
            "target_zone": training_state.target_zone,
            "source_type": training_state.source_type,
            "current_frame": training_state.current_frame_idx,
            "total_frames": training_state.total_frames,
            "score": training_state.score,
            "hits": training_state.hits,
            "misses": training_state.misses,
            "total_shots": training_state.hits + training_state.misses,
            "accuracy": training_state.accuracy,
            "events": training_state.events,
            "zone_stats": training_state.zone_stats,
            "most_hits_summary": training_state.most_hits_summary,
            "most_misses_summary": training_state.most_misses_summary
        }


def _mjpeg_generator():
    while True:
        with training_state.lock:
            jpg = training_state.latest_jpeg
            active = training_state.active
        if jpg:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
            )
        if not active and jpg is not None:
            break
        time.sleep(0.033)


@app.get("/api/training/video_feed")
def api_video_feed():
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/api/ranking")
def api_ranking():
    return storage.get_ranking()


@app.post("/api/shutdown")
def api_shutdown():
    """Encerra a sessão ativa e desliga o servidor do aplicativo."""
    with training_state.lock:
        training_state.stop_requested = True

    def _kill():
        time.sleep(0.4)
        os._exit(0)

    threading.Thread(target=_kill, daemon=True).start()
    return {"shutdown": True}


def main():
    port = 8000
    url = f"http://127.0.0.1:{port}"
    print(f"Iniciando Top Training em {url} ...")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
