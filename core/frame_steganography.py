"""
Módulo para ocultar mensajes de texto en los frames de videos usando esteganografía LSB.
"""

import cv2
import numpy as np
from typing import Tuple
from pathlib import Path


class FrameStegano:
    """Clase para manejar la esteganografía de texto en frames de video."""
    
    MAGIC_MARKER = b'STEG_TEXT_START'
    MAGIC_END = b'STEG_TEXT_END'
    
    def __init__(self):
        self.temp_dir = Path("temp")
        self.output_dir = Path("output")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def calculate_text_capacity(self, video_path: str) -> Tuple[int, dict]:
        """
        Calcula cuántos caracteres de texto se pueden ocultar en el video.
        
        Returns:
            Tuple[int, dict]: (capacidad_en_caracteres, info_video)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("No se pudo abrir el video")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # Calcular capacidad
        pixels_per_frame = width * height
        bits_per_frame = pixels_per_frame * 3  # 3 canales RGB
        bytes_per_frame = bits_per_frame // 8
        
        # Reservar frames para overhead
        usable_frames = max(0, total_frames - 5)
        total_bytes = bytes_per_frame * usable_frames
        
        # Restar overhead de marcadores
        overhead = len(self.MAGIC_MARKER) + len(self.MAGIC_END) + 100
        usable_bytes = max(0, total_bytes - overhead)
        
        # Caracteres UTF-8 (aproximadamente 1-4 bytes por carácter, usamos 2 como promedio)
        approx_chars = usable_bytes // 2
        
        info = {
            'total_frames': total_frames,
            'usable_frames': usable_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'duration_seconds': total_frames / fps if fps > 0 else 0,
            'capacity_bytes': usable_bytes,
            'capacity_chars': approx_chars
        }
        
        return approx_chars, info
    
    def hide_text_in_video(self, video_path: str, text: str, output_path: str,
                          progress_callback=None) -> Tuple[bool, str]:
        """
        Oculta texto en los frames de un video.
        
        Args:
            video_path: Ruta del video original
            text: Texto a ocultar
            output_path: Ruta del video de salida
            progress_callback: Función callback para reportar progreso (0-100)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # TODO: Implementar lógica completa de ocultación de texto
            # Por ahora, retorna un placeholder
            return False, "⚠️ Funcionalidad en desarrollo. Próximamente disponible."
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def extract_text_from_video(self, video_path: str, progress_callback=None) -> Tuple[bool, str, str]:
        """
        Extrae texto oculto de un video.
        
        Returns:
            Tuple[bool, str, str]: (éxito, mensaje, texto_extraído)
        """
        try:
            # TODO: Implementar lógica completa de extracción
            return False, "⚠️ Funcionalidad en desarrollo. Próximamente disponible.", ""
            
        except Exception as e:
            return False, f"Error: {str(e)}", ""
