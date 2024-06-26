import os
import subprocess


def convert_video(source):
    target = source.replace('.mp4', '_480p.mp4')
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, target)
    subprocess.run(cmd, capture_output=True, shell=True)


def convert_video_720p(source):
    target = source.replace('.mp4', '_720p.mp4')
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, target)
    subprocess.run(cmd, capture_output=True, shell=True)


def convert_video_1080p(source):
    target = source.replace('.mp4', '_1080p.mp4')
    cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, target)
    subprocess.run(cmd, capture_output=True, shell=True)


def extract_thumbnail(source):
    target = source.replace('.mp4', '.jpg')
    cmd = 'ffmpeg -i "{}" -ss 00:00:05 -vframes 1 "{}"'.format(source, target)
    subprocess.run(cmd, capture_output=True, shell=True)


def convert_video_delete(source):
    target = source.replace('.mp4', '_480p.mp4')
    target2 = source.replace('.mp4', '_720p.mp4')
    target3 = source.replace('.mp4', '_1080p.mp4')
    target4 = source.replace('.mp4', '.jpg')
    for t in [target, target2, target3, target4]:
        if os.path.isfile(t):
            os.remove(t)
