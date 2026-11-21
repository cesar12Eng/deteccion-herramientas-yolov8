#!/usr/bin/env python3


from ultralytics import YOLO
import cv2
import sys
import os

print("=" * 80)
print("PRUEBA DE MODELO - DETECCIÓN DE HERRAMIENTAS")
print("=" * 80)

MODELO = 'runs/detect/herramientas_mejorado/weights/best.pt'

if not os.path.exists(MODELO):
    print(f"Error: No se encuentra el modelo en {MODELO}")
    print("   ¿El entrenamiento terminó correctamente?")
    exit(1)

print(f"Modelo encontrado: {MODELO}")

print("\nCargando modelo...")
try:
    model = YOLO(MODELO)
    print("Modelo cargado exitosamente")
    print(f"Clases del modelo: {model.names}")
except Exception as e:
    print(f"Error al cargar modelo: {e}")
    exit(1)

print("\n" + "=" * 80)
print("DETECCIÓN EN IMAGEN")
print("=" * 80)

if len(sys.argv) > 1:
    imagen_path = sys.argv[1]
else:
    print("\nOpciones:")
    print("   1. Arrastra una imagen aquí y presiona Enter")
    print("   2. Escribe la ruta completa de la imagen")
    print("   3. Presiona Enter para usar la cámara\n")
    
    imagen_path = input("Ruta de la imagen (o Enter para cámara): ").strip()
    
    imagen_path = imagen_path.replace("'", "").replace('"', '')

if not imagen_path:
    print("\nModo cámara no implementado en este script")
    print("   Usa: python deteccion_camara.py")
    exit(0)

if not os.path.exists(imagen_path):
    print(f"Error: No se encuentra la imagen en {imagen_path}")
    exit(1)

print(f"\nImagen encontrada: {os.path.basename(imagen_path)}")

print("\nDetectando herramientas...")
try:
    results = model(imagen_path, conf=0.25, iou=0.6)
    
    result = results[0]
    
    num_detecciones = len(result.boxes)
    
    print(f"\nResultados:")
    print("=" * 80)
    print(f"Detecciones totales: {num_detecciones}")
    
    if num_detecciones == 0:
        print("No se detectaron herramientas en la imagen")
        print("   Posibles razones:")
        print("   • La herramienta no está visible claramente")
        print("   • La herramienta no está en el dataset de entrenamiento")
        print("   • La confianza es muy baja (prueba bajando conf)")
    else:
        print("\nHerramientas detectadas:")
        print("-" * 80)
        
        for i, box in enumerate(result.boxes):
            clase_id = int(box.cls[0])
            clase_nombre = model.names[clase_id]
            confianza = float(box.conf[0])
            
            print(f"  {i+1}. {clase_nombre.upper()}")
            print(f"     Confianza: {confianza*100:.1f}%")
            
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            print(f"     Posición: ({int(x1)}, {int(y1)}) ({int(x2)}, {int(y2)})")
            print()
    
    imagen_resultado = result.plot()
    
    os.makedirs('resultados_pruebas', exist_ok=True)
    
    nombre_base = os.path.splitext(os.path.basename(imagen_path))[0]
    salida_path = f'resultados_pruebas/{nombre_base}_detectado.jpg'
    
    cv2.imwrite(salida_path, imagen_resultado)
    
    print("=" * 80)
    print(f"Imagen guardada en: {salida_path}")
    print("\nAbriendo imagen...")
    
    os.system(f'open "{salida_path}"')
    
    print("\nPresiona cualquier tecla en la ventana para cerrar")
    cv2.imshow('Detección de Herramientas', imagen_resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
except Exception as e:
    print(f"Error durante la detección: {e}")
    exit(1)

print("\n" + "=" * 80)
print("Prueba completada exitosamente")
print("=" * 80)
print("\nPróximos pasos:")
print("   • Prueba con más imágenes")
print("   • Ejecuta: python deteccion_camara.py para detección en tiempo real")
print("=" * 80)