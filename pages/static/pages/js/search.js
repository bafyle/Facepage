var posts = document.getElementsByClassName("panel panel-default");
var people = document.getElementsByClassName("nearby-user");
var postsLabel = document.getElementById("posts-label");
var peopleLabel = document.getElementById("people-label");
var no_results = document.getElementById("no-results");

function postBtnClick()
{
    for(var i = 0; i < people.length; i++)
        people[i].style.display = 'none';
    if(peopleLabel != null)
        peopleLabel.style.display = 'none';
    if (postsLabel != null)
        postsLabel.style.display = 'block';

    if (posts.length > 0)
    {
        for(var i = 0; i < posts.length; i++)
            posts[i].style.display = 'block';
        no_results.style.display = 'none';
    }
    else
        no_results.style.display = 'block';
}
function peopleBtnClick()
{
    for(var i = 0; i < posts.length; i++)
        posts[i].style.display = 'none';
    if(peopleLabel != null)
        peopleLabel.style.display = 'block';
    if (postsLabel != null)
        postsLabel.style.display = 'none';
    if(people.length > 0)
    {
        for(var i = 0; i < people.length; i++)
            people[i].style.display = 'block';
        no_results.style.display = 'none';
    }
    else
        no_results.style.display = 'block';
}

function allBtnClick()
{
    if(posts.length > 0 || people.length > 0)
    {
        for(var i = 0; i < posts.length; i++)
            posts[i].style.display = 'block';
        for(var i = 0; i < people.length; i++)
            people[i].style.display = 'block';
        no_results.style.display = 'none';
    }
    else
        no_results.style.display = 'block';
    
    if(peopleLabel != null && postsLabel != null)
        peopleLabel.style.display = 'block';
    if(postsLabel != null)
        postsLabel.style.display ='block';
}
