import os

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video


class VideoflixBoard(APIView):
    def get(self, request, format=None):
        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        files = os.listdir(videos_dir)
        images = [file for file in files if file.endswith('.jpg')]
        return Response(images)


def download_image(request, image_name):
    video_name = image_name.replace('.jpg', '.mp4')
    video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_name)

    if os.path.exists(video_path):
        video_file = f'videos/{video_name}'
        video = get_object_or_404(Video, video_file=video_file)

        video_data = {
            'title': video.title,
            'description': video.description,
            'image_url': request.build_absolute_uri(f'{settings.MEDIA_URL}videos/{image_name}')
        }

        return JsonResponse(video_data)
    else:
        return HttpResponse('Video not found', status=404)


def get_video(request, video_name):
    video_name, _ = os.path.splitext(video_name)
    video_path = os.path.join(settings.MEDIA_ROOT, 'videos', f'{video_name}.mp4')

    if not os.path.exists(video_path):
        return HttpResponseNotFound('Video not found')

    video_urls = {
        '1080p': request.build_absolute_uri(f'{settings.MEDIA_URL}videos/{video_name}_1080p.mp4'),
        '720p': request.build_absolute_uri(f'{settings.MEDIA_URL}videos/{video_name}_720p.mp4'),
        '480p': request.build_absolute_uri(f'{settings.MEDIA_URL}videos/{video_name}_480p.mp4')
    }

    return JsonResponse(video_urls)
