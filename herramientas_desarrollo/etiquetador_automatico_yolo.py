#!/usr/bin/env python3

import cv2
import os
import glob
import numpy as np

CLASES = {
    0: "destornillador",
    1: "martillo", 
    2: "pinza",
    3: "llave_inglesa"
}

drawing = False
ix, iy = -1, -1
boxes = []
current_box = None
CLASE_ACTUAL = 0
CLASE_NOMBRE = ""

img_base = None
img_with_boxes = None
needs_redraw = True

def mouse_callback(event, x, y, flags, param):
    global ix, iy, drawing, boxes, current_box, needs_redraw
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        current_box = [x, y, x, y]
        needs_redraw = True
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_box[2] = x
            current_box[3] = y
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_box[2] = x
        current_box[3] = y
        
        width = abs(current_box[2] - current_box[0])
        height = abs(current_box[3] - current_box[1])
        
        if width > 10 and height > 10:
            x1 = min(current_box[0], current_box[2])
            y1 = min(current_box[1], current_box[3])
            x2 = max(current_box[0], current_box[2])
            y2 = max(current_box[1], current_box[3])
            
            boxes.append([x1, y1, x2, y2])
            print(f"    Cuadro {len(boxes)} agregado")
            needs_redraw = True
        
        current_box = None

def draw_boxes_optimized(img, boxes):
    """Dibuja los cuadros guardados en la imagen base (cache)"""
    display = img.copy()
    
    for box in boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(display, CLASE_NOMBRE, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return display

def draw_current_box(display, current_box):
    """Dibuja solo el cuadro temporal (más rápido)"""
    if current_box and drawing:
        x1, y1, x2, y2 = current_box
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)

def convert_to_yolo(boxes, img_width, img_height):
    yolo_data = []
    
    for box in boxes:
        x1, y1, x2, y2 = box
        
        center_x = ((x1 + x2) / 2) / img_width
        center_y = ((y1 + y2) / 2) / img_height
        width = abs(x2 - x1) / img_width
        height = abs(y2 - y1) / img_height
        
        yolo_data.append(f"{CLASE_ACTUAL} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")
    
    return "\n".join(yolo_data)

def save_annotation(image_name, boxes, img_width, img_height, carpeta_etiquetas):
    if len(boxes) == 0:
        return False
    
    os.makedirs(carpeta_etiquetas, exist_ok=True)
    
    label_name = os.path.splitext(image_name)[0] + ".txt"
    label_path = os.path.join(carpeta_etiquetas, label_name)
    
    yolo_data = convert_to_yolo(boxes, img_width, img_height)
    
    with open(label_path, 'w') as f:
        f.write(yolo_data)
    
    print(f"   Guardado: {label_name} ({len(boxes)} cuadros)")
    return True

def load_annotation(image_name, img_width, img_height, carpeta_etiquetas):
    label_name = os.path.splitext(image_name)[0] + ".txt"
    label_path = os.path.join(carpeta_etiquetas, label_name)
    
    if not os.path.exists(label_path):
        return []
    
    boxes = []
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                _, cx, cy, w, h = map(float, parts)
                
                center_x = cx * img_width
                center_y = cy * img_height
                width = w * img_width
                height = h * img_height
                
                x1 = int(center_x - width / 2)
                y1 = int(center_y - height / 2)
                x2 = int(center_x + width / 2)
                y2 = int(center_y + height / 2)
                
                boxes.append([x1, y1, x2, y2])
    
    return boxes

def etiquetar_herramienta(clase_id, clase_nombre, conjunto):
    global boxes, drawing, current_box, CLASE_ACTUAL, CLASE_NOMBRE
    global img_base, img_with_boxes, needs_redraw
    
    CLASE_ACTUAL = clase_id
    CLASE_NOMBRE = clase_nombre
    
    carpeta_imagenes = f"dataset/images/{conjunto}/{clase_nombre}"
    carpeta_etiquetas = f"dataset/labels/{conjunto}"
    
    print("\n" + "=" * 70)
    print(f"   ETIQUETANDO: {clase_nombre.upper()} ({conjunto.upper()})")
    print("=" * 70)
    
    if not os.path.exists(carpeta_imagenes):
        print(f"  Error: No existe {carpeta_imagenes}")
        return 0
    
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        image_paths.extend(glob.glob(os.path.join(carpeta_imagenes, ext)))
    image_paths.sort()
    
    if len(image_paths) == 0:
        print(f"   No se encontraron imágenes en {carpeta_imagenes}")
        return 0
    
    print(f"  Imágenes encontradas: {len(image_paths)}")
    print(f"  Guardando etiquetas en: {carpeta_etiquetas}")
    print("\n" + "=" * 70)
    print("  CONTROLES:")
    print("=" * 70)
    print("    Click + Arrastrar: Crear cuadro delimitador")
    print("  D o : Siguiente imagen (guarda automáticamente)")
    print("  A o : Imagen anterior")
    print("  S: Guardar etiqueta")
    print("  C: Limpiar todos los cuadros")
    print("  Backspace: Borrar último cuadro")
    print("  Q o ESC: Terminar con esta herramienta")
    print("=" * 70)
    
    current_index = 0
    labeled_count = 0
    
    window_name = f'Etiquetador: {clase_nombre} ({conjunto})'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    cv2.resizeWindow(window_name, 1280, 720)
    
    while current_index < len(image_paths):
        image_path = image_paths[current_index]
        image_name = os.path.basename(image_path)
        
        img_base = cv2.imread(image_path)
        if img_base is None:
            print(f"    Error al cargar: {image_name}")
            current_index += 1
            continue
        
        img_height, img_width = img_base.shape[:2]
        
        max_display_width = 1920
        max_display_height = 1080
        if img_width > max_display_width or img_height > max_display_height:
            scale = min(max_display_width / img_width, max_display_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img_base = cv2.resize(img_base, (new_width, new_height))
            img_height, img_width = img_base.shape[:2]
        
        boxes = load_annotation(image_name, img_width, img_height, carpeta_etiquetas)
        needs_redraw = True
        
        print(f"\nImagen {current_index + 1}/{len(image_paths)}: {image_name}")
        if len(boxes) > 0:
            print(f"    Cuadros cargados: {len(boxes)}")
        
        img_with_boxes = draw_boxes_optimized(img_base, boxes)
        
        while True:
            if needs_redraw:
                img_with_boxes = draw_boxes_optimized(img_base, boxes)
                needs_redraw = False
            
            display = img_with_boxes.copy()
            
            if drawing and current_box:
                draw_current_box(display, current_box)
            
            info_text = f"{clase_nombre} | {current_index + 1}/{len(image_paths)} | Cuadros: {len(boxes)} | Etiquetadas: {labeled_count}"
            cv2.putText(display, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
            
            cv2.putText(display, "D: Siguiente | A: Anterior | S: Guardar | C: Limpiar | Q: Salir",
                       (10, img_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            cv2.imshow(window_name, display)
            
            wait_time = 10 if not drawing else 16
            key = cv2.waitKey(wait_time) & 0xFF
            
            if key == ord('d') or key == ord('D') or key == 83:
                if save_annotation(image_name, boxes, img_width, img_height, carpeta_etiquetas):
                    labeled_count += 1
                current_index += 1
                break
            
            elif key == ord('a') or key == ord('A') or key == 81:
                if current_index > 0:
                    if len(boxes) > 0:
                        save_annotation(image_name, boxes, img_width, img_height, carpeta_etiquetas)
                    current_index -= 1
                    break
            
            elif key == ord('s') or key == ord('S'):
                if save_annotation(image_name, boxes, img_width, img_height, carpeta_etiquetas):
                    labeled_count += 1
                    needs_redraw = True
            
            elif key == ord('c') or key == ord('C'):
                boxes = []
                needs_redraw = True
                print("    Cuadros limpiados")
            
            elif key == 8 or key == 127:
                if len(boxes) > 0:
                    boxes.pop()
                    needs_redraw = True
                    print(f"    Último cuadro borrado. Quedan: {len(boxes)}")
            
            elif key == ord('q') or key == ord('Q') or key == 27:
                if len(boxes) > 0:
                    save_annotation(image_name, boxes, img_width, img_height, carpeta_etiquetas)
                cv2.destroyAllWindows()
                print(f"\n  Completado: {labeled_count} imágenes etiquetadas")
                return labeled_count
    
    cv2.destroyAllWindows()
    print(f"\n  ¡Completado! {labeled_count} imágenes etiquetadas")
    return labeled_count

def menu_principal():
    print("\n" + "=" * 70)
    print("   ETIQUETADOR OPTIMIZADO DE HERRAMIENTAS")
    print("=" * 70)
    print("\nClases disponibles:")
    for id, nombre in CLASES.items():
        print(f"  {id}: {nombre}")
    
    print("\n¿Qué deseas etiquetar?")
    print("  1. Etiquetar TODO (4 herramientas × train + val)")
    print("  2. Etiquetar solo TRAIN (4 herramientas)")
    print("  3. Etiquetar solo VAL (4 herramientas)")
    print("  4. Etiquetar una herramienta específica")
    print("  0. Salir")
    
    return input("\nSelecciona opción: ").strip()

def main():
    total_etiquetadas = 0
    
    while True:
        opcion = menu_principal()
        
        if opcion == "0":
            print("\n¡Hasta luego!")
            break
        
        elif opcion == "1":
            print("\nEtiquetando TODAS las herramientas (train + val)...")
            for clase_id, clase_nombre in CLASES.items():
                print(f"\n{'='*70}")
                print(f"TRAIN - {clase_nombre}")
                print(f"{'='*70}")
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "train")
                
                print(f"\n{'='*70}")
                print(f"VAL - {clase_nombre}")
                print(f"{'='*70}")
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "val")
        
        elif opcion == "2":
            print("\nEtiquetando solo TRAIN...")
            for clase_id, clase_nombre in CLASES.items():
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "train")
        
        elif opcion == "3":
            print("\nEtiquetando solo VAL...")
            for clase_id, clase_nombre in CLASES.items():
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "val")
        
        elif opcion == "4":
            print("\nSelecciona herramienta:")
            for id, nombre in CLASES.items():
                print(f"  {id}: {nombre}")
            clase_id = int(input("ID de herramienta: "))
            
            if clase_id not in CLASES:
                print("ID inválido")
                continue
            
            clase_nombre = CLASES[clase_id]
            
            print("\nSelecciona conjunto:")
            print("  1. Train")
            print("  2. Val")
            print("  3. Ambos")
            conjunto_op = input("Opción: ").strip()
            
            if conjunto_op == "1":
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "train")
            elif conjunto_op == "2":
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "val")
            elif conjunto_op == "3":
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "train")
                total_etiquetadas += etiquetar_herramienta(clase_id, clase_nombre, "val")
        
        else:
            print("Opción inválida")
    
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"Total de imágenes etiquetadas: {total_etiquetadas}")
    print("Etiquetas guardadas en: dataset/labels/train y dataset/labels/val")
    print("\nPróximo paso: Entrenar el modelo YOLOv8")
    print("=" * 70)

if __name__ == "__main__":
    main()