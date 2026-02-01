"""
Módulo para ocultar mensajes en la pista de audio de videos usando esteganografía LSB.
"""

import wave
import os
import subprocess
import numpy as np
from scipy.fftpack import dct, idct
from typing import Tuple, Optional
from pathlib import Path
import shutil

class AudioStegano:
    """
    Clase HÍBRIDA: Maneja tanto AUDIO (.wav) como VIDEO (.mp4, .avi)
    usando FFmpeg del sistema y Esteganografía por Frecuencia (DCT).
    """
    
    MAGIC_MARKER = b'STEG_START'
    MAGIC_END = b'STEG_END'
    
    # --- CONFIGURACIÓN ROBUSTA (Resiste compresión de video) ---
    BLOCK_SIZE = 128  
    P1 = 20          
    P2 = 21          
    MARGIN = 50.0     
    
    def __init__(self):
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    # --- HERRAMIENTAS DE FFMPEG ---
    
    def _extract_wav_from_video(self, video_path: str) -> Optional[str]:
        """Extrae el audio del video a un WAV temporal."""
        temp_audio = self.temp_dir / "temp_extract.wav"
        
        # Verificar si ffmpeg está accesible
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: FFmpeg no está instalado o no se encuentra en el PATH.")
            return None

        try:
            # Al tener FFmpeg en el PATH, llamamos directamente a "ffmpeg"
            cmd = [
                'ffmpeg', '-y', '-i', video_path, 
                '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                str(temp_audio)
            ]
            # shell=True ayuda en Windows a encontrar el comando en el PATH
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, shell=True)
            return str(temp_audio)
        except subprocess.CalledProcessError as e:
            print(f"Error FFmpeg Extract (Código {e.returncode}): Verifique que el video no esté corrupto.")
            return None
        except Exception as e:
            print(f"Error inesperado al extraer audio: {e}")
            return None

    def _merge_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Une el audio modificado con el video original.
        CORRECCIÓN: Usa códecs SIN PÉRDIDA (Lossless) para que el mensaje no se borre.
        """
        # Verificar si ffmpeg está accesible
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: FFmpeg no está instalado para la unión de video.")
            return False

        try:
            # Determinamos el códec de audio según el contenedor de video
            ext = os.path.splitext(output_path)[1].lower()
            
            if ext == '.mp4':
                # MP4 no acepta WAV crudo fácilmente. Usamos 'alac' (Apple Lossless)
                # o 'flac'. Ambos conservan los datos exactos.
                audio_codec = 'alac' 
            elif ext == '.mkv':
                # MKV acepta FLAC o WAV (pcm_s16le) perfectamente.
                audio_codec = 'flac'
            else:
                # Para AVI y otros, usamos PCM (WAV crudo)
                audio_codec = 'pcm_s16le'

            cmd = [
                'ffmpeg', '-y', 
                '-i', video_path, 
                '-i', audio_path,
                '-c:v', 'copy',       # Copiamos el video tal cual (sin perder calidad)
                '-c:a', audio_codec,  # <--- AQUÍ ESTÁ EL TRUCO (Sin compresión destructiva)
                '-map', '0:v:0',      # Tomamos el video del archivo 0
                '-map', '1:a:0',      # Tomamos el audio del archivo 1 (nuestro audio secreto)
                output_path
            ]
            
            # Ejecutamos el comando
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                print("❌ ERROR FFMPEG MERGE:")
                print(result.stderr)
                return False
                
            return True
            
        except Exception as e:
            print(f"Error Python Merge: {e}")
            return False

    def _is_video(self, path: str) -> bool:
        ext = os.path.splitext(path)[1].lower()
        return ext in ['.mp4', '.avi', '.mkv', '.mov']

    # --- LÓGICA CORE ---

    def hide_text_in_audio(self, input_path: str, text: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
        
        is_video = self._is_video(input_path)
        temp_wav_in = None
        temp_wav_out = self.temp_dir / "temp_stego.wav"

        # 1. Preparar Audio (Extraer si es video)
        if is_video:
            temp_wav_in = self._extract_wav_from_video(input_path)
            if not temp_wav_in: return False, "Error: No se pudo extraer audio con FFmpeg."
            working_file = temp_wav_in
        else:
            working_file = input_path 

        try:
            # 2. PROCESO DE ESTEGANOGRAFÍA (DCT)
            with wave.open(working_file, 'r') as wav:
                params = wav.getparams()
                n_channels = wav.getnchannels()
                raw = wav.readframes(wav.getnframes())
                signal = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

            if n_channels > 1:
                signal = signal.reshape(-1, n_channels)
                process_channel = signal[:, 0].copy()
            else:
                process_channel = signal.copy()

            payload = self.MAGIC_MARKER + text.encode('utf-8') + self.MAGIC_END
            bits = ''.join(format(b, '08b') for b in payload)
            
            # Chequeo de capacidad básico
            if len(bits) > (len(process_channel) // self.BLOCK_SIZE):
                return False, "Mensaje demasiado largo para este audio."

            # Inserción
            for i, bit in enumerate(bits):
                start = i * self.BLOCK_SIZE
                end = start + self.BLOCK_SIZE
                block = process_channel[start:end]
                dct_block = dct(block, norm='ortho')
                
                v1, v2 = dct_block[self.P1], dct_block[self.P2]
                
                if bit == '0':
                    if v1 >= v2 or (v2 - v1) < self.MARGIN:
                        center = (v1 + v2) / 2
                        dct_block[self.P1] = center - self.MARGIN
                        dct_block[self.P2] = center + self.MARGIN
                elif bit == '1':
                    if v1 <= v2 or (v1 - v2) < self.MARGIN:
                        center = (v1 + v2) / 2
                        dct_block[self.P1] = center + self.MARGIN
                        dct_block[self.P2] = center - self.MARGIN

                process_channel[start:end] = idct(dct_block, norm='ortho')
                if progress_callback and i % 1000 == 0: progress_callback((i/len(bits))*100)

            # Guardar WAV procesado
            process_channel = np.clip(process_channel, -32768, 32767)
            if n_channels > 1:
                signal[:, 0] = process_channel
                output_data = signal.astype(np.int16)
            else:
                output_data = process_channel.astype(np.int16)

            with wave.open(str(temp_wav_out), 'w') as wav_out:
                wav_out.setparams(params)
                wav_out.writeframes(output_data.tobytes())

            # 3. Finalización (Unir o Copiar)
            success = False
            msg = ""
            
            if is_video:
                if self._merge_audio_to_video(input_path, str(temp_wav_out), output_path):
                    success = True
                    msg = "Video generado correctamente."
                else:
                    msg = "Error al unir el video con FFmpeg."
            else:
                shutil.copy(str(temp_wav_out), output_path)
                success = True
                msg = "Audio WAV generado correctamente."

            # Limpieza
            if temp_wav_in and os.path.exists(temp_wav_in): os.remove(temp_wav_in)
            if os.path.exists(temp_wav_out): os.remove(temp_wav_out)
            
            return success, msg

        except Exception as e:
            return False, f"Error técnico: {e}"

    def extract_text_from_audio(self, input_path: str, progress_callback=None) -> Tuple[bool, str, str]:
        temp_wav = None
        working_file = input_path
        
        # Si es video, extraemos audio primero
        if self._is_video(input_path):
            temp_wav = self._extract_wav_from_video(input_path)
            if not temp_wav: return False, "Error extrayendo audio del video", ""
            working_file = temp_wav

        try:
            if not os.path.exists(working_file):
                return False, "Archivo de audio no accesible", ""

            with wave.open(working_file, 'r') as wav:
                raw = wav.readframes(wav.getnframes())
                signal = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
            
            if wav.getnchannels() > 1:
                signal = signal.reshape(-1, wav.getnchannels())
                process_channel = signal[:, 0]
            else:
                process_channel = signal

            bits_extracted = []
            num_blocks = len(process_channel) // self.BLOCK_SIZE
            
            for i in range(num_blocks):
                start = i * self.BLOCK_SIZE
                end = start + self.BLOCK_SIZE
                # Protección contra bloques incompletos al final
                if len(process_channel[start:end]) < self.BLOCK_SIZE: break
                
                dct_block = dct(process_channel[start:end], norm='ortho')
                bits_extracted.append('1' if dct_block[self.P1] > dct_block[self.P2] else '0')

            bits_str = "".join(bits_extracted)
            byte_list = []
            for i in range(0, len(bits_str), 8):
                chunk = bits_str[i:i+8]
                if len(chunk)==8: byte_list.append(int(chunk, 2))
            
            full_data = bytes(byte_list)
            
            start_idx = full_data.find(self.MAGIC_MARKER)
            if start_idx != -1:
                end_idx = full_data.find(self.MAGIC_END, start_idx)
                if end_idx != -1:
                    secret = full_data[start_idx+len(self.MAGIC_MARKER):end_idx].decode('utf-8')
                    if temp_wav and os.path.exists(temp_wav): os.remove(temp_wav)
                    return True, "Mensaje encontrado.", secret
            
            if temp_wav and os.path.exists(temp_wav): os.remove(temp_wav)
            return False, "No se encontró mensaje oculto.", ""
            
        except Exception as e:
            if temp_wav and os.path.exists(temp_wav): os.remove(temp_wav)
            return False, f"Error lectura: {e}", ""