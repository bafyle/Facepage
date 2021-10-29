from django.contrib import admin
from .models import Profile, Friend, EmailRequest

admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(EmailRequest)