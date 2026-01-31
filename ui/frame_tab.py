"""
Pestaña para ocultar mensajes de texto en frames de video.
Estructura base preparada para desarrollo futuro.
"""

import customtkinter as ctk
from tkinter import messagebox
from core.frame_steganography import FrameStegano


class FrameTab:
    """Pestaña para ocultar texto en frames de video."""
    
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.stegano = FrameStegano()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        
        # Frame principal con padding
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="📄 Ocultar Mensaje en Frames",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text']
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Descripción
        desc = ctk.CTkLabel(
            main_frame,
            text="Oculta mensajes de texto en los frames individuales del video usando esteganografía LSB.\n"
                 "El texto quedará invisible a simple vista pero podrá ser recuperado posteriormente.",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 20))
        
        # Frame de contenido
        content_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_light'], 
                                    corner_radius=15)
        content_frame.pack(fill="both", expand=True)
        
        content = ctk.CTkFrame(content_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Icono y mensaje
        icon_label = ctk.CTkLabel(
            content,
            text="🚧",
            font=ctk.CTkFont(size=80)
        )
        icon_label.pack(pady=(20, 20))
        
        status_label = ctk.CTkLabel(
            content,
            text="Funcionalidad en Desarrollo",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors['warning']
        )
        status_label.pack(pady=(0, 15))
        
        info_label = ctk.CTkLabel(
            content,
            text="Esta funcionalidad estará disponible próximamente.\n\n"
                 "Permitirá:\n"
                 "• Ocultar mensajes de texto en frames de video\n"
                 "• Extraer mensajes ocultos de videos procesados\n"
                 "• Análisis de capacidad de texto\n"
                 "• Opción de encriptación del mensaje\n\n"
                 "Por ahora, puedes usar la pestaña 'Ocultar por Archivo' que está completamente funcional.",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary'],
            justify="center"
        )
        info_label.pack(pady=(0, 30))
        
        # Botón de información
        info_btn = ctk.CTkButton(
            content,
            text="ℹ️ Más Información",
            command=self.show_info,
            fg_color=self.colors['accent'],
            hover_color=self.colors['secondary'],
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_btn.pack()
    
    def show_info(self):
        """Muestra información sobre la funcionalidad."""
        info_text = (
            "🔜 Próximamente: Ocultar Texto en Frames\n\n"
            "Esta funcionalidad permitirá ocultar mensajes de texto directamente "
            "en los frames del video usando el método LSB (Least Significant Bit).\n\n"
            "Características planificadas:\n"
            "• Ocultar hasta varios KB de texto\n"
            "• Encriptación AES opcional\n"
            "• Selección de frames específicos\n"
            "• Análisis de capacidad en tiempo real\n"
            "• Extracción automática de mensajes\n\n"
            "Mientras tanto, la pestaña 'Ocultar por Archivo' está completamente "
            "funcional y puede usarse para ocultar cualquier tipo de archivo."
        )
        messagebox.showinfo("Información", info_text)
