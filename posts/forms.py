from django import forms

class CreatePostForm(forms.Form):
    image = forms.ImageField(required=False)
    content = forms.CharField()