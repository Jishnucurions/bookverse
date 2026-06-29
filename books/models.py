from django.db import models
from django.contrib.auth.models import User

class SavedBook(models.Model):
    STATUS_CHOICES = [
        ('to_read', 'To Read'),
        ('reading', 'Currently Reading'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_books')
    work_key = models.CharField(max_length=100) # Open Library Work Key, e.g. "OL82586W"
    title = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255, blank=True, null=True)
    cover_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_read')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'work_key')

    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.status})"
