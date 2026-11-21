#!/usr/bin/env python3

from ultralytics import YOLO
import torch
import os
from datetime import datetime
import gc

print("=" * 80)
print("FINE-TUNING")
print("=" * 80)

gc.collect()
if torch.backends.mps.is_available():
    torch.mps.empty_cache()

print("\nVerificando hardware")
if torch.backends.mps.is_available():
    device = 'mps'
    print("MPS (Apple Silicon) detectado")

print(f"Dispositivo: {device}")

print("\n" + "=" * 80)
print("CONFIGURACION DE FINE-TUNING")
print("=" * 80)

MODELO_BASE = 'runs/detect/herramientas_v1/weights/best.pt'
DATASET_YAML = 'dataset.yaml'
EPOCHS = 50
BATCH_SIZE = 8
IMAGE_SIZE = 640
PATIENCE = 15
WORKERS = 4
LR_INICIAL = 0.001

print("\nVerificando archivos...")

if not os.path.exists(MODELO_BASE):
    print(f"Error: No se encuentra el modelo en {MODELO_BASE}")
    exit(1)

print("Modelo base encontrado")

if not os.path.exists(DATASET_YAML):
    print(f"Error: No se encuentra {DATASET_YAML}")
    exit(1)

print("Dataset encontrado")

print("\n" + "=" * 80)
print("CARGANDO MODELO ENTRENADO")
print("=" * 80)

try:
    model = YOLO(MODELO_BASE)
    print(f"Modelo cargado: {MODELO_BASE}")
    print(f"Clases del modelo: {model.names}")
except Exception as e:
    print(f"Error al cargar modelo: {e}")
    exit(1)

print("\n" + "=" * 80)
print("INICIANDO FINE-TUNING")
print("=" * 80)

inicio = datetime.now()

try:
    results = model.train(
        data=DATASET_YAML,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        device=device,
        patience=PATIENCE,
        save=True,
        project='runs/detect',
        name='herramientas_mejorado',
        exist_ok=True,
        workers=WORKERS,
        resume=True,
        pretrained=True,
        lr0=LR_INICIAL,
        lrf=0.0001,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=2,
        amp=True,
        cache='ram',
        iou=0.6,
        max_det=100,
        hsv_h=0.01,
        hsv_s=0.4,
        hsv_v=0.3,
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.5,
        mixup=0.0,
        verbose=True,
        plots=True,
        save_period=25,
        box=7.5,
        cls=0.5,
        dfl=1.5,
    )
    
    fin = datetime.now()
    duracion = fin - inicio
    
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    
    print("\n" + "=" * 80)
    print("FINE-TUNING COMPLETADO")
    print("=" * 80)
    print(f"Tiempo total: {duracion}")
    print(f"Modelo mejorado en: runs/detect/herramientas_mejorado/")
    
except KeyboardInterrupt:
    print("\nInterrumpido por el usuario")
    exit(0)
    
except Exception as e:
    print(f"\nError durante fine-tuning: {e}")
    exit(1)

print("\n" + "=" * 80)
print("COMPARACION: MODELO ORIGINAL vs MEJORADO")
print("=" * 80)

try:
    mejor_modelo = 'runs/detect/herramientas_mejorado/weights/best.pt'
    
    if os.path.exists(mejor_modelo):
        print(f"\nValidando modelo mejorado...")
        
        model_mejorado = YOLO(mejor_modelo)
        metrics_mejorado = model_mejorado.val()
        
        print("\nMODELO ORIGINAL:")
        print(f"   mAP50: 0.555 (55.5%)")
        print(f"   mAP50-95: 0.419 (41.9%)")
        print(f"   Precision: 0.499 (49.9%)")
        print(f"   Recall: 0.963 (96.3%)")
        
        print("\nMODELO MEJORADO:")
        print(f"   mAP50: {metrics_mejorado.box.map50:.3f} ({metrics_mejorado.box.map50*100:.1f}%)")
        print(f"   mAP50-95: {metrics_mejorado.box.map:.3f} ({metrics_mejorado.box.map*100:.1f}%)")
        print(f"   Precision: {metrics_mejorado.box.mp:.3f} ({metrics_mejorado.box.mp*100:.1f}%)")
        print(f"   Recall: {metrics_mejorado.box.mr:.3f} ({metrics_mejorado.box.mr*100:.1f}%)")
        
        mejora_map = (metrics_mejorado.box.map50 - 0.555) * 100
        mejora_precision = (metrics_mejorado.box.mp - 0.499) * 100
        
        print("\nMEJORAS:")
        if mejora_map > 0:
            print(f"   mAP50: +{mejora_map:.1f} puntos porcentuales")
        else:
            print(f"   mAP50: {mejora_map:.1f} puntos porcentuales")
            
        if mejora_precision > 0:
            print(f"   Precision: +{mejora_precision:.1f} puntos porcentuales")
        else:
            print(f"   Precision: {mejora_precision:.1f} puntos porcentuales")
        
        if metrics_mejorado.box.map50 > 0.70:
            print("\nEXCELENTE! El modelo mejoro significativamente")
            print("   Listo para usar en produccion")
        elif metrics_mejorado.box.map50 > 0.60:
            print("\nBIEN! Mejora notable en el modelo")
            print("   Aceptable para usar en la aplicacion")
        elif mejora_map > 0:
            print("\nMejora moderada. ")
        else:
            print("\nEl modelo no mejoro. Posibles causas:")
        
        
except Exception as e:
    print(f"Error en validacion: {e}")

print("=" * 80)
print("Fine-tuning completado exitosamente")
print("=" * 80)