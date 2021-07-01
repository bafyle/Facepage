from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import DeleteAccountForm, ChangePictureBioForm
from .models import Profile
from pathlib import Path
import os
from django.contrib.auth.models import User

# Create your views here.

def index(request):
    """
    view the login page or redirects to the home page if you are already logged in
    """
    if request.user.is_authenticated:
        return redirect('posts:home')
    return render(request, 'users/index.html', {})

def loginFunction(request):
    """
    this function takes the username and the password the user entered and
    check if they are valid or not. If they are vaild then it log you in and redirects 
    you to the index where itself redirects you to the home page
    """
    if request.user.is_authenticated:
        return redirect('posts:home')
    elif request.method == 'POST':
        username = request.POST['username']
        pw = request.POST['password']
        user = authenticate(username=username, password=pw)
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "wrong username or password")
    return redirect('users:index')

def logoutFunction(request):
    """
    this function log you out and redirects you to the login page
    """
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('users:index')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            new_profile = Profile(user=User.objects.get(username=request.POST.get('username')))
            new_profile.save()
            messages.success(request, "New account has been created, you can login now")
            return redirect('users:index')
    else:
        form = UserCreationForm()
    context = {'form':form}
    return render(request, 'users/register.html', context=context)

def accountSettings(request):
    """
    Takes the new user email and password and check if they are vaild and save them
    after saving it redirects to the login page to login again with the new data
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST['password1'] != request.POST['password2']:
                messages.error(request, "Passwords doesn't match")
                return redirect('users:settings')
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
                    messages.error(request, "password must have a at least 1 capitcal letter and it cannot be entirely numeric")
                    return redirect('users:settings')
            return redirect('users:index')
        else:
            default_values_for_form = dict()
            default_values_for_form['bio'] = request.user.profile.bio
            default_values_for_form['first_name'] = request.user.profile.first_name
            default_values_for_form['last_name'] = request.user.profile.last_name
            bio_form = ChangePictureBioForm(default_values_for_form)
            return render(request, 'users/settings.html', {'username':request.user.username, 'email': request.user.email, 'bio_form': bio_form})
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')

def changeBioAndProfilePicture(request):
    """
    This function is for changing the unnecessary data for the account like first and last name, 
    profile picture and bio
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            bioForm = ChangePictureBioForm(request.POST, request.FILES)
            if bioForm.is_valid():
                if bioForm.cleaned_data['profile_picture'] != 'profile_pics/default.jpg':
                    request.user.profile.profile_picture = bioForm.cleaned_data['profile_picture']
                request.user.profile.bio = bioForm.cleaned_data['bio']
                request.user.profile.first_name = bioForm.cleaned_data['first_name']
                request.user.profile.last_name = bioForm.cleaned_data['last_name']
                request.user.profile.save()
                messages.success(request, "changes saved")
            else:
                messages.error(request, "invalid data has been entered")
        return redirect('users:settings')
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
            messages.error(request, "you dont have a profile picture to delete")
            return redirect('users:settings')
        new_profile = Profile(bio=request.user.profile.bio,
                            first_name = request.user.profile.first_name,
                            last_name = request.user.profile.last_name,
        )
        request.user.profile.delete()
        new_profile.user = request.user
        new_profile.save()
        messages.success(request, "Profile picture deleted")
        return redirect('users:settings')
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
            return render(request, 'users/delete.html', context={'form': form})
        else:
            messages.error(request, "Can not delete a superuser account")
            return redirect('posts:home')
    else:
        messages.error(request, "you must login first")
        return redirect('users:index')


def deletePhoto(mediaPath):
    this_file_dir = Path(__file__).resolve().parent.parent
    file_path_without_edit = str(this_file_dir) + mediaPath
    file_path = file_path_without_edit.replace('\\', '/', -1)
    if os.path.isfile(file_path):
        os.remove(file_path)