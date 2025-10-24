#!/usr/bin/env python3
"""
CleanTrack MP3 - GUI front-end that extracts instrumental using Demucs and applies 'brillante' processing,
saving output as MP3.

Notes:
- This script expects bundled dependencies when compiled into an .exe.
- When run from source, install dependencies:
    pip install demucs torchaudio pedalboard soundfile pysimplegui
- MP3 encoding in soundfile may rely on libsndfile compiled with MP3 support; the GitHub Actions build installs ffmpeg and pydub fallback.
"""
import os
import sys
import tempfile
import traceback
import PySimpleGUI as sg

def run_processing(input_path, out_dir, output_format="mp3"):
    try:
        import torch, torchaudio
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        import soundfile as sf
        from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Compressor, Gain, Reverb
    except Exception as e:
        return False, f"Falta una dependencia: {e}"

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(input_path))[0]
    try:
        model = get_model(name="htdemucs")
        wav, sr = torchaudio.load(input_path)
        if wav.dim() > 1:
            wav = wav.mean(dim=0, keepdim=True)
        pred = apply_model(model, wav, shifts=1, overlap=0.25, split=True, device="cpu")[0]
        try:
            instrumental = pred[0]
        except Exception:
            instrumental = pred.mean(axis=0)
        temp_wav = os.path.join(out_dir, f"{base}_instrumental_temp.wav")
        torchaudio.save(temp_wav, instrumental.unsqueeze(0), sr)

        y, sr = sf.read(temp_wav)
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=120.0),
            LowpassFilter(cutoff_frequency_hz=20000.0),
            Compressor(threshold_db=-20, ratio=3.0, release_ms=200),
            Gain(gain_db=4.0),
            Reverb(room_size=0.18, wet_level=0.12)
        ])
        y_out = board(y, sr)
        final_wav = os.path.join(out_dir, f"{base}_instrumental_mejorado.wav")
        sf.write(final_wav, y_out, sr)

        # Convert to mp3 using pydub + ffmpeg (fallback if soundfile mp3 unsupported)
        try:
            from pydub import AudioSegment
            AudioSegment.from_wav(final_wav).export(os.path.join(out_dir, f"{base}_instrumental_mejorado.mp3"), format="mp3", bitrate="192k")
            os.remove(final_wav)
            os.remove(temp_wav)
            return True, os.path.join(out_dir, f"{base}_instrumental_mejorado.mp3")
        except Exception:
            # last resort: try soundfile write as MP3 (may fail if libsndfile lacks MP3)
            final_mp3 = os.path.join(out_dir, f"{base}_instrumental_mejorado.mp3")
            try:
                sf.write(final_mp3, y_out, sr, format='MP3', subtype='PCM_S16B')
                os.remove(final_wav)
                os.remove(temp_wav)
                return True, final_mp3
            except Exception as e:
                return False, f"No se pudo crear MP3 automáticamente: {e}"

    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Error: {e}\\n{tb}"

def main():
    sg.theme("LightBlue")
    layout = [
        [sg.Text("CleanTrack — Exportar instrumental (.mp3) - Modo Brillante")],
        [sg.Text("Archivo de entrada:"), sg.Input(key="-IN-"), sg.FileBrowse(file_types=(("Audio Files", "*.mp3;*.wav;*.flac"),))],
        [sg.Text("Carpeta de salida:"), sg.Input(key="-OUT-"), sg.FolderBrowse()],
        [sg.Button("Procesar MP3"), sg.Button("Salir")],
        [sg.Multiline(size=(80,10), key="-LOG-", disabled=True)]
    ]
    window = sg.Window("CleanTrack - MP3", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Salir"):
            break
        if event == "Procesar MP3":
            input_path = values["-IN-"]
            out_dir = values["-OUT-"]
            if not input_path or not out_dir:
                window["-LOG-"].print("Por favor seleccioná archivo de entrada y carpeta de salida.")
                continue
            window["-LOG-"].print("Iniciando procesamiento... esto puede tardar varios minutos.")
            window.refresh()
            ok, msg = run_processing(input_path, out_dir, output_format="mp3")
            if ok:
                window["-LOG-"].print(f"✅ Procesado completado: {msg}")
            else:
                window["-LOG-"].print(f"❌ {msg}")

    window.close()

if __name__ == "__main__":
    main()
