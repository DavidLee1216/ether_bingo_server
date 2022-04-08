from django.shortcuts import render
from .models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


@api_view(['POST'])
def bid(request):
    return Response(status=200)
