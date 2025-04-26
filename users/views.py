import json
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_registration.forms import RegistrationForm
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework import status

User = get_user_model()

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Gastbenutzer automatisch erstellen, wenn nicht vorhanden
        if username == 'gast':
            user, created = User.objects.get_or_create(username='gast', defaults={
                'email': 'gast@example.com',
                'is_active': True
            })
            if created:
                user.set_password('gast123')
                user.save()

        # Standard-Login-Logik
        serializer = self.serializer_class(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"error": "username or password are incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({"error": "Please confirm your email."}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
        

class PutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        todo = self.get_object(pk)
        serializer = UserSerializer(todo, data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404


class DeleteView(APIView):
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


@method_decorator(csrf_exempt, name='dispatch')
class CustomRegistrationView(View):
    form_class = RegistrationForm

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            username = body_data.get('username')
            email = body_data.get('email')
            password = body_data.get('password')
            User = get_user_model()

            # Zusätzliche Sicherheitsprüfung, auch wenn der Check schon im Frontend war
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'E-Mail ist bereits vergeben.'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Benutzername ist bereits vergeben.'}, status=400)

            # User erstellen
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()

            # Aktivierungsmail versenden
            self.send_activation_email(user)

            return JsonResponse({
                'message': 'User created successfully. Please check your email to activate your account.'
            })

        except Exception as e:
            print('❌ Fehler bei der Registrierung:', e)
            return JsonResponse({'error': 'Ein unerwarteter Fehler ist aufgetreten.'}, status=500)

    def send_activation_email(self, user):
        mail_subject = 'Activate your account'
        protocol = 'https' if self.request.is_secure() else 'http'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_key = f"{uid}-{token}"

        user.activation_token = token
        user.save()

        message = render_to_string('account_activation_email.html', {
            'user': user,
            'domain': 'sefaflixapi.duckdns.org',
            'protocol': protocol,
            'activation_key': activation_key,
        })

        to_email = user.email
        email = EmailMessage(mail_subject, message, 'videoflix_project@mail.de', to=[to_email])
        email.send()


@method_decorator(csrf_exempt, name='dispatch')
def register_view(request):
    if request.method == 'POST':
        return CustomRegistrationView.as_view()(request)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


class ActivationView(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, activation_key):
        try:
            uid, token, _ = activation_key.split('-')
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = get_user_model().objects.get(pk=uid_decoded)
        except (ValueError, OverflowError, get_user_model().DoesNotExist):
            return HttpResponse("Invalid activation link")
        token_user, token_second = user.activation_token.split('-')
        if token_user == token and token_second == _:
            user.is_active = True
            user.authenticated = True
            user.save()
            login(request, user)
            return HttpResponse("Thank You")
        else:
            return HttpResponse("Invalid activation link")


@method_decorator(csrf_exempt, name='dispatch')
class CheckUserView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        email = data.get('email')

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Benutzername ist bereits vergeben.'}, status=400)
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'E-Mail ist bereits registriert.'}, status=400)

        return JsonResponse({'message': 'Benutzername und E-Mail sind verfügbar.'}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetRequestView(View):
    def post(self, request, *args, **kwargs):
        try:
            request_body = json.loads(request.body.decode('utf-8'))
            email = request_body.get('email')

            if not email:
                return JsonResponse({"error": "E-Mail-Adresse ist erforderlich."}, status=400)
            try:
                user = CustomUser.objects.get(email=email)
                self.send_password_reset_email(user, request)
            except CustomUser.DoesNotExist:
                pass 

            return JsonResponse({"message": "Wenn ein Konto mit dieser E-Mail existiert, wurde eine Reset-Mail gesendet."}, status=200)

        except Exception as e:
            print("❌ Fehler bei Passwort-Reset-Anfrage:", e)
            return JsonResponse({"error": "Ein unerwarteter Fehler ist aufgetreten."}, status=500)

    def send_password_reset_email(self, user, request):
        domain = 'sefavideoflix.duckdns.org'
        mail_subject = 'Passwort zurücksetzen'
        protocol = 'https' if request.is_secure() else 'http'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{protocol}://{domain}/reset-password/{uid}/{token}/"

        message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })

        email = EmailMessage(
            mail_subject,
            message,
            'videoflix_project@mail.de',
            [user.email]
        )
        email.content_subtype = "html"  # ✅ HTML aktivieren
        email.send()

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetConfirmView(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (ValueError, OverflowError, get_user_model().DoesNotExist):
            return HttpResponse("Invalid password reset link")

        if default_token_generator.check_token(user, token):
            return redirect(f"http://localhost:4200/reset-password/{uidb64}/{token}/")
        else:
            return HttpResponse("Invalid password reset link")


@method_decorator(csrf_exempt, name='dispatch')
class SetNewPassword(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            uid = data.get('uid')
            token = data.get('token')
            new_password = data.get('new_password')

            if not uid or not token or not new_password:
                return JsonResponse({"error": "Alle Felder sind erforderlich."}, status=400)

            if len(new_password) < 7:
                return JsonResponse({"error": "Das Passwort muss mindestens 7 Zeichen lang sein."}, status=400)

            try:
                uid = urlsafe_base64_decode(uid).decode()
                user = get_user_model().objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
                return JsonResponse({"error": "Ungültiger Benutzer."}, status=400)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return JsonResponse({"message": "Passwort erfolgreich geändert."}, status=200)
            else:
                return JsonResponse({"error": "Ungültiges oder abgelaufenes Token."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Ungültiges JSON-Format."}, status=400)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
