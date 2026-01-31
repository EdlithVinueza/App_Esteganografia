"""
Módulo para ocultar archivos completos dentro de videos usando esteganografía LSB.
Permite incrustar cualquier tipo de archivo en los frames del video.
"""

import cv2
import numpy as np
import os
import json
from typing import Tuple, Optional
from pathlib import Path


class FileStegano:
    """Clase para manejar la esteganografía de archivos en videos."""
    
    # Formatos de archivo soportados (puedes agregar más)
    SUPPORTED_FORMATS = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'audio': ['.mp3', '.wav', '.ogg', '.flac', '.m4a'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
        'compressed': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c'],
        'other': ['.json', '.xml', '.csv', '.sql', '.db']
    }
    
    MAGIC_MARKER = b'STEG_FILE_START'  # Marcador para identificar inicio de archivo
    MAGIC_END = b'STEG_FILE_END'      # Marcador para identificar fin de archivo
    
    def __init__(self):
        self.temp_dir = Path("temp")
        self.output_dir = Path("output")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_file_category(self, file_path: str) -> str:
        """Obtiene la categoría del archivo basado en su extensión."""
        ext = Path(file_path).suffix.lower()
        for category, extensions in self.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return category
        return 'unknown'
    
    def is_file_supported(self, file_path: str) -> Tuple[bool, str]:
        """
        Verifica si el archivo es soportado.
        
        Returns:
            Tuple[bool, str]: (es_soportado, mensaje)
        """
        if not os.path.exists(file_path):
            return False, "El archivo no existe"
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "El archivo está vacío"
        
        ext = Path(file_path).suffix.lower()
        category = self.get_file_category(file_path)
        
        if category == 'unknown':
            return True, f"Archivo de tipo desconocido ({ext}), pero se puede intentar ocultar"
        
        return True, f"Archivo válido: {category.upper()} ({ext})"
    
    def calculate_video_capacity(self, video_path: str) -> Tuple[int, dict]:
        """
        Calcula la capacidad de almacenamiento del video en bytes.
        
        Returns:
            Tuple[int, dict]: (capacidad_en_bytes, info_video)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("No se pudo abrir el video")
        
        # Obtener información del video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Leer un frame para obtener información
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError("No se pudo leer el video")
        
        # Calcular capacidad
        # Usamos 1 bit por canal de color (RGB) = 3 bits por pixel
        # Dividimos entre 8 para obtener bytes
        pixels_per_frame = width * height
        bits_per_frame = pixels_per_frame * 3  # 3 canales (BGR)
        bytes_per_frame = bits_per_frame // 8
        
        # Reservamos algunos frames para metadata (10 frames)
        usable_frames = max(0, total_frames - 10)
        total_capacity = bytes_per_frame * usable_frames
        
        # Restamos el espacio para marcadores y metadata
        overhead = len(self.MAGIC_MARKER) + len(self.MAGIC_END) + 1024  # 1KB para metadata
        usable_capacity = max(0, total_capacity - overhead)
        
        info = {
            'total_frames': total_frames,
            'usable_frames': usable_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'duration_seconds': total_frames / fps if fps > 0 else 0,
            'pixels_per_frame': pixels_per_frame,
            'bytes_per_frame': bytes_per_frame,
            'total_capacity_bytes': total_capacity,
            'usable_capacity_bytes': usable_capacity,
            'total_capacity_mb': total_capacity / (1024 * 1024),
            'usable_capacity_mb': usable_capacity / (1024 * 1024)
        }
        
        return usable_capacity, info
    
    def can_hide_file(self, video_path: str, file_path: str) -> Tuple[bool, str, dict]:
        """
        Verifica si el archivo cabe en el video.
        
        Returns:
            Tuple[bool, str, dict]: (puede_ocultar, mensaje, info)
        """
        # Verificar archivo
        is_supported, support_msg = self.is_file_supported(file_path)
        if not is_supported:
            return False, support_msg, {}
        
        # Obtener tamaños
        file_size = os.path.getsize(file_path)
        capacity, video_info = self.calculate_video_capacity(video_path)
        
        # Calcular porcentaje de uso
        usage_percent = (file_size / capacity * 100) if capacity > 0 else 100
        
        info = {
            **video_info,
            'file_size_bytes': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'usage_percent': usage_percent,
            'remaining_bytes': capacity - file_size,
            'remaining_mb': (capacity - file_size) / (1024 * 1024)
        }
        
        if file_size > capacity:
            msg = (f"❌ El archivo es demasiado grande!\n\n"
                   f"Tamaño del archivo: {file_size / (1024*1024):.2f} MB\n"
                   f"Capacidad del video: {capacity / (1024*1024):.2f} MB\n"
                   f"Exceso: {(file_size - capacity) / (1024*1024):.2f} MB\n\n"
                   f"💡 Sugerencia: Usa un video más largo o comprime el archivo.")
            return False, msg, info
        
        msg = (f"✅ El archivo cabe perfectamente!\n\n"
               f"📁 Archivo: {file_size / (1024*1024):.2f} MB\n"
               f"🎥 Capacidad: {capacity / (1024*1024):.2f} MB\n"
               f"📊 Uso: {usage_percent:.1f}%\n"
               f"💾 Espacio restante: {(capacity - file_size) / (1024*1024):.2f} MB")
        
        return True, msg, info
    
    def _int_to_bytes(self, value: int, length: int = 4) -> bytes:
        """Convierte un entero a bytes."""
        return value.to_bytes(length, byteorder='big')
    
    def _bytes_to_int(self, data: bytes) -> int:
        """Convierte bytes a entero."""
        return int.from_bytes(data, byteorder='big')
    
    def _embed_bits_in_frame(self, frame: np.ndarray, data_bits: str, start_bit: int) -> Tuple[np.ndarray, int]:
        """
        Incrusta bits en un frame usando LSB.
        
        Returns:
            Tuple[np.ndarray, int]: (frame_modificado, bits_escritos)
        """
        height, width, channels = frame.shape
        max_bits = height * width * channels
        
        bits_to_write = min(len(data_bits) - start_bit, max_bits)
        if bits_to_write <= 0:
            return frame, 0
        
        # Aplanar el frame
        flat_frame = frame.flatten()
        
        # Incrustar bits
        for i in range(bits_to_write):
            bit = int(data_bits[start_bit + i])
            # Modificar el LSB
            flat_frame[i] = (flat_frame[i] & 0xFE) | bit
        
        # Restaurar forma original
        modified_frame = flat_frame.reshape(frame.shape)
        
        return modified_frame, bits_to_write
    
    def _extract_bits_from_frame(self, frame: np.ndarray, num_bits: int) -> str:
        """Extrae bits de un frame."""
        flat_frame = frame.flatten()
        bits = ''
        
        for i in range(min(num_bits, len(flat_frame))):
            bits += str(flat_frame[i] & 1)
        
        return bits
    
    def hide_file_in_video(self, video_path: str, file_path: str, output_path: str, 
                          progress_callback=None) -> Tuple[bool, str]:
        """
        Oculta un archivo completo dentro de un video.
        
        Args:
            video_path: Ruta del video original
            file_path: Ruta del archivo a ocultar
            output_path: Ruta del video de salida
            progress_callback: Función callback para reportar progreso (0-100)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar si el archivo cabe
            can_hide, msg, info = self.can_hide_file(video_path, file_path)
            if not can_hide:
                return False, msg
            
            # Leer el archivo a ocultar
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Crear metadata
            metadata = {
                'filename': os.path.basename(file_path),
                'filesize': len(file_data),
                'extension': Path(file_path).suffix
            }
            metadata_json = json.dumps(metadata).encode('utf-8')
            
            # Construir el payload completo
            # Formato: MAGIC_MARKER + tamaño_metadata(4 bytes) + metadata + tamaño_archivo(4 bytes) + archivo + MAGIC_END
            payload = (
                self.MAGIC_MARKER +
                self._int_to_bytes(len(metadata_json)) +
                metadata_json +
                self._int_to_bytes(len(file_data)) +
                file_data +
                self.MAGIC_END
            )
            
            # Convertir payload a bits
            payload_bits = ''.join(format(byte, '08b') for byte in payload)
            total_bits = len(payload_bits)
            
            # Abrir video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "No se pudo abrir el video"
            
            # Obtener propiedades del video
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Crear video de salida
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            bits_written = 0
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Si aún hay bits por escribir, incrustarlos
                if bits_written < total_bits:
                    modified_frame, written = self._embed_bits_in_frame(
                        frame, payload_bits, bits_written
                    )
                    bits_written += written
                    out.write(modified_frame)
                else:
                    # Escribir frames sin modificar
                    out.write(frame)
                
                frame_count += 1
                
                # Reportar progreso
                if progress_callback:
                    progress = int((frame_count / total_frames) * 100)
                    progress_callback(progress)
            
            cap.release()
            out.release()
            
            if bits_written < total_bits:
                return False, f"No se pudieron escribir todos los bits. Escritos: {bits_written}/{total_bits}"
            
            success_msg = (
                f"✅ ¡Archivo ocultado exitosamente!\n\n"
                f"📁 Archivo: {metadata['filename']}\n"
                f"📦 Tamaño: {len(file_data) / 1024:.2f} KB\n"
                f"🎥 Frames procesados: {frame_count}\n"
                f"💾 Video guardado en: {output_path}"
            )
            
            return True, success_msg
            
        except Exception as e:
            return False, f"Error al ocultar archivo: {str(e)}"
    
    def extract_file_from_video(self, video_path: str, output_dir: str, 
                               progress_callback=None) -> Tuple[bool, str, Optional[str]]:
        """
        Extrae un archivo oculto de un video.
        
        Args:
            video_path: Ruta del video con archivo oculto
            output_dir: Directorio donde guardar el archivo extraído
            progress_callback: Función callback para reportar progreso
        
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, ruta_archivo_extraído)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "No se pudo abrir el video", None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Extraer bits de los frames
            all_bits = ''
            frame_count = 0
            
            # Primero, necesitamos encontrar el marcador de inicio
            marker_bits = ''.join(format(byte, '08b') for byte in self.MAGIC_MARKER)
            marker_length = len(marker_bits)
            
            # Leer suficientes frames para encontrar el marcador y metadata
            while frame_count < min(50, total_frames):  # Leer máximo 50 frames iniciales
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_bits = self._extract_bits_from_frame(frame, frame.size)
                all_bits += frame_bits
                frame_count += 1
                
                if progress_callback:
                    progress_callback(int((frame_count / total_frames) * 50))
            
            # Buscar marcador de inicio
            marker_pos = all_bits.find(marker_bits)
            if marker_pos == -1:
                cap.release()
                return False, "No se encontró archivo oculto en el video", None
            
            # Extraer tamaño de metadata (4 bytes = 32 bits)
            pos = marker_pos + marker_length
            metadata_size_bits = all_bits[pos:pos + 32]
            if len(metadata_size_bits) < 32:
                # Necesitamos más frames
                while frame_count < total_frames and len(all_bits) < pos + 32:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_bits = self._extract_bits_from_frame(frame, frame.size)
                    all_bits += frame_bits
                    frame_count += 1
                
                metadata_size_bits = all_bits[pos:pos + 32]
            
            metadata_size = self._bytes_to_int(
                int(metadata_size_bits, 2).to_bytes(4, byteorder='big')
            )
            
            # Extraer metadata
            pos += 32
            metadata_bits = all_bits[pos:pos + (metadata_size * 8)]
            
            # Leer más frames si es necesario
            while len(metadata_bits) < metadata_size * 8 and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_bits = self._extract_bits_from_frame(frame, frame.size)
                all_bits += frame_bits
                frame_count += 1
                metadata_bits = all_bits[pos:pos + (metadata_size * 8)]
            
            metadata_bytes = int(metadata_bits, 2).to_bytes(metadata_size, byteorder='big')
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            # Extraer tamaño del archivo
            pos += metadata_size * 8
            file_size_bits = all_bits[pos:pos + 32]
            
            while len(file_size_bits) < 32 and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_bits = self._extract_bits_from_frame(frame, frame.size)
                all_bits += frame_bits
                frame_count += 1
                file_size_bits = all_bits[pos:pos + 32]
            
            file_size = self._bytes_to_int(
                int(file_size_bits, 2).to_bytes(4, byteorder='big')
            )
            
            # Extraer archivo
            pos += 32
            file_bits_needed = file_size * 8
            
            # Leer frames hasta tener todos los bits del archivo
            while len(all_bits) < pos + file_bits_needed and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_bits = self._extract_bits_from_frame(frame, frame.size)
                all_bits += frame_bits
                frame_count += 1
                
                if progress_callback:
                    progress = 50 + int((frame_count / total_frames) * 50)
                    progress_callback(progress)
            
            cap.release()
            
            file_bits = all_bits[pos:pos + file_bits_needed]
            
            if len(file_bits) < file_bits_needed:
                return False, "No se pudieron extraer todos los datos del archivo", None
            
            # Convertir bits a bytes
            file_bytes = bytearray()
            for i in range(0, len(file_bits), 8):
                byte_bits = file_bits[i:i+8]
                if len(byte_bits) == 8:
                    file_bytes.append(int(byte_bits, 2))
            
            # Guardar archivo
            output_path = os.path.join(output_dir, metadata['filename'])
            
            # Si el archivo ya existe, agregar número
            base_name = Path(metadata['filename']).stem
            extension = Path(metadata['filename']).suffix
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{base_name}_{counter}{extension}")
                counter += 1
            
            with open(output_path, 'wb') as f:
                f.write(file_bytes)
            
            success_msg = (
                f"✅ ¡Archivo extraído exitosamente!\n\n"
                f"📁 Archivo: {metadata['filename']}\n"
                f"📦 Tamaño: {file_size / 1024:.2f} KB\n"
                f"💾 Guardado en: {output_path}"
            )
            
            return True, success_msg, output_path
            
        except Exception as e:
            if 'cap' in locals():
                cap.release()
            return False, f"Error al extraer archivo: {str(e)}", None
    
    def get_supported_formats_text(self) -> str:
        """Retorna un texto formateado con los formatos soportados."""
        text = "📋 Formatos de archivo soportados:\n\n"
        for category, extensions in self.SUPPORTED_FORMATS.items():
            text += f"• {category.upper()}: {', '.join(extensions)}\n"
        text += "\n💡 También puedes intentar con otros formatos no listados."
        return text
