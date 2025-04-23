from django.urls import path
from .views import ReportListView, ReportCreateView, ReportDetailView

urlpatterns = [
    path('', ReportListView.as_view(), name='report-list'),
    path('create/', ReportCreateView.as_view(), name='report-create'),
    path('<uuid:pk>/', ReportDetailView.as_view(), name='report-detail'),
]
