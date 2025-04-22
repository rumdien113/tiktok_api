from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Like
from .serializers import LikeSerializer

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, target_id=None):
        if target_id:
            likes = Like.objects.filter(target_id=target_id)
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, target_id):
        try:
            like = Like.objects.get(target_id=target_id, user=request.user)
        except Like.DoesNotExist:
            return Response({
                'error': 'Like not found'
            }, status=status.HTTP_404_NOT_FOUND)
        like.delete()
        return Response({
            'message': 'Unlike successfully'
        }, status=status.HTTP_200_OK)
