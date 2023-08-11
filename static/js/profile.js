(async function ($) {
    let logout_button = $('#logout_button');
    let error = $("#error");

    // check if user is authenticated
    let authenticated = await $.ajax({
        url: "/authenticated",
        type: "Get"
    });
    if(!authenticated.success){
        error.text("Not logged in!");
        error.show();
    }
})(window.jQuery);