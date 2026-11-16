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

    def detect_frame(self, frame, curr_gray=None, prev_gray=None, last_center=None, frames_since_last=999, imgsz=640):
        results = self.model.predict(
            frame,
            conf=0.15,
            imgsz=imgsz,
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

            # 1. Filtro de Movimento Real (cv2.absdiff) para descartar bolas paradas no chão
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
            trail_points = []
            for t in range(max(0, idx - trail_length), idx + 1):
                if 1 in ball_detections[t]:
                    bx1, by1, bx2, by2 = ball_detections[t][1]
                    trail_points.append((int((bx1 + bx2) / 2), int((by1 + by2) / 2)))
                else:
                    trail_points = []

            for p_idx in range(1, len(trail_points)):
                cv2.line(frame, trail_points[p_idx - 1], trail_points[p_idx], (0, 200, 255), 2)

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
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                cv2.circle(frame, (center_x, center_y), 6, (0, 255, 0), -1)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)

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
        positions = [x.get(1, [np.nan, np.nan, np.nan, np.nan]) for x in ball_positions]
        df = pd.DataFrame(positions, columns=['x1', 'y1', 'x2', 'y2'], dtype=float)
        df = df.interpolate(method='linear', limit=max_gap, limit_area='inside')

        interpolated_positions = []
        for _, row in df.iterrows():
            if row.isna().any():
                interpolated_positions.append({})
            else:
                interpolated_positions.append({1: row.tolist()})
        return interpolated_positions

    def detect_bounces(self, ball_positions, min_drop_px=6.0, min_rise_px=5.0, cooldown_frames=12):
        """
        Detecta momentos reais de quique no solo e descarta rebatidas de raquete (strokes):
          1. Identifica tanto inversões verticais clássicas quanto quiques em perspectiva
             (onde a bola que vem em direção à câmera freia bruscamente em Y ao tocar o piso).
          2. Filtro Anti-Rebatida por Restituição Física: num quique passivo no solo (e < 1),
             a velocidade de subida nunca supera em >32% a velocidade de queda anterior.
             Quando o jogador rebate com a raquete de volta para a rede, há forte injeção de
             energia cinética para cima (rise_4 > 1.32 * drop_4) e/ou inversão horizontal brusca.
        """
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
        n = len(ball_positions)
        bounces = []
        last_bounce_frame = -999

        for i in range(3, n - 4):
            if (i - last_bounce_frame) < cooldown_frames:
                continue

            win_x = s_x.iloc[i - 3 : i + 4]
            win_y = s_y.iloc[i - 3 : i + 4]
            if win_y.isna().any() or win_x.isna().any():
                continue

            # 1. Descarta cortes de cena ou troca de bola (salto > 220 px entre frames adjacentes)
            step_dists = np.hypot(np.diff(win_x.values), np.diff(win_y.values))
            if np.max(step_dists) > 220.0:
                continue

            curr_y = float(s_y.iloc[i])
            curr_x = float(s_x.iloc[i])

            y_prev3 = float(s_y.iloc[i - 3])
            y_prev1 = float(s_y.iloc[i - 1])
            drop_3 = curr_y - y_prev3
            if drop_3 < min_drop_px or curr_y < y_prev1:
                continue

            y_next1 = float(s_y.iloc[i + 1])
            y_next2 = float(s_y.iloc[i + 2])
            y_next3 = float(s_y.iloc[i + 3])
            min_after = min(y_next1, y_next2, y_next3)
            rise_3 = curr_y - min_after

            # Caso A: Quique com inversão vertical clássica
            is_classic_bounce = (curr_y >= float(np.max(win_y.values)) - 0.5) and (rise_3 >= min_rise_px)

            # Caso B: Quique em perspectiva (bola rápida vindo na direção da câmera)
            dy_after1 = y_next1 - curr_y
            dy_after2 = y_next2 - y_next1
            is_perspective_bounce = (
                drop_3 >= 28.0
                and curr_y >= y_prev1
                and curr_y >= y_next1
                and rise_3 >= 0.5
                and dy_after1 <= 0.0
                and dy_after2 <= 1.5
            )

            if not (is_classic_bounce or is_perspective_bounce):
                continue

            # --- FILTRO ANTI-REBATIDA (DESCARTE DE GOLPES DE RAQUETE) ---
            i_back = max(0, i - 4)
            i_fwd = min(n - 1, i + 4)
            drop_4 = curr_y - float(s_y.iloc[i_back]) if not np.isnan(s_y.iloc[i_back]) else drop_3
            rise_4 = curr_y - float(s_y.iloc[i_fwd]) if not np.isnan(s_y.iloc[i_fwd]) else rise_3

            dx_before = curr_x - float(s_x.iloc[i - 3])
            dx_after = float(s_x.iloc[i + 3]) - curr_x

            # 1) Super-aceleração pós-impacto (raquete injeta velocidade superior à queda livre)
            if rise_4 > 95.0 and rise_4 > 1.32 * max(drop_4, 8.0):
                continue

            # 2) Inversão de sentido horizontal X combinada com disparo rápido para a outra meia-quadra
            if abs(dx_before) >= 12.0 and abs(dx_after) >= 10.0 and (dx_before * dx_after < 0) and rise_3 >= 45.0:
                continue

            bounces.append({
                'frame': i,
                'x': curr_x,
                'y': curr_y
            })
            last_bounce_frame = i

        return bounces
