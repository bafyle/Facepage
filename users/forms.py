from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class DeleteAccountForm(forms.Form):
    username = forms.CharField(max_length=100, label='Your username')
    confirmation = forms.CharField(widget=forms.Textarea, label='Confirmation')

class ChangePictureBioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'first_name', 'last_name', 'phone_number', 'gender']

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    birthday = forms.DateField(widget=forms.DateInput())
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=[('M', 'Male'), ('F', 'Female')])
