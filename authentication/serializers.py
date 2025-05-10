from rest_framework import serializers
from user.models import User # Import model User
from django.core.exceptions import ObjectDoesNotExist

class RequestEmailVerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("Tài khoản này đã được xác thực.")
            return value
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Không tìm thấy người dùng với email này.")

class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')

        if not email or not otp_code:
            raise serializers.ValidationError("Cần cung cấp email và mã OTP.")

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Không tìm thấy người dùng với email này.")

        if user.is_verified:
             raise serializers.ValidationError("Tài khoản này đã được xác thực.")

        if not user.is_otp_valid(otp_code):
             raise serializers.ValidationError("Mã OTP không hợp lệ hoặc đã hết hạn.")

        data['user'] = user # Lưu đối tượng user vào validated_data
        return data

class RequestPasswordResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Không tìm thấy người dùng với email này.")
        return value

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True) # Mật khẩu mới
    confirm_new_password = serializers.CharField(min_length=8, write_only=True) # Xác nhận mật khẩu mới

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if not email or not otp_code or not new_password or not confirm_new_password:
            raise serializers.ValidationError("Vui lòng điền đầy đủ các trường.")

        if new_password != confirm_new_password:
            raise serializers.ValidationError("Mật khẩu mới và xác nhận mật khẩu không khớp.")

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Không tìm thấy người dùng với email này.")

        # Kiểm tra OTP
        if not user.is_otp_valid(otp_code):
            raise serializers.ValidationError("Mã OTP không hợp lệ hoặc đã hết hạn.")

        data['user'] = user # Lưu đối tượng user vào validated_data để sử dụng trong view
        return data
