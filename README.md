# CleanTrack

**CleanTrack** es un paquete que extrae la pista instrumental de un archivo de audio, aplica procesamiento *brillante* (ecualización, compresión ligera, limpieza de fondo) y exporta en **WAV** o **MP3**.

## Qué contiene este repositorio
- `cleantrack_wav.py` — aplicación GUI que produce **.wav** como salida.
- `cleantrack_mp3.py` — aplicación GUI que produce **.mp3** como salida.
- `build_cleantrack.bat` — script para construir los ejecutables localmente (requiere Python).
- `.github/workflows/build-windows.yml` — workflow para GitHub Actions que compila los .exe en Windows y los sube como artefactos.

## Objetivo
Proveer dos ejecutables (`CleanTrack_WAV.exe`, `CleanTrack_MP3.exe`) para Windows 11 que no requieran Python instalado en el equipo final. Debido a restricciones de publicación de binarios, este repositorio incluye todo lo necesario para **compilar** los ejecutables en:
- una máquina local con Python (ejecutando `build_cleantrack.bat`), o
- mediante **GitHub Actions** (el workflow `build-windows` compilará los ejecutables en un runner de Windows y subirá los exes como artifacts).

## Cómo obtener los .exe sin instalar Python en tu equipo final
1. Crea un repositorio en GitHub (público o privado).
2. Sube todo el contenido de este paquete a la rama `main`.
3. En GitHub → **Actions**, ejecuta el workflow manualmente (o haz push a main). El workflow compilará los .exe.
4. Después de la ejecución, descarga los artefactos desde la run del workflow o configúralo para crear una Release con los ejecutables. Los artefactos serán `dist/CleanTrack_WAV.exe` y `dist/CleanTrack_MP3.exe`.

> ⚠️ Nota sobre tamaño: el workflow descarga el modelo de Demucs en tiempo de ejecución; los artefactos finales pueden pesar varias centenas de MB.

## Si preferís que yo prepare el repo en GitHub por vos
No puedo, por limitaciones, subir directamente archivos ejecutables ni crear repositorios en tu cuenta. Pero si querés, te doy los pasos exactos (comandos `git`) para crear el repo y subirlo, o te doy el contenido listo para subir.

## Uso local (si decidís compilar en una máquina con Python)
1. Ejecutá `build_cleantrack.bat` en una máquina Windows con Python 3.10+.
2. Encontrarás los ejecutables en la carpeta `dist`.

## Soporte
Si querés, te puedo:
- Generar el repositorio ZIP listo para subir a GitHub (incluye todos estos archivos).  
- Proveer los comandos `git` exactos para crear el repo y subirlo desde tu máquina.  
- Ayudarte a ajustar la GUI o parámetros de procesamiento.

Salú — decime qué preferís que haga ahora.
