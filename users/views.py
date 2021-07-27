from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from facepage.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .forms import DeleteAccountForm, ChangePictureBioForm, RegisterForm
from .models import Profile
from .id_generator import id_generator
from pathlib import Path
from django.contrib.auth.models import User
from .models import Friend
from notifications.models import Notification

import os

# Create your views here.

def index(request):
    """
    view the login page or redirects to the home page if you are already logged in
    """
    if request.user.is_authenticated:
        return redirect('posts:home')
    return render(request, 'pages/Login.html')

def loginFunction(request):
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
            login(request, user)
        else:
            messages.error(request, "wrong username or password")
    return redirect('users:index')

def logoutFunction(request):
    """
    this function logs you out and redirects you to the login page
    """
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('users:index')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                newLink = ''
                while True:
                    id_generated = id_generator(user, settings.ID_LENGTH)
                    if User.objects.filter(profile__link=id_generated).count() == 0:
                        newLink = id_generated
                        break
                new_profile = Profile(user=user, link=newLink, birthday=form.cleaned_data['birthday'], gender=form.cleaned_data['gender'])
                new_profile.save()
                sendEmail(request, user)
                return redirect('users:verification-sent')
            except Exception as e:
                user.delete()
                raise e
        else:
            messages.error(request, "Invalid input")
            return render(request, 'pages/Register.html', {'form':form})
    else:
        form = RegisterForm()
    return render(request, 'pages/Register.html', {'form':form})

def addFriend(request, link):
    """
    Not working right now since there is no button to invoke it

    This view create a new Friend in the Friends table between request.user and username
    """
    new_relation = Friend(side1=request.user, side2=User.objects.get(profile__link=link))
    try:
        new_relation.save()
        if Notification.objects.filter(user_from=request.user, user_to=new_relation.side2, route_id=request.user.profile.link).count() <= 0:
            notification_content = f"{request.user.first_name} {request.user.last_name} sent you a friend request"
            newNotification = Notification(
                user_from=request.user,
                user_to=new_relation.side2,
                content=notification_content,
                type='F',
                picture=request.user.profile.profile_picture.url,
                route_id=request.user.profile.link
            )
            newNotification.save()
    except:
        messages.error(request, f"you already a friend with {new_relation.side2.profile.name()}")
        return redirect('posts:home')
    finally:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def accountSettings2(request):
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
                for errorMessage in error:
                    messages.error(request, errorMessage)
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

@DeprecationWarning
def accountSettings(request):
    """
    Takes the new user email and password and check if they are valid and save them
    after saving it redirects to the login page to login again with the new data
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST['password1'] != request.POST['password2']:
                messages.error(request, "Passwords doesn't match")
                return redirect('users:account-settings')
            else:
                new_password = request.POST['password1']
                password_security = 0
                for char in new_password:
                    char = str(char)
                    if char.isalpha():
                        password_security += 1
                    if char.isupper():
                        password_security += 1
                if password_security > 2:
                    user = request.user
                    user.set_password(request.POST['password1'])
                    if request.POST['email'] is not None:
                        user.email = request.POST['email']
                    else:
                        user.email = ''
                    user.save()
                    messages.success(request, "password has changed, you need to login again")
                else:
                    messages.error(request, "password must have a at least 1 uppercase letter and it cannot be entirely numeric")
                    return redirect('users:account-settings')
            return redirect('users:index')
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

def personalSettings(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            bioForm = ChangePictureBioForm(request.POST, request.FILES)
            if bioForm.is_valid():
                if bioForm.cleaned_data['profile_picture'] != 'profile_pics/default.jpg':
                    old_image = request.user.profile.profile_picture.url
                    if old_image.split('/')[-1] != 'default.jpg':
                        deletePhoto(old_image)
                    request.user.profile.profile_picture = bioForm.cleaned_data['profile_picture']
                if bioForm.cleaned_data['profile_cover'] != 'profile_covers/default.jpg':
                    old_image = request.user.profile.profile_cover.url
                    if old_image.split('/')[-1] != 'default.jpg':
                        deletePhoto(old_image)
                    request.user.profile.profile_cover = bioForm.cleaned_data['profile_cover']
                request.user.profile.bio = bioForm.cleaned_data['bio']
                request.user.first_name = bioForm.cleaned_data['first_name']
                request.user.last_name = bioForm.cleaned_data['last_name']
                request.user.profile.phone_number = bioForm.cleaned_data['phone_number']
                request.user.profile.gender = bioForm.cleaned_data['gender']
                request.user.profile.birthday = bioForm.cleaned_data['birthday']
                request.user.profile.save()
                request.user.save()
                messages.success(request, "changes saved")
            else:
                messages.error(request, "invalid data has been entered")
        else:
            default_values_for_form = {
                'bio': request.user.profile.bio,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': request.user.profile.phone_number,
                'gender': request.user.profile.gender,
                'birthday': request.user.profile.birthday.strftime("%Y-%m-%d"),
            }
            bioForm = ChangePictureBioForm(default_values_for_form)
        context = {
            'profile_pic': request.user.profile.profile_picture.url,
            'profile_cover': request.user.profile.profile_cover.url,
            'navbar_name': request.user.first_name,
            'navbar_link': request.user.profile.link,
            'email': request.user.email,
            'username': request.user.username,
            'bio_form': bioForm,
        }
        return render(request, 'pages/newPersonalSettings.html', context)
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def deleteMyProfileCover(request):
    if request.user.is_authenticated:
        old_image = request.user.profile.profile_cover.url
        if old_image.split('/')[-1] != 'default.jpg':
            deletePhoto(old_image)
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

def deleteMyProfilePicture(request):
    """
    This function is for deleting the existing profile picture of the account
    and set it to the default one by deleting the profile instance from the
    database and create a new one
    """
    if request.user.is_authenticated:
        old_image = request.user.profile.profile_picture.url
        if old_image.split('/')[-1] != 'default.jpg':
            deletePhoto(old_image)
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

def deleteAccount(request):
    """
    This function makes sure that the user want to delete his account
    it takes the confirmations and the username text from the user 
    and check if they are correct and deletes the account
    """
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            if request.method == 'POST':
                form = DeleteAccountForm(request.POST)
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
            return render(request, 'pages/DeleteAccount.html', context={'form': form})
        else:
            messages.error(request, "Can not delete a superuser account")
            return redirect('posts:home')
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')


def sendEmail(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your Facepage account.'
    message = render_to_string('pages/AccountActivation.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
    })
    email = EmailMessage(
            mail_subject,
            message,
            to=[user.email],
    )
    email.send()

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
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

def verifyEmailView(request):
    return render(request, 'pages/VerificationSent.html')

def deletePhoto(mediaPath):
    print(mediaPath)
    this_file_dir = Path(__file__).resolve().parent.parent
    file_path_without_edit = str(this_file_dir) + mediaPath
    file_path = file_path_without_edit.replace('\\', '/', -1)
    if os.path.isfile(file_path):
        os.remove(file_path)