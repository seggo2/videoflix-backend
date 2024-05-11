from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import os
from django.http import HttpResponse




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
    image_path = os.path.join(settings.MEDIA_ROOT, 'videos', image_name)
    if os.path.exists(image_path):
        with open(image_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='image/jpeg')
            response['Content-Disposition'] = f'attachment; filename="{image_name}"'
            return response
    else:
        return HttpResponse('Image not found', status=404)

