from ultralytics import YOLO

# Carrega o modelo com os melhores pesos gerados no treinamento
model = YOLO('models/yolov8_best.pt')

# Executa a inferência no vídeo de entrada, salva o resultado e define a confiança mínima (20%)
result = model.predict('src\\input_videos\\input_video.mp4', conf=0.2, save=True)

print(result)
print("boxes:")
# Imprime as coordenadas (bounding boxes) encontradas no primeiro frame processado
for box in result[0].boxes:
    print(box)