import os
import subprocess

def convert_video(source):
    target=source +'_480p.mp4'
    print(source)
    cmd='ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source,target)
    subprocess.run(cmd,capture_output=True)
    
