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
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import UserSerializer


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            if not user.is_authenticated:
                return Response({'detail': 'Please confirm your email.'},
                                status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })
        except Exception:
            return Response({'detail': 'Username or password are wrong.'},
                            status=status.HTTP_400_BAD_REQUEST)


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
        body_data = json.loads(request.body.decode('utf-8'))
        username = body_data.get('username')
        email = body_data.get('email')
        password = body_data.get('password')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'A user with this email already exists.'},
                                status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        self.send_activation_email(user)

        return JsonResponse({
            'message': 'User created successfully. Please check your email to activate your account.'
        })

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
            'domain': 'sefa-gur.developerakademie.org',
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


class UserDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address,
            'phone': user.phone
        }
        return Response(user_data)

    def put(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        try:
            data = json.loads(request.body)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.address = data.get('address', user.address)
            user.phone = data.get('phone', user.phone)
            user.save()

            return JsonResponse({
                'message': 'User details updated successfully',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'address': user.address,
                'phone': user.phone
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetRequestView(View):
    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body.decode('utf-8'))
        email = request_body.get('email')
        user = get_object_or_404(CustomUser, email=email)
        self.send_password_reset_email(user)
        return JsonResponse({"message": "Password reset email sent."}, status=200)

    def send_password_reset_email(self, user):
        domain = 'sefa-gur.developerakademie.org'
        mail_subject = 'Passwort zurücksetzen'
        protocol = 'https' if self.request.is_secure() else 'http'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{protocol}://{domain}/reset-password/{uid}/{token}/"

        message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        to_email = user.email
        email = EmailMessage(mail_subject, message, 'videoflix_project@mail.de', to=[to_email])
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

            try:
                uid = urlsafe_base64_decode(uid).decode()
                user = get_user_model().objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
                return JsonResponse({"error": "Invalid user ID"}, status=400)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return JsonResponse({"message": "Password has been reset successfully"}, status=200)
            else:
                return JsonResponse({"error": "Invalid token"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
