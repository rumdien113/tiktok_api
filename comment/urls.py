from django.urls import path
from .views import CommentView

urlpatterns = [
    path('', CommentView.as_view()),
    path('<uuid:id>/', CommentView.as_view())
]

