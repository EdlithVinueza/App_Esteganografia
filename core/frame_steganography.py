"""
Módulo para ocultar mensajes de texto en los frames de videos usando esteganografía LSB con cifrado.
"""

import cv2
import numpy as np
import os
from typing import Tuple
from pathlib import Path
from cryptography.fernet import Fernet
import hashlib
import base64
import subprocess

class FrameStegano:
    """Clase para manejar la esteganografía de texto en frames de video con cifrado."""
    
    # Marcadores para delimitar el mensaje
    MAGIC_MARKER = "STEG_START"
    MAGIC_END = "STEG_END"
    
    def __init__(self):
        self.temp_dir = Path("temp")
        self.output_dir = Path("output")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def _derive_key(self, password: str) -> bytes:
        """
        Deriva una clave segura a partir de una contraseña.
        Usa PBKDF2 con SHA256.
        """
        salt = b'steg_salt_2024'  # Salt fijo para este proyecto
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        # Fernet requiere una clave base64 de 32 bytes
        return base64.urlsafe_b64encode(key[:32])
    
    def _encrypt_message(self, message: str, password: str) -> bytes:
        """Cifra un mensaje usando Fernet con la contraseña."""
        try:
            key = self._derive_key(password)
            cipher = Fernet(key)
            encrypted = cipher.encrypt(message.encode())
            return encrypted
        except Exception as e:
            raise Exception(f"Error al cifrar mensaje: {str(e)}")
    
    def _decrypt_message(self, encrypted_data: bytes, password: str) -> str:
        """Descifra un mensaje usando Fernet con la contraseña."""
        try:
            key = self._derive_key(password)
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            raise Exception(f"Error al descifrar mensaje: {str(e)}")
    
    def _to_bin(self, data):
        """Convierte datos (string o bytes) a formato binario."""
        if isinstance(data, str):
            return ''.join([format(ord(i), "08b") for i in data])
        elif isinstance(data, bytes):
            return ''.join([format(i, "08b") for i in data])
        elif isinstance(data, int):
            return format(data, "08b")
        else:
            raise TypeError("Tipo no soportado")

    def _bin_to_str(self, binary):
        """Convierte binario a string."""
        data = [binary[i:i+8] for i in range(0, len(binary), 8)]
        return "".join([chr(int(d, 2)) for d in data if d])

    def calculate_text_capacity(self, video_path: str) -> Tuple[int, dict]:
        """Calcula capacidad aproximada considerando el cifrado."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("No se pudo abrir el video")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Usamos 1 bit por píxel (solo canal Azul) en el 80% de los frames
        pixels_per_frame = width * height
        usable_frames = max(1, int(total_frames * 0.8)) 
        
        # Capacidad total en bits
        total_bits = pixels_per_frame * usable_frames
        
        # El mensaje cifrado con Fernet es ~30% más largo que el original
        # Convertir a caracteres (8 bits por char)
        capacity_chars = (total_bits // 8) // 1.5
        
        info = {
            'total_frames': total_frames,
            'width': width,
            'height': height,
            'fps': fps,
            'capacity_chars': int(capacity_chars)
        }
        return int(capacity_chars), info
    
    
    def _extract_audio_from_video(self, video_path: str) -> str:
        """Extrae el audio del video original usando FFmpeg."""
        temp_audio = self.temp_dir / "temp_original_audio.wav"
        try:
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                str(temp_audio)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, shell=True)
            return str(temp_audio)
        except Exception as e:
            return None

    def _merge_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """Une el audio con el video procesado usando FFmpeg."""
        try:
            ext = os.path.splitext(output_path)[1].lower()
            
            # Seleccionar códec de audio sin pérdida según formato
            if ext == '.mp4':
                audio_codec = 'aac'  # AAC para MP4
            elif ext == '.mkv':
                audio_codec = 'flac'  # FLAC para MKV
            else:
                audio_codec = 'pcm_s16le'  # PCM para AVI

            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', audio_codec,
                '-map', '0:v:0',
                '-map', '1:a:0',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return result.returncode == 0
            
        except Exception as e:
            return False

    def hide_text_in_video(self, video_path: str, text: str, password: str, output_path: str, 
                          progress_callback=None) -> Tuple[bool, str]:
        """Oculta texto cifrado en los frames usando LSB."""
        try:
            # 1. Cifrar el mensaje
            encrypted_message = self._encrypt_message(text, password)
            
            # 2. Preparar el mensaje para incrustar
            full_msg = f"{self.MAGIC_MARKER}{len(encrypted_message):016d}"
            full_msg_bin = self._to_bin(full_msg)
            encrypted_bin = self._to_bin(encrypted_message)
            end_marker_bin = self._to_bin(self.MAGIC_END)
            
            bits = full_msg_bin + encrypted_bin + end_marker_bin
            total_bits = len(bits)
            bit_idx = 0
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "No se pudo abrir el video"
                
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Crear archivo temporal sin audio
            temp_video_path = str(self.temp_dir / f"temp_no_audio_{Path(output_path).name}")
            
            # Lista de códecs en orden de preferencia
            codec_options = [
                ('FFV1', '.avi'),
                ('XVID', '.avi'),
                ('MJPG', '.avi'),
            ]
            
            fourcc = None
            video_created = False
            codec_name = None
            
            # Intentar con cada códec hasta que uno funcione
            for codec_name, recommended_ext in codec_options:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*codec_name)
                    output_test = temp_video_path
                    if not temp_video_path.lower().endswith(recommended_ext):
                        output_test = str(Path(temp_video_path).with_suffix(recommended_ext))
                    
                    out = cv2.VideoWriter(output_test, fourcc, fps, (width, height))
                    
                    if out.isOpened():
                        temp_video_path = output_test
                        video_created = True
                        break
                    else:
                        out.release()
                except Exception as e:
                    continue
            
            if not video_created:
                cap.release()
                return False, (
                    "No se pudo crear el video de salida.\n\n"
                    "Posibles soluciones:\n"
                    "1. Usa la extensión .avi en lugar de .mp4\n"
                    "2. Instala ffmpeg en el sistema\n"
                    "3. Verifica que el directorio de salida sea escribible"
                )
            
            frame_count = 0
            finished = False
            
            # Procesar frames
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if not finished and bit_idx < total_bits:
                    blue_channel = frame[:, :, 0].flatten()
                    bits_needed = total_bits - bit_idx
                    bits_to_write = min(len(blue_channel), bits_needed)
                    msg_bits_chunk = bits[bit_idx : bit_idx + bits_to_write]
                    bits_array = np.array([int(b) for b in msg_bits_chunk], dtype=np.uint8)
                    blue_channel[:bits_to_write] = (blue_channel[:bits_to_write] & 254) | bits_array
                    frame[:, :, 0] = blue_channel.reshape((height, width))
                    bit_idx += bits_to_write
                    if bit_idx >= total_bits:
                        finished = True
                
                out.write(frame)
                frame_count += 1
                
                if progress_callback and frame_count % 10 == 0:
                    prog = int((frame_count / total_frames) * 50)
                    progress_callback(prog)
            
            cap.release()
            out.release()
            
            if not finished:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                return False, "El video es demasiado corto para este mensaje."
            
            # 3. Agregar audio usando FFmpeg
            try:
                if progress_callback:
                    progress_callback(60)
                
                # Extraer audio del video original
                temp_audio_path = self._extract_audio_from_video(video_path)
                
                if temp_audio_path and os.path.exists(temp_audio_path):
                    if progress_callback:
                        progress_callback(70)
                    
                    # Ajustar extensión de salida
                    final_output = output_path
                    if not output_path.lower().endswith(('.mp4', '.avi', '.mkv')):
                        final_output = str(Path(output_path).with_suffix('.mp4'))
                    
                    # Combinar video procesado con audio original
                    if self._merge_audio_to_video(temp_video_path, temp_audio_path, final_output):
                        if progress_callback:
                            progress_callback(100)
                        
                        # Limpiar archivos temporales
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        if os.path.exists(temp_audio_path):
                            os.remove(temp_audio_path)
                        
                        size_mb = os.path.getsize(final_output) / (1024 * 1024)
                        
                        return True, (
                            f"✅ Mensaje oculto exitosamente.\n"
                            f"Guardado como: {Path(final_output).name}\n"
                            f"Tamaño: {size_mb:.2f} MB\n"
                            f"Cifrado: Fernet (AES-128)\n"
                            f"Códec: {codec_name}\n"
                            f"Audio: Sí"
                        )
                    else:
                        # Si falla merge, usar video sin audio
                        import shutil
                        shutil.move(temp_video_path, output_path)
                        size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        
                        return True, (
                            f"⚠️ Mensaje oculto, pero sin audio.\n"
                            f"Error al combinar audio con FFmpeg.\n"
                            f"Guardado como: {Path(output_path).name}\n"
                            f"Tamaño: {size_mb:.2f} MB\n"
                            f"Códec: {codec_name}"
                        )
                else:
                    # Video original sin audio
                    import shutil
                    shutil.move(temp_video_path, output_path)
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    
                    return True, (
                        f"✅ Mensaje oculto exitosamente.\n"
                        f"Guardado como: {Path(output_path).name}\n"
                        f"Tamaño: {size_mb:.2f} MB\n"
                        f"Cifrado: Fernet (AES-128)\n"
                        f"Códec: {codec_name}\n"
                        f"Audio: No (video original sin audio)"
                    )
                    
            except Exception as audio_error:
                # Si falla todo el proceso de audio
                if os.path.exists(temp_video_path):
                    import shutil
                    shutil.move(temp_video_path, output_path)
                
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                return True, (
                    f"⚠️ Mensaje oculto, pero sin audio.\n"
                    f"Error: {str(audio_error)}\n"
                    f"Guardado como: {Path(output_path).name}\n"
                    f"Tamaño: {size_mb:.2f} MB\n"
                    f"Códec: {codec_name}"
                )
            
        except Exception as e:
            return False, f"Error: {str(e)}"

    def extract_text_from_video(self, video_path: str, password: str, 
                               progress_callback=None) -> Tuple[bool, str, str]:
        """Extrae y descifra texto oculto LSB."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "No se pudo abrir el video", ""
                
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            extracted_bits = ""
            marker_len_bits = len(self._to_bin(self.MAGIC_MARKER))
            
            # Variables de estado
            found_marker = False
            msg_length = 0
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extraer LSB del canal azul
                blue_channel = frame[:, :, 0].flatten()
                
                # Obtener solo el último bit: pixel & 1
                lsb_bits = (blue_channel & 1)
                
                # Convertir a string de bits '0'/'1'
                bits_str = "".join(lsb_bits.astype(str))
                extracted_bits += bits_str
                
                # Lógica de procesamiento de flujo
                # 1. Buscar marcador inicial
                if not found_marker and len(extracted_bits) >= marker_len_bits + 128:
                    try:
                        # Chequeamos si encontramos el marcador
                        temp_text = self._bin_to_str(extracted_bits[:marker_len_bits + 128])
                        if self.MAGIC_MARKER in temp_text:
                            found_marker = True
                            # Recortar los bits hasta donde termina el marker
                            marker_idx = temp_text.find(self.MAGIC_MARKER)
                            bit_offset = (marker_idx + len(self.MAGIC_MARKER)) * 8
                            extracted_bits = extracted_bits[bit_offset:]
                    except:
                        pass
                            
                # 2. Leer longitud (16 caracteres numéricos = 128 bits)
                if found_marker and msg_length == 0:
                    if len(extracted_bits) >= 128:
                        length_bits = extracted_bits[:128]
                        try:
                            length_str = self._bin_to_str(length_bits)
                            msg_length = int(length_str)
                            extracted_bits = extracted_bits[128:]  # Remover bits de longitud
                        except:
                            cap.release()
                            return False, "Error al leer la longitud del mensaje", ""

                # 3. Leer el mensaje encriptado
                if found_marker and msg_length > 0:
                    needed_bits = msg_length * 8
                    if len(extracted_bits) >= needed_bits:
                        final_msg_bits = extracted_bits[:needed_bits]
                        
                        # Convertir bits a bytes
                        encrypted_data = bytes([int(final_msg_bits[i:i+8], 2) 
                                               for i in range(0, len(final_msg_bits), 8)])
                        
                        try:
                            # Desencriptar con la contraseña
                            secret_text = self._decrypt_message(encrypted_data, password)
                            cap.release()
                            return True, "✅ Mensaje recuperado y desencriptado con éxito", secret_text
                        except Exception as decrypt_error:
                            cap.release()
                            return False, f"❌ Error al desencriptar: Contraseña incorrecta o mensaje corrupto", ""
                
                frame_count += 1
                if progress_callback and frame_count % 10 == 0:
                    prog = int((frame_count / total_frames) * 100)
                    progress_callback(prog)
            
            cap.release()
            return False, "⚠️ No se encontró mensaje oculto o video incompleto", ""
            
        except Exception as e:
            return False, f"Error de extracción: {str(e)}", ""