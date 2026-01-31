"""
Ventana principal de la aplicación de esteganografía de video.
Interfaz moderna con CustomTkinter inspirada en diseños contemporáneos.
"""

import customtkinter as ctk
from ui.frame_tab import FrameTab
from ui.audio_tab import AudioTab
from ui.file_tab import FileTab


class MainWindow(ctk.CTk):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Video Steganography - Oculta información en videos")
        self.geometry("1200x800")
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Colores personalizados inspirados en la imagen
        self.colors = {
            'primary': '#1e3a5f',      # Azul oscuro
            'secondary': '#2d5f7f',    # Azul medio
            'accent': '#4a9eff',       # Azul claro
            'success': '#4ade80',      # Verde
            'warning': '#fbbf24',      # Amarillo
            'error': '#f87171',        # Rojo
            'bg_dark': '#1a1a2e',      # Fondo oscuro
            'bg_light': '#16213e',     # Fondo claro
            'text': '#eaeaea',         # Texto claro
            'text_secondary': '#a0a0a0' # Texto secundario
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        
        # Frame principal con padding
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Tabview para las diferentes funcionalidades
        self.create_tabview()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Crea el header de la aplicación."""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['primary'], 
                                   corner_radius=15, height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Contenedor interno con padding
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            header_content,
            text="🎥 Video Steganography",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['text']
        )
        title_label.pack(anchor="w")
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_content,
            text="Oculta información secreta en videos de forma segura e imperceptible",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
    
    def create_tabview(self):
        """Crea el tabview con las tres funcionalidades."""
        # Frame contenedor para el tabview
        tab_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        tab_container.pack(fill="both", expand=True)
        
        # Tabview
        self.tabview = ctk.CTkTabview(
            tab_container,
            corner_radius=15,
            fg_color=self.colors['bg_light'],
            segmented_button_fg_color=self.colors['secondary'],
            segmented_button_selected_color=self.colors['accent'],
            segmented_button_selected_hover_color=self.colors['primary']
        )
        self.tabview.pack(fill="both", expand=True)
        
        # Crear las tres pestañas
        tab_frame = self.tabview.add("📄 Ocultar por Frame")
        tab_audio = self.tabview.add("🔊 Ocultar por Audio")
        tab_file = self.tabview.add("📦 Ocultar por Archivo")
        
        # Inicializar las pestañas con sus respectivas vistas
        self.frame_tab = FrameTab(tab_frame, self.colors)
        self.audio_tab = AudioTab(tab_audio, self.colors)
        self.file_tab = FileTab(tab_file, self.colors)
    
    def create_footer(self):
        """Crea el footer de la aplicación."""
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=40)
        footer_frame.pack(fill="x", pady=(20, 0))
        footer_frame.pack_propagate(False)
        
        # Información del footer
        footer_label = ctk.CTkLabel(
            footer_frame,
            text="💡 Tip: Usa videos sin compresión para mejores resultados | Desarrollado con Python & CustomTkinter",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        footer_label.pack(side="left")
        
        # Versión
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        version_label.pack(side="right")


def run_app():
    """Función para ejecutar la aplicación."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    run_app()
