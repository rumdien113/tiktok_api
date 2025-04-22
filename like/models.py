from django.db import models
import uuid

from user.models import User

class Like(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_id = models.UUIDField()
    target_type = models.CharField(max_length=10, choices=[('post', 'Post'), ('comment', 'Comment')])

    def __str__(self):
        return self.target_id

    class Meta: 
        unique_together = ('user', 'target_id', 'target_type')
