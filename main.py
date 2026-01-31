"""
Aplicación de Esteganografía de Video
Permite ocultar información en videos mediante tres métodos:
- Ocultar por Frame: Mensajes de texto en frames
- Ocultar por Audio: Mensajes en la pista de audio
- Ocultar por Archivo: Archivos completos en el video

Autor: Video Steganography Team
Versión: 1.0.0
"""

import sys
import os

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import run_app


def main():
    """Función principal de la aplicación."""
    print("=" * 60)
    print("🎥 Video Steganography Application")
    print("=" * 60)
    print("Iniciando aplicación...")
    print("Presiona Ctrl+C en la terminal para cerrar la aplicación")
    print("=" * 60)
    
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación cerrada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
