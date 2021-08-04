from django.shortcuts import render

# Create your views here.

def testView(request):
    return render(request, 'pages/Notifications.html');