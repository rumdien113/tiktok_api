import uuid
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from user.serializers import UserSerializer # Keep existing import
from post.models import Post
from user.models import User
from like.models import Like
from .models import Comment
from ai_result.utils import analyze_comment_text
import logging
logger = logging.getLogger(__name__)

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.CharField(write_only=True)
    parent_comment = serializers.CharField(write_only=True, required=False, allow_null=True)
    parent_comment_id = serializers.UUIDField(source='parent_comment.id', read_only=True)
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent_comment', 'parent_comment_id', 'content', 'is_liked', 'likes_count', 'create_at', 'updated_at'] # Remove 'user'

    def get_is_liked(self, obj):
        """
        Kiểm tra xem người dùng đang request đã like comment này hay chưa.
        """
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            # Kiểm tra trong bảng Like
            return Like.objects.filter(
                user=request.user,     # Người dùng hiện tại
                target_id=obj.id,      # ID của comment
                target_type='comment'  # Loại đối tượng là comment
            ).exists()
        return False # Trả về False nếu không có request hoặc người dùng chưa đăng nhập

    def get_likes_count(self, obj):
        """
        Đếm số lượng like cho comment này.
        """
        # Đếm trong bảng Like
        return Like.objects.filter(
            target_id=obj.id,     # ID của comment
            target_type='comment'  # Loại đối tượng là comment
        ).count()

    def get_object_by_id(self, model, obj_id, field_name):
        try:
            uuid.UUID(str(obj_id))
        except ValueError:
            raise serializers.ValidationError({field_name: 'Invalid UUID format'})
        
        try:
            return model.objects.get(id=obj_id)
        except model.DoesNotExist:
            raise serializers.ValidationError({field_name: f'{model.__name__} not found'})

    def create(self, validated_data):
        # Lấy nội dung comment từ validated_data
        comment_content = validated_data.get('content')
        logger.info(f"Processing comment creation for content: '{comment_content[:50]}...'")

        # --- Gọi hàm phân tích văn bản AI và xử lý kết quả ---
        if comment_content: # Chỉ kiểm tra AI nếu nội dung comment không rỗng
            try:
                # Gọi hàm phân tích văn bản. Nó trả về status và message.
                status_code, message = analyze_comment_text(comment_content)

                if status_code == 1: # Nội dung không phù hợp
                    logger.warning(f"Comment content flagged by AI: {message}")
                    # Raise ValidationError liên kết với trường 'content'
                    raise ValidationError({'content': [message]})

                elif status_code == -1: # Hệ thống AI chưa sẵn sàng
                    logger.error(f"AI text analysis system not ready: {message}")
                    # Raise ValidationError liên kết với trường 'content'
                    raise ValidationError({'content': [message]})

                elif status_code == -2: # Lỗi xử lý trong AI
                    logger.error(f"AI text analysis processing error: {message}")
                     # Raise ValidationError liên kết với trường 'content'
                    raise ValidationError({'content': [message]})

                # Nếu status_code là 0, tức là hợp lệ, không làm gì cả và tiếp tục
                logger.info("Comment content passed AI analysis.")

            except ValidationError:
                # Bắt các ValidationError mà chúng ta cố tình raise bên trong khối try
                # và re-raise chúng để DRF xử lý đúng.
                raise

            except Exception as e:
                 # Bắt các lỗi không mong muốn khác xảy ra trong quá trình gọi analyze_comment_text
                 # Những lỗi này không phải do kết quả phân tích, mà là lỗi kỹ thuật
                 logger.error(f"Unexpected error during AI text analysis call: {e}", exc_info=True)
                 # Đây là lỗi thực sự không mong muốn, nên non_field_errors là phù hợp.
                 raise ValidationError({'non_field_errors': [f'Đã xảy ra lỗi không mong muốn khi kiểm tra comment: {e}']})
        else:
            logger.info("Comment content is empty, skipping AI analysis.")
        # -------------------------------------------------


        # Tiếp tục logic tạo comment nếu AI kiểm tra thành công (status_code == 0)
        post = self.get_object_by_id(Post, validated_data.pop('post'), 'post')

        parent_comment = validated_data.pop('parent_comment', None)
        parent_comment_obj = None

        if parent_comment:
            parent_comment_obj = self.get_object_by_id(Comment, parent_comment, 'parent_comment')

        # Gán user từ request (đã được xử lý bởi CommentListCreateView.perform_create)
        # validated_data['user'] = user # Dòng này không cần thiết nếu perform_create xử lý user

        validated_data['post'] = post
        validated_data['parent_comment'] = parent_comment_obj

        # Tạo đối tượng Comment
        return Comment.objects.create(**validated_data)
