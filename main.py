import cv2
import os
from trackers.ball_tracker import BallTracker

def main():
    # 1. Configurar caminhos
    video_path = "src/input_videos/8224226-hd_1280_720_30fps.mp4"
    output_path = "runs/output_video.mp4"
    model_path = "models/yolov8_best.pt"
    stub_path = "stubs/ball_detections.pkl" # Salva as deteções para não reprocessar nos testes

    # Criar pastas de saída caso não existam
    os.makedirs("stubs", exist_ok=True)
    os.makedirs("runs", exist_ok=True)

    print("A carregar o vídeo...")
    # 2. Ler todos os frames do vídeo usando OpenCV
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        sucesso, frame = cap.read()
        if not sucesso:
            break
        frames.append(frame)
    cap.release()
    print(f"Vídeo carregado: {len(frames)} frames.")

    # 3. Inicializar o Rastreador da Bola
    print("A inicializar o modelo YOLO...")
    tracker = BallTracker(model_path)

    # 4. Detetar a bola (ou ler do stub se já foi detetado antes para poupar tempo)
    print("A iniciar a deteção (pode demorar na primeira vez)...")
    ball_detections = tracker.detect_frames(frames, read_stub=True, stub_path=stub_path)

    # 5. Interpolar os buracos (preencher posições nos frames em que o YOLO falhou)
    print("A interpolar dados perdidos...")
    ball_detections = tracker.interpolate_ball_positions(ball_detections)

    # 6. Desenhar as caixas nos frames
    print("A desenhar as caixas no vídeo...")
    output_frames = tracker.draw_boxes(frames, ball_detections)

    # 7. Salvar o vídeo processado
    print("A exportar o vídeo final...")
    height, width, _ = output_frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec moderno para .mp4
    
    # 30.0 é o FPS do vídeo. Ajuste se o seu vídeo original for de 60fps
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

    for frame in output_frames:
        out.write(frame)
    out.release()

    print(f"Concluído! Vídeo salvo em: {output_path}")

if __name__ == "__main__":
    main()