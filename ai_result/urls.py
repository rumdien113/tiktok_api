from django.urls import path
from . import views

urlpatterns = [
    path('predict_text/', views.predict_text, name='predict_text'),
    path('check_video/', views.check_video, name='check_video'),
    path('check_image/', views.check_image, name='check_image'),
]
