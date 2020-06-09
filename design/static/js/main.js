$( document ).ready(function() {
    //Chrome has an issue where double click in Unity does
    //a select all on the whole page
    //This disables default behavior for multi-clicks
    document.addEventListener('mousedown', function (event) {
        if (event.detail > 1) {
        event.preventDefault();
        }
    }, false);    
});