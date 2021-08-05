# Facepage

Facepage is two-person project to make minimal website that looks like Facebook for the purpose of learning using Python and Django

## Content:
- [Facepage](#facepage)
  - [Content:](#content)
  - [Technologies and Dependencies](#technologies-and-dependencies)
  - [Create Virtual Environment](#create-virtual-environment)
  - [Running the server](#running-the-server)
  - [User interactions](#user-interactions)

## Technologies and Dependencies
The website is made using these technologies:
* Python 3.9.1 64bit
* Django 3.2.5 library
* SQLite3 Database
* HTML, CSS, bootstrap, Javascript, jQuery

Python libraries that has been used:
* Pillow 8.1.2
* six 1.16.0

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

* Activate you virtual environment by going to:
~~~
$ cd ./venv/Scripts/
$ ./activate
~~~
* Now you can install any python library you want without affecting your main python interpreter

* From here you can install django and the dependencies into you new environment

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
Simply by holding CTRL and clicking that link, your main browser will open with the login page

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
