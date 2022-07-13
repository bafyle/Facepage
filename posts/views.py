from django.http.response import HttpResponseNotAllowed, JsonResponse
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model as User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from users.models import FriendRequest
from notifications.models import Notification
from users.models import Friend
from .forms import CreatePostForm
from .models import Post, Comment, Like
from notifications.signals import comment_signal, like_signal
from .signals import create_post_signal
from django.db.models.query import QuerySet
@login_required
def home_view(request):
    """
    Home view, get your latest post and all your friends posts
    """
    friends = Friend.objects.filter(Q(side2=request.user) | Q(side1=request.user)).select_related("side1", "side2")
    
    friends_posts = None
    for friend in friends:
        if friend.side1.username == request.user.username:
            if friends_posts is None:
                friends_posts = Post.objects.filter(creator=friend.side2).order_by('-create_date')[:2].select_related("creator")
            else:
                friends_posts.union(Post.objects.filter(creator=friend.side2).order_by('-create_date')[:2].select_related("creator"))
        else:
            if friends_posts is None:
                friends_posts = Post.objects.filter(creator=friend.side1).order_by('-create_date')[:2].select_related("creator")
            else:
                friends_posts.union(Post.objects.filter(creator=friend.side1).order_by('-create_date')[:2].select_related("creator"))
    friends_posts = list(friends_posts)
    friends_posts.sort(key=lambda x: x.create_date, reverse=True)
    last_post = Post.objects.filter(creator=request.user).select_related("creator").last()
    if last_post is not None:
        friends_posts.insert(0, last_post)
    likes = Like.objects.filter(liker=request.user).select_related("post")
    liked_posts = [like.post for like in likes]
    
    context = {
        'friends_posts':friends_posts,
        'liked_posts': liked_posts,
    }
    
    return render(request, 'pages/NewHome.html', context)

@login_required
def profile_view(request, link):
    """
    Profile view, get all the posts of this user and be friend with them
    """
    context = dict()
    user = get_object_or_404(User(), profile__link=link)
    if request.user != user:
        friends_requests = FriendRequest.objects.filter(((Q(user_from=request.user) & Q(user_to=user)) | (Q(user_from=user) & Q(user_to=request.user)))
                ).select_related("user_from", "user_to")
        
        if not friends_requests.exists():
            context['friendship_status'] = 'not-friends'
        elif friends_requests.first().status == FriendRequest.FRIEND_REQUEST_ACCEPTED:
            context['friendship_status'] = 'accepted'
        elif friends_requests.first().status == FriendRequest.FRIEND_REQUEST_DECLINED:
            if friends_requests.first().user_from == request.user:
                context['friendship_status'] = 'declined'
            else:
                context['friendship_status'] = 'not-friends'
        elif friends_requests.first().status == FriendRequest.FRIEND_REQUEST_WAITING:
            if friends_requests.first().user_from == request.user:
                context['friendship_status'] = 'sent'
            else:
                context['friendship_status'] = 'received'

    profile_posts = Post.objects.filter(creator__profile__link=link).order_by('-create_date')
    likes = Like.objects.filter(liker=request.user)
    liked_posts = []
    for like in likes:
        liked_posts.append(Post.objects.get(id=like.post.id))
    
    paginator = Paginator(profile_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context['user_profile_link'] = link
    context['page_obj'] = page_obj
    context['liked_posts'] = liked_posts
    context['user_profile_pic'] = user.profile.profile_picture
    context['user_profile_cover'] = user.profile.profile_cover
    context['user_profile_name'] = user.profile.name()
    context['user_bio'] = user.profile.bio

    context['pages_count'] = len(profile_posts) // 5
    return render(request, 'pages/NewProfile.html', context)


def get_profile_posts(request: HttpRequest, link:str):
    page = int(request.GET.get('page'))
    lowIndex = page*5
    highIndex = lowIndex + 5
    profile_posts = Post.objects.filter(
                        creator__profile__link=link
                    ).order_by('-create_date')[lowIndex:highIndex].values(
                                                                        'comments',
                                                                        'create_date',
                                                                        'creator',
                                                                        'image',
                                                                        'likes',
                                                                        'original_post',
                                                                        'post_content',
                                                                        'shared_post',
                                                                        'id')
    posts = dict()
    for index, query in enumerate(profile_posts):
        post = dict()
        for key in query:
            if key == 'create_date':
                post[key] = timezone.localdate(query[key]).strftime("%Y/%m/%d %H:%M:%S")
                continue;
            post[key] = query[key]
        comments = dict()
        comments_query = Comment.objects.filter(post__id = query.get('id'))
        for index2, commentItem in enumerate(comments_query):
            comment = dict()
            comment['comment_content'] = commentItem.comment_content
            comment['comment_creator'] = commentItem.creator.profile.name()
            comment['comment_creator_profile_picture_url'] = commentItem.creator.profile.profile_picture.url
            comments[index2] = comment
        post['liked'] = bool(Like.objects.filter(post__id=post['id'], liker=request.user))
        post['comments'] = comments
        posts[index] = post
    return JsonResponse(posts)

@login_required
def search_view(request: HttpRequest):
    """
    Search view, get all posts and accounts that contains what a particular word
    """
    search = str(request.GET.get('search-text')).strip()
    if search is None or search == "":
        messages.error(request, "search text cannot be empty")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    search_keywords = search.split(' ')
    posts = set()
    users = set()
    for keyword in search_keywords:
        for post in Post.objects.filter(post_content__icontains=keyword).select_related("creator").distinct():
            posts.add(post)
        for user in User().objects.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)):
                are_they_friends = Friend.objects.select_related("side1", "side2").filter(
                        ((Q(side1=request.user) & Q(side2=user)) | (Q(side1=user) & Q(side2=request.user))
                        )).exists()
                    
                users.add((user, are_they_friends))
    context = {'search': search, 'posts': posts, 'users': users}
    return render(request, 'pages/NewSearch.html', context)

@login_required
def create_post_view(request):
    """
    This function create a new post with with data from 'new-post-content' that comes
    from a post request and redirects to the same page
    """
    post_creation_form = CreatePostForm(request.POST, request.FILES)
    if post_creation_form.is_valid():
        new_post = Post(post_content=post_creation_form.cleaned_data['content'], creator=request.user, image=post_creation_form.cleaned_data['image'])
        new_post.save()
        create_post_signal.send(sender=new_post)
    else:
        # debug
        print(post_creation_form.errors)
        messages.error(request, "post hasn't been created")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def update_post_view(request: HttpRequest, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.creator:
        messages.error(request, "cannot edit someone else post")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if request.method == "POST":
        if request.POST.get("submit-button").lower() == "save":
            post.post_content = request.POST['new-post-content']
            try:
                post.save()
            except ValidationError as error:
                return render(request, 'pages/NewUpdate.html', {'post': post, 'errors': error.messages})
            messages.success(request, "Post updated successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect('profile', link=request.user.profile.link)
    return render(request, 'pages/NewUpdate.html', {'post': post})

# def update_post_view(request: HttpRequest, post_id):
#     """
#     Update view, update a particular post by the id of the post
#     """
#     if request.user.is_authenticated:
#         post = get_object_or_404(Post, id=post_id)
#         if post.creator == request.user:
#             if request.method == "POST":
#                 if request.POST.get("submit-button").lower() == "save":
#                     post.post_content = request.POST['new-post-content']
#                     try:
#                         post.save()
#                     except ValidationError as error:
#                         return render(request, 'pages/NewUpdate.html', {'post': post, 'errors': error.messages})
#                     messages.success(request, "Post updated successfully")
#                     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#                 else:
#                     return redirect('profile', link=request.user.profile.link)
#             else:
#                 return render(request, 'pages/NewUpdate.html', {'post': post})
#         else:
#             raise HttpResponseNotAllowed(["POST"])
#     else:
#         messages.error(request, "You must login first")
#         return redirect('users:index')


@login_required
def view_post_view(request: HttpRequest, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
        'liked': Like.objects.filter(liker=request.user, post=post).exists(),
        'my_post': post.creator == request.user,
    }
    return render(request, 'pages/ViewPost.html', context)
    

@login_required
def share_post_view(request: HttpRequest, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.shared_post:
        new_post = Post(
            creator=request.user,
            shared_post=True,
            original_post=post.original_post
        )
    else:
        new_post = Post(
            creator=request.user,
            shared_post=True,
            original_post=post
        )
    new_post.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def delete_post_ajax(request, post_id):
    """
    This function delete a particular post by the id of that post
    and redirect to the same page
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.creator:
        post.delete()
        return JsonResponse({"message": "good"})
    else:
        raise HttpResponseNotAllowed(["DELETE", "POST"])


@login_required
def like_post_view(request, post_id):
    """
    This function add a like to the database for a particular post
    and update that post like number by recounting how many rows in the 
    like table for that post
    """
    post = Post.objects.get(id=post_id)
    isPostLiked = bool(Like.objects.filter(post=post, liker=request.user))
    if not isPostLiked:
        new_like = Like(post=post, liker=request.user)
        new_like.save()
        post.likes = Like.objects.filter(post=post).count()
        post.save()

        if request.user != post.creator:
            if Notification.objects.filter(user_from=request.user, type='L', route_id=post_id).count() <= 0:
                notification_content = f"{request.user.profile.name()} liked your post: "
                if not post.shared_post:
                    if len(post.post_content) > 20:
                        notification_content += f"{post.post_content[0:20]}..."
                    else:
                        notification_content += f"{post.post_content}"
                else:
                    notification_content = f"{request.user.profile.name()} liked your you shared"
                newNotification = Notification(
                    user_from=request.user,
                    user_to=post.creator,
                    content=notification_content,
                    type='L',
                    picture=request.user.profile.profile_picture.url,
                    content_object=post,
                    route_id=post.id,
                )
                newNotification.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def like_post_ajax(request, post_id):
    post = Post.objects.get(id=post_id)
    if not Like.objects.filter(post=post, liker=request.user).exists():
        like_object = Like.objects.create(post=post, liker=request.user)
        if request.user != post.creator:
            notification_content = f"{request.user.profile.name()} liked your post: "
            if not post.shared_post:
                if len(post.post_content) > 20:
                    notification_content += f"{post.post_content[0:20]}..."
                else:
                    notification_content += f"{post.post_content}"
            else:
                notification_content = f"{request.user.profile.name()} liked your you shared"
            like_signal.send(
                sender=Like,
                user_from=request.user,
                user_to=post.creator,
                content=notification_content,
                type='L',
                picture=request.user.profile.profile_picture.url,
                content_object=like_object,
                route_id=post.id,
            )
    # missing the elses of each if
    return JsonResponse({"message":"good", 'likes': post.likes})

@login_required
def unlike_post_view(request, post_id):
    """
    This function removes a like from the database for a particular post
    and update that post like number by recounting how many rows in the 
    like table for that post
    """
    
    post = Post.objects.get(id=post_id)
    query = Like.objects.filter(post=post, liker=request.user)
    if query.exists():
        query.first().delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

def unlike_post_ajax(request, post_id):
    """
    This function removes a like from the database for a particular post
    and update that post like number by recounting how many rows in the 
    like table for that post
    """
    if not request.user.is_authenticated:
        return JsonResponse({"message":"not-authed"})
    
    post = Post.objects.get(id=post_id)
    query = Like.objects.filter(post=post, liker=request.user)
    if query.exists():
        query.first().delete()
    post.refresh_from_db()
    return JsonResponse({"message":"good", 'likes': post.likes})
    
        
@login_required
def add_comment_view(request, post_id):
    """
    Same idea of the likePost functions, adds a comment to a post via a
    GET request and recount how many comments for that post to update
    the comment counter for that post
    """
    comment_text = request.GET.get('comment-content')
    commented_post = Post.objects.get(id=post_id)

    comment_object = Comment.objects.create(comment_content=comment_text, post=commented_post, creator=request.user)
    if request.user != commented_post.creator:
        notification_content = f"{request.user.profile.name()} commented on your post: "
        if not commented_post.shared_post:
            if len(comment_text) > 20:
                notification_content += f"{comment_text[0:20]}..."
            else:
                notification_content += f"{comment_text}"
        else:
            notification_content = f"{request.user.profile.name()} commented on a post you shared"
        comment_signal.send(
            sender=Comment,
            user_from=request.user,
            user_to=commented_post.creator,
            content=notification_content,
            type='C',
            picture=request.user.profile.profile_picture.url,
            content_object=comment_object,
            route_id=commented_post.id,
        )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

def add_comment_ajax(request, post_id):
    """
    Same idea of the likePost functions, adds a comment to a post via a
    GET request and recount how many comments for that post to update
    the comment counter for that post
    """
    if not request.user.is_authenticated:
        return JsonResponse({"message":"not-authed"})
    comment_text = request.GET.get('comment-content')
    commented_post = Post.objects.get(id=post_id)

    comment_object = Comment.objects.create(comment_content=comment_text, post=commented_post, creator=request.user)
    if request.user != commented_post.creator:
        if Notification.objects.filter(user_from=request.user, type='C', route_id=post_id).count() <= 0:
            notification_content = f"{request.user.profile.name()} commented on your post: "
            if not commented_post.shared_post:
                if len(comment_text) > 20:
                    notification_content += f"{comment_text[0:20]}..."
                else:
                    notification_content += f"{comment_text}"
            else:
                notification_content = f"{request.user.profile.name()} commented on a post you shared"
            comment_signal.send(
                sender=Comment,
                user_from=request.user,
                user_to=commented_post.creator,
                content=notification_content,
                type='C',
                picture=request.user.profile.profile_picture.url,
                content_object=comment_object,
                route_id=commented_post.id,
            )
    return JsonResponse({"message":"good"})
