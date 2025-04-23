from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Follow
from .serializers import FollowSerializer, FollowCreateSerializer
from user.models import User

class IsFollowerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.follower == request.user

class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsFollowerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FollowCreateSerializer
        return FollowSerializer
    
    def get_queryset(self):
        queryset = Follow.objects.all()
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            # Get followers or following list for specific user
            type_param = self.request.query_params.get('type', 'following')
            if type_param == 'followers':
                queryset = queryset.filter(followed__id=user_id)
            else:  # default to 'following'
                queryset = queryset.filter(follower__id=user_id)
                
        return queryset
    
    @action(detail=False, methods=['delete'])
    def unfollow(self, request):
        """Unfollow a user by their ID"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            follow = Follow.objects.get(follower=request.user, followed__id=user_id)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                {"error": "You are not following this user"}, 
                status=status.HTTP_404_NOT_FOUND
            )
