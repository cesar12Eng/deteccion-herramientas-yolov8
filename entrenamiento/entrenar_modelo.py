#!/usr/bin/env python3

from ultralytics import YOLO
import torch
import os
from datetime import datetime
import gc

print("=" * 80)
print("ENTRENAMIENTO YOLOV8 - MODO REANUDACIÓN")
print("=" * 80)

gc.collect()
if torch.backends.mps.is_available():
    torch.mps.empty_cache()

print("\nVerificando hardware...")
if torch.backends.mps.is_available():
    device = 'mps'
    print("MPS (Apple Silicon) - GPU acelerada")
elif torch.cuda.is_available():
    device = 'cuda'
    print("CUDA (NVIDIA) - GPU acelerada")
else:
    device = 'cpu'
    print("Solo CPU disponible")

print(f"Dispositivo: {device}")

print("\n" + "=" * 80)
print("CONFIGURACIÓN")
print("=" * 80)

EPOCHS = 100
BATCH_SIZE = 8
IMAGE_SIZE = 640
PATIENCE = 20
WORKERS = 4
SAVE_PERIOD = 25

CHECKPOINT = 'runs/detect/herramientas_v1/weights/last.pt'
REANUDAR = True

DATASET_YAML = 'dataset.yaml'

print(f"""
Configuración:
   • Modo: {'REANUDACIÓN' if REANUDAR else 'NUEVO'}
   • {'Checkpoint' if REANUDAR else 'Modelo base'}: {CHECKPOINT if REANUDAR else 'yolov8n.pt'}
   • Épocas: {EPOCHS}
   • Batch size: {BATCH_SIZE}
   • Workers: {WORKERS}
   • Dispositivo: {device}
""")

if REANUDAR:
    if not os.path.exists(CHECKPOINT):
        print(f"ERROR: No se encuentra checkpoint: {CHECKPOINT}")
        print("\nOpciones:")
        print("   1. Verifica la ruta del checkpoint")
        print("   2. Cambia REANUDAR = False para entrenar desde cero")
        exit(1)
    print(f"Checkpoint encontrado: {CHECKPOINT}")
else:
    if not os.path.exists(DATASET_YAML):
        print(f"ERROR: No se encuentra {DATASET_YAML}")
        exit(1)
    print(f"Dataset encontrado: {DATASET_YAML}")

print("\n" + "=" * 80)
print("CARGANDO MODELO")
print("=" * 80)

try:
    if REANUDAR:
        model = YOLO(CHECKPOINT)
        print(f"Modelo cargado desde checkpoint (época 10)")
    else:
        model = YOLO('yolov8n.pt')
        print(f"Modelo YOLOv8n cargado (inicio desde cero)")
except Exception as e:
    print(f"Error al cargar modelo: {e}")
    exit(1)

print("\n" + "=" * 80)
print("INICIANDO ENTRENAMIENTO")
print("=" * 80)

if REANUDAR:
    print("Continuando desde época 10...")
    print("Tiempo estimado: 15-20 minutos")
else:
    print("Entrenamiento nuevo desde época 1...")
    print("Tiempo estimado: 20-30 minutos")

print("\nTIPS:")
print("   • NO abras apps pesadas")
print("   • Mantén conectado el cargador")
print("   • El ventilador puede activarse\n")

inicio = datetime.now()

try:
    if REANUDAR:
        print("Reanudando con configuración optimizada...")
        
        results = model.train(
            resume=True,
            device=device,
            epochs=100,
        )
    else:
        results = model.train(
            data=DATASET_YAML,
            epochs=EPOCHS,
            imgsz=IMAGE_SIZE,
            batch=BATCH_SIZE,
            device=device,
            patience=PATIENCE,
            save=True,
            project='runs/detect',
            name='herramientas_v1',
            exist_ok=True,
            workers=WORKERS,
            
            amp=True,
            cache='ram',
            
            lr0=0.01,
            lrf=0.001,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            
            hsv_h=0.01,
            hsv_s=0.5,
            hsv_v=0.3,
            degrees=5.0,
            translate=0.1,
            scale=0.3,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=0.8,
            mixup=0.0,
            
            verbose=True,
            plots=True,
            save_period=SAVE_PERIOD,
        )
    
    fin = datetime.now()
    duracion = fin - inicio
    
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    
    print("\n" + "=" * 80)
    print("¡ENTRENAMIENTO COMPLETADO!")
    print("=" * 80)
    print(f"Tiempo total: {duracion}")
    print(f"Resultados: runs/detect/herramientas_v1/")
    
except KeyboardInterrupt:
    print("\nInterrumpido por usuario")
    print("   Checkpoint guardado en: runs/detect/herramientas_v1/")
    exit(0)
    
except RuntimeError as e:
    if "out of memory" in str(e).lower():
        print("\nERROR DE MEMORIA")
        print("Reduce BATCH_SIZE a 4 y vuelve a intentar")
    else:
        print(f"\nError: {e}")
    exit(1)
    
except Exception as e:
    print(f"\nError: {e}")
    exit(1)

print("\n" + "=" * 80)
print("VALIDACIÓN")
print("=" * 80)

try:
    mejor_modelo = 'runs/detect/herramientas_v1/weights/best.pt'
    
    if os.path.exists(mejor_modelo):
        print(f"Mejor modelo: {mejor_modelo}")
        
        model = YOLO(mejor_modelo)
        metrics = model.val()
        
        print("\nMÉTRICAS:")
        print("=" * 80)
        print(f"   mAP50: {metrics.box.map50:.3f}")
        print(f"   mAP50-95: {metrics.box.map:.3f}")
        print(f"   Precisión: {metrics.box.mp:.3f}")
        print(f"   Recall: {metrics.box.mr:.3f}")
        print("=" * 80)
        
        if metrics.box.map50 > 0.85:
            print("\n¡EXCELENTE! >85% precisión")
        elif metrics.box.map50 > 0.70:
            print("\n¡MUY BIEN! 70-85% precisión")
        elif metrics.box.map50 > 0.50:
            print("\nACEPTABLE 50-70% - Considera más imágenes")
        else:
            print("\nBAJO <50% - Revisa etiquetas o agrega más datos")
        
        print("\nArchivos generados:")
        archivos = ['results.png', 'confusion_matrix.png', 'F1_curve.png']
        carpeta = 'runs/detect/herramientas_v1'
        
        for archivo in archivos:
            if os.path.exists(os.path.join(carpeta, archivo)):
                print(f"   {archivo}")
    
except Exception as e:
    print(f"Error en validación: {e}")

print("\n" + "=" * 80)
print("¡FINALIZADO!")
print("=" * 80)
print(f"""
Modelo entrenado:
   {os.path.abspath('runs/detect/herramientas_v1/weights/best.pt')}

PRÓXIMOS PASOS:

1. Ver métricas:
   open runs/detect/herramientas_v1/results.png

2. Probar modelo:
   python probar_modelo.py

3. Detección en tiempo real:
   python app_taller.py

4. Base de datos de herramientas

5.  Interfaz gráfica
""")

print("=" * 80)
print("¡Felicidades!")
print("=" * 80)