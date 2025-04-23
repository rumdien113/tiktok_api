from django.urls import path
from drf_yasg.views import get_schema_view
from .views import UserView, CurrentUserView

urlpatterns = [
    path('', UserView.as_view(), name='user-list-create'),
    path('current-user/', CurrentUserView.as_view()),
    path('<str:id>/', UserView.as_view(), name='user-detail-update-delete'),
]
