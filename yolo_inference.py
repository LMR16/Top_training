from ultralytics import YOLO

# Carrega o modelo com os melhores pesos gerados no treinamento
model = YOLO('models/yolov8_best_3.pt')

# Executa a inferência no vídeo de entrada, salva o resultado e define a confiança mínima (20%)
result = model.track('src\\input_videos\\quadra_3.MOV', conf=0.3, persist=True, tracker="bytetrack.yaml", save=True)

print(result)
print("boxes:")
# Imprime as coordenadas (bounding boxes) encontradas no primeiro frame processado
for box in result[0].boxes:
    print(box)