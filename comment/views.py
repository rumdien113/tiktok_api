from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from comment.models import Comment
from .serializers import CommentSerializer

class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, id=None):
        if id:
            try:
                comment = Comment.objects.get(id=id)
                serializer = CommentSerializer(comment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Comment.DoesNotExist:
                return Response({
                    'error': 'Comment not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def patch(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return Response({
                'error': 'Comment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return Response({
                'error': 'Comment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response({
            'message': 'Comment deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
