from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Like
from .serializers import LikeSerializer, LikeCreateSerializer

class LikeCreateDestroyView(generics.CreateAPIView,
                           generics.DestroyAPIView):
    """
    Create a like or unlike (delete) a post or comment.
    """
    serializer_class = LikeCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'target_id'  # Use target_id for delete

    def get_queryset(self):
        target_id = self.kwargs['target_id']
        target_type = self.kwargs['target_type']
        return Like.objects.filter(user=self.request.user, target_id=target_id, target_type=target_type)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "Liked successfully."}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "You haven't liked this item yet."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(queryset.first())
        return Response({"detail": "Unliked successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    

class LikedUsersListView(generics.ListAPIView):
    """
    Get all users who liked a specific post or comment.
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]  # Or AllowAny, depending on your requirements

    def get_queryset(self):
        target_id = self.kwargs['target_id']
        target_type = self.kwargs['target_type']
        return Like.objects.filter(target_id=target_id, target_type=target_type)
