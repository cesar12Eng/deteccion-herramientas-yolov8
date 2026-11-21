#!/usr/bin/env python3

from ultralytics import YOLO
import torch
import os
from datetime import datetime
import gc

print("=" * 80)
print("ENTRENAMIENTO YOLOV8 - MODO MÁXIMO RENDIMIENTO")
print("=" * 80)

gc.collect()
if torch.backends.mps.is_available():
    torch.mps.empty_cache()

print("\nVerificando hardware...")
if torch.backends.mps.is_available():
    device = 'mps'
    print("MPS (Apple Silicon) detectado - Entrenamiento acelerado por GPU")
    print("Modo: MÁXIMO RENDIMIENTO")
elif torch.cuda.is_available():
    device = 'cuda'
    print("CUDA (NVIDIA) detectado - Entrenamiento acelerado por GPU")
else:
    device = 'cpu'
    print("Solo CPU disponible - Entrenamiento será más lento")

print(f"Dispositivo seleccionado: {device}")


EPOCHS = 150             
BATCH_SIZE = 8           
IMAGE_SIZE = 640         
PATIENCE = 20            
MODELO_BASE = 'yolov8n.pt'  

DATASET_YAML = 'dataset.yaml'
WORKERS = 4  
SAVE_PERIOD = 25  
if not os.path.exists(DATASET_YAML):
    print(f"ERROR: No se encuentra {DATASET_YAML}")
    exit(1)

print("Archivo dataset.yaml encontrado")

try:
    model = YOLO(MODELO_BASE)
    print(f"Modelo {MODELO_BASE} cargado exitosamente")
except Exception as e:
    print(f"Error al cargar modelo: {e}")
    exit(1)

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
        name='herramientas_v1',  
        exist_ok=True,
        workers=WORKERS,
        
        amp=True,          
        cache='ram',        
        
        iou=0.6,            
        max_det=100,        
        
        lr0=0.01,
        lrf=0.001,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
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
        copy_paste=0.0,
        
        verbose=True,
        plots=True,
        save_period=SAVE_PERIOD,
        
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
    print("¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
    print("=" * 80)
    print(f"Tiempo total: {duracion}")
    print(f"Resultados: runs/detect/herramientas_v1/")
    
except KeyboardInterrupt:
    print("\nEntrenamiento interrumpido por el usuario")
    print("   Checkpoints guardados en: runs/detect/herramientas_v1/")
    exit(0)
    
except RuntimeError as e:
    if "out of memory" in str(e).lower():
        print("\nERROR DE MEMORIA")
        print("Solución: Reduce BATCH_SIZE a 8 o 4 en el script")
    else:
        print(f"\nError durante el entrenamiento: {e}")
    exit(1)
    
except Exception as e:
    print(f"\nError durante el entrenamiento: {e}")
    exit(1)

print("\n" + "=" * 80)
print("VALIDACIÓN DEL MODELO ENTRENADO")
print("=" * 80)

try:
    mejor_modelo = 'runs/detect/herramientas_v2/weights/best.pt'
    
    if os.path.exists(mejor_modelo):
        print(f"Cargando mejor modelo: {mejor_modelo}")
        
        model = YOLO(mejor_modelo)
        metrics = model.val()
        
        print("\nMÉTRICAS FINALES:")
        print("=" * 80)
        print(f"   mAP50 (precisión al 50%): {metrics.box.map50:.3f}")
        print(f"   mAP50-95 (precisión general): {metrics.box.map:.3f}")
        print(f"   Precisión: {metrics.box.mp:.3f}")
        print(f"   Recall: {metrics.box.mr:.3f}")
        print("=" * 80)
        
        if metrics.box.map50 > 0.85:
            print("\n¡EXCELENTE! Rendimiento superior al 85%")
            print("   Tu modelo está listo para producción")
        elif metrics.box.map50 > 0.70:
            print("\n¡MUY BIEN! Rendimiento bueno (70-85%)")
            print("   El modelo funciona correctamente")
        elif metrics.box.map50 > 0.50:
            print("\nACEPTABLE (50-70%)")
            print("   Considera agregar más imágenes para mejorar")
        else:
            print("\nBAJO RENDIMIENTO (<50%)")
            print("   Recomendaciones:")
            print("   • Revisar calidad de etiquetas")
            print("   • Capturar más imágenes")
            print("   • Verificar variedad en las fotos")
        
        print("\nArchivos generados:")
        archivos = [
            'results.png',
            'confusion_matrix.png',
            'F1_curve.png',
            'P_curve.png',
            'R_curve.png',
            'PR_curve.png'
        ]
        
        carpeta = 'runs/detect/herramientas_v1'
        for archivo in archivos:
            ruta = os.path.join(carpeta, archivo)
            if os.path.exists(ruta):
                print(f"   {archivo}")
        
    else:
        print("No se encontró el modelo entrenado")
        
except Exception as e:
    print(f"Error en validación: {e}")

print("\n" + "=" * 80)
print("¡ENTRENAMIENTO FINALIZADO!")
print("=" * 80)
print(f"""
Tu modelo está listo en:
   {os.path.abspath('runs/detect/herramientas_v1/weights/best.pt')}

PRÓXIMOS PASOS:

1. Revisa las métricas:
   open runs/detect/herramientas_v1/results.png
   open runs/detect/herramientas_v1/confusion_matrix.png

2. Prueba con una imagen:
   python probar_modelo.py

3. Detección en tiempo real:
   python deteccion_camara.py

4. Crear interfaz de usuario

¿Necesitas ayuda con alguno de estos pasos?
""")

print("=" * 80)
print("¡Felicidades por completar el entrenamiento!")
print("=" * 80)