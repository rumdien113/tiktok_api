from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Share
from .serializers import ShareSerializer, ShareCreateSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ShareViewSet(viewsets.ModelViewSet):
    queryset = Share.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return ShareCreateSerializer
        return ShareSerializer
    
    def get_queryset(self):
        queryset = Share.objects.all()
        user_id = self.request.query_params.get('user_id')
        post_id = self.request.query_params.get('post_id')
        
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        if post_id:
            queryset = queryset.filter(post__id=post_id)
            
        return queryset
