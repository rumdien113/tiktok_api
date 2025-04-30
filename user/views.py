from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from .serializers import UserSerializer, PasswordChangeSerializer
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

    @swagger_auto_schema(
        operation_description="Cập nhật thông tin người dùng hiện tại.",
        request_body=UserSerializer,
        responses={
            200: 'User updated successfully',
            400: 'Invalid input data',
            401: 'Unauthorized'
        },
        security=[{'Bearer': []}],
    )
    def patch(self, request):
        user = request.user  # Get the current authenticated user

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data
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
        operation_description="Thay đổi mật khẩu của người dùng hiện tại.",
        request_body=PasswordChangeSerializer,
        responses={
            200: 'Password changed successfully',
            400: 'Invalid input data or old password incorrect',
            401: 'Unauthorized'
        },
        security=[{'Bearer': []}],
    )
    def put(self, request): # Using PUT for full update of password
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({
                    'code': 400,
                    'message': 'Mật khẩu cũ không đúng.'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({
                'code': 200,
                'message': 'Đổi mật khẩu thành công.'
            }, status=status.HTTP_200_OK)
        return Response({
            'code': 400,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated] # Keep IsAuthenticated for other methods if needed

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_description="Lấy thông tin người dùng theo ID.",
        # Thêm định nghĩa tường minh cho tham số ID trong path
        manual_parameters=[
            openapi.Parameter(
                'id', # Tên tham số phải khớp với tên trong URL pattern
                openapi.IN_PATH,
                description="UUID của người dùng cần lấy thông tin chi tiết",
                type=openapi.TYPE_STRING, # Hoặc openapi.TYPE_INTEGER nếu ID là int
                format=openapi.FORMAT_UUID, # Sử dụng format UUID nếu ID là UUID
                required=True # Tham số path luôn là bắt buộc
            ),
        ],
        responses={
            200: openapi.Response('User data retrieved successfully', UserSerializer), # Sử dụng serializer để mô tả response
            404: 'User not found',
            401: 'Unauthorized'
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

    # @swagger_auto_schema(
    #     security=[{'Bearer': []}],
    #     operation_description="Xóa người dùng.",
    #     responses={
    #         200: 'User deleted successfully',
    #         404: 'User not found'
    #     }
    # )
    # def delete(self, request, id):
    #     try:
    #         user = User.objects.get(id=id)
    #     except ObjectDoesNotExist:
    #         return Response({
    #             'error': 'User not found'
    #         }, status=status.HTTP_404_NOT_FOUND)
    #     user.delete()
    #     return Response({
    #         'message': 'User deleted successfully'
    #     }, status=status.HTTP_200_OK)

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_description="Tìm kiếm người dùng theo username.",
        manual_parameters=[
             openapi.Parameter(
                'username',
                openapi.IN_QUERY,
                description="Username để tìm kiếm (tìm kiếm gần đúng)",
                type=openapi.TYPE_STRING,
                required=True # Tham số tìm kiếm là bắt buộc cho API search này
            ),
        ],
        responses={
            200: openapi.Response(
                description="Danh sách người dùng tìm thấy.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=UserSerializer # Mảng các UserSerializer
                )
            ),
            401: 'Unauthorized',
            400: 'Bad Request' # Nếu thiếu tham số username
        }
    )
    def get(self, request):
        username_query = request.query_params.get('username', None)

        if not username_query:
             return Response({'username': ['This query parameter is required for search.']}, status=status.HTTP_400_BAD_REQUEST)

        # Tìm kiếm username chứa chuỗi username_query (không phân biệt hoa thường)
        users = User.objects.filter(username__icontains=username_query)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
