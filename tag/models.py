from django.db import models
import uuid

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
