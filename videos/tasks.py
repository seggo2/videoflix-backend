import os
import subprocess
from .models import Video
from django.dispatch import receiver

def convert_video(source):
    target = source.replace('.mp4', '_480p.mp4')
    cmd='ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source,target)
    subprocess.run(cmd,capture_output=True)


def convert_video_delete(source):
    target = source.replace('.mp4', '_480p.mp4')
    if target:
        if os.path.isfile(target):
            os.remove(target)