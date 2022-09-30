# Facepage

Facepage is a two-person project to make a minimal website that looks like Facebook as a challenge for ourselves using Python programming language and Django web framework

## Content:
- [Facepage](#facepage)
  - [Content:](#content)
  - [Technologies and Dependencies](#technologies-and-dependencies)
  - [Create Virtual Environment](#create-virtual-environment)
  - [Running the server](#running-the-server)
  - [User interactions](#user-interactions)

## Technologies and Dependencies
The website is made using these technologies:
* Python 3
* Django 3.2 library
* Django channels for handling sockets
All dependencies needed are in requirement.txt file. Installing dependencies are in [create virtual environment](#create-virtual-environment) section

## Create Virtual Environment
* If you don't have virtualenv installed in python, install it using:
~~~
$ pip install virtualenv
~~~
* After that go ahead and open the console where you want to make your virtual environment and type:
~~~
$ virtualenv venv
~~~
You can change 'venv' to anything else if you want

* Activate you virtual environment by:
~~~
$ cd ./venv/Scripts/
$ ./activate
~~~
* Now you can install any python library you want without affecting your main python interpreter

* From here you can install the dependencies into your new environment
~~~
$ pip install -r requirements.txt
~~~

## Running the server
After installing Pillow and six using pip, you can clone the repo and run the server by going the repo folder (which is Facepage) and running this command:
~~~
$ python manage.py runserver
~~~
a message will pop like this
~~~
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
July 27, 2021 - 21:25:07
Django version 3.2.5, using settings 'facepage.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
~~~
Go to https://127.0.0.1:8000/ and the login page will be there waiting for you

## User interactions
users can:

* Login and register
* Create, delete, update and share posts
* Like and comment on posts
* View other users posts
* Make friends with other users
* View their profile
* Chat with friends
* Change account settings (password, first name, last name, etc...)
* Change profile picture
* Change profile cover picture
* Search for users or posts
* Get notifications about likes, comments and friend requests


## Todo:
- [ ] Better password reset mechanism
- [x] Make users have finite amount of login attempts
- [x] Make users cannot spam forget password requests
- [x] Add styling to these buttons:
    * Send friend request
    * Cancel friend request
    * Unfriend
- [x] Redesign the chat app using websocket (The project now uses ASGI/Channels)
- [x] Test the new redesigned chat
- [ ] Change the backend of the WebSocket from InMemoryChannelLayer to redis
- [ ] Implement some functionalities using AJAX:
  * [x] Like a post
  * [ ] Comment
- [ ] Make media management system (far future)
- [x] Redesign the friendship system between the users (if needed)
- [x] Use signals in:
  * Sending notifications (alpha version, needs some redesigns)
    - [x] use SSE to push notification alarm (needs a redesign for the frontend)
  * Creating the profile and activation link objects for the new registered users
- [ ] Implement background processes using Celery like:
  * [x] Compress the uploaded photos
  * [ ] deactivate or delete inactive users
- [ ] Document the code

  

