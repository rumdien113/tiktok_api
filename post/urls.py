from django.urls import path
from .views import PostView

urlpatterns = [
    path('', PostView.as_view()),
    path('<uuid:id>/', PostView.as_view())
]

