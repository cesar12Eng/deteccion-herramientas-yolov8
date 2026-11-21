import os
import shutil
import random
from pathlib import Path

HERRAMIENTAS = [
    "destornillador",
    "martillo",
    "pinza",
    "llave_inglesa"
]

CARPETA_TRAIN = "dataset/images/train"
CARPETA_VAL = "dataset/images/val"
PORCENTAJE_VALIDACION = 0.20

print("=" * 80)
print("DIVISIÓN AUTOMÁTICA DEL DATASET - TRAIN/VALIDATION")
print("=" * 80)
print(f"División: {int((1-PORCENTAJE_VALIDACION)*100)}% Train / {int(PORCENTAJE_VALIDACION*100)}% Validation")
print("=" * 80)

def dividir_herramienta(herramienta):
    carpeta_train_origen = os.path.join(CARPETA_TRAIN, herramienta)
    carpeta_val_destino = os.path.join(CARPETA_VAL, herramienta)
    
    if not os.path.exists(carpeta_train_origen):
        print(f"{herramienta}: No se encontró carpeta de entrenamiento - OMITIENDO")
        return None
    
    imagenes = [f for f in os.listdir(carpeta_train_origen) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(imagenes) == 0:
        print(f"{herramienta}: No se encontraron imágenes - OMITIENDO")
        return None
    
    ya_tiene_val = os.path.exists(carpeta_val_destino) and \
                   len([f for f in os.listdir(carpeta_val_destino) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) > 0
    
    if ya_tiene_val:
        respuesta = input(f"\n{herramienta} ya tiene imágenes de validación. ¿Reorganizar? (s/n): ").lower()
        if respuesta != 's':
            print(f"   Manteniendo división existente")
            return {
                'herramienta': herramienta,
                'total': len(imagenes),
                'train': len(imagenes),
                'val': len([f for f in os.listdir(carpeta_val_destino) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))]),
                'reorganizado': False
            }
        else:
            if os.path.exists(carpeta_val_destino):
                for img in os.listdir(carpeta_val_destino):
                    if img.lower().endswith(('.jpg', '.jpeg', '.png')):
                        shutil.move(
                            os.path.join(carpeta_val_destino, img),
                            os.path.join(carpeta_train_origen, img)
                        )
            imagenes = [f for f in os.listdir(carpeta_train_origen) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"\nProcesando: {herramienta.upper().replace('_', ' ')}")
    print(f"   Total de imágenes: {len(imagenes)}")
    
    random.seed(42)
    random.shuffle(imagenes)
    
    num_val = max(1, int(len(imagenes) * PORCENTAJE_VALIDACION))
    num_train = len(imagenes) - num_val
    
    imagenes_val = imagenes[:num_val]
    imagenes_train = imagenes[num_val:]
    
    print(f"   • Train: {num_train} imágenes ({int((num_train/len(imagenes))*100)}%)")
    print(f"   • Val: {num_val} imágenes ({int((num_val/len(imagenes))*100)}%)")
    
    os.makedirs(carpeta_val_destino, exist_ok=True)
    
    for img in imagenes_val:
        origen = os.path.join(carpeta_train_origen, img)
        destino = os.path.join(carpeta_val_destino, img)
        shutil.move(origen, destino)
    
    print(f"   División completada")
    
    return {
        'herramienta': herramienta,
        'total': len(imagenes),
        'train': num_train,
        'val': num_val,
        'reorganizado': True
    }

resultados = []

print("\nBuscando herramientas con imágenes...\n")

for herramienta in HERRAMIENTAS:
    resultado = dividir_herramienta(herramienta)
    if resultado:
        resultados.append(resultado)

if len(resultados) == 0:
    print("\nNo se encontraron herramientas para procesar.")
    print("   Asegúrate de haber capturado imágenes primero usando capturar_fotos.py")
else:
    print("\n" + "=" * 80)
    print("DIVISIÓN COMPLETADA - RESUMEN DEL DATASET")
    print("=" * 80)
    print(f"{'Herramienta':<20} {'Total':<10} {'Train':<10} {'Val':<10} {'Estado':<15}")
    print("-" * 80)
    
    total_imagenes = 0
    total_train = 0
    total_val = 0
    
    for res in resultados:
        estado = "Dividido" if res['reorganizado'] else "Existente"
        print(f"{res['herramienta']:<20} {res['total']:<10} {res['train']:<10} "
              f"{res['val']:<10} {estado:<15}")
        
        total_imagenes += res['total']
        total_train += res['train']
        total_val += res['val']
    
    print("-" * 80)
    print(f"{'TOTAL':<20} {total_imagenes:<10} {total_train:<10} {total_val:<10}")
    print("=" * 80)
    
    print("\nEstructura del dataset:")
    print(f"   {CARPETA_TRAIN}/")
    for res in resultados:
        print(f"      ├── {res['herramienta']}/ ({res['train']} imágenes)")
    print(f"   {CARPETA_VAL}/")
    for res in resultados:
        print(f"      ├── {res['herramienta']}/ ({res['val']} imágenes)")
    
    print("\n" + "=" * 80)
    print("SIGUIENTE PASO:")
    print("=" * 80)
    print("   Ya tienes el dataset dividido en Train/Validation")
    print("   Ahora necesitas etiquetar las imágenes con tu etiquetador_yolo.py")
    print("   Después podrás entrenar el modelo YOLOv8")
    print("=" * 80)