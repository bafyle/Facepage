from django.shortcuts import render
from .models import Notification
# Create your views here.

def testView(request):
    notifications = Notification.objects.filter(user_to=request.user).order_by('-date')[0:10]
    context = {
        'navbar_name': request.user.first_name,
        'navbar_link': request.user.profile.link,
        'profile_pic': request.user.profile.profile_picture.url,
        'notifications': notifications,
    }
    return render(request, 'pages/NewNotifications.html', context);