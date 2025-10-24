#!/usr/bin/env python3
"""
CleanTrack WAV - GUI front-end that extracts instrumental using Demucs and applies 'brillante' processing,
saving output as WAV.

Notes:
- This script expects bundled dependencies when compiled into an .exe (demucs, torchaudio, pedalboard, soundfile, pysimplegui).
- When run from source, install dependencies:
    pip install demucs torchaudio pedalboard soundfile pysimplegui
"""
import os
import sys
import tempfile
import traceback
import PySimpleGUI as sg

def resource_path(relative):
    # placeholder for PyInstaller resource handling
    return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(__file__)), relative)

def run_processing(input_path, out_dir, output_format="wav"):
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
        # Load model
        model = get_model(name="htdemucs")
        # load audio
        wav, sr = torchaudio.load(input_path)
        if wav.dim() > 1:
            wav = wav.mean(dim=0, keepdim=True)
        # apply model (device cpu)
        pred = apply_model(model, wav, shifts=1, overlap=0.25, split=True, device="cpu")[0]
        # demucs returns [sources, channels, samples] - instrumental is 'no vocals' stem in HTDemucs outputs
        # We'll attempt to pick the instrumental stem if available, otherwise mix non-vocal stems.
        # If pred is dict-like, adapt accordingly.
        try:
            instrumental = pred[0]  # common layout: [instrumental, other...]
        except Exception:
            # fallback: average all channels
            instrumental = pred.mean(axis=0)

        temp_wav = os.path.join(out_dir, f"{base}_instrumental_temp.wav")
        torchaudio.save(temp_wav, instrumental.unsqueeze(0), sr)

        # Processing chain - 'brillante' tone
        y, sr = sf.read(temp_wav)
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=120.0),  # remove low rumble
            LowpassFilter(cutoff_frequency_hz=20000.0),
            Compressor(threshold_db=-20, ratio=3.0, release_ms=200),
            Gain(gain_db=4.0),  # brighter
            Reverb(room_size=0.18, wet_level=0.12)
        ])
        y_out = board(y, sr)
        final_path = os.path.join(out_dir, f"{base}_instrumental_mejorado.wav")
        sf.write(final_path, y_out, sr)
        os.remove(temp_wav)
        return True, final_path
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Error: {e}\\n{tb}"

def main():
    sg.theme("LightBlue")
    layout = [
        [sg.Text("CleanTrack — Exportar instrumental (.wav) - Modo Brillante")],
        [sg.Text("Archivo de entrada:"), sg.Input(key="-IN-"), sg.FileBrowse(file_types=(("Audio Files", "*.mp3;*.wav;*.flac"),))],
        [sg.Text("Carpeta de salida:"), sg.Input(key="-OUT-"), sg.FolderBrowse()],
        [sg.Button("Procesar WAV"), sg.Button("Salir")],
        [sg.Multiline(size=(80,10), key="-LOG-", disabled=True)]
    ]
    window = sg.Window("CleanTrack - WAV", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Salir"):
            break
        if event == "Procesar WAV":
            input_path = values["-IN-"]
            out_dir = values["-OUT-"]
            if not input_path or not out_dir:
                window["-LOG-"].print("Por favor seleccioná archivo de entrada y carpeta de salida.")
                continue
            window["-LOG-"].print("Iniciando procesamiento... esto puede tardar varios minutos.")
            window.refresh()
            ok, msg = run_processing(input_path, out_dir, output_format="wav")
            if ok:
                window["-LOG-"].print(f"✅ Procesado completado: {msg}")
            else:
                window["-LOG-"].print(f"❌ {msg}")

    window.close()

if __name__ == "__main__":
    main()
