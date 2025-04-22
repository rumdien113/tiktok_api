from django.urls import path
from .views import LikeView

urlpatterns = [
    path('', LikeView.as_view()),
    path('<uuid:target_id>/', LikeView.as_view())
]

