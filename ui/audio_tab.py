"""
Pestaña para ocultar mensajes en el audio de videos.
Estructura base preparada para desarrollo futuro.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from core.audio_steganography import AudioStegano

class AudioTab:
    """Pestaña para esteganografía en VIDEO y AUDIO."""
    
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.stegano = AudioStegano()
        self.selected_file = None
        self.setup_ui()
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- HEADER ---
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="🎬 Video & Audio Steganography", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color=self.colors['text']).pack(anchor="w")
        
        ctk.CTkLabel(header, text="Oculta mensajes en el audio de tus videos (.mp4) o archivos de sonido (.wav).",
                     text_color=self.colors['text_secondary']).pack(anchor="w")

        # --- SELECCIÓN ---
        file_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['bg_light'])
        file_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(file_frame, text="Archivo Multimedia:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        input_box = ctk.CTkFrame(file_frame, fg_color="transparent")
        input_box.pack(fill="x", padx=15, pady=(0, 15))
        
        self.file_entry = ctk.CTkEntry(input_box, placeholder_text="Selecciona video (.mp4) o audio (.wav)...")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # BOTÓN BUSCAR
        ctk.CTkButton(input_box, text="📂 Buscar", width=100, command=self.select_file,
                      fg_color=self.colors['primary']).pack(side="right")

        # --- TABS ---
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)
        self.tab_view.add("Ocultar")
        self.tab_view.add("Revelar")
        
        # Tab Ocultar
        hide_tab = self.tab_view.tab("Ocultar")
        ctk.CTkLabel(hide_tab, text="Mensaje Secreto:", anchor="w").pack(fill="x", pady=5)
        self.msg_input = ctk.CTkTextbox(hide_tab, height=100)
        self.msg_input.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkButton(hide_tab, text="🔒 Procesar y Guardar", command=self.run_hide,
                      fg_color=self.colors['accent'], height=40).pack(fill="x", pady=10)

        # Tab Revelar
        reveal_tab = self.tab_view.tab("Revelar")
        ctk.CTkLabel(reveal_tab, text="Mensaje Encontrado:", anchor="w").pack(fill="x", pady=5)
        self.msg_output = ctk.CTkTextbox(reveal_tab, height=100, state="disabled")
        self.msg_output.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkButton(reveal_tab, text="🔓 Analizar Archivo", command=self.run_extract,
                      fg_color=self.colors['success'], height=40).pack(fill="x", pady=10)

        # --- STATUS ---
        self.status_bar = ctk.CTkProgressBar(self.main_frame)
        self.status_bar.pack(fill="x", pady=(10, 5))
        self.status_bar.set(0)
        self.status_lbl = ctk.CTkLabel(self.main_frame, text="Listo")
        self.status_lbl.pack(anchor="e")

    def select_file(self):
        # AHORA ACEPTA VIDEO Y AUDIO
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo",
            filetypes=[
                ("Video y Audio", "*.mp4 *.avi *.wav"),
                ("Video MP4", "*.mp4"),
                ("Audio WAV", "*.wav")
            ]
        )
        if filename:
            self.selected_file = filename
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)
            self.status_lbl.configure(text=f"Cargado: {os.path.basename(filename)}")
            self.status_bar.set(0)

    def update_prog(self, val):
        self.status_bar.set(val/100)
        self.parent.update_idletasks()

    def run_hide(self):
        if not self.selected_file: return
        msg = self.msg_input.get("1.0", "end-1c").strip()
        if not msg: return messagebox.showwarning("Error", "Escribe un mensaje")

        # Detectar extensión para guardar con la misma
        _, ext = os.path.splitext(self.selected_file)
        save_path = filedialog.asksaveasfilename(
            title="Guardar Resultado",
            defaultextension=ext,
            filetypes=[("Mismo formato", f"*{ext}")]
        )
        if not save_path: return

        self.status_lbl.configure(text="Procesando... Espere...")
        self.parent.after(100, lambda: self._exec_hide(msg, save_path))

    def _exec_hide(self, msg, path):
        ok, info = self.stegano.hide_text_in_audio(self.selected_file, msg, path, self.update_prog)
        self.status_lbl.configure(text=info if ok else "Error")
        self.status_bar.set(1 if ok else 0)
        if ok: messagebox.showinfo("Éxito", f"Archivo guardado en:\n{path}")
        else: messagebox.showerror("Error", info)

    def run_extract(self):
        if not self.selected_file: return
        self.status_lbl.configure(text="Analizando...")
        self.status_bar.set(0.5)
        self.parent.after(100, self._exec_extract)

    def _exec_extract(self):
        ok, info, text = self.stegano.extract_text_from_audio(self.selected_file)
        self.status_bar.set(1)
        self.status_lbl.configure(text=info)
        
        self.msg_output.configure(state="normal")
        self.msg_output.delete("1.0", "end")
        self.msg_output.insert("1.0", text if ok else f"--- {info} ---")
        self.msg_output.configure(state="disabled")
        
        if ok: messagebox.showinfo("Encontrado", "¡Mensaje secreto detectado!")
        else: messagebox.showwarning("Resultado", info)