from django.db import models
import uuid
from post.models import Post
from tag.models import Tag

class PostTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='posts')
    
    class Meta:
        unique_together = ('post', 'tag')
    
    def __str__(self):
        return f"{self.post.id} - {self.tag.name}"
