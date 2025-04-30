from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Follow
from .serializers import FollowSerializer, FollowerListSerializer, FollowingListSerializer
from user.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class FollowView(generics.CreateAPIView):
    """
    API view to follow a user.
    Requires authentication.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Follow a user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['followed'],
            properties={
                'followed': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the user to follow'),
            },
        ),
        responses={201: FollowSerializer, 400: "Bad Request", 401: "Unauthorized", 409: "Conflict", 404: "Not Found"}
    )
    def post(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed')
        if not followed_user_id:
            return Response({'followed': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({'followed': ['User not found.']}, status=status.HTTP_404_NOT_FOUND)

        if request.user == followed_user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already following
        if Follow.objects.filter(follower=request.user, followed=followed_user).exists():
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_409_CONFLICT)

        # Use serializer to create the follow instance, ensuring the follower is the requesting user
        serializer = self.get_serializer(data={'followed': followed_user_id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UnfollowView(APIView):
    """
    API view to unfollow a user.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Unfollow a user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['followed'],
            properties={
                'followed': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='UUID of the user to unfollow'),
            },
        ),
        responses={204: "No Content", 400: "Bad Request", 401: "Unauthorized", 404: "Not Found"}
    )
    def delete(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed')
        if not followed_user_id:
            return Response({'followed': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
             return Response({'followed': ['User not found.']}, status=status.HTTP_404_NOT_FOUND)


        follow_instance = get_object_or_404(Follow, follower=request.user, followed=followed_user)
        follow_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowerListView(generics.ListAPIView):
    """
    API view to list users who are following the current user.
    Requires authentication.
    """
    serializer_class = FollowerListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List users who are following the current user.",
        responses={200: FollowerListSerializer(many=True), 401: "Unauthorized"}
    )
    def get_queryset(self):
        # Get the current user's followers
        return Follow.objects.filter(followed=self.request.user)


class FollowingListView(generics.ListAPIView):
    """
    API view to list users that the current user is following.
    Requires authentication.
    """
    serializer_class = FollowingListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List users that the current user is following.",
        responses={200: FollowingListSerializer(many=True), 401: "Unauthorized"}
    )
    def get_queryset(self):
        # Get the users the current user is following
        return Follow.objects.filter(follower=self.request.user)

class CheckFollowStatusView(APIView):
    """
    API view to check if the current user is following a specific user.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Check if the current user is following a specific user.",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                description="UUID of the user to check follow status for",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful retrieval of follow status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_following': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if the current user is following the target user, false otherwise'),
                    }
                )
            ),
            401: "Unauthorized",
            404: "User not found"
        }
    )
    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        is_following = Follow.objects.filter(follower=request.user, followed=target_user).exists()
        return Response({'is_following': is_following}, status=status.HTTP_200_OK)
