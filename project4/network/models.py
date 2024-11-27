from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content =models.CharField(max_length=200)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="author")
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} was made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
class Follow(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="following_user")
    followeruser=models.ForeignKey(User,on_delete=models.CASCADE,related_name="follower_user")

    def __str__(self):
        return f"{self.followeruser} is following{self.user} "

class Like(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_like")
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="liked_post")
    def __str__(self):
        return f"{self.user} liked{self.post} "

