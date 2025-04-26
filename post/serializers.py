# serializers.py

from rest_framework import serializers
from .models import Post # Assuming your Post model is in models.py
from user.serializers import UserSerializer # Keep existing import
import requests
import os
import io # Import io

# Assuming your FastAPI AI service is running at this URL
# AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://192.168.1.32:3000") # **Update with your actual AI service URL**
AI_SERVICE_URL="http://host.docker.internal:3000"

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'media', 'description', 'created_at', 'updated_at',
                 'likes_count', 'comments_count', 'shares_count']

    def get_likes_count(self, obj):
        # Import inside method to avoid circular imports
        from like.models import Like
        return Like.objects.filter(target_id=obj.id, target_type='post').count()

    def get_comments_count(self, obj):
        # Import inside method to avoid circular imports
        from comment.models import Comment
        return Comment.objects.filter(post=obj).count()

    def get_shares_count(self, obj):
        # Import inside method to avoid circular imports
        from share.models import Share
        return Share.objects.filter(post=obj).count()

class PostCreateSerializer(serializers.ModelSerializer):
    # Add a field for file upload. It's write_only as we will save the URL to the 'media' field
    media_file = serializers.FileField(write_only=True)
    # Keep description field for text content
    description = serializers.CharField(allow_blank=True, required=False)


    class Meta:
        model = Post
        # We will handle 'media' through media_file upload and AI response
        fields = ['description', 'media_file'] # Include media_file for input

    def create(self, validated_data):
        media_file = validated_data.pop('media_file')
        # description is optional
        description = validated_data.get('description', '')
        user = self.context['request'].user

        # Determine if it's an image or video based on content type
        # You might need a more robust way to check file type, e.g., using python-magic
        if media_file.content_type.startswith('image'):
            ai_endpoint = f'{AI_SERVICE_URL}/check_image/'
            file_type = 'image'
        elif media_file.content_type.startswith('video'):
            ai_endpoint = f'{AI_SERVICE_URL}/check_video/'
            file_type = 'video'
        else:
            raise serializers.ValidationError("Unsupported file type.")

        # Prepare the file for sending to the AI service
        # Use io.BytesIO to make the InMemoryUploadedFile seekable if needed by requests,
        # although requests.post with files handles file-like objects well.
        # Ensure the file pointer is at the beginning
        media_file.file.seek(0)
        files = {'file': (media_file.name, media_file.file, media_file.content_type)}

        try:
            # Call the AI service
            response = requests.post(ai_endpoint, files=files)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            ai_response_data = response.json()

            if response.status_code == 200:
                # Media is valid, get the URL from the AI response
                if file_type == 'image':
                    media_url = ai_response_data.get('image_url')
                else: # file_type == 'video'
                    media_url = ai_response_data.get('video_url')

                if not media_url:
                     # This case might happen if AI returns 200 but no URL for some reason
                     raise serializers.ValidationError("AI service did not return a media URL.")

                # Create the post with the description and media URL
                # The media URL is saved in the 'media' field of the Post model
                post = Post.objects.create(user=user, description=description, media=media_url)
                return post

            # AI service returns 400 if content is invalid
            elif response.status_code == 400:
                message = ai_response_data.get('message', 'Media violates standards.')
                raise serializers.ValidationError({'media_file': [message]}) # Link error to media_file field

            else:
                # Handle other potential error codes from AI service
                error_message = ai_response_data.get('detail', f"AI service returned an unexpected status code: {response.status_code}")
                raise serializers.ValidationError({'non_field_errors': [f"AI service error: {error_message}"]})


        except requests.exceptions.RequestException as e:
            # Handle errors during the request to the AI service (network issues, connection refused, etc.)
            raise serializers.ValidationError({'non_field_errors': [f"Error communicating with AI service: {e}"]})
        except Exception as e:
            # Handle any other unexpected errors during the process
            raise serializers.ValidationError({'non_field_errors': [f"An unexpected error occurred during post creation: {e}"]})
