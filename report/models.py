from django.db import models
import uuid
from user.models import User

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected')
    ]
    
    TARGET_TYPE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('user', 'User')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    target_id = models.UUIDField()
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Report on {self.target_type} {self.target_id} by {self.user.username}"
