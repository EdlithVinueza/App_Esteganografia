"""
Módulo para ocultar archivos completos dentro de videos usando inyección EOF (End Of File).
Permite incrustar cualquier tipo de archivo en el contenedor del video sin modificar los frames es decir sin recodificar.
"""

import cv2
import numpy as np
import os
import json
import shutil
from typing import Tuple, Optional
from pathlib import Path

class FileStegano:
    """Clase para manejar la esteganografía de archivos en videos mediante inyección EOF."""
    
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
    
    MAGIC_MARKER = b'STEG_EOF_START'  # Marcador para identificar inicio de archivo oculto
    
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
        Calcula la capacidad de almacenamiento del video.
        En el método EOF, la capacidad es teóricamente ilimitada, 
        limitada solo por el sistema de archivos, pero devolvemos datos para la UI.
        
        Returns:
            Tuple[int, dict]: (capacidad_en_bytes, info_video)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            # Si no se puede abrir con OpenCV, intentamos devolver datos básicos
            # O lanzamos error si es crítico. Asumiremos video válido para operaciones de archivo.
             raise ValueError("No se pudo abrir el video para leer metadata")
        
        # Obtener información del video (solo para mostrar en UI)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # En EOF, la capacidad no depende de los pixels. 
        # Ponemos un número muy grande arbitrario o el espacio libre en disco.
        # Por simplicidad, usamos un valor "virtualmente infinito" para la UI (e.j. 100 GB).
        usable_capacity = 100 * 1024 * 1024 * 1024  # 100 GB
        
        # Algunos reproductores pueden tener problemas con archivos > 4GB si son MP4 antiguos,
        # pero para propósitos de steganografía moderna, es razonable.
        
        info = {
            'total_frames': total_frames,
            'usable_frames': total_frames, # Irrelevante para EOF
            'fps': fps,
            'width': width,
            'height': height,
            'duration_seconds': total_frames / fps if fps > 0 else 0,
            'pixels_per_frame': width * height,
            'bytes_per_frame': 0, # Irrelevante
            'total_capacity_bytes': usable_capacity,
            'usable_capacity_bytes': usable_capacity,
            'total_capacity_mb': usable_capacity / (1024 * 1024),
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
        
        # Calcular porcentaje de uso (simbólico, ya que capacity es ficticio)
        usage_percent = (file_size / capacity * 100) if capacity > 0 else 0.1
        
        info = {
            **video_info,
            'file_size_bytes': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'usage_percent': usage_percent,
            'remaining_bytes': capacity - file_size,
            'remaining_mb': (capacity - file_size) / (1024 * 1024)
        }
        
        msg = (f"✅ El archivo se puede inyectar (EOF).\n\n"
               f"📁 Archivo: {file_size / (1024*1024):.2f} MB\n"
               f"ℹ️ Método: Inyección en contenedor (No modifica frames)\n"
               f"El video resultante será reproducible, pero el archivo oculto\n"
               f"se perderá si el video es convertido o re-comprimido.")
        
        return True, msg, info
    
    def hide_file_in_video(self, video_path: str, file_path: str, output_path: str, 
                          progress_callback=None) -> Tuple[bool, str]:
        """
        Oculta un archivo completo dentro de un video usando inyección EOF.
        
        Args:
            video_path: Ruta del video original
            file_path: Ruta del archivo a ocultar
            output_path: Ruta del video de salida
            progress_callback: Función callback para reportar progreso (0-100)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            if progress_callback:
                progress_callback(10)
            
            # Leer el archivo a ocultar
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            if progress_callback:
                progress_callback(30)
                
            # Crear metadata
            metadata = {
                'filename': os.path.basename(file_path),
                'filesize': len(file_data),
                'extension': Path(file_path).suffix,
                'method': 'EOF'
            }
            metadata_json = json.dumps(metadata).encode('utf-8')
            
            # Convertir longitudes a bytes (4 bytes big endian)
            metadata_len_bytes = len(metadata_json).to_bytes(4, byteorder='big')
            
            # Construir el payload a inyectar al final
            # Payload = MAGIC_MARKER + metadata_len(4) + metadata + file_data
            # Al extraer, buscaremos MAGIC_MARKER de atrás hacia adelante o
            # simplemente concatenamos en un orden conocido.
            
            # Diseño simple para lectura secuencial inversa o búsqueda:
            # VideoOriginal + [MAGIC_MARKER + MetadataLength + Metadata + SecretFile]
            
            # Mejor diseño para robustez: 
            # VideoOriginal + SecretFile + Metadata + MetadataLength + MAGIC_MARKER
            # Así podemos leer los últimos bytes para saber si hay algo oculto.
            
            payload = (
                file_data +
                metadata_json +
                metadata_len_bytes + 
                self.MAGIC_MARKER 
            )
            
            if progress_callback:
                progress_callback(50)
            
            # Copiar el video original al destino primero (o leer y escribir)
            shutil.copy2(video_path, output_path)
            
            if progress_callback:
                progress_callback(70)
                
            # Añadir el payload al final del archivo copiado
            with open(output_path, 'ab') as f_out:
                f_out.write(payload)
                
            if progress_callback:
                progress_callback(100)
            
            success_msg = (
                f"✅ ¡Archivo ocultado exitosamente (EOF)!\n\n"
                f"📁 Archivo: {metadata['filename']}\n"
                f"📦 Tamaño: {len(file_data) / 1024:.2f} KB\n"
                f"💾 Video guardado en: {output_path}\n\n"
                f"⚠️ ADVERTENCIA: No conviertas ni comprimas este video, o perderás el archivo."
            )
            
            return True, success_msg
            
        except Exception as e:
            return False, f"Error al ocultar archivo: {str(e)}"
    
    def extract_file_from_video(self, video_path: str, output_dir: str, 
                               progress_callback=None) -> Tuple[bool, str, Optional[str]]:
        """
        Extrae un archivo oculto del final de un video (EOF).
        
        Args:
            video_path: Ruta del video con archivo oculto
            output_dir: Directorio donde guardar el archivo extraído
            progress_callback: Función callback para reportar progreso
        
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, ruta_archivo_extraído)
        """
        try:
            if progress_callback:
                progress_callback(10)
                
            file_size = os.path.getsize(video_path)
            
            with open(video_path, 'rb') as f:
                # 1. Buscar el MAGIC_MARKER al final del archivo
                marker_len = len(self.MAGIC_MARKER)
                f.seek(-marker_len, 2) # Ir al final menos la longitud del marcador
                read_marker = f.read(marker_len)
                
                if read_marker != self.MAGIC_MARKER:
                     return False, "No se encontró el marcador de archivo oculto (EOF) en este video.", None
                
                if progress_callback:
                    progress_callback(30)
                
                # 2. Leer la longitud de la metadata
                # La estructura es: ... + Metadata + MetadataLength(4) + MAGIC_MARKER
                # Entonces debemos retroceder: MarkerLen + 4 bytes
                
                seek_offset = marker_len + 4
                if file_size < seek_offset:
                    return False, "Archivo corrupto o demasiado pequeño.", None
                    
                f.seek(-seek_offset, 2)
                metadata_len_bytes = f.read(4)
                metadata_len = int.from_bytes(metadata_len_bytes, byteorder='big')
                
                if progress_callback:
                    progress_callback(50)
                
                # 3. Leer la metadata
                # Retroceder: MarkerLen + 4 + MetadataLen
                seek_offset += metadata_len
                if file_size < seek_offset:
                    return False, "Metadata corrupta.", None
                
                f.seek(-seek_offset, 2)
                metadata_bytes = f.read(metadata_len)
                try:
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                except json.JSONDecodeError:
                    return False, "Error al decodificar la metadata.", None
                
                filename = metadata.get('filename', 'extracted_file')
                hidden_file_size = metadata.get('filesize', 0)
                
                if hidden_file_size <= 0:
                     return False, "Tamaño de archivo inválido en metadata.", None

                if progress_callback:
                    progress_callback(70)

                # 4. Leer el archivo oculto
                # Retroceder: MarkerLen + 4 + MetadataLen + FileSize
                seek_offset += hidden_file_size
                if file_size < seek_offset:
                     return False, "El archivo parece estar truncado.", None
                
                f.seek(-seek_offset, 2)
                file_data = f.read(hidden_file_size)
                
                # Guardar el archivo extraído
                output_path = os.path.join(output_dir, filename)
                
                # Si el archivo ya existe, agregar número para no sobrescribir
                base_name = Path(filename).stem
                extension = Path(filename).suffix
                counter = 1
                while os.path.exists(output_path):
                    output_path = os.path.join(output_dir, f"{base_name}_{counter}{extension}")
                    counter += 1
                
                if progress_callback:
                    progress_callback(90)
                    
                with open(output_path, 'wb') as f_out:
                    f_out.write(file_data)
                
                if progress_callback:
                    progress_callback(100)
                
                success_msg = (
                    f"✅ ¡Archivo extraído exitosamente!\n\n"
                    f"📁 Archivo: {filename}\n"
                    f"📦 Tamaño: {hidden_file_size / 1024:.2f} KB\n"
                    f"💾 Guardado en: {output_path}"
                )
                
                return True, success_msg, output_path

        except Exception as e:
            return False, f"Error al extraer archivo: {str(e)}", None

    def get_supported_formats_text(self) -> str:
        """Retorna un texto formateado con los formatos soportados."""
        text = "📋 Formatos de archivo soportados:\n\n"
        for category, extensions in self.SUPPORTED_FORMATS.items():
            text += f"• {category.upper()}: {', '.join(extensions)}\n"
        text += "\n💡 En modo EOF, prácticamente cualquier archivo binario es soportado."
        return text
