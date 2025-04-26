# videos/tasks.py

import os
import subprocess

def run_ffmpeg_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg Error: {result.stderr}")
    return result

def delete_files(file_paths):
    for path in file_paths:
        if os.path.isfile(path):
            os.remove(path)

def process_full_video(source):
    try:
        # Zielpfade definieren
        target_480p = source.replace('.mp4', '_480p.mp4')
        target_720p = source.replace('.mp4', '_720p.mp4')
        thumbnail = source.replace('.mp4', '.jpg')

        # 1. Screenshot erzeugen (direkt bei Sekunde 1)
        run_ffmpeg_command(f'ffmpeg -y -i "{source}" -ss 00:00:01 -vframes 1 "{thumbnail}"')

        # 2. Videos konvertieren
        run_ffmpeg_command(f'ffmpeg -y -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target_480p}"')
        run_ffmpeg_command(f'ffmpeg -y -i "{source}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target_720p}"')

        # 3. Sicherstellen, dass alle Dateien existieren
        for file in [target_480p, target_720p, thumbnail]:
            if not os.path.isfile(file):
                raise Exception(f"Missing file after processing: {file}")

    except Exception as e:
        # Bei Fehler alles löschen
        print(f"Error detected during processing: {e}. Cleaning up...")
        delete_files([target_480p, target_720p, thumbnail])
        raise e

def convert_video_delete(source):
    # Manuelles Löschen der erzeugten Versionen
    target_480p = source.replace('.mp4', '_480p.mp4')
    target_720p = source.replace('.mp4', '_720p.mp4')
    thumbnail = source.replace('.mp4', '.jpg')
    delete_files([target_480p, target_720p, thumbnail])
