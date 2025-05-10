from django.urls import path
from .views import RegisterView, LoginView, LogoutView, RequestEmailVerificationOTPView, VerifyEmailOTPView, RequestPasswordResetOTPView, ResetPasswordConfirmView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('request-email-otp/', RequestEmailVerificationOTPView.as_view(), name='request_email_otp'), # URL mới
    path('verify-email-otp/', VerifyEmailOTPView.as_view(), name='verify_email_otp'), # URL mới
    path('request-password-reset-otp/', RequestPasswordResetOTPView.as_view(), name='request_password_reset_otp'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
]
