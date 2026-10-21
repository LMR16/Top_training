import cv2
import os
from trackers.ball_tracker import BallTracker

def main():
    # 1. Configurar caminhos
    video_path = "src/input_videos/treino_3.mp4"
    output_dir = "runs/Ball_Tracker"
    model_path = "models/yolov8_best_2.pt"
    video_stem = os.path.splitext(os.path.basename(video_path))[0]
    model_stem = os.path.splitext(os.path.basename(model_path))[0]
    stub_path = f"stubs/{video_stem}_{model_stem}_detections.pkl" # Salva as deteções para não reprocessar nos testes

    # Criar pastas de saída caso não existam
    os.makedirs("stubs", exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Define o nome sequencial do vídeo (out_video_1.mp4, out_video_2.mp4, ...)
    seq_num = 1
    while os.path.exists(f"{output_dir}/out_video_{seq_num}.mp4"):
        seq_num += 1
    output_path = f"{output_dir}/out_video_{seq_num}.mp4"

    print(f"A carregar o vídeo ({video_path})...")
    # 2. Ler todos os frames do vídeo usando OpenCV
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []
    while True:
        sucesso, frame = cap.read()
        if not sucesso:
            break
        frames.append(frame)
    cap.release()
    if not frames:
        raise FileNotFoundError(f"Não foi possível carregar frames do vídeo: '{video_path}'. Verifique se o caminho está correto.")
    print(f"Vídeo carregado: {len(frames)} frames ({fps:.1f} FPS).")

    # 3. Inicializar o Rastreador da Bola
    print("A inicializar o modelo YOLO...")
    tracker = BallTracker(model_path)

    # 4. Detetar a bola (ou ler do stub se já foi detetado antes para poupar tempo)
    print("A iniciar a deteção (pode demorar na primeira vez)...")
    ball_detections = tracker.detect_frames(frames, read_stub=True, stub_path=stub_path)
    raw_count = sum(1 for d in ball_detections if 1 in d)
    print(f"Frames com bola em movimento detetada: {raw_count}/{len(frames)}")

    # 5. Interpolar os buracos (preencher posições nos frames em que o YOLO falhou)
    print("A interpolar dados perdidos...")
    ball_detections = tracker.interpolate_ball_positions(ball_detections)
    interp_count = sum(1 for d in ball_detections if 1 in d)
    print(f"Frames com bola após interpolação: {interp_count}/{len(frames)}")

    # 6. Detetar os momentos de quique da bola
    print("A detetar quiques da bola...")
    bounces = tracker.detect_bounces(ball_detections)
    print(f"Total de quiques detetados: {len(bounces)}")
    for idx_b, b in enumerate(bounces, start=1):
        print(f"  -> Quique #{idx_b}: Frame {b['frame']} ({b['frame']/fps:.2f}s) | Posição (x={b['x']:.1f}, y={b['y']:.1f})")

    # 7. Desenhar as caixas, rastro e quiques nos frames
    print("A desenhar as caixas e quiques no vídeo...")
    output_frames = tracker.draw_boxes(frames, ball_detections, bounces=bounces)

    # 8. Salvar o vídeo processado
    print("A exportar o vídeo final...")
    height, width, _ = output_frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec moderno para .mp4
    
    # Usa o FPS real do vídeo de entrada
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in output_frames:
        out.write(frame)
    out.release()

    print(f"Concluído! Vídeo salvo em: {output_path}")

if __name__ == "__main__":
    main()