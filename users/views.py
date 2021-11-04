from typing import Tuple
from django.db.models import Q
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model as User
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext as _
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.dispatch import Signal

from .forms import DeleteAccountForm, ChangePictureBioForm, RegisterForm
from .models import Friend, Profile, SendEmailRequest, NewAccountActivationLink
from .id_generator import *
from .tokens import account_activation_token
from notifications.models import Notification
import json

from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie

def index(request: HttpRequest):
    """
    view the login page or redirects to the home page if you are already logged in
    """
    if request.user.is_authenticated:
        return redirect('posts:home')
    return render(request, 'pages/Login.html')

@DeprecationWarning
def login_view(request: HttpRequest):
    """
    this function takes the username and the password the user entered and
    check if they are valid. If they are valid then it logs the user in and redirects 
    to the index where itself redirects you to the home page
    """
    if request.user.is_authenticated:
        return redirect('users:index')
    elif request.method == 'POST':
        username = request.POST['username']
        pw = request.POST['pass']
        user = authenticate(username=username, password=pw)
        if user is not None:
            if Profile.objects.get(user=user).verified == False:
                if SendEmailRequest.objects.get_or_create(user=user)[0].get_time_difference() > (5 * 60):
                    send_activate_email(request, user, True)
                messages.error(request,"Your account is not verified, check your email")
                return redirect('users:index')
            else:
                login(request, user)
        else:
            messages.error(request, "Wrong username or password")
    return redirect('users:index')

def login_with_limit_view(request: HttpRequest):
    """
    Login view function
    with the respect of the login attempts in request.sessions dict
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
                clear_login_details_from_session(request)
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
    if (x := request.session.get("login_attempts")) == None:
        return_value = bool()
        request.session['login_attempts'] = 0
        return_value = True
    else:
        request.session['login_attempts'] += 1
        if x < 3:
            return_value = True
        else:
            last_loggin_attempt_from_session = timezone.datetime.strptime(request.session.get("last_login_attempt"), "%c")
            last_logging_attempt_from_session_aware = timezone.make_aware(last_loggin_attempt_from_session)
            if (timezone.localtime(timezone.now()) - last_logging_attempt_from_session_aware).total_seconds() > 5 * 60:
                return_value = True
            else:
                return_value = False
    request.session['last_login_attempt'] = timezone.localtime(timezone.now()).strftime("%c")
    return return_value

def clear_login_details_from_session(request: HttpRequest) -> None:
    """
    Clear the login_attempts and last_login_attempt variables in
    request.session
    """
    try:
        del request.session['login_attempts']
        del request.session['last_login_attempt']
    except KeyError:
        pass

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
    Register view that creates the profile and
    account activation link objects without signals
    """
    if request.user.is_authenticated:
        return redirect('users:index')
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.instance
            new_link = ''
            while True:
                id_generated = id_generator(user, settings.ID_LENGTH)
                if User().objects.filter(profile__link=id_generated).count() == 0:
                    new_link = id_generated
                    break
            new_profile = Profile(user=user, link=new_link, birthday=form.cleaned_data['birthday'], gender=form.cleaned_data['gender'])
            form.save()
            new_profile.save()
            send_email = send_activate_email(request, user, True)
            if not send_email[0]:
                user.delete()
                return JsonResponse({"message": "email not send"})
            NewAccountActivationLink(
                user=user,
                link=f"{send_email[1]}/{send_email[2]}"
            ).save()
            return JsonResponse({'message':'good'})
        else:
            return JsonResponse(json.loads(form.errors.as_json()))
    else:
        form = RegisterForm()
    return render(request, 'pages/Register.html', {'form':form})

@ImportWarning
@ensure_csrf_cookie
def register_view2(request: HttpRequest):
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
            send_email = send_activate_email(request, user, True)
            if not send_email[0]:
                user.delete()
                return JsonResponse({"message": "email not send"})
            profile_signal = Signal()
            profile_signal.send(
                sender=user,
                kwargs={
                    'birthday': form.cleaned_data['birthday'],
                    'gender': form.cleaned_data['gender'],
                    'send_email_1': send_email[1],
                    'send_email_2': send_email[2]
                }
            )
            return JsonResponse({'message':'good'})
        else:
            return JsonResponse(json.loads(form.errors.as_json()))
    else:
        form = RegisterForm()
    return render(request, 'pages/Register.html', {'form':form})

def send_friend_request_view(request: HttpRequest, link: str):
    if request.user.is_authenticated:
        user = get_object_or_404(User(), profile__link=link)
        friendship_check = bool(
            Friend.objects.filter(((Q(side1=request.user) & Q(side2=user)) | (Q(side1=user) & Q(side2=request.user)))))
        if not friendship_check:
            new_relation = Friend(side1=request.user, side2=user)
            new_relation.save()
        else:
            messages.error(request, "you are already friends")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        notification = Notification.objects.filter(
            user_from=request.user,
            user_to=user,
            route_id=request.user.profile.link
        ).first()
        if notification:
            notification.delete()
        notification_content = f"{request.user.profile.name()} sent you a friend request"
        new_notification = Notification(
            user_from=request.user,
            user_to=user,
            content=notification_content,
            type='F',
            picture=request.user.profile.profile_picture.url,
            content_object=new_relation,
            route_id=request.user.profile.link,
        )
        new_notification.save()
        messages.success(request, "friend request sent")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def accept_friend_request_view(request: HttpRequest, link: str):
    if request.user.is_authenticated:
        sender = User().objects.filter(profile__link=link).first()
        if sender:
            friendship = Friend.objects.filter(side1=sender, side2=request.user, accepted=False).first()
            if friendship:
                friendship.accepted = True
                friendship.acceptance_date = timezone.localtime(timezone.now())
                friendship.save()
                notification = Notification.objects.filter(
                    user_from=sender,
                    user_to=request.user,
                    type='F'
                ).first()
                if notification:
                    notification.delete()
            else:
                messages.error(request, "no such friend request to accept")
            messages.success(request, "friendship accepted")
        else:
            messages.error(request, "no such user")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def decline_friend_request_view(request: HttpRequest, link: str):
    """Delete a comming friend request """
    if request.user.is_authenticated:
        sender = User().objects.filter(profile__link=link).first()
        if sender:
            friendship = Friend.objects.filter((Q(side1=sender) & Q(side2=request.user)) | (Q(side1=request.user) & Q(side2=sender))).first()
            if friendship and friendship.accepted == False:
                friendship.delete()
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
            messages.success(request, "friendship declined")
        else:
            messages.error(request, "no such user")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')

def cancel_friend_request_view(request: HttpRequest, link: str):
    """ delete a request that has been sent by the request.user"""
    if request.user.is_authenticated:
        user = get_object_or_404(User(), profile__link = link)
        friendship = Friend.objects.filter(side1=request.user, side2=user).first()
        if friendship and friendship.accepted == False:
            friendship.delete()
        else:
            messages.error(request, "no such friend request to cancel")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        notification = Notification.objects.filter(
            user_from=request.user,
            user_to=user,
            route_id=request.user.profile.link,
            type='F'
        ).first()
        if notification:
            notification.delete()
        messages.success(request, "friendship declined")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')

def unfriend_view(request: HttpRequest, link: str):
    if request.user.is_authenticated:
        user = User().objects.filter(profile__link=link).first()
        if user:
            friendship = Friend.objects.filter(
                ((Q(side1=user) & Q(side2=request.user)) | (Q(side1=request.user) & Q(side2=user))) &  
                Q(accepted=True)).first()
            if friendship:
                friendship.delete()
            else:
                messages.error(request, "no such friend")
            messages.success(request, "friendship deleted")
        else:
            messages.error(request, "no such user")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')
        
def accout_settings_view(request: HttpRequest):
    """
    Takes the new user email and password and check if they are valid and save them
    after saving it redirects to the login page to login again with the new data
    """
    if request.user.is_authenticated:
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
                'profile_pic': request.user.profile.profile_picture.url,
                'navbar_name': request.user.first_name,
                'navbar_link': request.user.profile.link,
                'email': request.user.email,
                'username': request.user.username,
            }
            return render(request, 'pages/newAccountSettings.html', context)
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def personal_settings_view(request: HttpRequest):
    if request.user.is_authenticated:
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
                request.user.profile.bio = bio_form.cleaned_data['bio']
                request.user.first_name = bio_form.cleaned_data['first_name']
                request.user.last_name = bio_form.cleaned_data['last_name']
                request.user.profile.phone_number = bio_form.cleaned_data['phone_number']
                request.user.profile.gender = bio_form.cleaned_data['gender']
                request.user.profile.birthday = bio_form.cleaned_data['birthday']
                request.user.profile.save()
                request.user.save()
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
            'navbar_name': request.user.first_name,
            'navbar_link': request.user.profile.link,
            'email': request.user.email,
            'username': request.user.username,
            'bio_form': bio_form,
        }
        return render(request, 'pages/newPersonalSettings.html', context)
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def delete_profile_cover_view(request: HttpRequest):
    if request.user.is_authenticated:
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
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def delete_profile_picture_view(request: HttpRequest):
    """
    This function is for deleting the existing profile picture of the account
    and set it to the default one by deleting the profile instance from the
    database and create a new one
    """
    if request.user.is_authenticated:
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
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def delete_account_view(request: HttpRequest):
    """
    This function makes sure that the user want to delete his account
    it takes the confirmations and the username text from the user 
    and check if they are correct and deletes the account
    """
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            if request.method == 'POST':
                form = DeleteAccountForm(request.POST)
                for key in request.POST:
                    print(key + " " + request.POST[key])
                if form.is_valid():
                    if form.cleaned_data['username'] == request.user.username and form.cleaned_data['confirmation'] == "i want to delete my account":
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
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')


def send_activate_email(request: HttpRequest, user: User(), failSilently: bool = False) -> Tuple[int, str, str]:
    """
    This is not a view function, it sends an email with
    an activation link and returns tuple with
    int: 1 if email send successfully
    str: the uid of the user
    str: the token of the user
    """
    current_site = get_current_site(request)
    mail_subject = 'Activate your Facepage account.'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    message = render_to_string('pages/AccountActivation.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':uid,
        'token':token,
    })
    email = EmailMessage(
            mail_subject,
            message,
            to=[user.email],
    )
    return email.send(fail_silently=failSilently), uid, token

def send_new_password(password, email, fail_silently: bool = False):
    """
    Not view function, It sends a new password to user email
    if this user forgot his password
    """
    mail_subject = 'Facepage: password reset'
    message = f"""
Your new password is: {password}\nPlease do NOT share it with anyone and
don't forget to change your password once you log in to Facepage again\n
AND DO NOT FORGET IT AGAIN!!! """
    email = EmailMessage(
            mail_subject,
            message,
            to=[email],
    )
    return email.send(fail_silently=fail_silently)

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

@DeprecationWarning
def verify_email_view(request: HttpRequest):
    return render(request, 'pages/VerificationSent.html')
