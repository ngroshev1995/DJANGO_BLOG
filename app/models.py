from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(args, kwargs)
    #     self.likes = None

    def __str__(self):
        return self.title

    def get_like_count(self):
        return self.likes.count()

    def user_liked(self, user):
        return self.likes.filter(user=user).exists()

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}."