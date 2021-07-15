from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class DeleteAccountForm(forms.Form):
    username = forms.CharField(max_length=100, label='Your username')
    confirmation = forms.CharField(widget=forms.Textarea, label='Confirmation')

class ChangePictureBioForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label='First name', required=False)
    last_name = forms.CharField(max_length=150, label='Last name', required=False)
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'phone_number', 'gender', 'birthday']
        widgets = {
            'bio': forms.Textarea(),
            'birthday': forms.DateInput(format='%d/%m/%Y'),
        }

class RegisterForm(UserCreationForm):
    birthday = forms.DateField(widget=forms.DateInput())
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=[('M', 'Male'), ('F', 'Female')])

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']


    
