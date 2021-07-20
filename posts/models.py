from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils import timezone
# Create your models here.

class Post(models.Model):
    post_content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

    def __str__(self):
        string = self.post_content[0:30]
        if len(string) == 30:
            string += "..."
        return f"{string}, Post ID: {self.id} for: {self.creator}"

class Comment(models.Model):
    comment_content = models.CharField(max_length=1000)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        comment = self.comment_content[0:10]
        if len(comment) > 10:
            comment += "..."
        return f"{comment}, Comment ID: {self.id} for: {self.creator}"


class Friend(models.Model):
    class Meta:
        unique_together = (('side1', 'side2'), )
        
    side1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Side1")
    side2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Side2")

    def __str__(self):
        return f"Friendship {self.side1.username} and {self.side2.username}"

class Like(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liker = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Like ID: {self.id} On Post: {self.post.id} from: {self.liker.username}"