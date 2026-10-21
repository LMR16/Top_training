import os
import cv2
import pickle
import numpy as np
import pandas as pd
from ultralytics import YOLO

class BallTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_frames(self, frames, read_stub=False, stub_path=None):
        if read_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                cached_detections = pickle.load(f)
            # Garante que o cache não está vazio e corresponde exatamente ao número de frames do vídeo atual
            if len(cached_detections) > 0 and len(cached_detections) == len(frames):
                return cached_detections

        ball_detections = []
        prev_gray = None
        last_center = None
        last_det_idx = -999

        for idx, frame in enumerate(frames):
            curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ball_dict = self.detect_frame(
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

            ball_detections.append(ball_dict)
            prev_gray = curr_gray

        ball_detections = self._remove_isolated_spikes(ball_detections)
        
        if stub_path is not None and len(ball_detections) > 0:
            with open(stub_path, 'wb') as f:
                pickle.dump(ball_detections, f)
                
        return ball_detections

    # def detect_frame(self, frame):
    #     # verbose=False limpa o terminal durante o processamento
    #     results = self.model.predict(frame, conf=0.15, verbose=False)[0]
    #     ball_dict = {}
        
    #     # Filtro de Falsos Positivos: Pega apenas a bola com maior nível de confiança
    #     if len(results.boxes) > 0:
    #         best_box = max(results.boxes, key=lambda b: b.conf[0].item())
    #         ball_dict[1] = best_box.xyxy[0].tolist()
            
    #     return ball_dict

    def detect_frame(self, frame, curr_gray=None, prev_gray=None, last_center=None, frames_since_last=999):
        # Executa a deteção em imgsz=640 (resolução nativa do treino do yolov8_best_2.pt)
        results = self.model.predict(
            frame,
            conf=0.15,
            imgsz=640,
            verbose=False
        )[0]
        
        ball_dict = {}
        if len(results.boxes) == 0:
            return ball_dict

        h, w = frame.shape[:2]
        candidates = []

        for box in results.boxes:
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

            # 1. Filtro de Movimento Real (cv2.absdiff) para descartar bolas paradas no chão e falsos positivos fixos
            if curr_gray is not None and prev_gray is not None:
                pad = 4
                ix1, iy1 = max(0, int(x1) - pad), max(0, int(y1) - pad)
                ix2, iy2 = min(w, int(x2) + pad), min(h, int(y2) + pad)
                crop_curr = curr_gray[iy1:iy2, ix1:ix2]
                crop_prev = prev_gray[iy1:iy2, ix1:ix2]

                if crop_curr.size > 0:
                    motion_diff = float(np.mean(cv2.absdiff(crop_curr, crop_prev)))
                    if motion_diff < 5.5:
                        continue

            # 2. Continuidade Espacial: prioriza caixas próximas da última posição conhecida da bola em jogo
            score = conf
            if last_center is not None and frames_since_last <= 8:
                dist = float(np.hypot(cx - last_center[0], cy - last_center[1]))
                max_allowed_dist = 160.0 * frames_since_last
                if dist <= max_allowed_dist:
                    score += 0.25 * (1.0 - dist / max_allowed_dist)
                elif conf < 0.35:
                    continue

            candidates.append((score, [x1, y1, x2, y2]))

        if candidates:
            best_bbox = max(candidates, key=lambda item: item[0])[1]
            # Mantém chave 1 padronizada para a bola em jogo (compatível com a interpolação do Pandas)
            ball_dict[1] = best_bbox
            
        return ball_dict

    def _remove_isolated_spikes(self, ball_positions, window=3, max_jump=220.0):
        cleaned = [dict(d) for d in ball_positions]
        n = len(cleaned)
        for i in range(n):
            if 1 not in cleaned[i]:
                continue
            x1, y1, x2, y2 = cleaned[i][1]
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

            neighbor_dists = []
            for j in range(max(0, i - window), min(n, i + window + 1)):
                if i == j or 1 not in cleaned[j]:
                    continue
                nx1, ny1, nx2, ny2 = cleaned[j][1]
                ncx, ncy = (nx1 + nx2) / 2.0, (ny1 + ny2) / 2.0
                neighbor_dists.append(np.hypot(cx - ncx, cy - ncy) / abs(i - j))

            if not neighbor_dists or min(neighbor_dists) > max_jump:
                cleaned[i] = {}

        return cleaned

    def draw_boxes(self, video_frames, ball_detections, bounces=None, trail_length=10):
        if bounces is None:
            bounces = []

        output_frames = []
        for idx, (frame, ball_dict) in enumerate(zip(video_frames, ball_detections)):
            # Desenha diretamente no frame (in-place) para não duplicar o consumo de memória RAM
            # Desenha o rastro recente da bola para evidenciar a parábola e o quique
            trail_points = []
            for t in range(max(0, idx - trail_length), idx + 1):
                if 1 in ball_detections[t]:
                    bx1, by1, bx2, by2 = ball_detections[t][1]
                    trail_points.append((int((bx1 + bx2) / 2), int((by1 + by2) / 2)))
                else:
                    trail_points = []

            for p_idx in range(1, len(trail_points)):
                cv2.line(frame, trail_points[p_idx - 1], trail_points[p_idx], (0, 200, 255), 2)

            # Desenha as marcações fixas de todos os quiques já ocorridos até este frame
            active_bounces = [b for b in bounces if b['frame'] <= idx]
            for b_num, b in enumerate(active_bounces, start=1):
                bx, by = int(b['x']), int(b['y'])
                cv2.circle(frame, (bx, by), 10, (0, 0, 255), 2)
                cv2.circle(frame, (bx, by), 4, (0, 255, 255), -1)
                cv2.putText(
                    frame,
                    f"Quique #{b_num}",
                    (bx + 12, by - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2
                )

            for track_id, bbox in ball_dict.items():
                x1, y1, x2, y2 = bbox
                
                # Desenho do centro da bola (mais moderno para rastreio desportivo)
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                cv2.circle(frame, (center_x, center_y), 6, (0, 255, 0), -1)
                
                # Caixa delimitadora subtil
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)

            # Painel com contador de quiques
            cv2.rectangle(frame, (20, 20), (310, 75), (20, 20, 20), -1)
            cv2.putText(
                frame,
                f"Quiques: {len(active_bounces)}",
                (35, 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )

            output_frames.append(frame)
        return output_frames

    def interpolate_ball_positions(self, ball_positions, max_gap=12):
        # Extrai coordenadas para colunas numéricas independentes
        # O Pandas não consegue interpolar listas embutidas [x1, y1, x2, y2]
        positions = [x.get(1, [np.nan, np.nan, np.nan, np.nan]) for x in ball_positions]
        df = pd.DataFrame(positions, columns=['x1', 'y1', 'x2', 'y2'], dtype=float)
        
        # Interpolação linear apenas de buracos curtos (até max_gap frames) dentro da jogada
        df = df.interpolate(method='linear', limit=max_gap, limit_area='inside')
        
        # Reconstrói a lista de dicionários no formato original
        interpolated_positions = []
        for _, row in df.iterrows():
            if row.isna().any():
                interpolated_positions.append({})
            else:
                interpolated_positions.append({1: row.tolist()})
        return interpolated_positions

    def detect_bounces(self, ball_positions, min_drop_px=6.0, min_rise_px=5.0, cooldown_frames=12):
        """Detecta momentos de quique onde a trajetória vertical Y atinge um máximo local (descida -> subida)."""
        centers_x = []
        centers_y = []
        for d in ball_positions:
            if 1 in d:
                x1, y1, x2, y2 = d[1]
                centers_x.append((x1 + x2) / 2.0)
                centers_y.append((y1 + y2) / 2.0)
            else:
                centers_x.append(np.nan)
                centers_y.append(np.nan)

        s_x = pd.Series(centers_x, dtype=float)
        s_y = pd.Series(centers_y, dtype=float)
        y_smooth = s_y.rolling(window=3, center=True, min_periods=1).mean()

        bounces = []
        n = len(ball_positions)
        look = 3
        last_bounce_frame = -999

        for i in range(look, n - look):
            if (i - last_bounce_frame) < cooldown_frames:
                continue

            window_vals = y_smooth.iloc[i - look : i + look + 1]
            if window_vals.isna().any():
                continue

            curr_y = float(y_smooth.iloc[i])
            if curr_y < float(window_vals.max()):
                continue

            drop_before = curr_y - float(y_smooth.iloc[i - look])
            rise_after = curr_y - float(y_smooth.iloc[i + look])

            if drop_before >= min_drop_px and rise_after >= min_rise_px:
                bounces.append({
                    'frame': i,
                    'x': float(s_x.iloc[i]),
                    'y': float(s_y.iloc[i])
                })
                last_bounce_frame = i

        return bounces