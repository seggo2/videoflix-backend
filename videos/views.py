from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView





class VideoflixBoard(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
      if request.method == 'GET':
        
        return Response()
      else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

