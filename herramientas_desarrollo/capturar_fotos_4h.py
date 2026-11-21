import cv2
import os
from datetime import datetime

HERRAMIENTAS_DISPONIBLES = [
    "destornillador",
    "martillo", 
    "pinza",
    "llave_inglesa"
]

META_FOTOS = 70  
MINIMO_RECOMENDADO = 50


def mostrar_estado_proyecto():
    print("\n" + "=" * 70)
    print("  ESTADO DEL PROYECTO - CAPTURA DE IMAGENES")
    print("=" * 70)
    print(f"{'Herramienta':<20} {'Fotos Train':<15} {'Fotos Val':<15} {'Progreso':<15}")
    print("-" * 70)
    
    total_fotos = 0
    
    for herramienta in HERRAMIENTAS_DISPONIBLES:
        carpeta_train = f"dataset/images/train/{herramienta}"
        fotos_train = 0
        if os.path.exists(carpeta_train):
            fotos_train = len([f for f in os.listdir(carpeta_train) 
                              if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        carpeta_val = f"dataset/images/val/{herramienta}"
        fotos_val = 0
        if os.path.exists(carpeta_val):
            fotos_val = len([f for f in os.listdir(carpeta_val) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        total_herramienta = fotos_train + fotos_val
        total_fotos += total_herramienta
        
        progreso = min(100, int((total_herramienta / META_FOTOS) * 100))
        barra = "█" * (progreso // 5) + "░" * (20 - progreso // 5)
        
        if total_herramienta >= META_FOTOS:
            simbolo = "[OK]"
        elif total_herramienta >= MINIMO_RECOMENDADO:
            simbolo = "[!]"
        else:
            simbolo = "[X]"
        
        print(f"{simbolo} {herramienta:<17} {fotos_train:<15} {fotos_val:<15} {barra} {progreso}%")
    
    print("-" * 70)
    print(f"{'TOTAL':<20} {'':<15} {'':<15} {total_fotos} fotos")
    print("=" * 70)
    
    return total_fotos


def seleccionar_herramienta():
    while True:
        print("\n" + "=" * 70)
        print("SELECCIONA LA HERRAMIENTA A CAPTURAR")
        print("=" * 70)
        
        for i, herramienta in enumerate(HERRAMIENTAS_DISPONIBLES, 1):
            carpeta_train = f"dataset/images/train/{herramienta}"
            fotos = 0
            if os.path.exists(carpeta_train):
                fotos = len([f for f in os.listdir(carpeta_train) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            status = "" if fotos >= META_FOTOS else "[*]"
            print(f"  {i}. {status} {herramienta.upper().replace('_', ' '):<20} ({fotos} fotos)")
        
        print(f"  0.  Salir")
        print("=" * 70)
        
        try:
            opcion = input("\nSelecciona una opcion (0-4): ").strip()
            
            if opcion == "0":
                return None
            
            opcion_num = int(opcion)
            if 1 <= opcion_num <= len(HERRAMIENTAS_DISPONIBLES):
                return HERRAMIENTAS_DISPONIBLES[opcion_num - 1]
            else:
                print("\nOpcion invalida. Intenta de nuevo.")
        except ValueError:
            print("\nPor favor ingresa un numero valido.")


def capturar_fotos(herramienta):
    CARPETA_SALIDA = f"dataset/images/train/{herramienta}"
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    
    fotos_existentes = len([f for f in os.listdir(CARPETA_SALIDA) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    contador = fotos_existentes + 1
    
    print(f"Herramienta: {herramienta.upper().replace('_', ' ')}")
    print(f"Guardando en: {CARPETA_SALIDA}")
    print(f"Fotos existentes: {fotos_existentes}")
    print(f"Meta recomendada: {META_FOTOS} fotos")
    print(f"Faltan: {max(0, META_FOTOS - fotos_existentes)} fotos")
    print("\n" + "=" * 70)
    print("CONTROLES:")
    print("  ESPACIO -> Tomar foto")
    print("  Q       -> Volver al menu")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("Error: No se pudo acceder a la camara")
        return 0
    
    print("Camara iniciada correctamente\n")
    
    fotos_capturadas = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error al capturar frame")
            break
        
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]
        
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)
        
        cv2.putText(display_frame, f"Herramienta: {herramienta.upper().replace('_', ' ')}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Sesion: {fotos_capturadas} | Total: {fotos_existentes + fotos_capturadas}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        progreso_actual = fotos_existentes + fotos_capturadas
        porcentaje = min(100, int((progreso_actual / META_FOTOS) * 100))
        barra_w = int((w - 40) * (progreso_actual / META_FOTOS))
        cv2.rectangle(display_frame, (20, 75), (w - 20, 90), (100, 100, 100), -1)
        cv2.rectangle(display_frame, (20, 75), (20 + barra_w, 90), (0, 255, 0), -1)
        cv2.putText(display_frame, f"{porcentaje}%", (w - 60, 87), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        overlay_bottom = display_frame.copy()
        cv2.rectangle(overlay_bottom, (0, h - 60), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay_bottom, 0.6, display_frame, 0.4, 0, display_frame)
        
        cv2.putText(display_frame, "ESPACIO: Capturar | Q: Salir", 
                    (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Captura de Imagenes - Proyecto Herramientas', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(''):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{herramienta}_{contador}_{timestamp}.jpg"
            ruta_completa = os.path.join(CARPETA_SALIDA, nombre_archivo)
            
            cv2.imwrite(ruta_completa, frame)
            
            print(f"Foto {contador} guardada: {nombre_archivo}")
            contador += 1
            fotos_capturadas += 1
            
            white_frame = frame.copy()
            white_frame[:] = (255, 255, 255)
            cv2.imshow('Captura de Imagenes - Proyecto Herramientas', white_frame)
            cv2.waitKey(100)
        
        elif key == ord('q') or key == ord('Q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def main():
    print("\n" + "=" * 70)
    print("SISTEMA DE CAPTURA DE IMAGENES - RECONOCIMIENTO DE HERRAMIENTAS")
    print("=" * 70)
    
    while True:
        mostrar_estado_proyecto()
        
        herramienta = seleccionar_herramienta()
        
        if herramienta is None:
            print("\nSaliendo del programa...")
            print("=" * 70)
            break
        
        capturar_fotos(herramienta)
        
        input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    main()