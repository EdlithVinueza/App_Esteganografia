"""
Pestaña para ocultar archivos completos en videos.
Implementación completa con todas las funcionalidades.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path
from core.file_steganography import FileStegano


class FileTab:
    """Pestaña para ocultar archivos en videos."""
    
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.stegano = FileStegano()
        
        # Variables
        self.video_path = None
        self.file_path = None
        self.output_path = None
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        
        # Scroll frame principal
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título de la sección
        title = ctk.CTkLabel(
            self.scroll_frame,
            text="📦 Ocultar Archivo Completo en Video",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text']
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Descripción
        desc = ctk.CTkLabel(
            self.scroll_frame,
            text="Incrusta cualquier tipo de archivo dentro de un video usando esteganografía LSB.\n"
                 "El archivo quedará completamente oculto y el video mantendrá su apariencia original.",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 20))
        
        # Crear las dos columnas principales
        self.create_two_column_layout()
    
    def create_two_column_layout(self):
        """Crea el layout de dos columnas."""
        
        # Frame contenedor de columnas
        columns_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)
        
        # Columna izquierda - Ocultar archivo
        left_column = ctk.CTkFrame(columns_frame, fg_color=self.colors['bg_light'], 
                                  corner_radius=15)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Columna derecha - Extraer archivo
        right_column = ctk.CTkFrame(columns_frame, fg_color=self.colors['bg_light'], 
                                   corner_radius=15)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Configurar columnas
        self.setup_hide_column(left_column)
        self.setup_extract_column(right_column)
    
    def setup_hide_column(self, parent):
        """Configura la columna para ocultar archivos."""
        
        # Padding interno
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Título
        title = ctk.CTkLabel(
            content,
            text="🔒 Ocultar Archivo",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['accent']
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Sección 1: Seleccionar video
        self.create_section_header(content, "1️⃣ Seleccionar Video")
        
        video_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], 
                                  corner_radius=10)
        video_frame.pack(fill="x", pady=(5, 15))
        
        video_content = ctk.CTkFrame(video_frame, fg_color="transparent")
        video_content.pack(fill="x", padx=15, pady=15)
        
        self.video_label = ctk.CTkLabel(
            video_content,
            text="📹 No se ha seleccionado ningún video",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.video_label.pack(anchor="w", pady=(0, 10))
        
        video_btn = ctk.CTkButton(
            video_content,
            text="🎬 Seleccionar Video",
            command=self.select_video,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['primary'],
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        video_btn.pack(fill="x")
        
        # Información del video
        self.video_info_label = ctk.CTkLabel(
            video_content,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        self.video_info_label.pack(anchor="w", pady=(10, 0))
        
        # Sección 2: Seleccionar archivo
        self.create_section_header(content, "2️⃣ Seleccionar Archivo a Ocultar")
        
        file_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], 
                                 corner_radius=10)
        file_frame.pack(fill="x", pady=(5, 15))
        
        file_content = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_content.pack(fill="x", padx=15, pady=15)
        
        self.file_label = ctk.CTkLabel(
            file_content,
            text="📄 No se ha seleccionado ningún archivo",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.file_label.pack(anchor="w", pady=(0, 10))
        
        file_btn = ctk.CTkButton(
            file_content,
            text="📁 Seleccionar Archivo",
            command=self.select_file,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['primary'],
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        file_btn.pack(fill="x")
        
        # Información del archivo
        self.file_info_label = ctk.CTkLabel(
            file_content,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        self.file_info_label.pack(anchor="w", pady=(10, 0))
        
        # Mostrar formatos soportados
        formats_btn = ctk.CTkButton(
            file_content,
            text="ℹ️ Ver formatos soportados",
            command=self.show_supported_formats,
            fg_color="transparent",
            hover_color=self.colors['bg_dark'],
            height=30,
            font=ctk.CTkFont(size=11)
        )
        formats_btn.pack(fill="x", pady=(5, 0))
        
        # Sección 3: Análisis de capacidad
        self.create_section_header(content, "3️⃣ Análisis de Capacidad")
        
        capacity_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], 
                                     corner_radius=10)
        capacity_frame.pack(fill="x", pady=(5, 15))
        
        capacity_content = ctk.CTkFrame(capacity_frame, fg_color="transparent")
        capacity_content.pack(fill="x", padx=15, pady=15)
        
        self.capacity_label = ctk.CTkLabel(
            capacity_content,
            text="⏳ Selecciona un video y un archivo para analizar la capacidad",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            justify="left",
            wraplength=400
        )
        self.capacity_label.pack(anchor="w")
        
        analyze_btn = ctk.CTkButton(
            capacity_content,
            text="🔍 Analizar Capacidad",
            command=self.analyze_capacity,
            fg_color=self.colors['accent'],
            hover_color=self.colors['secondary'],
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        analyze_btn.pack(fill="x", pady=(10, 0))
        
        # Sección 4: Procesar
        self.create_section_header(content, "4️⃣ Ocultar Archivo")
        
        process_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], 
                                    corner_radius=10)
        process_frame.pack(fill="x", pady=(5, 0))
        
        process_content = ctk.CTkFrame(process_frame, fg_color="transparent")
        process_content.pack(fill="x", padx=15, pady=15)
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            process_content,
            mode="determinate",
            progress_color=self.colors['success']
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            process_content,
            text="Listo para procesar",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.progress_label.pack(anchor="w", pady=(0, 10))
        
        # Botón de procesar
        self.hide_btn = ctk.CTkButton(
            process_content,
            text="🚀 Ocultar Archivo en Video",
            command=self.hide_file,
            fg_color=self.colors['success'],
            hover_color="#22c55e",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.hide_btn.pack(fill="x")
    
    def setup_extract_column(self, parent):
        """Configura la columna para extraer archivos."""
        
        # Padding interno
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Título
        title = ctk.CTkLabel(
            content,
            text="🔓 Extraer Archivo",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['accent']
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Descripción
        desc = ctk.CTkLabel(
            content,
            text="Extrae archivos ocultos de videos procesados previamente.",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            justify="left",
            wraplength=400
        )
        desc.pack(anchor="w", pady=(0, 20))
        
        # Sección 1: Seleccionar video
        self.create_section_header(content, "1️⃣ Seleccionar Video con Archivo Oculto")
        
        extract_video_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], 
                                          corner_radius=10)
        extract_video_frame.pack(fill="x", pady=(5, 15))
        
        extract_video_content = ctk.CTkFrame(extract_video_frame, fg_color="transparent")
        extract_video_content.pack(fill="x", padx=15, pady=15)
        
        self.extract_video_label = ctk.CTkLabel(
            extract_video_content,
            text="📹 No se ha seleccionado ningún video",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.extract_video_label.pack(anchor="w", pady=(0, 10))
        
        extract_video_btn = ctk.CTkButton(
            extract_video_content,
            text="🎬 Seleccionar Video",
            command=self.select_video_to_extract,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['primary'],
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        extract_video_btn.pack(fill="x")
        
        # Sección 2: Extraer
        self.create_section_header(content, "2️⃣ Extraer Archivo")
        
        extract_process_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], 
                                            corner_radius=10)
        extract_process_frame.pack(fill="x", pady=(5, 15))
        
        extract_process_content = ctk.CTkFrame(extract_process_frame, fg_color="transparent")
        extract_process_content.pack(fill="x", padx=15, pady=15)
        
        # Barra de progreso para extracción
        self.extract_progress_bar = ctk.CTkProgressBar(
            extract_process_content,
            mode="determinate",
            progress_color=self.colors['accent']
        )
        self.extract_progress_bar.pack(fill="x", pady=(0, 10))
        self.extract_progress_bar.set(0)
        
        self.extract_progress_label = ctk.CTkLabel(
            extract_process_content,
            text="Listo para extraer",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.extract_progress_label.pack(anchor="w", pady=(0, 10))
        
        # Botón de extraer
        self.extract_btn = ctk.CTkButton(
            extract_process_content,
            text="📤 Extraer Archivo del Video",
            command=self.extract_file,
            fg_color=self.colors['accent'],
            hover_color=self.colors['secondary'],
            height=50,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.extract_btn.pack(fill="x")
        
        # Resultado de extracción
        self.extract_result_label = ctk.CTkLabel(
            extract_process_content,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary'],
            justify="left",
            wraplength=400
        )
        self.extract_result_label.pack(anchor="w", pady=(15, 0))
    
    def create_section_header(self, parent, text):
        """Crea un encabezado de sección."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text']
        )
        label.pack(anchor="w", pady=(10, 5))
    
    def select_video(self):
        """Selecciona el video para ocultar archivo."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Video",
            filetypes=[
                ("Videos", "*.mp4 *.avi *.mkv *.mov *.wmv"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            filename = os.path.basename(file_path)
            self.video_label.configure(text=f"✅ {filename}")
            
            # Obtener información del video
            try:
                _, info = self.stegano.calculate_video_capacity(file_path)
                info_text = (
                    f"📊 Resolución: {info['width']}x{info['height']} | "
                    f"Frames: {info['total_frames']} | "
                    f"Duración: {info['duration_seconds']:.1f}s\n"
                    f"💾 Capacidad máxima: {info['usable_capacity_mb']:.2f} MB"
                )
                self.video_info_label.configure(text=info_text)
            except Exception as e:
                self.video_info_label.configure(text=f"⚠️ Error al leer video: {str(e)}")
    
    def select_file(self):
        """Selecciona el archivo a ocultar."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Archivo a Ocultar",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            # Verificar si es soportado
            is_supported, msg = self.stegano.is_file_supported(file_path)
            category = self.stegano.get_file_category(file_path)
            
            self.file_label.configure(text=f"✅ {filename}")
            
            info_text = f"📦 Tamaño: {file_size:.2f} MB | Tipo: {category.upper()}\n{msg}"
            self.file_info_label.configure(text=info_text)
    
    def show_supported_formats(self):
        """Muestra los formatos soportados."""
        formats_text = self.stegano.get_supported_formats_text()
        messagebox.showinfo("Formatos Soportados", formats_text)
    
    def analyze_capacity(self):
        """Analiza si el archivo cabe en el video."""
        if not self.video_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona un video primero")
            return
        
        if not self.file_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo primero")
            return
        
        try:
            can_hide, msg, info = self.stegano.can_hide_file(self.video_path, self.file_path)
            
            if can_hide:
                self.capacity_label.configure(
                    text=msg,
                    text_color=self.colors['success']
                )
            else:
                self.capacity_label.configure(
                    text=msg,
                    text_color=self.colors['error']
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar capacidad: {str(e)}")
    
    def hide_file(self):
        """Oculta el archivo en el video."""
        if self.is_processing:
            messagebox.showwarning("Advertencia", "Ya hay un proceso en ejecución")
            return
        
        if not self.video_path or not self.file_path:
            messagebox.showwarning("Advertencia", "Selecciona un video y un archivo primero")
            return
        
        # Verificar capacidad
        can_hide, msg, _ = self.stegano.can_hide_file(self.video_path, self.file_path)
        if not can_hide:
            messagebox.showerror("Error", msg)
            return
        
        # Seleccionar ubicación de salida
        output_path = filedialog.asksaveasfilename(
            title="Guardar Video con Archivo Oculto",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4"), ("AVI Video", "*.avi")]
        )
        
        if not output_path:
            return
        
        self.output_path = output_path
        self.is_processing = True
        self.hide_btn.configure(state="disabled", text="⏳ Procesando...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Iniciando proceso...")
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=self._hide_file_thread)
        thread.daemon = True
        thread.start()
    
    def _hide_file_thread(self):
        """Thread para ocultar archivo."""
        def update_progress(progress):
            self.progress_bar.set(progress / 100)
            self.progress_label.configure(text=f"Procesando... {progress}%")
        
        success, msg = self.stegano.hide_file_in_video(
            self.video_path,
            self.file_path,
            self.output_path,
            progress_callback=update_progress
        )
        
        # Actualizar UI en el thread principal
        self.parent.after(0, self._hide_file_complete, success, msg)
    
    def _hide_file_complete(self, success, msg):
        """Callback cuando termina de ocultar archivo."""
        self.is_processing = False
        self.hide_btn.configure(state="normal", text="🚀 Ocultar Archivo en Video")
        
        if success:
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="✅ ¡Completado!")
            messagebox.showinfo("Éxito", msg)
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text="❌ Error en el proceso")
            messagebox.showerror("Error", msg)
    
    def select_video_to_extract(self):
        """Selecciona el video del cual extraer archivo."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Video con Archivo Oculto",
            filetypes=[
                ("Videos", "*.mp4 *.avi *.mkv *.mov *.wmv"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.extract_video_path = file_path
            filename = os.path.basename(file_path)
            self.extract_video_label.configure(text=f"✅ {filename}")
    
    def extract_file(self):
        """Extrae el archivo del video."""
        if self.is_processing:
            messagebox.showwarning("Advertencia", "Ya hay un proceso en ejecución")
            return
        
        if not hasattr(self, 'extract_video_path') or not self.extract_video_path:
            messagebox.showwarning("Advertencia", "Selecciona un video primero")
            return
        
        # Seleccionar directorio de salida
        output_dir = filedialog.askdirectory(title="Seleccionar carpeta para guardar el archivo")
        
        if not output_dir:
            return
        
        self.is_processing = True
        self.extract_btn.configure(state="disabled", text="⏳ Extrayendo...")
        self.extract_progress_bar.set(0)
        self.extract_progress_label.configure(text="Iniciando extracción...")
        self.extract_result_label.configure(text="")
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=self._extract_file_thread, args=(output_dir,))
        thread.daemon = True
        thread.start()
    
    def _extract_file_thread(self, output_dir):
        """Thread para extraer archivo."""
        def update_progress(progress):
            self.extract_progress_bar.set(progress / 100)
            self.extract_progress_label.configure(text=f"Extrayendo... {progress}%")
        
        success, msg, extracted_path = self.stegano.extract_file_from_video(
            self.extract_video_path,
            output_dir,
            progress_callback=update_progress
        )
        
        # Actualizar UI en el thread principal
        self.parent.after(0, self._extract_file_complete, success, msg, extracted_path)
    
    def _extract_file_complete(self, success, msg, extracted_path):
        """Callback cuando termina de extraer archivo."""
        self.is_processing = False
        self.extract_btn.configure(state="normal", text="📤 Extraer Archivo del Video")
        
        if success:
            self.extract_progress_bar.set(1.0)
            self.extract_progress_label.configure(text="✅ ¡Completado!")
            self.extract_result_label.configure(text=msg, text_color=self.colors['success'])
            messagebox.showinfo("Éxito", msg)
        else:
            self.extract_progress_bar.set(0)
            self.extract_progress_label.configure(text="❌ Error en la extracción")
            self.extract_result_label.configure(text=msg, text_color=self.colors['error'])
            messagebox.showerror("Error", msg)
