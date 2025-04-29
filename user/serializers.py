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

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstname', 'lastname',
                  'birthdate', 'phone', 'gender', 'avatar', 'bio', 'avatar_file']
        read_only_fields = ['id', 'username', 'email']

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
 
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
