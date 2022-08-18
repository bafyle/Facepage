from django.db.models import Q
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model as User
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext as _

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .forms import DeleteAccountForm, ChangePictureBioForm, RegisterForm
from .models import Friend, Profile, SendEmailRequest, NewAccountActivationLink, FriendRequest

from .signals import create_activation_link_signal, create_profile_signal
from notifications.models import Notification
from notifications.signals import send_friend_request_signal
import json

from .utils.utils import create_user_link, send_activate_email, send_new_password
from .utils.id_generator import generate_random_characters, generator_letters, id_generator
from .utils.tokens import account_activation_token

from django.views.decorators.csrf import ensure_csrf_cookie
from .utils.constants import FIVE_MINUTES


def index(request: HttpRequest):
    """
    view the login page or redirects to the home page if you are already logged in
    """
    if request.user.is_authenticated:
        return redirect('posts:home')
    return render(request, 'pages/Login.html')


def login_with_limit_view(request: HttpRequest):
    """
    Login view function, it prevents logging more than 3 times 
    """
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        if not can_login_again(request):
            messages.error(request, "Please wait some time before logging again")
            return redirect("users:index")
        username = request.POST.get("username")
        password = request.POST.get("pass")
        if (user := authenticate(username=username, password=password)) is not None:
            if Profile.objects.get(user=user).verified == False:
                if not SendEmailRequest.objects.get_or_create(user=user)[0].is_still_soon():
                    send_activate_email(request, user, True)
                    messages.warning(request,"Your account is not verified, check your email for the activation link")
                else:
                    messages.warning(request,
                    """
                    Your account is not activated, and cannot send an activation link to you right now, try again later
                    """.strip()
                    )
            else:
                clear_login_attempts_data_from_session(request)
                login(request, user)
        else:
            messages.error(request, "Wrong username or password, please try again")
    return redirect('users:index')

def can_login_again(request: HttpRequest) -> bool:
    """
    if the user tried to login with wrong credentials more
    than 3 times this function returns false
    and this user has to wait five mimutes to login again

    returns true if the user entered credentials less than 3 or
    if the user waited for the five minutes after the third attempt

    """
    
    if request.session.get('last_login_attempt') is None:
        request.session['last_login_attempt'] = timezone.localtime(timezone.now()).strftime("%c")
    if (x := request.session.get("login_attempts")) == None:
        request.session['login_attempts'] = 1
        return True
    request.session['login_attempts'] += 1
    if x < 3:
        return True
    last_loggin_attempt_from_session = timezone.datetime.strptime(request.session.get("last_login_attempt"), "%c")
    last_logging_attempt_from_session_aware = timezone.make_aware(last_loggin_attempt_from_session)
    time_after_last_login_attempt = (timezone.localtime(timezone.now()) - last_logging_attempt_from_session_aware).total_seconds()
    if time_after_last_login_attempt > FIVE_MINUTES:
        request.session['last_login_attempt'] = timezone.localtime(timezone.now()).strftime("%c")
        return True
    else:
        return False


def clear_login_attempts_data_from_session(request: HttpRequest) -> None:
    """
    Clear the login_attempts and last_login_attempt variables in
    request.session
    """
    try:
        del request.session['login_attempts']
        del request.session['last_login_attempt']
    except KeyError:
        return


def logout_view(request: HttpRequest):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('users:index')


def forgot_password_view(request: HttpRequest):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            validate_email(email)
        except ValidationError as error:
            return JsonResponse({"message": error.messages})
        if (requester := User().objects.filter(email=email).first()) == None:
            return JsonResponse({"message": "no user"})
        forget_password_request = SendEmailRequest.objects.get_or_create(user=requester)[0]
        if forget_password_request.is_still_soon():
            return JsonResponse({"message": "time limit"})
        new_password = generate_random_characters(10, generator_letters())
        requester.set_password(new_password)
        requester.save()
        try:
            send_new_password(new_password, email)
            forget_password_request.last_request = timezone.localtime(timezone.now())
            forget_password_request.save()
        except Exception as e:
            return JsonResponse({'message': e.__str__()})
        return JsonResponse({'message':'good'})
    else:
        return render(request, 'pages/ForgotPassword.html')


@ensure_csrf_cookie
def register_view(request: HttpRequest):
    """
    UNDER DEVELOPMENT
    Register view that creates profile and
    activation link using signals
    """
    if request.user.is_authenticated:
        return redirect('users:index')
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            new_link = create_user_link(user)
            create_profile_signal.send(
                sender=User(),
                user=user,
                link=new_link,
                birthday= form.cleaned_data['birthday'],
                gender= form.cleaned_data['gender'],
            )
            send_email_success, uid, token = send_activate_email(request, user, True)
            if not send_email_success:
                user.delete()
                return JsonResponse({"message": "email not send"})
            create_activation_link_signal.send(
                sender=User(),
                user=user,
                activation_link= f"{uid}/{token}"
            )
            return JsonResponse({'message':'good'})
        else:
            return JsonResponse(json.loads(form.errors.as_json()))
    else:
        form = RegisterForm()
    return render(request, 'pages/Register.html', {'form':form})

@login_required
def send_friend_request_view(request: HttpRequest, link: str):
    user = get_object_or_404(User(), profile__link=link)
    is_there_friendship = Friend.objects.filter(((Q(side1=request.user) & Q(side2=user)) | (Q(side1=user) & Q(side2=request.user)))).exists()

    if is_there_friendship:
        messages.error(request, "you are already friends")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if (friend_request := FriendRequest.objects.filter(Q(user_from=request.user) & Q(user_to=user))).exists():
        if friend_request.first().status == FriendRequest.FRIEND_REQUEST_DECLINED:
            if friend_request.first().user_from == user:
                friend_request.first().status = FriendRequest.FRIEND_REQUEST_WAITING
                friend_request.first().save()
            else:
                messages.success(request, "cannot accept friend request right now")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.success(request, "friend request already sent")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        new_friend_request = FriendRequest(user_from=request.user, user_to=user)
        new_friend_request.save()
    notification_content = f"{request.user.profile.name()} sent you a friend request"
    send_friend_request_signal.send(
        sender=User(), 
        user_from=request.user,
        user_to=user,
        content=notification_content,
        type='F',
        picture=request.user.profile.profile_picture.url,
        content_object=new_friend_request,
        route_id=request.user.profile.link,
    )
    messages.success(request, "friend request sent")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def accept_friend_request_view(request: HttpRequest, link: str):
    sender = User().objects.filter(profile__link=link).first()
    if not sender:
        messages.error(request, "no such user")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    friend_request = FriendRequest.objects.filter(user_from=sender, user_to=request.user).first()
    if not friend_request:
        messages.error(request, "no such friend request to accept")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if friend_request.status == FriendRequest.FRIEND_REQUEST_ACCEPTED:
        messages.success(request, "you are already friends")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    friend_request.accept_friend_request()
    notification = Notification.objects.filter(
        user_from=sender,
        user_to=request.user,
        type='F'
    ).first()
    if notification:
        notification.delete()
    messages.success(request, "friendship accepted")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def decline_friend_request_view(request: HttpRequest, link: str):
    """Delete a comming friend request """
   
    sender = User().objects.filter(profile__link=link).first()
    if not sender:
        messages.error(request, "no such user")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    friend_request = FriendRequest.objects.filter(user_from=sender, user_to=request.user).first()

    if friend_request.status == FriendRequest.FRIEND_REQUEST_WAITING:
        friend_request.decline_friend_request()
    else:
        messages.error(request, "no such friend request to decline")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    notification = Notification.objects.filter(
        user_from=sender,
        user_to=request.user,
        type='F'
    ).first()
    if notification:
        notification.delete()
    messages.success(request, "Friend request declined")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def cancel_friend_request_view(request: HttpRequest, link: str):
    """ delete a request that has been sent by the request.user"""

    user = get_object_or_404(User(), profile__link = link)
    friend_request = FriendRequest.objects.filter(user_from=request.user, user_to=user).first()
    if friend_request.status == FriendRequest.FRIEND_REQUEST_ACCEPTED:
        messages.error(request, "Friend request is accepted, cannot be cancelled right now")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    friend_request.delete()
    notification = Notification.objects.filter(
        user_from=request.user,
        user_to=user,
        route_id=request.user.profile.link,
        type='F'
    ).first()
    if notification:
        notification.delete()
    messages.success(request, "Friend request cancelled")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def unfriend_view(request: HttpRequest, link: str):
    user = User().objects.filter(profile__link=link).first()
    if user:
        friendship = Friend.objects.filter(
            ((Q(side1=user) & Q(side2=request.user)) | (Q(side1=request.user) & Q(side2=user)))).first()
        friend_request = FriendRequest.objects.filter((Q(user_from=request.user) & Q(user_to=user)) | (Q(user_from=user) & Q(user_to=request.user)))
        if friendship:
            friendship.delete()
            if friend_request:
                friend_request.delete()
        else:
            messages.error(request, "no such friend")
        messages.success(request, "friendship deleted")
    else:
        messages.error(request, "no such user")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def account_settings_view(request: HttpRequest):
    """
    Takes the new user email and password and check if they are valid and save them
    after saving it redirects to the login page to login again with the new data
    """
    
    if request.method == "POST":
        try:
            if request.POST['password1'] != request.POST['password2']:
                raise ValidationError(_("Passwords doesn't match"))
            validate_password(request.POST['password1'])
            request.user.set_password(request.POST['password1'])
            # if request.POST['email'] is not None:
            #     request.user.email = request.POST['email']
            # else:
            #     request.user.email = ''
            request.user.save()
            messages.success(request, "password has changed, you need to login again")
            return redirect('users:index')
        except ValidationError as error:
            for error_message in error:
                messages.error(request, error_message)
            return redirect('users:account-settings')
    else:
        context = {
            # 'profile_pic': request.user.profile.profile_picture.url,
            # 'navbar_name': request.user.first_name,
            # 'navbar_link': request.user.profile.link,
            'email': request.user.email,
            'username': request.user.username,
            'active_user': User().objects.select_related('profile').get(pk=request.user.pk)
        }
        return render(request, 'pages/newAccountSettings.html', context)


@login_required
def personal_settings_view(request: HttpRequest):
    if request.method == "POST":
        bio_form = ChangePictureBioForm(request.POST, request.FILES)
        if bio_form.is_valid():
            if bio_form.cleaned_data['profile_picture'] != 'profile_pics/default.jpg':
                old_image = request.user.profile.profile_picture.url
                if old_image.split('/')[-1] != 'default.jpg':
                    request.user.profile.profile_picture.delete(False)
                request.user.profile.profile_picture = bio_form.cleaned_data['profile_picture']
            if bio_form.cleaned_data['profile_cover'] != 'profile_covers/default.jpg':
                old_image = request.user.profile.profile_cover.url
                if old_image.split('/')[-1] != 'default.jpg':
                    request.user.profile.profile_cover.delete(False)
                request.user.profile.profile_cover = bio_form.cleaned_data['profile_cover']
            request.user.profile.copy_new_data(bio_form.cleaned_data)
            # request.user.first_name = bio_form.cleaned_data['first_name']
            # request.user.last_name = bio_form.cleaned_data['last_name']
            # request.user.profile.phone_number = bio_form.cleaned_data['phone_number']
            # request.user.profile.gender = bio_form.cleaned_data['gender']
            # request.user.profile.birthday = bio_form.cleaned_data['birthday']
            # request.user.profile.bio = bio_form.cleaned_data['bio']
            # request.user.profile.save()
            # request.user.save()
            messages.success(request, "changes saved")
        else:
            messages.error(request, "invalid data has been entered")
    bio_form = ChangePictureBioForm({
        'bio': request.user.profile.bio,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone_number': request.user.profile.phone_number,
        'gender': request.user.profile.gender,
        'birthday': request.user.profile.birthday.strftime("%Y-%m-%d"),
    })
    context = {
        'profile_pic': request.user.profile.profile_picture.url,
        'profile_cover': request.user.profile.profile_cover.url,
        'email': request.user.email,
        'username': request.user.username,
        'bio_form': bio_form,
        'active_user': User().objects.select_related('profile').get(pk=request.user.pk)
    }
    return render(request, 'pages/newPersonalSettings.html', context)


@login_required
def delete_profile_cover_view(request: HttpRequest):
    old_image = request.user.profile.profile_cover.url
    if old_image.split('/')[-1] != 'default.jpg':
        request.user.profile.profile_cover.delete(False)
    else:
        messages.error(request, "you don't have a profile picture to delete")
        return redirect('users:personal-settings')
    
    request.user.profile.profile_cover = 'profile_covers/default.jpg'
    request.user.profile.save()
    request.user.save()
    messages.success(request, "Profile picture deleted")
    return redirect('users:personal-settings')

@login_required
def delete_profile_picture_view(request: HttpRequest):
    """
    This function is for deleting the existing profile picture of the account
    and set it to the default one by deleting the profile instance from the
    database and create a new one
    """
    
    old_image = request.user.profile.profile_picture.url
    if old_image.split('/')[-1] != 'default.jpg':
        request.user.profile.profile_picture.delete(False)
    else:
        messages.error(request, "you don't have a profile picture to delete")
        return redirect('users:personal-settings')
    request.user.profile.profile_picture = 'profile_pics/default.jpg'
    request.user.profile.save()
    request.user.save()
    messages.success(request, "Profile picture deleted")
    return redirect('users:personal-settings')


@login_required
def delete_account_view(request: HttpRequest):
    """
    This function makes sure that the user want to delete his account
    it takes the confirmations and the username text from the user 
    and check if they are correct and deletes the account
    """
    if not request.user.is_superuser:
        if request.method == 'POST':
            form = DeleteAccountForm(request.POST)
            for key in request.POST:
                print(key + " " + request.POST[key])
            if form.is_valid():
                if form.cleaned_data['username'] == request.user.username and form.cleaned_data['confirmation'] == "I want to delete my account":
                    user = request.user
                    logout(request)
                    user.delete()
                    messages.success(request, "You have deleted your account")
                    return redirect('users:index')
                else:
                    messages.error(request, "incorrect input")
                    return redirect('users:delete')
            else:
                messages.error(request, "incorrect input")
                return redirect('users:delete')
        else:
            form = DeleteAccountForm()
            context = {
                'profile_pic': request.user.profile.profile_picture.url,
                'navbar_name': request.user.first_name,
                'navbar_link': request.user.profile.link,
                'form': form,
            }
        return render(request, 'pages/DeleteAccount.html', context)
    else:
        messages.error(request, "Can not delete a superuser account")
        return redirect('posts:home')

@login_required
def show_all_friends_view(request: HttpRequest):
    active_user = User().objects.select_related('profile').get(pk=request.user.pk)
    friends_query = Friend.objects.filter(Q(side1=active_user) | Q(side2=active_user)).select_related("side1", "side2", "side1__profile", "side2__profile")
    friends_list = []
    for friend in friends_query:
        if friend.side1 != request.user:
            friends_list.append(friend.side1)
        else:
            friends_list.append(friend.side2)
    context = {
        'users': friends_list,
        'active_user': active_user
    }
    return render(request, "pages/FriendList.html", context)

def activate_view(request: HttpRequest, uidb64, token):
    """
    Activate account view function
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User().objects.get(pk=uid)
        if (x := NewAccountActivationLink.objects.filter(
                    user=user,
                    link=f"{uidb64}/{token}"
                ).first()):
            if x.expired():
                x.delete()
                user.delete()
                messages.success(request, "Expired activation link, please register with a new account")
                return redirect('users:index')
    except(TypeError, ValueError, OverflowError, User().DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.profile.verified = True
        user.profile.save()
        login(request, user)
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('users:index')
    else:
        messages.success(request, 'Activation link is invalid!')
        return redirect('users:login')
