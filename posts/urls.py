from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path(r'', views.home_view, name='home'),
    path(r'createpost/', views.create_post_view, name='add-post'),
    path(r'post/<int:post_id>/', views.view_post_view, name='view-post'),
    path(r'update/<int:post_id>/', views.update_post_view, name='update'),
    path(r'like/<int:post_id>/', views.like_post_view, name='like-post'),
    path(r'unlike/<int:post_id>/', views.unlike_post_view, name='unlike-post'),
    path(r'comment/<int:post_id>/', views.add_comment_view, name='add-comment'),
    path(r'search/', views.search_view, name='search'),
    path(r'share/<int:post_id>/', views.share_post_view, name='share-post'),
    
    #ajax
    path(r'ajax-like/<int:post_id>/', views.like_post_ajax, name='like-post-ajax'),
    path(r'ajax-unlike/<int:post_id>/', views.unlike_post_ajax, name='unlike-post-ajax'),
    path(r'ajax-comment/<int:post_id>/', views.add_comment_ajax, name='add-comment-ajax'),
    path(r'delete/<int:post_id>/', views.delete_post_ajax, name='delete'),
]
