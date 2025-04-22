from django.db import models

class ReportCounter(models.Model):
    TARGET_TYPE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('user', 'User')
    ]
    
    target_id = models.UUIDField()
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    count = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('target_id', 'target_type')
    
    def __str__(self):
        return f"{self.target_type} {self.target_id}: {self.count} reports"
