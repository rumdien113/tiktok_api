from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Post
from .serializers import PostSerializer, PostCreateSerializer
from django.db.models import Q

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['description']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get posts from followed users and the requesting user"""
        user = request.user
        # Get list of followed users' IDs
        from follows.models import Follow
        followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
        
        # Get posts from followed users and the user's own posts
        posts = Post.objects.filter(
            Q(user__in=followed_users) | Q(user=user)
        ).order_by('-created_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_posts(self, request):
        """Get posts from a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        posts = Post.objects.filter(user__id=user_id).order_by('-created_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
