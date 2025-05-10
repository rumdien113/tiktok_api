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

from tiktok_api import settings # Giữ lại import này nếu cần các cài đặt khác từ settings
from user.serializers import UserCreateSerializer, UserLoginSerializer # Giữ lại import này
from user.models import User # Giữ lại import này
from .utils import send_otp_email # Import hàm gửi email
from .serializers import RequestEmailVerificationOTPSerializer, VerifyEmailOTPSerializer, RequestPasswordResetOTPSerializer, ResetPasswordConfirmSerializer

class RegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Đăng ký người dùng mới.",
        request_body=UserCreateSerializer,
        responses={
            201: openapi.Response('User registered successfully'),
            400: openapi.Response('Invalid input data', UserCreateSerializer),
            500: 'Error sending verification email'
        }
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Đặt is_verified = False mặc định (nếu chưa có trong model, cần thêm vào serializer create method)
            # Tuy nhiên, cách tốt nhất là đặt default=False trong model.
            user = serializer.save(password=make_password(serializer.validated_data['password'])) # Lưu người dùng

            # Tạo và gửi OTP
            otp = user.generate_otp()
            email_sent = send_otp_email(user.email, otp)

            if email_sent:
                return Response({
                    'message': 'Đăng ký thành công. Vui lòng kiểm tra email để xác thực tài khoản.'
                }, status=status.HTTP_201_CREATED)
            else:
                # Xử lý trường hợp gửi email thất bại (tùy chọn: xóa user hoặc đánh dấu cần gửi lại email)
                # Tạm thời trả về lỗi, trong thực tế nên xử lý mềm hơn.
                user.delete() # Hoặc đánh dấu để gửi lại sau
                return Response({
                    'error': 'Đăng ký thành công nhưng không gửi được email xác thực. Vui lòng thử lại sau.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class RequestEmailVerificationOTPView(APIView):
    @swagger_auto_schema(
        operation_description="Yêu cầu gửi lại mã OTP xác thực email.",
        request_body=RequestEmailVerificationOTPSerializer,
        responses={
            200: 'OTP sent successfully',
            400: 'Invalid input or user already verified',
            404: 'User not found',
            500: 'Error sending email'
        }
    )
    def post(self, request):
        serializer = RequestEmailVerificationOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email) # Đã kiểm tra sự tồn tại trong serializer validate

            otp = user.generate_otp()
            email_sent = send_otp_email(user.email, otp)

            if email_sent:
                return Response({
                    'message': 'Mã OTP đã được gửi lại. Vui lòng kiểm tra email của bạn.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                     'error': 'Không gửi được email xác thực. Vui lòng thử lại sau.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailOTPView(APIView):
    @swagger_auto_schema(
        operation_description="Xác thực mã OTP để hoàn tất đăng ký.",
        request_body=VerifyEmailOTPSerializer,
        responses={
            200: 'Email verified successfully',
            400: 'Invalid input or OTP invalid/expired'
        }
    )
    def post(self, request):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user'] # Lấy user từ validated_data

            user.is_verified = True
            user.clear_otp() # Xóa OTP sau khi xác thực thành công
            user.save()

            return Response({
                'message': 'Xác thực email thành công. Tài khoản của bạn đã sẵn sàng.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetOTPView(APIView):
    @swagger_auto_schema(
        operation_description="Yêu cầu gửi mã OTP để đặt lại mật khẩu.",
        request_body=RequestPasswordResetOTPSerializer,
        responses={
            200: 'OTP for password reset sent successfully',
            400: 'Invalid input or user not found',
            500: 'Error sending email'
        }
    )
    def post(self, request):
        serializer = RequestPasswordResetOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email) # Đã được validate là có tồn tại trong serializer

            otp = user.generate_otp()
            # Sử dụng subject và message_template riêng cho quên mật khẩu
            email_sent = send_otp_email(
                user.email,
                otp,
                subject="Mã OTP đặt lại mật khẩu của bạn",
                message_template="Mã OTP để đặt lại mật khẩu của bạn là: {otp_code}. Mã này có hiệu lực trong 5 phút."
            )

            if email_sent:
                return Response({
                    'message': 'Mã OTP đặt lại mật khẩu đã được gửi đến email của bạn.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                     'error': 'Không gửi được email đặt lại mật khẩu. Vui lòng thử lại sau.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View để xác nhận OTP và đặt mật khẩu mới
class ResetPasswordConfirmView(APIView):
    @swagger_auto_schema(
        operation_description="Xác nhận mã OTP và đặt lại mật khẩu mới.",
        request_body=ResetPasswordConfirmSerializer,
        responses={
            200: 'Password reset successfully',
            400: 'Invalid input or OTP invalid/expired'
        }
    )
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user'] # Lấy user từ validated_data
            new_password = serializer.validated_data['new_password']

            user.set_password(new_password) # Đặt mật khẩu mới
            user.clear_otp() # Xóa OTP sau khi sử dụng thành công
            user.save()

            return Response({
                'message': 'Mật khẩu của bạn đã được đặt lại thành công.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
