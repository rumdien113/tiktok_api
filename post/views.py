from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random

from .models import Post
from .serializers import PostSerializer, PostCreateSerializer
from user.models import User  # Import User model

class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="List all posts.",
        responses={
            200: openapi.Response("A list of posts.", PostSerializer(many=True)),
        }
    )
    def get(self, request):
        if request.user.is_authenticated:
            posts = Post.objects.filter(user=request.user)
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description="Create a new post.",
        request_body=PostCreateSerializer,
        responses={
            201: openapi.Response("Post created successfully.", PostSerializer),
            400: "Bad Request",
        },
        security=[{'Bearer': []}]
    )
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPostListView(APIView):
    @swagger_auto_schema(
        operation_description="Get all posts by a specific user.",
        responses={
            200: openapi.Response("List of posts by user.", PostSerializer(many=True)),
            404: "User not found",
        }
    )
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            posts = Post.objects.filter(user=user)
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class PostDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a single post by ID.",
        responses={
            200: openapi.Response("Post details.", PostSerializer),
            404: "Post not found.",
        }
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a post by ID.",
        request_body=PostCreateSerializer,  # Or a PostUpdateSerializer if needed
        responses={
            200: openapi.Response("Post updated.", PostSerializer),
            400: "Bad Request",
            403: "Not allowed to update this post.",
            404: "Post not found.",
        },
        security=[{'Bearer': []}]
    )
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.user != request.user:
            return Response({"detail": "Not allowed to update this post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostCreateSerializer(post, data=request.data)  # Or PostUpdateSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Partially update a post by ID.",
        request_body=PostCreateSerializer,  # Or a PostUpdateSerializer if needed
        responses={
            200: openapi.Response("Post updated.", PostSerializer),
            400: "Bad Request",
            403: "Not allowed to update this post.",
            404: "Post not found.",
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.user != request.user:
            return Response({"detail": "Not allowed to update this post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostCreateSerializer(post, data=request.data, partial=True)  # Or PostUpdateSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a post by ID.",
        responses={
            204: "Post deleted successfully.",
            403: "Not allowed to delete this post.",
            404: "Post not found.",
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.user != request.user:
            return Response({"detail": "Not allowed to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({"detail": "Post deleted successfully."}, status=status.HTTP_200_OK)  # Thay đổi từ 204 thành 200

NUM_RANDOM_POSTS = 3

class RandomPostView(APIView):
    # Cân nhắc thêm permission nếu chỉ user đăng nhập mới cần check is_liked
    # permission_classes = [IsAuthenticatedOrReadOnly] # Cho phép xem nhưng chỉ user đăng nhập mới check được is_liked

    @swagger_auto_schema(
        # Cập nhật lại mô tả và response cho đúng là list các post
        operation_description=f"Get up to {NUM_RANDOM_POSTS} random posts for a frontend queue.",
        responses={
            200: openapi.Response(f"A list of up to {NUM_RANDOM_POSTS} random posts.", PostSerializer(many=True)),
            404: "No posts available.",
        }
    )

    def get(self, request):
        # Lấy danh sách tất cả các ID một cách hiệu quả
        post_ids = list(Post.objects.values_list('id', flat=True))

        posts_count = len(post_ids)

        if posts_count == 0:
            return Response({"detail": "No posts available."}, status=status.HTTP_404_NOT_FOUND)

        # Xác định số lượng post thực tế cần lấy
        num_to_sample = min(posts_count, NUM_RANDOM_POSTS)

        # Chọn ngẫu nhiên các ID từ danh sách
        random_ids = random.sample(post_ids, num_to_sample)

        # Fetch các post tương ứng với các ID đã chọn
        random_posts_queryset = Post.objects.filter(id__in=random_ids)

        # Serialize danh sách các post
        # Phải thêm many=True khi serialize nhiều đối tượng
        # SỬA LỖI is_liked tại đây: Thêm context={'request': request}
        serializer = PostSerializer(random_posts_queryset, many=True, context={'request': request}) # <-- ĐÃ SỬA

        # Trả về danh sách dữ liệu post
        return Response(serializer.data)

class PostSearchView(APIView):
    """
    API view to search for posts by description.
    """
    # Quyền truy cập: cho phép bất kỳ ai (đăng nhập hoặc không) xem kết quả tìm kiếm
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Search for posts by description.",
        manual_parameters=[
            openapi.Parameter(
                'query', # Tên query parameter, bạn có thể dùng 'description' nếu muốn
                openapi.IN_QUERY,
                description="Search term for post description (case-insensitive partial match).",
                type=openapi.TYPE_STRING,
                required=True # Tham số tìm kiếm là bắt buộc cho API search này
            ),
        ],
        responses={
            200: openapi.Response(
                description="A list of posts matching the search query.",
                # Sử dụng PostSerializer cho danh sách các post
                schema=PostSerializer(many=True)
            ),
            400: "Bad Request (if query parameter is missing)",
        },
         # Thêm security nếu chỉ user đăng nhập mới được search
        # security=[{'Bearer': []}]
    )
    def get(self, request):
        search_query = request.query_params.get('query', None) # Lấy query parameter tên là 'query'

        if not search_query:
            # Trả về lỗi nếu thiếu tham số tìm kiếm
            return Response({'query': ['This query parameter is required for search.']}, status=status.HTTP_400_BAD_REQUEST)

        # Thực hiện tìm kiếm trong trường description (không phân biệt hoa thường, chứa chuỗi)
        posts = Post.objects.filter(description__icontains=search_query)

        # Serialize kết quả tìm kiếm
        # Truyền context để PostSerializer có thể xác định is_liked
        serializer = PostSerializer(posts, many=True, context={'request': request})

        # Trả về danh sách các bài đăng tìm thấy
        return Response(serializer.data, status=status.HTTP_200_OK)
