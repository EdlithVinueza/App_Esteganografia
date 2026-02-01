"""
Pestaña para ocultar mensajes en el audio de videos.
Estructura base preparada para desarrollo futuro.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from core.audio_steganography import AudioStegano

class AudioTab:
    """
    Pestaña para ocultar MENSAJES DE TEXTO en Audio/Video.
    Diseño de dos columnas (Ocultar / Revelar).
    """
    
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.stegano = AudioStegano()
        
        # Variables de estado
        self.hide_file_path = None      # Archivo original para ocultar
        self.extract_file_path = None   # Archivo procesado para extraer
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario con Scroll y 2 columnas."""
        
        # Frame principal con Scroll (Igual que FileTab)
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- HEADER ---
        title = ctk.CTkLabel(
            self.scroll_frame,
            text="🔊 Ocultar Texto en Audio/Video",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text']
        )
        title.pack(anchor="w", pady=(0, 10))
        
        desc = ctk.CTkLabel(
            self.scroll_frame,
            text="Oculta mensajes secretos de texto dentro de las frecuencias de audio de tus videos (.mp4) o archivos de sonido (.wav).\n"
                 "El mensaje es resistente a la compresión de video.",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 20))
        
        # --- LAYOUT DE 2 COLUMNAS ---
        self.create_two_column_layout()

    def create_two_column_layout(self):
        columns_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)
        
        # Columna Izquierda (Ocultar)
        left_column = ctk.CTkFrame(columns_frame, fg_color=self.colors['bg_light'], corner_radius=15)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Columna Derecha (Extraer)
        right_column = ctk.CTkFrame(columns_frame, fg_color=self.colors['bg_light'], corner_radius=15)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.setup_hide_column(left_column)
        self.setup_extract_column(right_column)

    # ------------------------------------------------------------------------
    #                           COLUMNA IZQUIERDA: OCULTAR
    # ------------------------------------------------------------------------
    def setup_hide_column(self, parent):
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Título
        ctk.CTkLabel(content, text="🔒 Ocultar Mensaje", font=ctk.CTkFont(size=20, weight="bold"), 
                     text_color=self.colors['accent']).pack(anchor="w", pady=(0, 20))
        
        # 1. Seleccionar Video/Audio
        self.create_section_header(content, "1️⃣ Seleccionar Archivo Multimedia")
        
        file_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], corner_radius=10)
        file_frame.pack(fill="x", pady=(5, 15))
        
        file_content = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_content.pack(fill="x", padx=15, pady=15)
        
        self.lbl_hide_filename = ctk.CTkLabel(file_content, text="🚫 Ningún archivo seleccionado", 
                                              text_color=self.colors['text_secondary'], font=ctk.CTkFont(size=12))
        self.lbl_hide_filename.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkButton(file_content, text="📂 Buscar Video o Audio", command=self.select_hide_file,
                      fg_color=self.colors['secondary'], hover_color=self.colors['primary'], width=200).pack(fill="x")

        # 2. Escribir Mensaje
        self.create_section_header(content, "2️⃣ Escribir Mensaje Secreto")
        
        self.msg_input = ctk.CTkTextbox(content, height=120, corner_radius=10, border_width=1, border_color=self.colors['bg_dark'])
        self.msg_input.pack(fill="x", pady=(5, 15))

        # 3. Procesar
        self.create_section_header(content, "3️⃣ Procesar y Guardar")
        
        process_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], corner_radius=10)
        process_frame.pack(fill="x", pady=(5, 0))
        process_inner = ctk.CTkFrame(process_frame, fg_color="transparent")
        process_inner.pack(fill="x", padx=15, pady=15)

        self.progress_bar_hide = ctk.CTkProgressBar(process_inner, mode="determinate", progress_color=self.colors['success'])
        self.progress_bar_hide.pack(fill="x", pady=(0, 10))
        self.progress_bar_hide.set(0)
        
        self.status_lbl_hide = ctk.CTkLabel(process_inner, text="Listo para procesar", font=ctk.CTkFont(size=11), text_color=self.colors['text_secondary'])
        self.status_lbl_hide.pack(anchor="w", pady=(0, 10))

        self.btn_hide = ctk.CTkButton(process_inner, text="🚀 Ocultar Mensaje", command=self.run_hide_process,
                                      fg_color=self.colors['success'], height=45, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_hide.pack(fill="x")

    # ------------------------------------------------------------------------
    #                           COLUMNA DERECHA: EXTRAER
    # ------------------------------------------------------------------------
    def setup_extract_column(self, parent):
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Título
        ctk.CTkLabel(content, text="🔓 Revelar Mensaje", font=ctk.CTkFont(size=20, weight="bold"), 
                     text_color=self.colors['accent']).pack(anchor="w", pady=(0, 20))
        
        # 1. Seleccionar Video/Audio
        self.create_section_header(content, "1️⃣ Seleccionar Archivo con Mensaje")
        
        file_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], corner_radius=10)
        file_frame.pack(fill="x", pady=(5, 15))
        
        file_content = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_content.pack(fill="x", padx=15, pady=15)
        
        self.lbl_extract_filename = ctk.CTkLabel(file_content, text="🚫 Ningún archivo seleccionado", 
                                                 text_color=self.colors['text_secondary'], font=ctk.CTkFont(size=12))
        self.lbl_extract_filename.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkButton(file_content, text="📂 Buscar Video o Audio", command=self.select_extract_file,
                      fg_color=self.colors['secondary'], hover_color=self.colors['primary']).pack(fill="x")

        # 2. Extraer
        self.create_section_header(content, "2️⃣ Analizar y Extraer")
        
        process_frame = ctk.CTkFrame(content, fg_color=self.colors['bg_dark'], corner_radius=10)
        process_frame.pack(fill="x", pady=(5, 15))
        process_inner = ctk.CTkFrame(process_frame, fg_color="transparent")
        process_inner.pack(fill="x", padx=15, pady=15)
        
        self.progress_bar_extract = ctk.CTkProgressBar(process_inner, mode="determinate", progress_color=self.colors['accent'])
        self.progress_bar_extract.pack(fill="x", pady=(0, 10))
        self.progress_bar_extract.set(0)

        self.status_lbl_extract = ctk.CTkLabel(process_inner, text="Listo para analizar", font=ctk.CTkFont(size=11), text_color=self.colors['text_secondary'])
        self.status_lbl_extract.pack(anchor="w", pady=(0, 10))

        self.btn_extract = ctk.CTkButton(process_inner, text="🔍 Analizar Archivo", command=self.run_extract_process,
                                         fg_color=self.colors['accent'], height=45, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_extract.pack(fill="x")

        # 3. Resultado
        self.create_section_header(content, "3️⃣ Mensaje Encontrado")
        self.msg_output = ctk.CTkTextbox(content, height=150, corner_radius=10, state="disabled", 
                                         border_width=1, border_color=self.colors['bg_dark'])
        self.msg_output.pack(fill="both", expand=True, pady=(5, 0))

    # --- AYUDAS ---
    def create_section_header(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=14, weight="bold"), 
                     text_color=self.colors['text']).pack(anchor="w", pady=(10, 5))

    # --- LÓGICA DE SELECCIÓN ---
    def select_hide_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Video o Audio",
            filetypes=[("Multimedia", "*.mp4 *.avi *.wav *.mkv"), ("Todos", "*.*")]
        )
        if filename:
            self.hide_file_path = filename
            self.lbl_hide_filename.configure(text=f"✅ {os.path.basename(filename)}")
            self.status_lbl_hide.configure(text="Archivo cargado.")
            self.progress_bar_hide.set(0)

    def select_extract_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Video o Audio con Mensaje",
            filetypes=[("Multimedia", "*.mp4 *.avi *.wav *.mkv"), ("Todos", "*.*")]
        )
        if filename:
            self.extract_file_path = filename
            self.lbl_extract_filename.configure(text=f"✅ {os.path.basename(filename)}")
            self.status_lbl_extract.configure(text="Archivo cargado.")
            self.msg_output.configure(state="normal")
            self.msg_output.delete("1.0", "end")
            self.msg_output.configure(state="disabled")
            self.progress_bar_extract.set(0)

    # --- LÓGICA DE PROCESAMIENTO (THREADS) ---
    
    # 1. OCULTAR
    def run_hide_process(self):
        if self.is_processing: return
        if not self.hide_file_path:
            messagebox.showwarning("Atención", "Selecciona un archivo multimedia primero.")
            return
        
        message = self.msg_input.get("1.0", "end-1c").strip()
        if not message:
            messagebox.showwarning("Atención", "Escribe un mensaje secreto.")
            return

        # Pedir dónde guardar
        _, ext = os.path.splitext(self.hide_file_path)
        save_path = filedialog.asksaveasfilename(
            title="Guardar Resultado",
            defaultextension=ext,
            filetypes=[("Mismo formato", f"*{ext}")]
        )
        if not save_path: return

        # UI Update
        self.is_processing = True
        self.btn_hide.configure(state="disabled", text="⏳ Procesando...")
        self.status_lbl_hide.configure(text="Iniciando codificación...")
        self.progress_bar_hide.set(0)

        # Thread
        thread = threading.Thread(target=self._hide_thread, args=(message, save_path))
        thread.daemon = True
        thread.start()

    def _hide_thread(self, message, save_path):
        def update_prog(val):
            self.progress_bar_hide.set(val/100)
        
        success, info = self.stegano.hide_text_in_audio(self.hide_file_path, message, save_path, update_prog)
        
        # Volver al hilo principal
        self.parent.after(0, self._hide_complete, success, info, save_path)

    def _hide_complete(self, success, info, save_path):
        self.is_processing = False
        self.btn_hide.configure(state="normal", text="🚀 Ocultar Mensaje")
        
        if success:
            self.progress_bar_hide.set(1)
            self.status_lbl_hide.configure(text="¡Proceso Exitoso!")
            messagebox.showinfo("Éxito", f"Mensaje ocultado en:\n{os.path.basename(save_path)}")
            self.msg_input.delete("1.0", "end")
        else:
            self.progress_bar_hide.set(0)
            self.status_lbl_hide.configure(text="Error")
            messagebox.showerror("Error", info)

    # 2. EXTRAER
    def run_extract_process(self):
        if self.is_processing: return
        if not self.extract_file_path:
            messagebox.showwarning("Atención", "Selecciona el archivo para analizar.")
            return

        self.is_processing = True
        self.btn_extract.configure(state="disabled", text="⏳ Analizando...")
        self.status_lbl_extract.configure(text="Analizando frecuencias...")
        self.progress_bar_extract.set(0.5) # Indeterminado

        thread = threading.Thread(target=self._extract_thread)
        thread.daemon = True
        thread.start()

    def _extract_thread(self):
        success, info, text = self.stegano.extract_text_from_audio(self.extract_file_path)
        self.parent.after(0, self._extract_complete, success, info, text)

    def _extract_complete(self, success, info, text):
        self.is_processing = False
        self.btn_extract.configure(state="normal", text="🔍 Analizar Archivo")
        self.progress_bar_extract.set(1)
        
        self.msg_output.configure(state="normal")
        self.msg_output.delete("1.0", "end")
        
        if success:
            self.status_lbl_extract.configure(text="Mensaje Encontrado")
            self.msg_output.insert("1.0", text)
            messagebox.showinfo("Éxito", "¡Mensaje secreto encontrado!")
        else:
            self.status_lbl_extract.configure(text="No se encontró nada")
            self.msg_output.insert("1.0", f"--- {info} ---")
            messagebox.showwarning("Resultado", info)
        
        self.msg_output.configure(state="disabled")