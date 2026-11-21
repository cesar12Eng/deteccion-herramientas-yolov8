#!/usr/bin/env python3

import os
from pathlib import Path

print("=" * 80)
print("VERIFICADOR DE DATASET YOLO")
print("=" * 80)

base_path = Path('dataset')
splits = ['train', 'val']
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

total_images = 0
total_labels = 0
images_sin_labels = []
labels_sin_images = []

for split in splits:
    print(f"\nVerificando {split.upper()}:")
    print("-" * 80)
    
    images_path = base_path / 'images' / split
    labels_path = base_path / 'labels' / split
    
    if not images_path.exists():
        print(f"No existe: {images_path}")
        continue
    if not labels_path.exists():
        print(f"No existe: {labels_path}")
        continue
    
    images = []
    for ext in image_extensions:
        images.extend(list(images_path.glob(f"*{ext}")))
        images.extend(list(images_path.glob(f"*{ext.upper()}")))
    
    labels = list(labels_path.glob("*.txt"))
    
    print(f"Imágenes encontradas: {len(images)}")
    print(f"Etiquetas encontradas: {len(labels)}")
    
    total_images += len(images)
    total_labels += len(labels)
    
    images_stems = {img.stem for img in images}
    labels_stems = {lbl.stem for lbl in labels}
    
    sin_label = images_stems - labels_stems
    sin_imagen = labels_stems - images_stems
    
    if sin_label:
        print(f"\n{len(sin_label)} imágenes SIN etiqueta:")
        for stem in list(sin_label)[:5]:
            print(f"   - {stem}")
        if len(sin_label) > 5:
            print(f"   ... y {len(sin_label) - 5} más")
        images_sin_labels.extend(sin_label)
    
    if sin_imagen:
        print(f"\n{len(sin_imagen)} etiquetas SIN imagen:")
        for stem in list(sin_imagen)[:5]:
            print(f"   - {stem}")
        if len(sin_imagen) > 5:
            print(f"   ... y {len(sin_imagen) - 5} más")
        labels_sin_images.extend(sin_imagen)
    
    etiquetas_vacias = []
    etiquetas_con_error = []
    
    for label_file in labels[:10]:
        try:
            with open(label_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    etiquetas_vacias.append(label_file.stem)
                else:
                    lines = content.split('\n')
                    for line in lines:
                        parts = line.split()
                        if len(parts) != 5:
                            etiquetas_con_error.append(label_file.stem)
                            break
                        try:
                            [float(p) for p in parts]
                        except:
                            etiquetas_con_error.append(label_file.stem)
                            break
        except Exception as e:
            etiquetas_con_error.append(f"{label_file.stem} (error: {e})")
    
    if etiquetas_vacias:
        print(f"\n{len(etiquetas_vacias)} etiquetas VACÍAS:")
        for stem in etiquetas_vacias[:5]:
            print(f"   - {stem}.txt")
    
    if etiquetas_con_error:
        print(f"\n{len(etiquetas_con_error)} etiquetas con FORMATO INCORRECTO:")
        for stem in etiquetas_con_error[:5]:
            print(f"   - {stem}.txt")

print("\n" + "=" * 80)
print("RESUMEN GENERAL")
print("=" * 80)
print(f"Total imágenes: {total_images}")
print(f"Total etiquetas: {total_labels}")

if total_images == 0:
    print("\nNO HAY IMÁGENES")
    print("   Agrega imágenes en dataset/images/train/ y dataset/images/val/")
elif total_labels == 0:
    print("\nNO HAY ETIQUETAS - ESTE ES TU PROBLEMA")
    print("\nSOLUCIONES:")
    print("   1. Usa Roboflow (https://roboflow.com) para etiquetar")
    print("   2. Usa LabelImg: pip install labelImg")
    print("   3. Si ya tienes etiquetas, asegúrate que estén en:")
    print("      - dataset/labels/train/*.txt")
    print("      - dataset/labels/val/*.txt")
elif len(images_sin_labels) > 0:
    print(f"\n{len(images_sin_labels)} imágenes sin etiquetas")
    print("   Necesitas etiquetar estas imágenes antes de entrenar")
elif total_images == total_labels:
    print("\n¡DATASET CORRECTO!")
    print("   Todas las imágenes tienen sus etiquetas")
    print("\nPuedes proceder con el entrenamiento:")
    print("   python entrenar_modelo.py")
else:
    print(f"\nImágenes: {total_images}, Etiquetas: {total_labels}")
    print("   Hay un desbalance")

print("\n" + "=" * 80)
print("VERIFICANDO dataset.yaml")
print("=" * 80)

yaml_path = Path('dataset.yaml')
if yaml_path.exists():
    print("dataset.yaml encontrado")
    with open(yaml_path, 'r') as f:
        content = f.read()
        print("\nContenido:")
        print(content)
else:
    print("dataset.yaml NO encontrado")
    print("\nCrea el archivo dataset.yaml con:")
    print("""
path: /ruta/completa/a/tu/proyecto
train: dataset/images/train
val: dataset/images/val

nc: 4
names: ['clase1', 'clase2', 'clase3', 'clase4']
    """)

print("=" * 80)