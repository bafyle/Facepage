from django.contrib import admin
from .models import Profile, Friend, SendEmailRequest, NewAccountActivationLink

admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(SendEmailRequest)
admin.site.register(NewAccountActivationLink)
