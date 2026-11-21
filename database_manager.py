import sqlite3
import os
from typing import List, Dict, Optional

class HerramientasDB:
    
    def __init__(self, db_path: str = "herramientas.db"):
        self.db_path = db_path
        self.conn = None
        self.crear_tablas()
    
    def conectar(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def desconectar(self):
        if self.conn:
            self.conn.close()
    
    def crear_tablas(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS herramientas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                nombre_clase TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER DEFAULT 0,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        self._migrar_columna_cantidad(cursor, conn)
        self.desconectar()
        print("Base de datos inicializada correctamente")
    
    def _migrar_columna_cantidad(self, cursor, conn):
        try:
            cursor.execute("PRAGMA table_info(herramientas)")
            columnas = cursor.fetchall()
            nombres_columnas = [col[1] for col in columnas]
            
            if 'cantidad' not in nombres_columnas:
                print("Migrando base de datos: agregando columna 'cantidad'...")
                cursor.execute("""
                    ALTER TABLE herramientas 
                    ADD COLUMN cantidad INTEGER DEFAULT 0
                """)
                conn.commit()
                print("Columna 'cantidad' agregada exitosamente")
        except Exception as e:
            print(f"Error en migracion: {str(e)}")
    
    def agregar_herramienta(self, nombre: str, nombre_clase: str, 
                           descripcion: str = None, cantidad: int = 1) -> int:
        conn = self.conectar()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, activo FROM herramientas WHERE nombre = ?
            ''', (nombre,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                herramienta_id = resultado['id']
                esta_activa = resultado['activo']
                
                if esta_activa:
                    print(f"Error: La herramienta '{nombre}' ya existe en el inventario")
                    self.desconectar()
                    return -1
                else:
                    cursor.execute('''
                        UPDATE herramientas 
                        SET activo = 1, nombre_clase = ?, descripcion = ?, cantidad = ?
                        WHERE id = ?
                    ''', (nombre_clase, descripcion, cantidad, herramienta_id))
                    conn.commit()
                    print(f"Herramienta '{nombre}' reactivada con ID: {herramienta_id}")
                    self.desconectar()
                    return herramienta_id
            
            cursor.execute('''
                INSERT INTO herramientas (nombre, nombre_clase, descripcion, cantidad)
                VALUES (?, ?, ?, ?)
            ''', (nombre, nombre_clase, descripcion, cantidad))
            
            herramienta_id = cursor.lastrowid
            conn.commit()
            print(f"Herramienta '{nombre}' agregada con ID: {herramienta_id} y cantidad: {cantidad}")
            self.desconectar()
            return herramienta_id
            
        except sqlite3.IntegrityError as e:
            print(f"Error IntegrityError: No se pudo agregar la herramienta '{nombre}': {str(e)}")
            self.desconectar()
            return -1
        except Exception as e:
            print(f"Error inesperado al agregar herramienta '{nombre}': {str(e)}")
            self.desconectar()
            return -2
    
    def listar_herramientas(self, solo_activas: bool = True) -> List[Dict]:
        conn = self.conectar()
        cursor = conn.cursor()
        
        if solo_activas:
            cursor.execute('SELECT * FROM herramientas WHERE activo = 1 ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM herramientas ORDER BY nombre')
        
        rows = cursor.fetchall()
        self.desconectar()
        
        return [dict(row) for row in rows]
    
    def actualizar_herramienta(self, id_herramienta: int = None, herramienta_id: int = None, **kwargs) -> bool:
        herr_id = id_herramienta if id_herramienta is not None else herramienta_id
        
        if herr_id is None:
            return False
        
        campos_permitidos = ['nombre', 'nombre_clase', 'descripcion', 'cantidad', 'activo']
        campos_actualizar = {k: v for k, v in kwargs.items() if k in campos_permitidos}
        
        if not campos_actualizar:
            return False
        
        conn = self.conectar()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in campos_actualizar.keys()])
        values = list(campos_actualizar.values()) + [herr_id]
        
        cursor.execute(f'''
            UPDATE herramientas SET {set_clause} WHERE id = ?
        ''', values)
        
        conn.commit()
        filas_afectadas = cursor.rowcount
        self.desconectar()
        
        return filas_afectadas > 0
    
    def eliminar_herramienta(self, herramienta_id: int, permanente: bool = False) -> bool:
        conn = self.conectar()
        cursor = conn.cursor()
        
        if permanente:
            cursor.execute('DELETE FROM herramientas WHERE id = ?', (herramienta_id,))
        else:
            cursor.execute('UPDATE herramientas SET activo = 0 WHERE id = ?', (herramienta_id,))
        
        conn.commit()
        filas_afectadas = cursor.rowcount
        self.desconectar()
        
        return filas_afectadas > 0
    
    def incrementar_cantidad(self, herramienta_id: int = None, nombre_clase: str = None, 
                            cantidad: int = 1) -> bool:
        conn = self.conectar()
        cursor = conn.cursor()
        
        try:
            if herramienta_id:
                cursor.execute('''
                    UPDATE herramientas 
                    SET cantidad = cantidad + ? 
                    WHERE id = ? AND activo = 1
                ''', (cantidad, herramienta_id))
                print(f"Intentando incrementar por ID: {herramienta_id}, cantidad: {cantidad}")
            elif nombre_clase:
                cursor.execute('''
                    UPDATE herramientas 
                    SET cantidad = cantidad + ? 
                    WHERE nombre_clase = ? AND activo = 1
                ''', (cantidad, nombre_clase))
                print(f"Intentando incrementar por clase: {nombre_clase}, cantidad: {cantidad}")
            else:
                print("Error: No se proporciono ID ni nombre_clase")
                return False
            
            conn.commit()
            filas_afectadas = cursor.rowcount
            
            if filas_afectadas > 0:
                print(f"Cantidad incrementada en {cantidad} (filas afectadas: {filas_afectadas})")
                return True
            else:
                print(f"No se encontro la herramienta para incrementar (filas afectadas: 0)")
                return False
                
        except Exception as e:
            print(f"Error al incrementar cantidad: {str(e)}")
            return False
        finally:
            self.desconectar()
    
    def decrementar_cantidad(self, herramienta_id: int = None, nombre_clase: str = None, 
                            cantidad: int = 1) -> bool:
        conn = self.conectar()
        cursor = conn.cursor()
        
        try:
            if herramienta_id:
                cursor.execute('SELECT cantidad FROM herramientas WHERE id = ?', (herramienta_id,))
                resultado = cursor.fetchone()
                if resultado and resultado['cantidad'] >= cantidad:
                    cursor.execute('''
                        UPDATE herramientas 
                        SET cantidad = cantidad - ? 
                        WHERE id = ? AND activo = 1
                    ''', (cantidad, herramienta_id))
                else:
                    print(f"No hay suficiente cantidad para decrementar")
                    return False
                    
            elif nombre_clase:
                cursor.execute('SELECT cantidad FROM herramientas WHERE nombre_clase = ?', (nombre_clase,))
                resultado = cursor.fetchone()
                if resultado and resultado['cantidad'] >= cantidad:
                    cursor.execute('''
                        UPDATE herramientas 
                        SET cantidad = cantidad - ? 
                        WHERE nombre_clase = ? AND activo = 1
                    ''', (cantidad, nombre_clase))
                else:
                    print(f"No hay suficiente cantidad para decrementar")
                    return False
            else:
                return False
            
            conn.commit()
            print(f"Cantidad decrementada en {cantidad}")
            return True
                
        finally:
            self.desconectar()
    
    def obtener_cantidad(self, herramienta_id: int = None, nombre_clase: str = None) -> int:
        conn = self.conectar()
        cursor = conn.cursor()
        
        try:
            if herramienta_id:
                cursor.execute('''
                    SELECT cantidad FROM herramientas 
                    WHERE id = ? AND activo = 1
                ''', (herramienta_id,))
                print(f"Consultando cantidad por ID: {herramienta_id}")
            elif nombre_clase:
                cursor.execute('''
                    SELECT cantidad FROM herramientas 
                    WHERE nombre_clase = ? AND activo = 1
                ''', (nombre_clase,))
                print(f"Consultando cantidad por clase: {nombre_clase}")
            else:
                print("Error: No se proporciono ID ni nombre_clase")
                return 0
            
            resultado = cursor.fetchone()
            if resultado:
                cantidad = resultado['cantidad']
                print(f"Cantidad encontrada: {cantidad}")
                return cantidad
            else:
                print(f"No se encontro la herramienta")
                return 0
            
        except Exception as e:
            print(f"Error al obtener cantidad: {str(e)}")
            return 0
        finally:
            self.desconectar()
    
    def establecer_cantidad(self, herramienta_id: int = None, nombre_clase: str = None, 
                           cantidad: int = 0) -> bool:
        conn = self.conectar()
        cursor = conn.cursor()
        
        try:
            if herramienta_id:
                cursor.execute('''
                    UPDATE herramientas 
                    SET cantidad = ? 
                    WHERE id = ? AND activo = 1
                ''', (cantidad, herramienta_id))
            elif nombre_clase:
                cursor.execute('''
                    UPDATE herramientas 
                    SET cantidad = ? 
                    WHERE nombre_clase = ? AND activo = 1
                ''', (cantidad, nombre_clase))
            else:
                return False
            
            conn.commit()
            filas_afectadas = cursor.rowcount
            
            if filas_afectadas > 0:
                print(f"Cantidad establecida a {cantidad}")
                return True
            return False
                
        finally:
            self.desconectar()
    
    def obtener_herramienta_por_clase(self, nombre_clase: str) -> Optional[Dict]:
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM herramientas WHERE nombre_clase = ? AND activo = 1
        ''', (nombre_clase,))
        
        row = cursor.fetchone()
        self.desconectar()
        
        if row:
            return dict(row)
        return None
    
    def inicializar_herramientas_base(self):
        herramientas_base = [
            ("Destornillador", "destornillador", "Herramienta para atornillar y desatornillar", 0),
            ("Martillo", "martillo", "Herramienta para golpear y clavar", 0),
            ("Pinza", "pinza", "Herramienta para sujetar y cortar", 0),
            ("Llave Inglesa", "llave_inglesa", "Herramienta ajustable para tuercas y tornillos", 0)
        ]
        
        print("\nInicializando herramientas base...")
        contador_exitosos = 0
        for nombre, clase, desc, cant in herramientas_base:
            resultado = self.agregar_herramienta(nombre, clase, desc, cant)
            if resultado > 0:
                contador_exitosos += 1
        
        print(f"{contador_exitosos}/{len(herramientas_base)} herramientas inicializadas\n")
    
    def verificar_herramienta_existe(self, nombre: str) -> bool:
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM herramientas WHERE nombre = ?', (nombre,))
        resultado = cursor.fetchone()
        self.desconectar()
        
        return resultado['count'] > 0
    
    def contar_herramientas(self, solo_activas: bool = True) -> int:
        conn = self.conectar()
        cursor = conn.cursor()
        
        if solo_activas:
            cursor.execute('SELECT COUNT(*) as count FROM herramientas WHERE activo = 1')
        else:
            cursor.execute('SELECT COUNT(*) as count FROM herramientas')
        
        resultado = cursor.fetchone()
        self.desconectar()
        
        return resultado['count']
    
    def limpiar_base_datos(self, confirmar: bool = False):
        if not confirmar:
            print("Operacion cancelada. Usa confirmar=True para limpiar la BD")
            return
        
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print("Base de datos eliminada")
            self.crear_tablas()
        else:
            print("No existe base de datos para limpiar")


def mostrar_tabla_herramientas(herramientas: List[Dict]):
    if not herramientas:
        print("   No hay herramientas registradas")
        return
    
    print(f"\n{'ID':<5} {'Nombre':<25} {'Clase YOLO':<20} {'Cantidad':<10} {'Estado':<10}")
    print("-" * 75)
    for h in herramientas:
        estado = "Activo"
        cantidad = h.get('cantidad', 0)
        print(f"{h['id']:<5} {h['nombre']:<25} {h['nombre_clase']:<20} {cantidad:<10} {estado:<10}")