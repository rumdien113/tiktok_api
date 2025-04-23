from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import UserSerializer
from .models import User

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lấy thông tin của người dùng hiện tại.",
        responses={
            200: 'User data retrieved successfully',
            401: 'Unauthorized'
        },
        security=[{'Bearer': []}],
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_description="Lấy thông tin người dùng. Nếu cung cấp ID, trả về thông tin của người dùng đó, nếu không sẽ trả về tất cả người dùng.",
        responses={
            200: 'User data retrieved successfully',
            404: 'User not found'
        }
    )
    def get(self, request, id=None):
        if id:
            try:
                user = User.objects.get(id=id)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_description="Cập nhật thông tin người dùng.",
        responses={
            200: 'User updated successfully',
            400: 'Invalid input data',
            404: 'User not found'
        }
    )
    def patch(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data  # Lấy dữ liệu đã serialize
            return Response({
                'code': 200,
                'message': 'ok',
                'user': user_data
            }, status=status.HTTP_200_OK)
        return Response({
            'code': 400,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_description="Xóa người dùng.",
        responses={
            200: 'User deleted successfully',
            404: 'User not found'
        }
    )
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)
