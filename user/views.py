from django.shortcuts import render

from game.models import UserCoin
from .models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .serializer import UserSerializer
from .random_n_digit import random_with_N_digits
from .get_token import get_tokens_for_user
from ether_bingo_server import settings
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['POST'])
@permission_classes((AllowAny, ))
def signup(request):
    email = request.data.get('email', False)
    password = request.data.get('password', False)
    username = request.data.get('username', False)
    first_name = request.data.get('firstname', False)
    last_name = request.data.get('lastname', False)
    if User.objects.filter(email__iexact=email).exists():
        return Response({"message": "Email already in use", "type": "email"}, status=status.HTTP_409_CONFLICT)
    elif User.objects.filter(username__iexact=username).exists():
        return Response({"message": "Username already exists", "type": "username"}, status=status.HTTP_409_CONFLICT)
    else:
        user = User.objects.create_user(
            email=email, password=password, first_name=first_name, last_name=last_name, username=username)
        subject = "Hi, {}, Please confirm your email".format(
            username)
        number = random_with_N_digits(16)
        user.auth_code = str(number)
        user.save()
        email_template_name = "registration_verification.html"
        # url_link = "http://localhost:8000/api/user/auth/{}/verify/{}".format(
        #     user.id, number)
        url = "auth/{}/{}".format(user.id, user.auth_code)
        html_message = render(request, email_template_name, {
                              'id': user.id, 'key': user.auth_code, 'email': user.email, 'username': user.username, 'protocol': 'http', 'domain': '127.0.0.1:3000', 'site_name': 'crown bingo', 'url': url}).content.decode('utf-8')
        message = "This is the email from crown bingo. This is authentication link.\r\n {}".format(
            number)
        # user.email_user(
        #     subject, message, from_email=settings.EMAIL_HOST_USER, html_message=html_message)
        send_mail(subject=subject, message=message,
                  html_message=html_message, from_email=settings.EMAIL_HOST_USER, recipient_list=[email], fail_silently=False)
        userSerialized = UserSerializer(user)
        return Response(userSerialized.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def resend_auth_email(request):
    email = request.data.get('email', False)
    first_name = request.data.get('first_name', False)
    last_name = request.data.get('last_name', False)
    username = request.data.get('username', False)
    user = User.objects.filter(email=email).first()
    if user is not None:
        if user.is_active == False:
            subject = "Hi, {}, Please confirm your email".format(
                username)
            number = 0  # random_with_N_digits(6)
            user.auth_code = str(number)
            user.save()
            email_template_name = "registration_verification.html"
            html_message = render(request, email_template_name, {
                                  'auth_code': number}).content.decode('utf-8')
            message = "This is the email from online language school. This is authentication code.\r\n {}".format(
                number)
            user.email_user(
                subject, message, from_email=settings.EMAIL_HOST_USER, html_message=html_message)
        return Response(status=200)
    else:
        return Response(status=404)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def signin(request):
    email = request.data.get('email', False)
    password = request.data.get('password', False)
    user = authenticate(email=email, password=password)
    if user is None:
        user = authenticate(username=email, password=password)
    user_serialized = UserSerializer(user)
    if user is not None:
        token = get_tokens_for_user(user)
        login(request, user)
        data = {"user": user_serialized.data, "token": token}

        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data="Something is wrong.", status=404)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def authorize(request):
    id = request.data.get('id', False)
    key = request.data.get('key', False)
    user = User.objects.get(id=id)
    original_key = user.auth_code
    if user is not None and key == original_key:
        user.is_active = True
        user.save()
        user_serialized = UserSerializer(user)
        user_coin = UserCoin(user=user, coin=0)
        user_coin.save()
        token = get_tokens_for_user(user)
        login(request, user)
        data = {"user": user_serialized.data, "token": token}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data="Something is wrong.", status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def email_authorize(request, id, key):
    user = User.objects.get(id=id)
    original_key = user.auth_code
    if user is not None and key == original_key:
        user.is_active = True
        user.save()
        login(request, user)
        # user_serialized = UserSerializer(user)
        return Response(status=200)
    else:
        return Response(data="Something is wrong.", status=404)


@login_required
@api_view(['POST'])
def signout(request):
    logout(request)
    return Response(status=200)
