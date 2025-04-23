from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from tiktok_api import settings
from user.serializers import UserCreateSerializer, UserLoginSerializer
from user.models import User

class RegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Đăng ký người dùng mới.",
        request_body=UserCreateSerializer,  # Specify the serializer for the request body
        responses={
            201: openapi.Response('User registered successfully'),
            400: openapi.Response('Invalid input data', UserCreateSerializer),
        }
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()

            return Response({
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Đăng nhập người dùng.",
        request_body=UserLoginSerializer,
        responses={
            200: 'Login successful, returns access and refresh tokens',
            400: 'Email or password is incorrect'
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                username = serializer.validated_data['email'],
                password = serializer.validated_data['password']
            )
            if user:
                refresh = TokenObtainPairSerializer.get_token(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
                }
                return Response(data, status=status.HTTP_200_OK)
            return Response({
                'error': 'Email or password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Đăng xuất người dùng bằng cách hủy bỏ refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            required=['refresh']
        ),
        responses={
            205: openapi.Response('Logout successful'),
            400: openapi.Response('Error occurred while logging out')
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message': 'Login successful'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
