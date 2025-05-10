from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp_code, subject="Mã xác thực tài khoản của bạn", message_template="Mã xác thực tài khoản của bạn là: {otp_code}"):
    """Gửi email chứa mã OTP."""
    message = message_template.format(otp_code=otp_code)
    try:
        print(f"DEBUG: Đang cố gắng gửi email từ '{settings.EMAIL_HOST_USER}' đến '{email}'")
        print(f"DEBUG: Mã OTP: {otp_code}")

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, # Địa chỉ email gửi đi từ settings.py
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}") # Log lỗi chi tiết hơn trong thực tế
        return False
