from django.contrib import admin
from .models import Profile, Friend, ForgetPassswordRequests

admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(ForgetPassswordRequests)