# Facepage

Facepage is a two-person project to make a minimal website that looks similar to Facebook as a challenge and practice for ourselves on backend development and frontend development.
Facepage is built using Python programming language and Django web framework and other technologies that explained in the [Technologies and Dependencies](#technologies-and-dependencies) section.

## Content:
- [Facepage](#facepage)
  - [Content:](#content)
  - [Technologies and Dependencies](#technologies-and-dependencies)
  - [User interactions](#user-interactions)
  - [Todo:](#todo)

## Technologies and Dependencies
The main packages are:
* Python 3.7+
* Django 3.2 library
* django-channels 3.0.5
* jQuery 3.6.0

All packages and dependencies are in requirements.txt file.

## User interactions
users can:

* Login and register
* Create posts, delete and update their posts and share other people posts
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
- [ ] Implement media management system (far future)
- [x] Redesign the friendship system between the users (if needed)
- [x] Use signals in:
  * Sending notifications (alpha version, needs some redesigns)
    - [ ] use SSE to push notification alarm (needs a redesign for the frontend to work)
  * Creating the profile and activation link objects for the new registered users
- [x] Uploading media to AWS
- [x] Optimize database queries
- [x] Deploy the project on heroku
- [ ] Implement background processes using Celery like:
  * [x] Compress the uploaded photos
  * [ ] deactivate or delete inactive users
- [ ] Document the code
  * [ ] Compress the uploaded media before storing them in aws
- [x] Adding a limit to login attempts (users have to wait 5 minutes after 3 failed login attempts)

  

