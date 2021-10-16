from django.urls import path
from .views import *

app_name = 'posts'
urlpatterns = [
    path(r'', home_view, name='home'),
    path(r'createpost/', create_post_view, name='add-post'),
    path(r'post/<int:post_id>/', view_post_view, name='view-post'),
    path(r'update/<int:post_id>/', update_post_view, name='update'),
    path(r'like/<int:post_id>/', like_post_view, name='like-post'),
    path(r'unlike/<int:post_id>/', unlike_post_view, name='unlike-post'),
    path(r'comment/<int:post_id>/', add_comment_view, name='add-comment'),
    path(r'search/', search_view, name='search'),
    path(r'share/<int:post_id>/', share_post_view, name='share-post'),
    
    #ajax
    path(r'ajax-like/<int:post_id>/', like_post_ajax, name='like-post-ajax'),
    path(r'ajax-unlike/<int:post_id>/', unlike_post_ajax, name='unlike-post-ajax'),
    path(r'ajax-comment/<int:post_id>/', add_comment_ajax, name='add-comment-ajax'),
    path(r'delete/<int:post_id>/', delete_post_ajax, name='delete'),
]
