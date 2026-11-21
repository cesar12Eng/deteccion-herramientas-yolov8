#!/usr/bin/env python3

import os
import glob

CLASES = {
    0: "destornillador",
    1: "martillo",
    2: "pinza",
    3: "llave_inglesa"
}

def contar_archivos(carpeta, extensiones):
    """Cuenta archivos con extensiones específicas"""
    archivos = []
    for ext in extensiones:
        archivos.extend(glob.glob(os.path.join(carpeta, f"**/*{ext}"), recursive=True))
    return archivos

def verificar_conjunto(conjunto):
    """Verifica un conjunto (train o val)"""
    print(f"\n{'='*70}")
    print(f"VERIFICANDO: {conjunto.upper()}")
    print(f"{'='*70}")
    
    carpeta_imagenes = f"dataset/images/{conjunto}"
    carpeta_etiquetas = f"dataset/labels/{conjunto}"
    
    if not os.path.exists(carpeta_imagenes):
        print(f"No existe: {carpeta_imagenes}")
        return
    
    if not os.path.exists(carpeta_etiquetas):
        print(f"No existe: {carpeta_etiquetas}")
        return
    
    total_imagenes = 0
    total_etiquetas = 0
    imagenes_sin_etiqueta = []
    etiquetas_sin_imagen = []
    estadisticas_clases = {i: 0 for i in range(len(CLASES))}
    
    for clase_id, clase_nombre in CLASES.items():
        carpeta_herramienta = os.path.join(carpeta_imagenes, clase_nombre)
        
        if not os.path.exists(carpeta_herramienta):
            print(f"\n{clase_nombre}: carpeta no existe")
            continue
        
        imagenes = []
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            imagenes.extend(glob.glob(os.path.join(carpeta_herramienta, f"*{ext}")))
        
        print(f"\n{clase_nombre.upper()}")
        print(f"   Imágenes encontradas: {len(imagenes)}")
        
        etiquetas_encontradas = 0
        for img_path in imagenes:
            img_nombre = os.path.basename(img_path)
            img_nombre_sin_ext = os.path.splitext(img_nombre)[0]
            
            etiqueta_path = os.path.join(carpeta_etiquetas, f"{img_nombre_sin_ext}.txt")
            
            if os.path.exists(etiqueta_path):
                etiquetas_encontradas += 1
                
                with open(etiqueta_path, 'r') as f:
                    lineas = f.readlines()
                    for linea in lineas:
                        partes = linea.strip().split()
                        if len(partes) >= 5:
                            clase_en_etiqueta = int(partes[0])
                            estadisticas_clases[clase_en_etiqueta] += 1
            else:
                imagenes_sin_etiqueta.append(img_path)
        
        print(f"   Etiquetas encontradas: {etiquetas_encontradas}")
        if etiquetas_encontradas < len(imagenes):
            print(f"    Faltan {len(imagenes) - etiquetas_encontradas} etiquetas")
        else:
            print(f"   Todas las imágenes tienen etiqueta")
        
        total_imagenes += len(imagenes)
        total_etiquetas += etiquetas_encontradas
    
    todas_etiquetas = glob.glob(os.path.join(carpeta_etiquetas, "*.txt"))
    for etiqueta_path in todas_etiquetas:
        etiqueta_nombre = os.path.basename(etiqueta_path)
        etiqueta_nombre_sin_ext = os.path.splitext(etiqueta_nombre)[0]
        
        encontrada = False
        for clase_nombre in CLASES.values():
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                img_path = os.path.join(carpeta_imagenes, clase_nombre, f"{etiqueta_nombre_sin_ext}{ext}")
                if os.path.exists(img_path):
                    encontrada = True
                    break
            if encontrada:
                break
        
        if not encontrada:
            etiquetas_sin_imagen.append(etiqueta_path)
    
    print(f"\n{'='*70}")
    print(f"RESUMEN - {conjunto.upper()}")
    print(f"{'='*70}")
    print(f"Total de imágenes: {total_imagenes}")
    print(f"Total de etiquetas: {total_etiquetas}")
    
    if len(imagenes_sin_etiqueta) > 0:
        print(f"\nImágenes sin etiqueta: {len(imagenes_sin_etiqueta)}")
        for img in imagenes_sin_etiqueta[:5]:
            print(f"   - {img}")
        if len(imagenes_sin_etiqueta) > 5:
            print(f"   ... y {len(imagenes_sin_etiqueta) - 5} más")
    
    if len(etiquetas_sin_imagen) > 0:
        print(f"\nEtiquetas sin imagen: {len(etiquetas_sin_imagen)}")
        for etq in etiquetas_sin_imagen[:5]:
            print(f"   - {etq}")
        if len(etiquetas_sin_imagen) > 5:
            print(f"   ... y {len(etiquetas_sin_imagen) - 5} más")
    
    print(f"\nObjetos etiquetados por clase:")
    for clase_id, clase_nombre in CLASES.items():
        count = estadisticas_clases[clase_id]
        print(f"   {clase_id} - {clase_nombre}: {count} objetos")
    
    if total_imagenes == total_etiquetas and len(imagenes_sin_etiqueta) == 0:
        print(f"\n¡TODO PERFECTO! Listo para entrenar")
    else:
        print(f"\nRevisa los problemas arriba antes de entrenar")
    
    return {
        'total_imagenes': total_imagenes,
        'total_etiquetas': total_etiquetas,
        'imagenes_sin_etiqueta': len(imagenes_sin_etiqueta),
        'etiquetas_sin_imagen': len(etiquetas_sin_imagen),
        'estadisticas_clases': estadisticas_clases
    }

def main():
    print("=" * 70)
    print("VERIFICADOR DE ETIQUETAS YOLO")
    print("=" * 70)
    
    stats_train = verificar_conjunto("train")
    
    stats_val = verificar_conjunto("val")
    
    print("\n" + "=" * 70)
    print("RESUMEN GLOBAL")
    print("=" * 70)
    
    if stats_train and stats_val:
        total_imgs = stats_train['total_imagenes'] + stats_val['total_imagenes']
        total_etqs = stats_train['total_etiquetas'] + stats_val['total_etiquetas']
        
        print(f"Total imágenes (train + val): {total_imgs}")
        print(f"Total etiquetadas (train + val): {total_etqs}")
        
        print(f"\nDistribución:")
        print(f"   Train: {stats_train['total_imagenes']} imágenes ({int(stats_train['total_imagenes']/total_imgs*100)}%)")
        print(f"   Val: {stats_val['total_imagenes']} imágenes ({int(stats_val['total_imagenes']/total_imgs*100)}%)")
        
        print(f"\nTotal de objetos etiquetados:")
        for clase_id, clase_nombre in CLASES.items():
            total_clase = stats_train['estadisticas_clases'][clase_id] + stats_val['estadisticas_clases'][clase_id]
            print(f"   {clase_nombre}: {total_clase} objetos")
        
        if (stats_train['imagenes_sin_etiqueta'] == 0 and 
            stats_val['imagenes_sin_etiqueta'] == 0 and
            total_imgs == total_etqs):
            print("\n" + "=" * 70)
            print("¡PERFECTO! Dataset listo para entrenamiento")
            print("=" * 70)
            print("\nPróximo paso:")
            print("   python entrenar_modelo.py")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("Hay problemas que resolver antes de entrenar")
            print("=" * 70)
    
if __name__ == "__main__":
    main()