function showMoreFunction(id, button_id)
{
    var container = document.getElementById(id);
    var dots = null;
    var moreText = null;
    var btnText = document.getElementById(button_id);
    for(var i = 0; i < container.children.length; i++)
    {
        if(container.children[i].classList.contains('dots'))
            dots = container.children[i];
        else if(container.children[i].classList.contains('more'))
            moreText = container.children[i];
        
    }
    if(dots && moreText && btnText)
    {
        
        dots.style.display = "none";
        btnText.style.display = 'none';
        moreText.style.display = "inline";
        
    }
    
    console.log(dots, moreText, btnText, container);
}