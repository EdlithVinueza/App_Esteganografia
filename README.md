# 🎥 Video Steganography App

Aplicación de esteganografía de video con interfaz gráfica moderna que permite ocultar información en videos mediante tres métodos diferentes.

## 🚀 Características y Estado del Proyecto

- **📦 Ocultar por Archivo**: **100% FUNCIONAL**. Permite incrustar archivos completos (PDF, DOCX, ZIP, etc.) dentro de un video.
- **🖼️ Ocultar por Frame**: Interfaz lista, lógica en desarrollo (LSB en frames).
- **🎵 Ocultar por Audio**: Interfaz lista, lógica en desarrollo (esteganografía en pista de audio).

---

## 📦 Instalación y Ejecución Rápida (Windows)

Para facilitar el uso, se ha creado un script único que prepara el entorno y ejecuta la aplicación:

1. **Doble clic en `start_app.bat`**
2. El script creará el entorno virtual (`venv`), instalará las librerías necesarias y abrirá la aplicación automáticamente.

### Requisitos Previos
- **Python 3.10+** instalado y en el PATH.
- **FFmpeg**: La aplicación intentará gestionarlo automáticamente, pero se recomienda tenerlo instalado en el sistema para mejor rendimiento.

---

## 🎮 Guía de Uso (Ocultar por Archivo)

### Paso 1: Ocultar Información
1. Abre la aplicación usando `start_app.bat`.
2. Ve a la pestaña **"📦 Ocultar por Archivo"**.
3. **Seleccionar Video**: Elige el video donde quieres ocultar el archivo.
4. **Seleccionar Archivo**: Elige el archivo (documento, imagen, zip) que quieres ocultar.
5. **Analizar Capacidad**: Verifica si el archivo cabe en el video.
6. **Ocultar Archivo**: Elige el nombre del archivo de salida y procesa.

### Paso 2: Extraer Información
1. En la misma pestaña, usa la columna derecha **"🔓 Extraer Archivo"**.
2. **Seleccionar Video**: Elige el video que contiene la información oculta.
3. **Extraer**: Elige la carpeta de destino y recupera tu archivo original.

---

## 📁 Estructura del Proyecto

```
App_Esteganografía/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── README.md              # Documentación consolidada
├── core/                  # Lógica de esteganografía (Frame, Audio, File)
├── ui/                    # Componentes de la interfaz gráfica
├── assets/                # Iconos y recursos visuales
├── temp/                  # Archivos temporales de procesamiento
└── output/                # Carpeta por defecto para resultados
```

---

## 📋 Formatos Soportados

- **Para ocultar**: PDF, DOCX, TXT, JPG, PNG, GIF, MP3, ZIP, RAR, PY, JS, etc.
- **Videos contenedores**: MP4, AVI, MKV (Se recomienda usar formatos sin pérdida para mayor seguridad).

### ⚠️ Importante
No subas los videos procesados a plataformas que recompriman el contenido (YouTube, WhatsApp, Redes Sociales), ya que la compresión destruirá los datos ocultos. Comparte el archivo directamente por USB, email o servicios de nube sin pérdida.

---

## 🆘 Solución de Problemas

### "El archivo es demasiado grande"
- Usa un video de mayor duración o resolución.
- Comprime el archivo en un ZIP antes de ocultarlo.

### "Error: ModuleNotFoundError"
- Asegúrate de estar ejecutando la aplicación a través de `start_app.bat`, el cual activa el entorno virtual correctamente.

### Problemas con FFmpeg
- Si recibes errores relacionados con el procesamiento de video, instala FFmpeg manualmente desde [ffmpeg.org](https://ffmpeg.org/download.html) y asegúrate de que esté en las variables de entorno (PATH).

---

## 🔧 Detalles Técnicos
- **Desarrollado con**: Python 3, CustomTkinter (UI), OpenCV y NumPy (Procesamiento), FFmpeg.
- **Seguridad**: Los archivos se ocultan mediante técnicas de manipulación de bits, con validación de capacidad previa.

---
**¡Disfruta ocultando información de forma segura!** 🎉🔒
