from django.urls import path
from drf_yasg.views import get_schema_view
from .views import UserView, CurrentUserView, UserSearchView

urlpatterns = [
    # path('', UserView.as_view(), name='user-list-create'),
    path('', CurrentUserView.as_view()),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('<str:id>/', UserView.as_view(), name='user-detail-update-delete'),
]
