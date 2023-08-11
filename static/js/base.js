function showConfirm(){
    let logoutModal = new bootstrap.Modal(document.getElementById("logout-modal"), {});
    logoutModal.show();
}

function collapseSidebar(){
    let sidebar = document.getElementById("sidebarMenu");
    if(sidebar.classList.contains("show")){
        let collapse = new bootstrap.Collapse(sidebar);
        collapse.hide();
    }
}

$(window).scroll(function() {
	var scrollDistance = $(window).scrollTop() + 150;

    $('.page-section').each(function(i) {
    	if ($(this).position().top <= scrollDistance) {
			$('.help-nav a.active').removeClass('active');
			$('.help-nav a').eq(i).addClass('active');
   		}
	});
}).scroll();

$(".collapse-animation").click(function () {
    $(this.querySelector('.collapse-right')).toggleClass("collapse-down");
})
