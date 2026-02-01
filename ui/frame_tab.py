"""
Pestaña para ocultar mensajes de texto en frames de video.
Implementación funcional usando LSB con cifrado.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path
from core.frame_steganography import FrameStegano

class FrameTab:
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.stegano = FrameStegano()
        
        # Variables
        self.video_path = None
        self.extract_video_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            self.scroll_frame, text="📄 Ocultar Texto en Píxeles (LSB)",
            font=ctk.CTkFont(size=24, weight="bold"), text_color=self.colors['text']
        )
        title.pack(anchor="w", pady=(0, 10))
        
        desc = ctk.CTkLabel(
            self.scroll_frame,
            text="Oculta mensajes modificando imperceptiblemente los píxeles del video.\n"
                 "Nota: Se guardará como .AVI (códec FFV1) para evitar que la compresión borre el mensaje.",
            font=ctk.CTkFont(size=13), text_color=self.colors['text_secondary'], justify="left"
        )
        desc.pack(anchor="w", pady=(0, 20))
        
        self.create_two_column_layout()

    def create_two_column_layout(self):
        columns_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)
        
        left_column = ctk.CTkFrame(columns_frame, fg_color=self.colors['bg_light'], corner_radius=15)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_column = ctk.CTkFrame(columns_frame, fg_color=self.colors['bg_light'], corner_radius=15)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.setup_hide_column(left_column)
        self.setup_extract_column(right_column)

    def setup_hide_column(self, parent):
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="🔒 Ocultar Mensaje", 
                    font=ctk.CTkFont(size=20, weight="bold"), text_color=self.colors['accent']).pack(anchor="w", pady=(0, 20))
        
        # 1. Video
        ctk.CTkButton(content, text="🎬 Seleccionar Video Fuente", command=self.select_video,
                     fg_color=self.colors['secondary']).pack(fill="x", pady=5)
        self.video_label = ctk.CTkLabel(content, text="Ningún video seleccionado", text_color="gray")
        self.video_label.pack(anchor="w", pady=(0, 10))
        
        # 2. Texto
        ctk.CTkLabel(content, text="Escribe tu mensaje secreto:", text_color=self.colors['text']).pack(anchor="w")
        self.text_input = ctk.CTkTextbox(content, height=80)
        self.text_input.pack(fill="x", pady=(5, 15))
        
        # 3. Clave de cifrado (NUEVO)
        ctk.CTkLabel(content, text="🔑 Clave de cifrado:", text_color=self.colors['text']).pack(anchor="w")
        self.password_input = ctk.CTkEntry(content, placeholder_text="Ingresa una clave segura", show="*")
        self.password_input.pack(fill="x", pady=(5, 15))
        
        # Botón para mostrar/ocultar contraseña
        show_password_frame = ctk.CTkFrame(content, fg_color="transparent")
        show_password_frame.pack(fill="x", pady=(0, 15))
        self.show_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(show_password_frame, text="Mostrar clave", variable=self.show_password_var,
                       command=self.toggle_password_visibility, text_color=self.colors['text']).pack(anchor="w")
        
        # 4. Capacidad
        self.capacity_label = ctk.CTkLabel(content, text="Calculando capacidad...", text_color="gray")
        self.capacity_label.pack(anchor="w", pady=(0, 15))
        
        # 5. Procesar
        self.progress_bar = ctk.CTkProgressBar(content)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.hide_btn = ctk.CTkButton(content, text="🚀 Ocultar Texto", command=self.hide_text,
                                     fg_color=self.colors['success'], state="disabled")
        self.hide_btn.pack(fill="x")

    def setup_extract_column(self, parent):
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="🔓 Leer Mensaje", 
                    font=ctk.CTkFont(size=20, weight="bold"), text_color=self.colors['accent']).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkButton(content, text="🎬 Seleccionar Video Portador", command=self.select_extract_video,
                     fg_color=self.colors['secondary']).pack(fill="x", pady=5)
        self.extract_video_label = ctk.CTkLabel(content, text="Ningún video seleccionado", text_color="gray")
        self.extract_video_label.pack(anchor="w", pady=(0, 15))
        
        # Clave de desencriptado (NUEVO)
        ctk.CTkLabel(content, text="🔑 Ingresa la clave:", text_color=self.colors['text']).pack(anchor="w")
        self.extract_password_input = ctk.CTkEntry(content, placeholder_text="Clave de desencriptado", show="*")
        self.extract_password_input.pack(fill="x", pady=(5, 10))
        
        # Botón para mostrar/ocultar contraseña
        show_extract_frame = ctk.CTkFrame(content, fg_color="transparent")
        show_extract_frame.pack(fill="x", pady=(0, 15))
        self.show_extract_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(show_extract_frame, text="Mostrar clave", variable=self.show_extract_password_var,
                       command=self.toggle_extract_password_visibility, text_color=self.colors['text']).pack(anchor="w")
        
        self.extract_btn = ctk.CTkButton(content, text="🔍 Extraer Mensaje", command=self.extract_text,
                                        fg_color=self.colors['accent'], state="disabled")
        self.extract_btn.pack(fill="x", pady=(0, 15))
        
        self.extract_progress = ctk.CTkProgressBar(content)
        self.extract_progress.set(0)
        self.extract_progress.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(content, text="Mensaje encontrado:", text_color=self.colors['text']).pack(anchor="w")
        self.result_text = ctk.CTkTextbox(content, height=120, state="disabled")
        self.result_text.pack(fill="x")

    def toggle_password_visibility(self):
        """Muestra u oculta la contraseña de ocultamiento."""
        if self.show_password_var.get():
            self.password_input.configure(show="")
        else:
            self.password_input.configure(show="*")

    def toggle_extract_password_visibility(self):
        """Muestra u oculta la contraseña de extracción."""
        if self.show_extract_password_var.get():
            self.extract_password_input.configure(show="")
        else:
            self.extract_password_input.configure(show="*")

    def select_video(self):
        """Selecciona un video y calcula su capacidad."""
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov")])
        if path:
            self.video_path = path
            self.video_label.configure(text=os.path.basename(path), text_color=self.colors['text'])
            self.hide_btn.configure(state="normal")
            
            # Calcular capacidad en segundo plano
            def calculate():
                try:
                    chars, info = self.stegano.calculate_text_capacity(path)
                    capacity_text = (
                        f"✅ Capacidad aprox: {chars:,} caracteres\n"
                        f"   Resolución: {info['width']}x{info['height']} @ {info['fps']:.1f}fps\n"
                        f"   Frames: {info['total_frames']}"
                    )
                    self.capacity_label.configure(text=capacity_text, text_color=self.colors['success'])
                except Exception as e:
                    self.capacity_label.configure(text=f"❌ Error: {str(e)}", text_color="#FF6B6B")
            
            threading.Thread(target=calculate, daemon=True).start()

    def hide_text(self):
        """Oculta el texto en el video."""
        text = self.text_input.get("1.0", "end-1c").strip()
        password = self.password_input.get().strip()
        
        if not text:
            messagebox.showwarning("Error", "El mensaje está vacío")
            return
        
        if not password:
            messagebox.showwarning("Error", "Debes ingresar una clave de cifrado")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Error", "La clave debe tener al menos 4 caracteres")
            return
        
        if not self.video_path:
            messagebox.showwarning("Error", "Selecciona un video primero")
            return
        
        # Validar tamaño del mensaje
        try:
            chars, _ = self.stegano.calculate_text_capacity(self.video_path)
            if len(text) > chars:
                messagebox.showwarning(
                    "Mensaje muy largo",
                    f"El mensaje es demasiado largo.\n"
                    f"Máximo: {chars:,} caracteres\n"
                    f"Tu mensaje: {len(text):,} caracteres"
                )
                return
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular capacidad: {e}")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".avi",
            filetypes=[("AVI Video (Lossless)", "*.avi")],
            initialfile="secret_video.avi"
        )
        if not output_path:
            return
        
        self.hide_btn.configure(state="disabled", text="⏳ Procesando...")
        self.progress_bar.set(0)
        
        def run():
            try:
                success, msg = self.stegano.hide_text_in_video(
                    self.video_path, text, password, output_path,
                    progress_callback=lambda p: self.progress_bar.set(p / 100)
                )
                
                self.hide_btn.configure(state="normal", text="🚀 Ocultar Texto")
                
                if success:
                    messagebox.showinfo("✅ Éxito", msg)
                    self.text_input.delete("1.0", "end")  # Limpiar texto
                    self.password_input.delete(0, "end")  # Limpiar clave
                else:
                    messagebox.showerror("❌ Error", msg)
            except Exception as e:
                self.hide_btn.configure(state="normal", text="🚀 Ocultar Texto")
                messagebox.showerror("Error", f"Error inesperado: {str(e)}")
                
        threading.Thread(target=run, daemon=True).start()

    def select_extract_video(self):
        """Selecciona un video para extraer mensaje."""
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.avi *.mkv *.mp4 *.mov")])
        if path:
            self.extract_video_path = path
            self.extract_video_label.configure(text=os.path.basename(path), text_color=self.colors['text'])
            self.extract_btn.configure(state="normal")

    def extract_text(self):
        """Extrae el mensaje oculto del video."""
        if not self.extract_video_path:
            messagebox.showwarning("Error", "Selecciona un video primero")
            return
        
        password = self.extract_password_input.get().strip()
        
        if not password:
            messagebox.showwarning("Error", "Debes ingresar la clave para desencriptar")
            return
        
        self.extract_btn.configure(state="disabled", text="🔍 Buscando...")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")
        self.extract_progress.set(0)
        
        def run():
            try:
                success, msg, text = self.stegano.extract_text_from_video(
                    self.extract_video_path, password,
                    progress_callback=lambda p: self.extract_progress.set(p / 100)
                )
                
                self.extract_btn.configure(state="normal", text="🔍 Extraer Mensaje")
                
                if success:
                    self.result_text.configure(state="normal")
                    self.result_text.insert("1.0", text)
                    self.result_text.configure(state="disabled")
                    messagebox.showinfo("✅ Encontrado", msg)
                else:
                    messagebox.showwarning("⚠️ Resultado", msg)
            except Exception as e:
                self.extract_btn.configure(state="normal", text="🔍 Extraer Mensaje")
                messagebox.showerror("Error", f"Error inesperado: {str(e)}")
                
        threading.Thread(target=run, daemon=True).start()