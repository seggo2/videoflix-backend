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
from django_registration.backends.activation.views import RegistrationView as BaseRegistrationView
from django_registration.forms import RegistrationForm
from django_registration.backends.activation.views import RegistrationView as BaseRegistrationView
from django_registration.forms import RegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode

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



class CustomRegistrationView(View):
    form_class = RegistrationForm

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        body_data = json.loads(request.body.decode('utf-8'))  # Parse JSON data
        username = body_data.get('username')
        email = body_data.get('email')
        password = body_data.get('password')
        User = get_user_model()  # Holen des richtigen Benutzermodells
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # Setze den Benutzer zunächst als inaktiv
        user.save()

        # Sende Aktivierungs-E-Mail
        self.send_activation_email(user)

        return JsonResponse({'message': 'User created successfully. Please check your email to activate your account.'})

    def send_activation_email(self, user):
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account'
        
        protocol = 'https' if self.request.is_secure() else 'http' 
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_key = f"{uid.encode()}-{token}"  # Kombiniere UID und Token
        
        message = render_to_string('account_activation_email.html', {
        'user': user,
        'domain': '127.0.0.1:8000',
        'protocol': protocol,  # Füge das Protokoll hinzu
        'activation_key': activation_key,  # Füge den Aktivierungsschlüssel hinzu
        })
        
        to_email = user.email
        email = EmailMessage(mail_subject, message,'videoflix_project@mail.de', to=[to_email])
        email.send()

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        return CustomRegistrationView.as_view()(request)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)  # Method Not Allowed



class ActivationView(View):
    @method_decorator(csrf_exempt)  # CSRF-Schutz für diese View deaktivieren (optional, je nach Bedarf)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, activation_key):
        try:
            uidb64, token = activation_key.split('-')
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (ValueError, OverflowError, get_user_model().DoesNotExist):
            return HttpResponse("Invalid activation link")

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)  # Optional: Automatisch den Benutzer einloggen
            return redirect(reverse_lazy('activation_success'))  # Erfolgsmeldung oder Weiterleitung
        else:
            return HttpResponse("Invalid activation link")
