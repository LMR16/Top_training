import cv2
import os
from pathlib import Path

# Configuração de caminhos
video_path = 'src/input_videos/quadra_3.MOV' # Caminho do seu vídeo
output_folder = 'src/frames_extraidos/video_3'

# Cria a pasta de saída se não existir
os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS)) # Descobre quantos frames o vídeo tem por segundo
frame_count = 0
saved_count = 0

print(f"Iniciando extração... (Vídeo a {fps} FPS)")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Salva exatamente 1 frame a cada segundo de vídeo
    if frame_count % fps == 0:
        filename = os.path.join(output_folder, f"quadra2_frame_{saved_count:04d}.jpg")
        cv2.imwrite(filename, frame)
        saved_count += 1
        
    frame_count += 1

cap.release()
print(f"Extração concluída! {saved_count} frames salvos na pasta: {output_folder}")