import os
import cv2
import pickle
import pandas as pd
from ultralytics import YOLO

class BallTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_frames(self, frames, read_stub=False, stub_path=None):
        if read_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                return pickle.load(f)

        ball_detections = []
        for frame in frames:
            ball_detections.append(self.detect_frame(frame))
        
        if stub_path is not None:
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

    def detect_frame(self, frame):
        # Utiliza o ByteTrack nativo para manter a identidade do objeto ao longo do tempo
        results = self.model.track(
            frame, 
            persist=True,        # Mantém a memória dos frames anteriores
            tracker="bytetrack.yaml", # Algoritmo de rastreio otimizado
            conf=0.10,           # Pode baixar a confiança, o tracker filtra o ruído
            verbose=False
        )[0]
        
        ball_dict = {}
        
        if len(results.boxes) > 0 and results.boxes.id is not None:
            # Pega na caixa com a maior confiança
            best_box = max(results.boxes, key=lambda b: b.conf[0].item())
            
            # O YOLO atribui um ID único a cada objeto detetado pelo tracker
            track_id = int(best_box.id[0].item()) 
            ball_dict[track_id] = best_box.xyxy[0].tolist()
            
        return ball_dict

    def draw_boxes(self, video_frames, ball_detections):
        output_frames = []
        for frame, ball_dict in zip(video_frames, ball_detections):
            for track_id, bbox in ball_dict.items():
                x1, y1, x2, y2 = bbox
                
                # Desenho do centro da bola (mais moderno para rastreio desportivo)
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                cv2.circle(frame, (center_x, center_y), 6, (0, 255, 0), -1)
                
                # Caixa delimitadora subtil
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)
            output_frames.append(frame)
        return output_frames

    def interpolate_ball_positions(self, ball_positions):
        # Extrai coordenadas para colunas numéricas independentes
        # O Pandas não consegue interpolar listas embutidas [x1, y1, x2, y2]
        positions = [x.get(1, [None, None, None, None]) for x in ball_positions]
        df = pd.DataFrame(positions, columns=['x1', 'y1', 'x2', 'y2'])
        
        # Interpolação linear de frames onde o YOLO falhou a deteção
        df = df.interpolate().bfill().ffill()
        
        # Reconstrói a lista de dicionários no formato original
        interpolated_positions = [{1: row.tolist()} for _, row in df.iterrows()]
        return interpolated_positions