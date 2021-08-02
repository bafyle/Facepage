from django.http.response import Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.paginator import Paginator
from notifications.models import Notification

from users.models import Friend


def home(request):
    """
    Home view, get your latest post and all your friends posts
    """
    if request.user.is_authenticated:
        friends = Friend.objects.filter(Q(side2=request.user) | Q(side1=request.user))
        friends_posts = []
        for friend in friends:
            if friend.side1.username == request.user.username:
                friends_posts.append(Post.objects.filter(creator=friend.side2).order_by('-create_date')[:2])
            else:
                friends_posts.append(Post.objects.filter(creator=friend.side1).order_by('-create_date')[:2])
        
        likes = Like.objects.filter(liker=request.user)
        liked_posts = []
        for like in likes:
            liked_posts.append(Post.objects.get(id=like.post.id))
        
        get_last_post = Post.objects.filter(creator=request.user.id)
        if not get_last_post:
            my_last_post = []
        else:
            my_last_post = get_last_post.latest('create_date')
        
        context = {
            'friends_posts':friends_posts,
            'liked_posts': liked_posts,
            'my_last_post': my_last_post,
            'navbar_link': request.user.profile.link,
            'profile_pic': request.user.profile.profile_picture.url,
            'navbar_name': request.user.first_name,
        }
        
        return render(request, 'pages/NewHome.html', context)
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')

def profile(request, link):
    """
    Profile view, get all the posts of this user and be friend with them
    """
    if request.user.is_authenticated:
        context = dict()
        user = get_object_or_404(User, profile__link=link)
        if request.user != user:
            are_they_friends = bool(
                Friend.objects.filter(
                    (Q(side1=request.user) & Q(side2=user)) | (Q(side1=user) & Q(side2=request.user))
                    )
                )
            context['are_they_friends'] = are_they_friends
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

        context['navbar_name'] = request.user.first_name
        context['navbar_link'] = request.user.profile.link
        context['profile_pic'] = request.user.profile.profile_picture.url
        return render(request, 'pages/NewProfile.html', context)
    else:
        messages.error(request, "You need to login first to view this profile")
        return redirect('posts:home')

def getProfilePosts(request, link:str):
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

def search(request):
    """
    Search view, get all posts and accounts that contains what a particular word
    """
    if request.user.is_authenticated:
        search = str(request.GET['search-text'])
        search_keywords = search.split(' ')
        while search_keywords.count('') > 0:
            search_keywords.remove('')
        posts = []
        users = list()
        for keyword in search_keywords:
            for post in Post.objects.filter(post_content__icontains=keyword):
                if post not in posts:
                    posts.append(post)
            for user in User.objects.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)):
                count = 0
                for L in users:
                    if L[1] != user.profile.link:
                        count += 1
                if count == len(users):
                    are_they_friends = bool(Friend.objects.filter((Q(side1=request.user) & Q(side2=user)) 
                                    | (Q(side1=user) & Q(side2=request.user))))
                    users.append([
                        user.profile.name(),
                        user.profile.link,
                        user.profile.profile_picture.url,
                        are_they_friends
                        ])
        context = {'search': search, 'posts': posts, 'users': users}
        context['navbar_name'] = request.user.first_name
        context['navbar_link'] = request.user.profile.link
        context['profile_pic'] = request.user.profile.profile_picture.url
        return render(request, 'Pages/NewSearch.html', context)
    else:
        messages.error(request, "You need to login first in order to do that")
        return redirect('posts:home')

def createPost(request):
    """
    This function create a new post with with data from 'new-post-content' that comes
    from a post request and redirects to the same page
    """
    if request.user.is_authenticated:
        new_post = Post(post_content=request.POST['new-post-content'], creator=request.user)
        new_post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You must be logged in first")
        return redirect('users:index')

def updatePost(request, post_id):
    """
    Update view, update a particular post by the id of the post
    """
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        if post.creator == request.user:
            if request.method == "POST":
                post.post_content = request.POST['new-post-content']
                post.save()
                messages.success(request, "Post updated successfully")
            context = {
                'post': post,
                'navbar_name': request.user.first_name,
                'navbar_link': request.user.profile.link,
                'profile_pic': request.user.profile.profile_picture.url
            }
            return render(request, 'pages/NewUpdate.html', context)
        else:
            raise Http404
    else:
        messages.error(request, "You must login first")
        return redirect('users:index')

def viewPost(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        context = {
            'post': post,
            'navbar_name': request.user.first_name,
            'navbar_link': request.user.profile.link,
            'profile_pic': request.user.profile.profile_picture.url,
            'my_post': post.creator == request.user,
        }
        return render(request, 'pages/ViewPost.html', context)
    else:
        messages.error(request, "you need to login first")
        return redirect('users:login')


def sharePost(request, post_id):
    if request.user.is_authenticated:
        referenced_post = get_object_or_404(Post, id=post_id)
        new_post = Post(
            creator=request.user,
            shared_post=True,
            original_post=referenced_post
        )
        new_post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You must be logged in first")
        return redirect('users:index')

def deletePost(request, post_id):
    """
    This function delete a particular post by the id of that post
    and redirect to the same page
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.creator:
        post.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        raise Http404

def likePost(request, post_id):
    """
    This function add a like to the database for a particular post
    and update that post like number by recounting how many rows in the 
    like table for that post
    """
    if request.user.is_authenticated:
        post = Post.objects.get(id=post_id)
        isPostLiked = bool(Like.objects.filter(post=post, liker=request.user))
        if not isPostLiked:
            new_like = Like(post=post, liker=request.user)
            new_like.save()
            post.likes = Like.objects.filter(post=post).count()
            post.save()

            if request.user is not post.creator:
                if Notification.objects.filter(user_from=request.user, user_to=post.creator, route_id=post_id).count() <= 0:
                    notification_content = f"{request.user.first_name} {request.user.last_name} liked your post: "
                    if len(post.post_content) > 10:
                        notification_content += f"{post.post_content[0:10]}..."
                    else:
                        notification_content += f"{post.post_content}"
                    newNotification = Notification(
                        user_from=request.user,
                        user_to=post.creator,
                        content=notification_content,
                        type='L',
                        picture=request.user.profile.profile_picture.url,
                        route_id=post_id
                    )
                    newNotification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You must be logged in first")
        return redirect('users:index')


def unlikePost(request, post_id):
    """
    This function removes a like from the database for a particular post
    and update that post like number by recounting how many rows in the 
    like table for that post
    """
    if request.user.is_authenticated:
        post = Post.objects.get(id=post_id)
        likeObject = Like.objects.filter(post=post, liker=request.user)
        isPostLiked = bool(likeObject)
        if isPostLiked:
            likeObject.delete()
            post.likes = Like.objects.filter(post=post).count()
            post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You must be logged in first")
        return redirect('users:index')

def addComment(request, post_id):
    """
    Same idea of the likePost functions, adds a comment to a post via a
    GET request and recount how many comments for that post to update
    the comment counter for that post
    """
    if request.user.is_authenticated:
        comment = request.GET['comment-content']
        commented_post = Post.objects.get(id=post_id)

        new_comment = Comment(comment_content=comment, post=commented_post, creator=request.user)
        new_comment.save()
        commented_post.comments = Comment.objects.filter(post=commented_post).count()
        commented_post.save()
        if request.user is not commented_post.creator:
            if Notification.objects.filter(user_from=request.user, user_to=commented_post.creator, route_id=post_id).count() <= 0:
                notification_content = f"{request.user.first_name} {request.user.last_name} commented on your post: "
                if len(comment) > 10:
                    notification_content += f"{comment[0:10]}..."
                else:
                    notification_content += f"{comment}"
                newNotification = Notification(
                    user_from=request.user,
                    user_to=commented_post.creator,
                    content=notification_content,
                    type='C',
                    picture=request.user.profile.profile_picture.url,
                    route_id=post_id
                )
                newNotification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You must be logged in first")
        return redirect('users:index')

