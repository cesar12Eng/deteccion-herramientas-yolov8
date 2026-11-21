#!/usr/bin/env python3

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import os
from datetime import datetime
import time

print("=" * 80)
print("CLASIFICACION EN TIEMPO REAL - ResNet50")
print("=" * 80)

NUM_CLASSES = 1000

print(f"\nCargando modelo ResNet50 preentrenado (ImageNet)...")

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Dispositivo: {device}")

try:
    model = models.resnet50(pretrained=True)
    model = model.to(device)
    model.eval()
    print("Modelo cargado exitosamente")
    
except Exception as e:
    print(f"Error al cargar modelo: {e}")
    exit(1)

IMAGENET_LABELS = None
try:
    import urllib.request
    import json
    
    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
    with urllib.request.urlopen(url) as response:
        IMAGENET_LABELS = json.loads(response.read())
    print(f"Etiquetas de ImageNet cargadas: {len(IMAGENET_LABELS)} clases")
except Exception as e:
    print(f"No se pudieron cargar etiquetas de ImageNet: {e}")
    print("Usando índices numéricos")

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                       std=[0.229, 0.224, 0.225])
])

CONF_THRESHOLD = 0.3

print(f"\nConfiguracion:")
print(f"   Confianza minima: {CONF_THRESHOLD*100}%")
print(f"   Tamaño de entrada: 224x224")

print("\nIniciando camara...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo acceder a la camara")
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Camara iniciada correctamente")

print("\n" + "=" * 80)
print("CONTROLES:")
print("=" * 80)
print("   ESPACIO: Capturar y guardar clasificacion")
print("   +: Aumentar confianza (+5%)")
print("   -: Disminuir confianza (-5%)")
print("   Q o ESC: Salir")
print("=" * 80)
print("\nMostrando clasificacion en tiempo real...\n")

os.makedirs('capturas_clasificacion', exist_ok=True)

frames_procesados = 0
capturas = 0

fps_start_time = time.time()
fps_counter = 0
fps_display = 0

def clasificar_frame(frame):
    """Clasifica un frame y devuelve la clase predicha y la confianza"""
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        input_tensor = transform(pil_image)
        input_batch = input_tensor.unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(input_batch)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, predicted_idx = torch.max(probabilities, 0)
        
        if IMAGENET_LABELS:
            predicted_class = IMAGENET_LABELS[predicted_idx.item()]
        else:
            predicted_class = f"Clase_{predicted_idx.item()}"
        
        confidence_value = confidence.item()
        
        return predicted_class, confidence_value, probabilities.cpu().numpy(), predicted_idx.item()
        
    except Exception as e:
        print(f"Error en clasificación: {e}")
        return None, 0.0, None, None

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error al capturar frame")
            break
        
        predicted_class, confidence, all_probs, class_idx = clasificar_frame(frame)
        
        annotated_frame = frame.copy()
        
        fps_counter += 1
        if fps_counter >= 10:
            fps_end_time = time.time()
            fps_display = 10 / (fps_end_time - fps_start_time)
            fps_start_time = time.time()
            fps_counter = 0
        
        cv2.putText(annotated_frame, f"FPS: {fps_display:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(annotated_frame, f"Umbral: {CONF_THRESHOLD*100:.0f}%", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if predicted_class and confidence >= CONF_THRESHOLD:
            color = (0, 255, 0)
            text = f"{predicted_class}"
            conf_text = f"Confianza: {confidence*100:.1f}%"
        else:
            color = (0, 0, 255)
            text = "Sin deteccion clara"
            conf_text = f"Max: {confidence*100:.1f}%"
        
        cv2.putText(annotated_frame, text, 
                   (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(annotated_frame, conf_text, 
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if all_probs is not None and IMAGENET_LABELS:
            y_offset = 170
            cv2.putText(annotated_frame, "Top 5 predicciones:", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            top5_indices = all_probs.argsort()[-5:][::-1]
            for i, idx in enumerate(top5_indices):
                prob_text = f"{i+1}. {IMAGENET_LABELS[idx]}: {all_probs[idx]*100:.1f}%"
                cv2.putText(annotated_frame, prob_text, 
                           (10, y_offset + 25 + i*25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(annotated_frame, "ESPACIO: Capturar | +/-: Umbral | Q: Salir", 
                   (10, annotated_frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Clasificacion ResNet50 - Tiempo Real', annotated_frame)
        
        frames_procesados += 1
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(''):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'capturas_clasificacion/clasificacion_{timestamp}.jpg'
            cv2.imwrite(filename, annotated_frame)
            capturas += 1
            print(f"Captura {capturas} guardada: {filename}")
            if predicted_class:
                print(f"   Clase: {predicted_class} ({confidence*100:.1f}%)")
            
            white_frame = annotated_frame.copy()
            white_frame[:] = (255, 255, 255)
            cv2.imshow('Clasificacion ResNet50 - Tiempo Real', white_frame)
            cv2.waitKey(100)
        
        elif key == ord('+') or key == ord('='):
            CONF_THRESHOLD = min(0.95, CONF_THRESHOLD + 0.05)
            print(f"Umbral aumentado a: {CONF_THRESHOLD*100:.0f}%")
        
        elif key == ord('-') or key == ord('_'):
            CONF_THRESHOLD = max(0.05, CONF_THRESHOLD - 0.05)
            print(f"Umbral reducido a: {CONF_THRESHOLD*100:.0f}%")
        
        elif key == ord('q') or key == ord('Q') or key == 27:
            print("\nSaliendo...")
            break

except KeyboardInterrupt:
    print("\n\nInterrumpido por el usuario")

finally:
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 80)
    print("RESUMEN DE SESION")
    print("=" * 80)
    print(f"Frames procesados: {frames_procesados}")
    print(f"Capturas guardadas: {capturas}")
    if capturas > 0:
        print(f"Ubicacion: capturas_clasificacion/")
    print("=" * 80)
    print("Sesion finalizada")
    print("=" * 80)