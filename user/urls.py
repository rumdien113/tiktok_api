from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UserView, CurrentUserView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('', UserView.as_view()),
    path('<uuid:id>/', UserView.as_view()),
    path('current-user/', CurrentUserView.as_view()),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
