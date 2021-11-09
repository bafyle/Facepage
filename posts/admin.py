from django.contrib import admin
from .models import Like, Comment, Post

class CommentsInline(admin.StackedInline):
    model=Comment
    extra=0

class PostAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ['post_content', 'creator', 'likes', 'comments', 'created_date']}),
    ]
    inlines = [CommentsInline]

admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Like)