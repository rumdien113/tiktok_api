from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  # Import IsAuthenticated

from .models import Comment
from .serializers import CommentSerializer

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Add permission check

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Add permission check
        

class CommentReplyListView(APIView):
    def get(self, request, parent_comment_id):
        replies = Comment.objects.filter(parent_comment_id=parent_comment_id)
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)

class CommentListViewByPost(generics.ListAPIView):
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated] # Optionally, require authentication to view comments

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)
