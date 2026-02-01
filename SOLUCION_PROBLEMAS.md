# 🔧 Solución de Problemas - Video Steganography

## ❌ Error: "ModuleNotFoundError: No module named 'cv2'"

### Problema
Cuando ejecutas `python main.py` aparece el error:
```
ModuleNotFoundError: No module named 'cv2'
```

### Causa
Estás usando el Python del sistema en lugar del Python del entorno virtual que tiene las dependencias instaladas.

### ✅ Soluciones

#### Solución 1: Usar run.bat (RECOMENDADO)
```bash
# Doble click en:
run.bat

# O desde PowerShell/CMD:
.\run.bat
```

#### Solución 2: Usar run.ps1 (PowerShell)
```powershell
# Desde PowerShell:
.\run.ps1
```

#### Solución 3: Ejecutar directamente con el Python del venv
```bash
# Desde CMD o PowerShell:
venv\Scripts\python.exe main.py
```

#### Solución 4: Activar correctamente el entorno virtual

**En PowerShell:**
```powershell
# Activar
venv\Scripts\Activate.ps1

# Ejecutar
python main.py
```

**En CMD:**
```cmd
# Activar
venv\Scripts\activate.bat

# Ejecutar
python main.py
```

---

## ⚠️ Otros Problemas Comunes

### Error: "venv\Scripts\python.exe no existe"

**Causa**: El entorno virtual no se creó correctamente.

**Solución**:
```bash
# Eliminar carpeta venv si existe
rmdir /s venv

# Crear nuevo entorno virtual
python -m venv venv

# Instalar dependencias
venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

### Error: "cannot be loaded because running scripts is disabled"

**Causa**: PowerShell tiene restricciones de ejecución de scripts.

**Solución**:
```powershell
# Opción 1: Cambiar política de ejecución (como administrador)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Opción 2: Ejecutar con bypass
PowerShell -ExecutionPolicy Bypass -File run.ps1

# Opción 3: Usar run.bat en su lugar
.\run.bat
```

---

### Error al instalar dependencias

**Causa**: Problemas con pip o compilación de librerías.

**Solución**:
```bash
# Actualizar pip
venv\Scripts\python.exe -m pip install --upgrade pip

# Instalar dependencias una por una
venv\Scripts\python.exe -m pip install customtkinter
venv\Scripts\python.exe -m pip install opencv-python
venv\Scripts\python.exe -m pip install Pillow
venv\Scripts\python.exe -m pip install numpy
venv\Scripts\python.exe -m pip install ffmpeg-python
venv\Scripts\python.exe -m pip install cryptography
```

---

### La aplicación no se abre o se cierra inmediatamente

**Posibles causas y soluciones**:

1. **Error en el código**:
   ```bash
   # Ejecutar desde terminal para ver el error
   venv\Scripts\python.exe main.py
   ```

2. **Falta CustomTkinter**:
   ```bash
   venv\Scripts\python.exe -m pip install customtkinter
   ```

3. **Problema con la pantalla**:
   - Verifica que tu sistema soporte interfaces gráficas
   - Intenta ejecutar desde el escritorio, no desde SSH/remoto

---

### Error: "No se pudo abrir el video" o errores de FFmpeg

**Causas posibles**:
- El video está corrupto o el formato no es compatible.
- Falta FFmpeg en el sistema o no está en el PATH.

**Solución Automática (Recomendada)**:
La aplicación ahora incluye `static-ffmpeg` para autogestionar la presencia de FFmpeg. Solo asegúrate de tener las dependencias actualizadas:
```bash
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Solución Manual**:
Si la solución automática falla, puedes instalar FFmpeg manualmente:
1. Descargar desde [ffmpeg.org](https://ffmpeg.org/download.html).
2. Extraer y agregar la carpeta `bin` al PATH del sistema.
3. Verificar con `ffmpeg -version` en una nueva terminal.

---

### Error: "El archivo es demasiado grande"

**Causa**: El archivo no cabe en el video seleccionado.

**Soluciones**:
1. Usa un video más largo
2. Usa un video de mayor resolución
3. Comprime el archivo antes (ZIP con compresión máxima)
4. Divide el archivo en partes más pequeñas

---

### No se puede extraer el archivo

**Causas posibles**:
1. El video fue recomprimido (YouTube, redes sociales)
2. El video no tiene archivo oculto
3. El video está corrupto

**Solución**:
- Usa el video original generado por la aplicación
- No subas el video a plataformas que recomprimen
- Comparte el video directamente (USB, email, etc.)

---

## 📝 Verificación del Entorno

### Comprobar que todo está instalado correctamente:

```bash
# 1. Verificar Python del venv
venv\Scripts\python.exe --version

# 2. Verificar dependencias instaladas
venv\Scripts\python.exe -m pip list

# Deberías ver:
# - customtkinter
# - opencv-python
# - Pillow
# - numpy
# - ffmpeg-python
# - cryptography
```

---

## 🆘 Si Nada Funciona

### Reinstalación completa:

```bash
# 1. Eliminar entorno virtual
rmdir /s venv

# 2. Crear nuevo entorno virtual
python -m venv venv

# 3. Actualizar pip
venv\Scripts\python.exe -m pip install --upgrade pip

# 4. Instalar dependencias
venv\Scripts\python.exe -m pip install -r requirements.txt

# 5. Ejecutar aplicación
venv\Scripts\python.exe main.py
```

---

## 💡 Mejores Prácticas

### Para evitar problemas:

1. **Siempre usa el Python del venv**:
   ```bash
   venv\Scripts\python.exe main.py
   ```

2. **O usa los scripts proporcionados**:
   ```bash
   run.bat  # Windows CMD
   run.ps1  # PowerShell
   ```

3. **No uses `python main.py` directamente** a menos que hayas activado correctamente el entorno virtual.

4. **Verifica que estás en la carpeta correcta**:
   ```bash
   cd C:\Users\edlit\OneDrive\Documentos\Esteganografía_Python
   ```

---

## 📞 Comandos Útiles

### Verificar instalación:
```bash
# Ver versión de Python
venv\Scripts\python.exe --version

# Ver paquetes instalados
venv\Scripts\python.exe -m pip list

# Ver información de un paquete
venv\Scripts\python.exe -m pip show opencv-python
```

### Actualizar dependencias:
```bash
# Actualizar todas las dependencias
venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt

# Actualizar una dependencia específica
venv\Scripts\python.exe -m pip install --upgrade customtkinter
```

### Limpiar caché:
```bash
# Limpiar caché de pip
venv\Scripts\python.exe -m pip cache purge

# Limpiar archivos .pyc
del /s /q *.pyc
del /s /q __pycache__
```

---

## ✅ Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] Estás en la carpeta correcta del proyecto
- [ ] El entorno virtual existe (`venv` folder)
- [ ] Las dependencias están instaladas (`pip list`)
- [ ] Usas el Python del venv (`venv\Scripts\python.exe`)
- [ ] O usas los scripts `run.bat` o `run.ps1`
- [ ] No hay errores en la terminal al ejecutar

---

**Si sigues teniendo problemas, revisa los mensajes de error en la terminal y busca en esta guía la solución correspondiente.**
