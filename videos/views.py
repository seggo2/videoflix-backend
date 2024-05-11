from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import os
from django.http import HttpResponse
from .models import Video
from django.shortcuts import get_object_or_404



class VideoflixBoard(APIView):
    def get(self, request, format=None):
        if request.method == 'GET':
            videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
            files = os.listdir(videos_dir)
            images = [file for file in files if file.endswith('.jpg')]
            return Response(images)
        else:
            return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
          
          
          
def download_image(request, image_name):
    video_name = image_name.replace('.jpg', '.mp4')
    video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_name)

    if os.path.exists(video_path):
        video_file = f'videos/{video_name}'
        video = get_object_or_404(Video, video_file=video_file)

        video_data = {
            'title': video.title,
            'description': video.description,
            'image_url': f'http://localhost:8000/media/videos/{image_name}'
        }

        return JsonResponse(video_data)
    else:
        return HttpResponse('Video not found', status=404)

