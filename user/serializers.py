from rest_framework import status
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import User
from ai_result.utils import process_and_upload_image, process_and_upload_video
import logging

logger = logging.getLogger(__name__)

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UserSerializer(serializers.ModelSerializer):
    avatar_file = serializers.FileField(write_only=True, required=False, allow_null=True)

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    total_likes_on_posts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstname', 'lastname',
                  'birthdate', 'phone', 'gender', 'avatar', 'bio', 'avatar_file', 'followers_count', 'following_count', 'total_likes_on_posts']
        read_only_fields = ['id', 'email']

    def update(self, instance, validated_data):
        avatar_file = validated_data.pop('avatar_file', None)
        if avatar_file:
            if not avatar_file.content_type.startswith('image'):
                logger.warning(f"Invalid file type for avatar: {avatar_file.content_type}")
                raise ValidationError({'avatar_file': ['Loai file avatar khong hop le. Chi chap nhan anh']})

            try:
                avatar_url = process_and_upload_image(avatar_file)
                instance.avatar = avatar_url
                logger.info(f"Instance avatar updated to URL: {instance.avatar}")

            except ValueError as e:
                logger.error(f"ValueError during avatar processing: {str(e)}")
                raise ValidationError({'avatar_file': [str(e)]})
            except Exception as e:
                logger.error(f"Unexpected error during avatar processing: {e}", exc_info=True)
                raise ValidationError({'non_field_errors': [f"Đã xảy ra lỗi không mong muốn khi cập nhật avatar: {e}"]})

        for attr, value in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, value)
            else:
                 logger.warning(f"Attempted to update non-existent field: {attr}")


        instance.save() 

        return instance

    # Phương thức để lấy số lượng người đang follow user này (người này là followed_id)
    def get_followers_count(self, obj):
        # Import model tại đây để tránh circular dependency
        from follow.models import Follow
        return Follow.objects.filter(followed_id=obj.id).count()

    # Phương thức để lấy số lượng user mà user này đang follow (người này là follower_id)
    def get_following_count(self, obj):
        # Import model tại đây để tránh circular dependency
        from follow.models import Follow
        return Follow.objects.filter(follower_id=obj.id).count()

    # Phương thức để lấy tổng số like trên tất cả các post của user này
    def get_total_likes_on_posts(self, obj):
        # Import models tại đây
        from post.models import Post
        from like.models import Like

        # Lấy danh sách ID của tất cả các bài post do user này tạo
        user_post_ids = Post.objects.filter(user_id=obj.id).values_list('id', flat=True)

        # Đếm tổng số like trên các bài post này
        # target_type='post' là cần thiết để đảm bảo chỉ đếm like của post
        return Like.objects.filter(target_id__in=list(user_post_ids), target_type='post').count()
 
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
