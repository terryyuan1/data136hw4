# cloudsky/app/models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author      = models.ForeignKey(User, on_delete=models.CASCADE)
    title       = models.CharField(max_length=255)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    hidden      = models.BooleanField(default=False)
    hide_reason = models.TextField(blank=True, null=True)

class Comment(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    post        = models.ForeignKey(Post, on_delete=models.CASCADE)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    hidden      = models.BooleanField(default=False)
    hide_reason = models.TextField(blank=True, null=True)
