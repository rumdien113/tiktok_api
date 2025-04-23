from django.urls import path
from .views import LikeCreateDestroyView, LikedUsersListView

urlpatterns = [
    path('<str:target_type>/<str:target_id>/like/', LikeCreateDestroyView.as_view(), name='like-create-destroy'),
    path('<str:target_type>/<str:target_id>/likes/', LikedUsersListView.as_view(), name='like-list'),
]
