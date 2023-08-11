var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverOptions = [].slice.call(document.querySelectorAll('[data-name="popover-options"]'))
let i = -1;
popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    i++;
    var options = {
        html: true,
        content: popoverOptions[i]
    }
    return new bootstrap.Popover(popoverTriggerEl, options);
});

let topBtn = document.getElementById("top-btn");
window.onscroll = function() { scrollFunction() };

function scrollFunction(){
    if(document.body.scrollTop > 20 || document.documentElement.scrollTop > 20){
        topBtn.style.display = "block";
    }
    else{
        topBtn.style.display = "none";
    }
}

function toTop(){
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

function toTable(){
    let sidebar = document.getElementById("sidebarMenu");
    if(sidebar.classList.contains("show")){
        let collapse = new bootstrap.Collapse(sidebar);
        collapse.hide();
    }
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}