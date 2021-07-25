onmessage = function(link)
{
    var xhr = new XMLHttpRequest();

    xhr.open("GET", link.data, true);

    xhr.onload = function()
    {
        if(this.status === 200)
        {
            postMessage(this.responseText);
        }
    }
    xhr.send();
}

