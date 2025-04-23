from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer

class ReportListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReportDetailView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]
