from django.urls import path
from .views import *

app_name = 'posts'
urlpatterns = [
    path(r'', home, name='home'),
    path(r'createpost/', createPost, name='add-post'),
    path(r'<int:post_id>/', viewPost, name='view-post'),
    path(r'update/<int:post_id>/', updatePost, name='update'),
    path(r'delete/<int:post_id>', deletePost, name='delete'),
    path(r'like/<int:post_id>/', likePost, name='like-post'),
    path(r'unlike/<int:post_id>/', unlikePost, name='unlike-post'),
    path(r'comment/<int:post_id>/', addComment, name='add-comment'),
    path(r'search/', search, name='search'),
    path(r'add/<slug:link>/', addFriend, name='add-friend'),
]
