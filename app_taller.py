#!/usr/bin/env python3

import cv2
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
from datetime import datetime
from ultralytics import YOLO
from database_manager import HerramientasDB
import os 


class AplicacionTaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Herramientas - Taller")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2c3e50')
        
        self.deteccion_activa = False
        self.cap = None
        self.modelo = None
        self.db = HerramientasDB()
        
        self.herramienta_detectada = None
        self.confianza_detectada = 0.0
        self.umbral_confianza = 0.4
        
        self.cargar_modelo()
        
        self.crear_interfaz()
        
        self.actualizar_tabla_inventario()
        
    def cargar_modelo(self):
        """Carga el modelo YOLOv8 entrenado"""
        try:
            modelo_path = 'runs/detect/herramientas_mejorado/weights/best.pt'
            
            if not os.path.exists(modelo_path):
                rutas_alternativas = ["best.pt", "weights/best.pt"]
                for ruta in rutas_alternativas:
                    if os.path.exists(ruta):
                        modelo_path = ruta
                        break
            
            if os.path.exists(modelo_path):
                self.modelo = YOLO(modelo_path)
                print(f"Modelo cargado desde: {modelo_path}")
            else:
                messagebox.showwarning("Advertencia", 
                    "No se encontró el modelo entrenado.\n"
                    "La detección automática no estará disponible.\n"
                    "Puedes usar la gestión manual del inventario.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar modelo: {str(e)}")
    
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        

        frame_superior = tk.Frame(self.root, bg='#34495e', height=70)
        frame_superior.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            frame_superior, 
            text="GESTIÓN DE HERRAMIENTAS", 
            font=('Arial', 22, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(pady=15)
        

        panel_izquierdo = tk.Frame(self.root, bg='#34495e')
        panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        tk.Label(
            panel_izquierdo,
            text="DETECCIÓN CON CÁMARA",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(pady=10)
        
        frame_video = tk.Frame(panel_izquierdo, bg='#1a1a1a', relief=tk.RAISED, bd=3, width=640, height=480)
        frame_video.pack(padx=10, pady=10)
        frame_video.pack_propagate(False)
        
        self.label_video = tk.Label(frame_video, bg='#1a1a1a', text="Cámara apagada", 
                                     font=('Arial', 16), fg='#7f8c8d')
        self.label_video.pack(fill=tk.BOTH, expand=True)
        
        frame_deteccion_info = tk.Frame(panel_izquierdo, bg='#2c3e50', relief=tk.RAISED, bd=2)
        frame_deteccion_info.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            frame_deteccion_info,
            text="Herramienta Detectada:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#bdc3c7'
        ).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        
        self.label_herramienta_detectada = tk.Label(
            frame_deteccion_info,
            text="---",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.label_herramienta_detectada.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(
            frame_deteccion_info,
            text="Confianza:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#bdc3c7'
        ).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        
        self.label_confianza = tk.Label(
            frame_deteccion_info,
            text="0%",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#3498db'
        )
        self.label_confianza.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        frame_controles = tk.Frame(panel_izquierdo, bg='#34495e')
        frame_controles.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_camara = tk.Button(
            frame_controles,
            text="INICIAR CÁMARA",
            font=('Arial', 13, 'bold'),
            bg='#27ae60',
            fg='black',
            command=self.toggle_deteccion,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2',
            height=2
        )
        self.btn_camara.pack(fill=tk.X, pady=5)
        
        frame_botones_agregar = tk.Frame(panel_izquierdo, bg='#34495e')
        frame_botones_agregar.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_agregar_cantidad = tk.Button(
            frame_botones_agregar,
            text="AGREGAR AL INVENTARIO",
            font=('Arial', 11, 'bold'),
            bg='#7f8c8d',
            fg='black',
            command=self.agregar_cantidad_detectada,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2',
            height=2,
            state=tk.DISABLED
        )
        self.btn_agregar_cantidad.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.btn_agregar_nueva = tk.Button(
            frame_botones_agregar,
            text="NUEVA HERRAMIENTA",
            font=('Arial', 11, 'bold'),
            bg='#7f8c8d',
            fg='black',
            command=self.agregar_herramienta_detectada,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2',
            height=2,
            state=tk.DISABLED
        )
        self.btn_agregar_nueva.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        

        panel_derecho = tk.Frame(self.root, bg='#34495e')
        panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        tk.Label(
            panel_derecho,
            text="INVENTARIO DE HERRAMIENTAS",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(pady=10)
        
        frame_tabla = tk.Frame(panel_derecho, bg='#34495e')
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(
            frame_tabla,
            columns=('ID', 'Nombre', 'Clase', 'Cantidad', 'Descripción', 'Estado'),
            show='headings',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=15
        )
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Clase', text='Clase YOLO')
        self.tree.heading('Cantidad', text='Cantidad')
        self.tree.heading('Descripción', text='Descripción')
        self.tree.heading('Estado', text='Estado')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Nombre', width=130)
        self.tree.column('Clase', width=110)
        self.tree.column('Cantidad', width=80, anchor='center')
        self.tree.column('Descripción', width=180)
        self.tree.column('Estado', width=80, anchor='center')
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',
                       background='#2c3e50',
                       foreground='#ecf0f1',
                       fieldbackground='#2c3e50',
                       rowheight=25)
        style.map('Treeview', background=[('selected', '#3498db')])
        
        frame_botones = tk.Frame(panel_derecho, bg='#34495e')
        frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            frame_botones,
            text="Agregar Manual",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='black',
            command=self.agregar_manual,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(
            frame_botones,
            text="Actualizar",
            font=('Arial', 11, 'bold'),
            bg='#f39c12',
            fg='black',
            command=self.actualizar_herramienta,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(
            frame_botones,
            text="Eliminar",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='black',
            command=self.eliminar_herramienta,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(
            frame_botones,
            text="Actualizar Tabla",
            font=('Arial', 11, 'bold'),
            bg='#9b59b6',
            fg='black',
            command=self.actualizar_tabla_inventario,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def toggle_deteccion(self):
        """Inicia o detiene la detección"""
        if not self.deteccion_activa:
            self.iniciar_deteccion()
        else:
            self.detener_deteccion()
    
    def iniciar_deteccion(self):
        """Inicia el proceso de detección"""
        if not self.modelo:
            messagebox.showerror("Error", "Modelo YOLO no está cargado")
            return
            
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            return
        
        self.deteccion_activa = True
        self.btn_camara.config(text="DETENER CÁMARA", bg='#e74c3c')
        
        thread = threading.Thread(target=self.procesar_video, daemon=True)
        thread.start()
    
    def detener_deteccion(self):
        """Detiene el proceso de detección"""
        self.deteccion_activa = False
        
        if self.cap:
            self.cap.release()
        
        self.btn_camara.config(text="INICIAR CÁMARA", bg='#27ae60')
        self.label_video.config(image='', text="Cámara apagada", 
                               font=('Arial', 16), fg='#7f8c8d')
        self.herramienta_detectada = None
        self.btn_agregar_cantidad.config(state=tk.DISABLED, bg='#7f8c8d')
        self.btn_agregar_nueva.config(state=tk.DISABLED, bg='#7f8c8d')
        self.label_herramienta_detectada.config(text="---")
        self.label_confianza.config(text="0%")
    
    def procesar_video(self):
        """Procesa el video y realiza detecciones"""
        while self.deteccion_activa:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            resultados = self.modelo(frame, conf=self.umbral_confianza, verbose=False)
            
            frame_anotado = resultados[0].plot()
            
            detecciones = resultados[0].boxes
            
            if len(detecciones) > 0:
                idx_max_conf = detecciones.conf.argmax()
                clase_id = int(detecciones.cls[idx_max_conf])
                confianza = float(detecciones.conf[idx_max_conf])
                
                nombre_clase = self.modelo.names[clase_id]
                
                self.herramienta_detectada = nombre_clase
                self.confianza_detectada = confianza
                
                self.root.after(0, self.actualizar_info_deteccion, nombre_clase, confianza)
            else:
                self.herramienta_detectada = None
                self.root.after(0, self.actualizar_info_deteccion, None, 0.0)
            
            frame_rgb = cv2.cvtColor(frame_anotado, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            label_width = self.label_video.winfo_width()
            label_height = self.label_video.winfo_height()
            
            if label_width > 1 and label_height > 1:
                img = img.resize((label_width, label_height), Image.Resampling.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(image=img)
            
            self.label_video.img_tk = img_tk
            self.label_video.config(image=img_tk, text='')
    
    def actualizar_info_deteccion(self, nombre_clase, confianza):
        """Actualiza la información de detección en la interfaz"""
        if nombre_clase:
            self.label_herramienta_detectada.config(
                text=nombre_clase.upper().replace('_', ''),
                fg='#2ecc71'
            )
            self.label_confianza.config(
                text=f"{confianza:.0%}",
                fg='#2ecc71' if confianza >= 0.7 else '#e67e22'
            )
            
            herramienta_existente = self.db.obtener_herramienta_por_clase(nombre_clase)
            
            if herramienta_existente:
                self.btn_agregar_cantidad.config(state=tk.NORMAL, bg='#3498db')
                self.btn_agregar_nueva.config(state=tk.DISABLED, bg='#7f8c8d')
            else:
                self.btn_agregar_cantidad.config(state=tk.DISABLED, bg='#7f8c8d')
                self.btn_agregar_nueva.config(state=tk.NORMAL, bg='#9b59b6')
        else:
            self.label_herramienta_detectada.config(text="---", fg='#95a5a6')
            self.label_confianza.config(text="0%", fg='#95a5a6')
            self.btn_agregar_cantidad.config(state=tk.DISABLED, bg='#7f8c8d')
            self.btn_agregar_nueva.config(state=tk.DISABLED, bg='#7f8c8d')
    
    def agregar_cantidad_detectada(self):
        """Incrementa la cantidad de la herramienta detectada existente"""
        if not self.herramienta_detectada:
            messagebox.showwarning("Advertencia", "No hay herramienta detectada")
            return
        
        clase_detectada = self.herramienta_detectada
        
        herramienta = self.db.obtener_herramienta_por_clase(clase_detectada)
        
        if not herramienta:
            messagebox.showerror("Error", "La herramienta no existe en el inventario")
            return
        
        cantidad = simpledialog.askinteger(
            "Agregar al Inventario",
            f"¿Cuántas unidades de '{herramienta['nombre']}' deseas agregar?",
            initialvalue=1,
            minvalue=1,
            maxvalue=1000
        )
        
        if cantidad:
            try:
                exito = self.db.incrementar_cantidad(nombre_clase=clase_detectada, cantidad=cantidad)
                
                if exito:
                    nueva_cantidad = self.db.obtener_cantidad(nombre_clase=clase_detectada)
                    messagebox.showinfo(
                        "Éxito", 
                        f"Se agregaron {cantidad} unidad(es)\n"
                        f"Cantidad total: {nueva_cantidad}"
                    )
                    self.actualizar_tabla_inventario()
                else:
                    messagebox.showerror("Error", "No se pudo incrementar la cantidad")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")
    
    def agregar_herramienta_detectada(self):
        """Agrega la herramienta detectada al inventario como nueva"""
        if not self.herramienta_detectada:
            messagebox.showwarning("Advertencia", "No hay herramienta detectada")
            return
        
        clase_detectada = self.herramienta_detectada
        confianza_actual = self.confianza_detectada
        
        herramienta_existente = self.db.obtener_herramienta_por_clase(clase_detectada)
        
        if herramienta_existente:
            messagebox.showwarning(
                "Advertencia", 
                f"La herramienta '{herramienta_existente['nombre']}' ya existe.\n"
                "Usa el botón 'Agregar al Inventario' para incrementar cantidad."
            )
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Nueva Herramienta")
        ventana.geometry("500x450")
        ventana.configure(bg='#2c3e50')
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(
            ventana,
            text="NUEVA HERRAMIENTA",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=20)
        
        frame_form = tk.Frame(ventana, bg='#34495e', relief=tk.RAISED, bd=2)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(frame_form, text="Nombre:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        entry_nombre = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_nombre.insert(0, clase_detectada.replace('_', '').title())
        entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Clase YOLO:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        tk.Label(frame_form, text=clase_detectada, font=('Arial', 11),
                bg='#95a5a6', fg='white', relief=tk.SUNKEN, padx=5, pady=5, anchor='w').grid(
                row=1, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(frame_form, text="Cantidad Inicial:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        entry_cantidad = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_cantidad.insert(0, "1")
        entry_cantidad.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Descripción:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=3, column=0, padx=10, pady=10, sticky='nw')
        text_desc = tk.Text(frame_form, font=('Arial', 10), width=30, height=5)
        text_desc.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text=f"Confianza: {confianza_actual:.0%}",
                font=('Arial', 11), bg='#34495e', fg='#3498db').grid(
                row=4, column=0, columnspan=2, pady=10)
        
        frame_btns = tk.Frame(ventana, bg='#2c3e50')
        frame_btns.pack(fill=tk.X, padx=20, pady=10)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            cantidad_str = entry_cantidad.get().strip()
            descripcion = text_desc.get('1.0', tk.END).strip()
            
            if not nombre:
                messagebox.showwarning("Advertencia", "El nombre es obligatorio")
                return
            
            try:
                cantidad = int(cantidad_str) if cantidad_str else 1
                if cantidad < 0:
                    raise ValueError("La cantidad no puede ser negativa")
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número válido")
                return
            
            try:
                resultado = self.db.agregar_herramienta(
                    nombre=nombre,
                    nombre_clase=clase_detectada,
                    descripcion=descripcion if descripcion else None,
                    cantidad=cantidad
                )
                
                if resultado > 0:
                    messagebox.showinfo("Éxito", f"Herramienta '{nombre}' agregada con {cantidad} unidad(es)")
                    self.actualizar_tabla_inventario()
                    ventana.destroy()
                elif resultado == -1:
                    messagebox.showwarning(
                        "Herramienta Existente", 
                        f"La herramienta '{nombre}' ya existe en el inventario.\n\n"
                        "Usa el botón 'Agregar al Inventario' para incrementar la cantidad."
                    )
                elif resultado == -2:
                    messagebox.showerror("Error", "Error de base de datos. Verifica la consola para más detalles.")
                else:
                    messagebox.showerror("Error", "No se pudo agregar la herramienta")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")
        
        tk.Button(frame_btns, text="Guardar", font=('Arial', 11, 'bold'),
                 bg='#27ae60', fg='black', command=guardar, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="Cancelar", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='black', command=ventana.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def agregar_manual(self):
        """Agrega una herramienta manualmente"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Herramienta Manual")
        ventana.geometry("500x450")
        ventana.configure(bg='#2c3e50')
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(
            ventana,
            text="AGREGAR HERRAMIENTA MANUAL",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=20)
        
        frame_form = tk.Frame(ventana, bg='#34495e', relief=tk.RAISED, bd=2)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(frame_form, text="Nombre*:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        entry_nombre = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Clase YOLO*:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        entry_clase = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_clase.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Cantidad Inicial:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        entry_cantidad = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_cantidad.insert(0, "1")
        entry_cantidad.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Descripción:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=3, column=0, padx=10, pady=10, sticky='nw')
        text_desc = tk.Text(frame_form, font=('Arial', 10), width=30, height=5)
        text_desc.grid(row=3, column=1, padx=10, pady=10)
        
        frame_btns = tk.Frame(ventana, bg='#2c3e50')
        frame_btns.pack(fill=tk.X, padx=20, pady=10)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            clase = entry_clase.get().strip()
            cantidad_str = entry_cantidad.get().strip()
            descripcion = text_desc.get('1.0', tk.END).strip()
            
            if not nombre or not clase:
                messagebox.showwarning("Advertencia", "Nombre y Clase YOLO son obligatorios")
                return
            
            try:
                cantidad = int(cantidad_str) if cantidad_str else 1
                if cantidad < 0:
                    raise ValueError("La cantidad no puede ser negativa")
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número válido")
                return
            
            try:
                resultado = self.db.agregar_herramienta(
                    nombre=nombre,
                    nombre_clase=clase,
                    descripcion=descripcion if descripcion else None,
                    cantidad=cantidad
                )
                
                if resultado > 0:
                    messagebox.showinfo("Éxito", f"Herramienta '{nombre}' agregada con {cantidad} unidad(es)")
                    self.actualizar_tabla_inventario()
                    ventana.destroy()
                elif resultado == -1:
                    messagebox.showwarning(
                        "Herramienta Existente", 
                        f"La herramienta '{nombre}' ya existe en el inventario.\n\n"
                        "Puedes editarla desde la tabla o usar un nombre diferente."
                    )
                elif resultado == -2:
                    messagebox.showerror("Error", "Error de base de datos. Verifica la consola para más detalles.")
                else:
                    messagebox.showerror("Error", "No se pudo agregar la herramienta")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")
        
        tk.Button(frame_btns, text="Guardar", font=('Arial', 11, 'bold'),
                 bg='#27ae60', fg='black', command=guardar, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="Cancelar", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='black', command=ventana.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def actualizar_herramienta(self):
        """Actualiza una herramienta seleccionada"""
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una herramienta de la tabla")
            return
        
        item = self.tree.item(seleccion[0])
        valores = item['values']
        id_herramienta = valores[0]
        
        herramientas = self.db.listar_herramientas(solo_activas=False)
        herramienta = next((h for h in herramientas if h['id'] == id_herramienta), None)
        
        if not herramienta:
            messagebox.showerror("Error", "No se encontró la herramienta")
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Actualizar Herramienta")
        ventana.geometry("500x450")
        ventana.configure(bg='#2c3e50')
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(
            ventana,
            text="ACTUALIZAR HERRAMIENTA",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=20)
        
        frame_form = tk.Frame(ventana, bg='#34495e', relief=tk.RAISED, bd=2)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(frame_form, text="Nombre*:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        entry_nombre = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_nombre.insert(0, herramienta['nombre'])
        entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Clase YOLO*:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=1, column=0, padx=10, pady=10, sticky='w')
        entry_clase = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_clase.insert(0, herramienta['nombre_clase'])
        entry_clase.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Cantidad:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=2, column=0, padx=10, pady=10, sticky='w')
        entry_cantidad = tk.Entry(frame_form, font=('Arial', 11), width=30)
        entry_cantidad.insert(0, str(herramienta.get('cantidad', 0)))
        entry_cantidad.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(frame_form, text="Descripción:", font=('Arial', 11, 'bold'),
                bg='#34495e', fg='white').grid(row=3, column=0, padx=10, pady=10, sticky='nw')
        text_desc = tk.Text(frame_form, font=('Arial', 10), width=30, height=5)
        if herramienta['descripcion']:
            text_desc.insert('1.0', herramienta['descripcion'])
        text_desc.grid(row=3, column=1, padx=10, pady=10)
        
        frame_btns = tk.Frame(ventana, bg='#2c3e50')
        frame_btns.pack(fill=tk.X, padx=20, pady=10)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            clase = entry_clase.get().strip()
            cantidad_str = entry_cantidad.get().strip()
            descripcion = text_desc.get('1.0', tk.END).strip()
            
            if not nombre or not clase:
                messagebox.showwarning("Advertencia", "Nombre y Clase YOLO son obligatorios")
                return
            
            try:
                cantidad = int(cantidad_str) if cantidad_str else 0
                if cantidad < 0:
                    raise ValueError("La cantidad no puede ser negativa")
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número válido")
                return
            
            try:
                self.db.actualizar_herramienta(
                    id_herramienta=id_herramienta,
                    nombre=nombre,
                    nombre_clase=clase,
                    cantidad=cantidad,
                    descripcion=descripcion if descripcion else None
                )
                messagebox.showinfo("Éxito", "Herramienta actualizada")
                self.actualizar_tabla_inventario()
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
        
        tk.Button(frame_btns, text="Actualizar", font=('Arial', 11, 'bold'),
                 bg='#f39c12', fg='black', command=guardar, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="Cancelar", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='black', command=ventana.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def eliminar_herramienta(self):
        """Elimina una herramienta seleccionada"""
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una herramienta de la tabla")
            return
        
        item = self.tree.item(seleccion[0])
        valores = item['values']
        id_herramienta = valores[0]
        nombre = valores[1]
        
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar '{nombre}'?\n\nEsta acción no se puede deshacer."
        )
        
        if respuesta:
            try:
                self.db.eliminar_herramienta(id_herramienta, permanente=True)
                messagebox.showinfo("Éxito", f"Herramienta '{nombre}' eliminada")
                self.actualizar_tabla_inventario()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")
    
    def actualizar_tabla_inventario(self):
        """Actualiza la tabla de inventario"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        herramientas = self.db.listar_herramientas(solo_activas=False)
        
        for h in herramientas:
            estado = "Activo" if h['activo'] else "Inactivo"
            descripcion = h['descripcion'][:50] + "..." if h['descripcion'] and len(h['descripcion']) > 50 else h['descripcion'] or ""
            cantidad = h.get('cantidad', 0)
            
            self.tree.insert('', tk.END, values=(
                h['id'],
                h['nombre'],
                h['nombre_clase'],
                cantidad,
                descripcion,
                estado
            ))
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación correctamente"""
        self.detener_deteccion()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AplicacionTaller(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar_aplicacion)
    root.mainloop()

if __name__ == "__main__":
    main()