# 🎥 Video Steganography App

Aplicación de esteganografía de video con interfaz gráfica moderna que permite ocultar información en videos mediante tres métodos diferentes.

## 🚀 Características

- **Ocultar por Frame**: Oculta mensajes de texto en los frames del video usando LSB
- **Ocultar por Audio**: Oculta mensajes en la pista de audio del video
- **Ocultar por Archivo**: Incrusta archivos completos dentro del video

## 📦 Instalación

### 1. Crear entorno virtual
```bash
python -m venv venv
```

### 2. Activar entorno virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar FFmpeg (requerido)
**Windows:**
- Descargar desde: https://ffmpeg.org/download.html
- Agregar al PATH del sistema

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

## 🎮 Uso

```bash
python main.py
```

## 📁 Estructura del Proyecto

```
Esteganografía_Python/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Documentación
├── core/                  # Lógica de negocio
│   ├── __init__.py
│   ├── frame_steganography.py    # Lógica para ocultar en frames
│   ├── audio_steganography.py    # Lógica para ocultar en audio
│   └── file_steganography.py     # Lógica para ocultar archivos
├── ui/                    # Interfaz gráfica
│   ├── __init__.py
│   ├── main_window.py     # Ventana principal
│   ├── frame_tab.py       # Pestaña de frames
│   ├── audio_tab.py       # Pestaña de audio
│   └── file_tab.py        # Pestaña de archivos
├── assets/                # Recursos (iconos, imágenes)
│   └── .gitkeep
├── temp/                  # Archivos temporales
│   └── .gitkeep
└── output/                # Videos procesados
    └── .gitkeep
```

## 🔒 Seguridad

- Los datos se ocultan usando técnicas LSB (Least Significant Bit)
- Opción de encriptación AES antes de ocultar
- Validación de capacidad del video

## ⚠️ Limitaciones

- Funciona mejor con formatos sin pérdida (AVI, MP4 sin compresión)
- La capacidad depende del tamaño y duración del video
- No subir videos procesados a plataformas que recomprimen (YouTube, etc.)

## 📝 Licencia

MIT License
