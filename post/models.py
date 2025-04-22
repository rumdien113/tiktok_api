from django.db import models
import uuid
from user.models import User

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    media = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # Based on your SQL schema
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Based on your SQL schema
    
    def __str__(self):
        return f"Post by {self.user.username}"
