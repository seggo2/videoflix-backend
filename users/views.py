import json
from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt


class LoginView(ObtainAuthToken):
  def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })  


class put(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request, pk, *args, **kwargs):
        if request.method == 'PUT':
            todo = self.get_object(pk)
            serializer = UserSerializer(todo, data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user)
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        else:
            return JsonResponse({'error': 'Only PUT requests are allowed'}, status=405)

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404


class delete(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            todo = self.get_object(pk)
            todo.delete()
            return JsonResponse({'message': 'Todo successfully deleted'}, status=204)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Todo not found'}, status=404)

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)  # Parse JSON data
        username = body_data.get('username')
        email = body_data.get('email')
        password = body_data.get('password')
        User = get_user_model()
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return JsonResponse({'message': 'User created successfully'})
    
    