from django import forms
from .models import Profile

class DeleteAccountForm(forms.Form):
    username = forms.CharField(max_length=100, label='Your username')
    confirmation = forms.CharField(widget=forms.Textarea, label='Confirmation')

class ChangePictureBioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'first_name', 'last_name']