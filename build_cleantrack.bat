@echo off
REM Build script for CleanTrack - builds two Windows exes with PyInstaller.
REM Requires Python installed on the build machine. This script is intended for use on a builder machine or CI.

SETLOCAL

echo Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller demucs torchaudio pedalboard soundfile pysimplegui pydub

echo Building WAV exe...
pyinstaller --noconfirm --onefile --name CleanTrack_WAV cleantrack_wav.py

echo Building MP3 exe...
pyinstaller --noconfirm --onefile --name CleanTrack_MP3 cleantrack_mp3.py

echo Build finished. Find binaries in the "dist" folder.
ENDLOCAL
pause
