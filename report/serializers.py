from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Report
        fields = ['id', 'target_id', 'target_type', 'user', 'reason', 'created_at', 'status']
        read_only_fields = ['id', 'user', 'created_at', 'status']

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['target_id', 'target_type', 'reason']

    def validate_target_type(self, value):
        valid_types = ['post', 'comment', 'user']
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid target_type. Must be one of: {', '.join(valid_types)}")
        return value

    def validate(self, data):
        target_type = data.get('target_type')
        target_id = data.get('target_id')

        if target_type == 'post':
            try:
                from posts.models import Post
                Post.objects.get(id=target_id)
            except ImportError:
                raise serializers.ValidationError("Post model not found. Ensure 'posts' app is installed.")
            except Post.DoesNotExist:
                raise serializers.ValidationError(f"Post with id {target_id} does not exist.")
        elif target_type == 'comment':
            try:
                from comments.models import Comment
                Comment.objects.get(id=target_id)
            except ImportError:
                raise serializers.ValidationError("Comment model not found. Ensure 'comments' app is installed.")
            except Comment.DoesNotExist:
                raise serializers.ValidationError(f"Comment with id {target_id} does not exist.")
        elif target_type == 'user':
            try:
                from user.models import User
                User.objects.get(id=target_id)
            except ImportError:
                raise serializers.ValidationError("User model not found. Ensure 'user' app is installed.")
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with id {target_id} does not exist.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        report = Report.objects.create(user=user, **validated_data)

        # Update or create report counter
        from report_counter.models import ReportCounter
        target_id = validated_data.get('target_id')
        target_type = validated_data.get('target_type')

        counter, created = ReportCounter.objects.get_or_create(
            target_id=target_id,
            target_type=target_type,
            defaults={'count': 1}
        )

        if not created:
            counter.count += 1
            counter.save()

        return report
