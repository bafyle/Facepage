from django.urls import path
from .views import (
    profile, addComment, addPost, likePost, search,
    addFriend, home, updatePost, deletePost, )

app_name = 'posts'
urlpatterns = [
    path(r'', home, name='home'),
    path(r'create_post/', addPost, name='add-post'),
    path(r'update/<int:post_id>/', updatePost, name='update'),
    path(r'delete/<int:post_id>', deletePost, name='delete'),
    path(r'like/<int:post_id>/', likePost, name='like-post'),
    path(r'comment/<int:post_id>/', addComment, name='add-comment'),
    path(r'search/', search, name='search'),
    path(r'add/<str:username>/', addFriend, name='add-friend'),
]
