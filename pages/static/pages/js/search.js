
var allBtn = document.getElementById("allbtn");
var peopleBtn = document.getElementById("peoplebtn");
var postBtn = document.getElementById("postsbtn");

var posts = document.getElementsByClassName("panel panel-default");
var people = document.getElementsByClassName("nearby-user");
var postsLabel = document.getElementById("posts-label");
var peopleLabel = document.getElementById("people-label");

postBtn.addEventListener('click', ()=> {
    for(var i = 0; i < people.length; i++)
    {
        people[i].style.display = 'none';
    }
    peopleLabel.style.display = 'none';

    for(var i = 0; i < posts.length; i++)
    {
        posts[i].style.display = 'block';
    }
});

peopleBtn.addEventListener('click', () => {
    for(var i = 0; i < posts.length; i++)
    {
        posts[i].style.display = 'none';
    }
    postsLabel.style.display ='none';

    for(var i = 0; i < people.length; i++)
    {
        people[i].style.display = 'block';
    }
});

allBtn.addEventListener('click', () => {
    for(var i = 0; i < posts.length; i++)
    {
        posts[i].style.display = 'block';
    }
    for(var i = 0; i < people.length; i++)
    {
        people[i].style.display = 'block';
    }
    peopleLabel.style.display = 'block';
    postsLabel.style.display ='block';
});

