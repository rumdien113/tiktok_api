from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Like
from .serializers import LikeSerializer, LikeCreateSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class LikeViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LikeCreateSerializer
        return LikeSerializer
    
    def get_queryset(self):
        """Filter likes by target_id and target_type if provided"""
        queryset = Like.objects.all()
        target_id = self.request.query_params.get('target_id')
        target_type = self.request.query_params.get('target_type')
        
        if target_id and target_type:
            queryset = queryset.filter(target_id=target_id, target_type=target_type)
        elif target_id:
            queryset = queryset.filter(target_id=target_id)
        elif target_type:
            queryset = queryset.filter(target_type=target_type)
            
        return queryset
    
    @action(detail=False, methods=['delete'])
    def unlike(self, request):
        """Remove a like by target_id and target_type"""
        target_id = request.query_params.get('target_id')
        target_type = request.query_params.get('target_type')
        
        if not target_id or not target_type:
            return Response(
                {"error": "Both target_id and target_type are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            like = Like.objects.get(
                user=request.user,
                target_id=target_id,
                target_type=target_type
            )
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(
                {"error": "Like does not exist"}, 
                status=status.HTTP_404_NOT_FOUND
            )
