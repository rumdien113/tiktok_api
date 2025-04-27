# serializers.py
from rest_framework import status
from rest_framework import serializers
from .models import Post # Assuming your Post model is in models.py
from user.serializers import UserSerializer # Keep existing import
# import requests
# import os
# import io # Import io
from ai_result.utils import process_and_upload_image, process_and_upload_video
from rest_framework.serializers import ValidationError
# Assuming your FastAPI AI service is running at this URL
# AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://192.168.1.32:3000") # **Update with your actual AI service URL**
# AI_SERVICE_URL="http://host.docker.internal:3000"

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
    media_file = serializers.FileField(write_only=True)
    description = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Post
        fields = ['description', 'media_file']

    def create(self, validated_data):
        media_file = validated_data.pop('media_file')
        description = validated_data.get('description', '')
        user = self.context['request'].user

        # Xác định loại file
        # Cân nhắc sử dụng thư viện như 'python-magic' để kiểm tra loại file đáng tin cậy hơn
        content_type = media_file.content_type
        if content_type.startswith('image'):
            file_type = 'image'
            process_func = process_and_upload_image
        elif content_type.startswith('video'):
            file_type = 'video'
            process_func = process_and_upload_video
        else:
            raise ValidationError("Loại file không được hỗ trợ.")


        try:
            # Gọi hàm xử lý và upload từ utils.py
            # Hàm này sẽ raise ValueError nếu có lỗi hoặc nội dung bạo lực
            media_url = process_func(media_file)

            # Tạo đối tượng Post với URL media nhận được
            post = Post.objects.create(user=user, description=description, media=media_url)
            return post

        except ValueError as e:
            # Bắt lỗi từ hàm xử lý (bao gồm lỗi bạo lực) và trả về lỗi xác thực
            raise ValidationError({'media_file': [str(e)]})
        except Exception as e:
            # Bắt các lỗi không mong muốn khác
             raise ValidationError({'non_field_errors': [f"Đã xảy ra lỗi không mong muốn trong quá trình tạo bài đăng: {e}"]})

