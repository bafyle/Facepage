from django.db import models
from django.contrib.auth import get_user_model as User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Post(models.Model):
    post_content = models.TextField(blank=True)
    creator = models.ForeignKey(User(), on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    image = models.ImageField(default='', blank=True, upload_to='posts_pics')
    shared_post = models.BooleanField(default=False)
    original_post = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self, *args, **kwargs) -> None:
        if self.shared_post and self.image != '':
            raise ValidationError(_("Shared post cannot have an image"), code="image-shared-post")
        if self.post_content == '' and not self.shared_post:
            raise ValidationError(_("non-shared posts cannot have no content"), code="shared-post-no-content")
        if self.original_post != None and self.shared_post == False:
            raise ValidationError(_("non-shared posts cannot have reference to any posts"), code="non-shared-post-reference")
        if self.shared_post and self.original_post == self:
            raise ValidationError(_("shared posts cannot reference themselves"), code="self-referencing")
        return super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        string = self.post_content[0:30]
        if len(string) == 30:
            string += "..."
        return f"{string}, Post ID: {self.id} from: {self.creator}"

class Comment(models.Model):
    comment_content = models.CharField(max_length=1000)
    creator = models.ForeignKey(User(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        comment = self.comment_content[0:10]
        if len(comment) > 10:
            comment += "..."
        return f"{comment}, Comment ID: {self.id} from: {self.creator} to post: {self.post}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liker = models.ForeignKey(User(), on_delete=models.CASCADE)

    @staticmethod
    def is_post_liked_by_user(user: User(), post: Post):
        return Like.objects.filter(liker=user, post=post).exists()
    
    def __str__(self):
        return f"Like ID: {self.id} On Post: {self.post.id} from: {self.liker.username}"
