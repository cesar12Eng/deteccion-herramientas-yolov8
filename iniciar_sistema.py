#!/usr/bin/env python3
"""
Launcher del Sistema de Reconocimiento de Herramientas
Menú principal para acceder a todas las funcionalidades
"""

import sys
import os
import subprocess

def limpiar_pantalla():
    os.system('clear' if os.name != 'nt' else 'cls')

def mostrar_menu():
    limpiar_pantalla()
    print("=" * 70)
    print("SISTEMA DE GESTIÓN DE HERRAMIENTAS - MENÚ PRINCIPAL")
    print("=" * 70)
    print("\nAPLICACIONES:")
    print("  1. Iniciar Aplicación de Taller")
    print("  2.  Gestionar Base de Datos")
    
    print("\nINFORMACIÓN:")
    print("  3. ℹ Ver Estado del Sistema")
    print("  4. Ver Guía de Uso")
    
    print("\n  0. Salir")
    print("=" * 70)

def verificar_archivo(archivo):
    """Verifica si un archivo existe"""
    if not os.path.exists(archivo):
        print(f"\nError: No se encontró el archivo '{archivo}'")
        input("\nPresiona ENTER para continuar...")
        return False
    return True

def ejecutar_aplicacion_taller():
    """Ejecuta la aplicación principal de taller"""
    if verificar_archivo("app_taller.py"):
        print("\nIniciando Aplicación de Taller...")
        print("   (Cierra la ventana de la aplicación para volver al menú)")
        subprocess.run([sys.executable, "app_taller.py"])

def ejecutar_setup_database():
    """Ejecuta el setup de la base de datos"""
    if verificar_archivo("setup_database.py"):
        limpiar_pantalla()
        subprocess.run([sys.executable, "setup_database.py"])


def mostrar_estado_proyecto():
    """Muestra el estado actual del proyecto"""
    limpiar_pantalla()
    print("=" * 70)
    print("ESTADO DEL SISTEMA")
    print("=" * 70)
    
    print("\nARCHIVOS DEL SISTEMA:")
    archivos_importantes = {
        "app_taller.py": "Aplicación Principal",
        "database_manager.py": "Gestor de Base de Datos",
        "setup_database.py": "Configuración de BD",
        "herramientas.db": "Base de Datos"
    }
    
    for archivo, descripcion in archivos_importantes.items():
        estado = "[OK]" if os.path.exists(archivo) else "[FALTA]"
        print(f"   {estado} {descripcion:<30} ({archivo})")
    
    print("\nMODELO DE IA:")
    modelo_paths = [
        "runs/detect/herramientas_v1/weights/best.pt",
        "best.pt",
        "weights/best.pt"
    ]
    
    modelo_encontrado = False
    for path in modelo_paths:
        if os.path.exists(path):
            print(f"   Modelo entrenado encontrado: {path}")
            modelo_encontrado = True
            break
    
    if not modelo_encontrado:
        print("    Modelo entrenado NO encontrado")
        print("      Coloca el archivo 'best.pt' en la carpeta raíz")
    
    print("\nBASE DE DATOS:")
    if os.path.exists("herramientas.db"):
        try:
            from database_manager import HerramientasDB
            db = HerramientasDB()
            
            total_herramientas = db.contar_herramientas()
            
            print(f"   Base de datos inicializada")
            print(f"      • Herramientas registradas: {total_herramientas}")
            
            if total_herramientas > 0:
                herramientas = db.listar_herramientas()
                print(f"      • Herramientas en inventario:")
                for h in herramientas[:5]:
                    print(f"        - {h['nombre']} ({h['nombre_clase']})")
                if total_herramientas > 5:
                    print(f"        ... y {total_herramientas - 5} más")
            
        except Exception as e:
            print(f"    Error al leer la base de datos: {str(e)}")
    else:
        print("   Base de datos no inicializada")
        print("      Ejecuta 'Gestionar Base de Datos' (opción 2)")
    
    print("\n" + "=" * 70)
    input("\nPresiona ENTER para continuar...")

def mostrar_guia_rapida():
    """Muestra una guía rápida de uso"""
    limpiar_pantalla()
    print("=" * 70)
    print("GUÍA DE USO")
    print("=" * 70)
    
    print("\nCONFIGURACIÓN INICIAL:")
    print("   1. Ejecuta 'Gestionar Base de Datos' (opción 2)")
    print("   2. Inicializa las 4 herramientas base (opción 3 en el menú)")
    print("   3. Ejecuta 'Iniciar Aplicación de Taller' (opción 1)")
    
    print("\nUSAR LA APLICACIÓN:")
    print("   • Opción 1 del menú principal")
    print("   • Click en 'INICIAR CÁMARA'")
    print("   • Muestra la herramienta frente a la cámara")
    print("   • El sistema detecta automáticamente")
    print("   • Click en 'AGREGAR AL INVENTARIO' para registrarla")
    
    print("\nGESTIÓN DEL INVENTARIO:")
    print("   Desde la aplicación de taller puedes:")
    print("   • Agregar nuevas herramientas manualmente")
    print("   •  Editar herramientas existentes")
    print("   •  Eliminar herramientas del inventario")
    print("   • Actualizar la tabla de inventario")
    
    print("\nCONSEJOS:")
    print("   • Mantén buena iluminación para mejor detección")
    print("   • El modelo funciona mejor con fondos simples")
    print("   • Centra la herramienta en el cuadro de la cámara")
    print("   • Haz backup de herramientas.db periódicamente")
    
    print("\nGESTIÓN DE LA BASE DE DATOS:")
    print("   • Opción 2 del menú principal")
    print("   • Ver inventario completo")
    print("   • Agregar herramientas manualmente")
    print("   • Inicializar herramientas base")
    print("   • Limpiar la base de datos (CUIDADO)")
    
    print("\n" + "=" * 70)
    input("\nPresiona ENTER para continuar...")

def main():
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == "1":
                ejecutar_aplicacion_taller()
            elif opcion == "2":
                ejecutar_setup_database()
            elif opcion == "3":
                mostrar_estado_proyecto()
            elif opcion == "4":
                mostrar_guia_rapida()
            elif opcion == "0":
                limpiar_pantalla()
                print("\n¡Hasta luego!\n")
                print("=" * 70)
                break
            else:
                print("\nOpción inválida")
                input("\nPresiona ENTER para continuar...")
                
        except KeyboardInterrupt:
            limpiar_pantalla()
            print("\n\nPrograma interrumpido por el usuario\n")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    main()