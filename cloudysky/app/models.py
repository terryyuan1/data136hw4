# app/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Usertype(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Users(models.Model):
    # Links your custom profile to the built-in User
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    usertype = models.ForeignKey(Usertype, on_delete=models.PROTECT)
    bio = models.TextField()
    avatar = models.ForeignKey(
        'Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_avatars'
    )

    def __str__(self):
        return self.user.username


class Post(models.Model):
    author      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    is_hidden   = models.BooleanField(default=False)
    hide_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Comment(models.Model):
    post        = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    is_hidden   = models.BooleanField(default=False)
    hide_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Media(models.Model):
    AVATAR        = 'avatar'
    POST_IMAGE    = 'post_image'
    COMMENT_IMAGE = 'comment_image'
    TYPE_CHOICES  = [
        (AVATAR, 'Avatar'),
        (POST_IMAGE, 'Post Image'),
        (COMMENT_IMAGE, 'Comment Image'),
    ]

    uploaded_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads'
    )
    media_type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default=AVATAR)
    file             = models.FileField(upload_to='media/')
    attached_post    = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='media'
    )
    attached_comment = models.ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='media'
    )
    uploaded_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} by {self.uploaded_by.username}"