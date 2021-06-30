from django import forms

class SendMessageForm(forms.Form):
    message_input = forms.CharField(widget=forms.Textarea, max_length=1000)