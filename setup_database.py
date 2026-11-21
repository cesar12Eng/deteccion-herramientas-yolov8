#!/usr/bin/env python3

from database_manager import HerramientasDB, mostrar_tabla_herramientas
import sys

def menu_principal():
    """Menú interactivo para gestionar la base de datos"""
    
    print("\n" + "=" * 70)
    print("  SETUP - SISTEMA DE GESTIÓN DE HERRAMIENTAS")
    print("=" * 70)
    
    db = HerramientasDB()
    
    while True:
        print("\n" + "=" * 70)
        print("MENÚ DE OPCIONES")
        print("=" * 70)
        print("  1. Ver inventario de herramientas")
        print("  2. Agregar herramienta manualmente")
        print("  3. Inicializar herramientas base (4 herramientas)")
        print("  4.  Limpiar base de datos (CUIDADO)")
        print("  0. Salir")
        print("=" * 70)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            ver_inventario(db)
        elif opcion == "2":
            agregar_herramienta_manual(db)
        elif opcion == "3":
            inicializar_base(db)
        elif opcion == "4":
            limpiar_bd(db)
        elif opcion == "0":
            print("\nSaliendo del sistema...")
            print("=" * 70)
            break
        else:
            print("\nOpción inválida")
        
        input("\nPresiona ENTER para continuar...")

def ver_inventario(db: HerramientasDB):
    """Muestra el inventario completo de herramientas"""
    print("\n" + "=" * 70)
    print("INVENTARIO DE HERRAMIENTAS")
    print("=" * 70)
    
    herramientas = db.listar_herramientas(solo_activas=False)
    
    if not herramientas:
        print("\n    No hay herramientas registradas")
        print("   Usa la opción 3 para inicializar las herramientas base")
    else:
        mostrar_tabla_herramientas(herramientas)
        print(f"\nTotal: {len(herramientas)} herramienta(s)")
    
    print("=" * 70)

def agregar_herramienta_manual(db: HerramientasDB):
    """Agrega una herramienta manualmente"""
    print("\n" + "=" * 70)
    print("AGREGAR NUEVA HERRAMIENTA")
    print("=" * 70)
    
    nombre = input("\nNombre descriptivo (ej: 'Destornillador Phillips'): ").strip()
    if not nombre:
        print("El nombre no puede estar vacío")
        return
    
    nombre_clase = input("Nombre de clase YOLO (ej: 'destornillador'): ").strip().lower().replace('', '_')
    if not nombre_clase:
        print("El nombre de clase no puede estar vacío")
        return
    
    descripcion = input("Descripción (opcional, presiona ENTER para omitir): ").strip()
    descripcion = descripcion if descripcion else None
    
    if db.verificar_herramienta_existe(nombre):
        print(f"\nYa existe una herramienta con el nombre '{nombre}'")
        return
    
    herramienta_id = db.agregar_herramienta(nombre, nombre_clase, descripcion)
    
    if herramienta_id > 0:
        print(f"\nHerramienta '{nombre}' agregada exitosamente con ID: {herramienta_id}")
    else:
        print("\nError al agregar la herramienta")

def inicializar_base(db: HerramientasDB):
    """Inicializa las 4 herramientas base del proyecto"""
    print("\n" + "=" * 70)
    print("INICIALIZAR HERRAMIENTAS BASE")
    print("=" * 70)
    
    print("\nEsto agregará las siguientes herramientas al inventario:")
    print("   1. Destornillador (destornillador)")
    print("   2. Martillo (martillo)")
    print("   3. Pinza (pinza)")
    print("   4. Llave Inglesa (llave_inglesa)")
    
    print("\nNota: Si alguna ya existe, no se duplicará")
    
    confirmar = input("\n¿Continuar? (s/n): ").strip().lower()
    
    if confirmar == 's':
        db.inicializar_herramientas_base()
        print("\nProceso completado")
    else:
        print("\nOperación cancelada")

def limpiar_bd(db: HerramientasDB):
    """Limpia toda la base de datos"""
    print("\n" + "=" * 70)
    print("  LIMPIAR BASE DE DATOS")
    print("=" * 70)
    
    print("\nADVERTENCIA: Esta acción eliminará:")
    print("   • Todas las herramientas del inventario")
    print("   • Toda la información almacenada")
    print("\n    ESTA ACCIÓN NO SE PUEDE DESHACER")
    
    confirmar1 = input("\n¿Estás seguro? (escribe 'SI' para confirmar): ").strip()
    
    if confirmar1 == "SI":
        confirmar2 = input("Confirmación final - Escribe 'ELIMINAR' para continuar: ").strip()
        
        if confirmar2 == "ELIMINAR":
            db.limpiar_base_datos(confirmar=True)
            print("\nBase de datos limpiada. Se creó una nueva vacía.")
        else:
            print("\nOperación cancelada")
    else:
        print("\nOperación cancelada")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
        sys.exit(0)
        