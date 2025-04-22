from django.db import models
import uuid
from user.models import User
from post.models import Post

class Share(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} shared {self.post.id}"
