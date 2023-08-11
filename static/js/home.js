(async function ($) {
    let login_form = $("#login_form");
    let login_text = $("#login_text");
    let email_input = $("#email");
    let password_input = $("#password");
    let nav_links = $(".nav-link");
    let profileText = $('#profileText');
    let navbar_nav = $('.navbar-nav');
    let side_bar = $('#home')
    let loadingSpinner = $("#loadingSpinner");
    let submitButton = $("#submitButton");
    
    loadingSpinner.hide();
    submitButton.show();

    // login form submission
    login_form.submit(async function(e){
        
        e.preventDefault();
        let email = email_input.val();
        let password = password_input.val();
        let valid = true;

        // input handling
        if(!email){ 
            valid = false;
        }
        if(!password){
            valid = false;
        }

        // ajax call to python backend
        if(valid){
            submitButton.hide();
            loadingSpinner.show();
            let response = await $.ajax({
                url: "/login",
                type: "Post",
                data: {"email": email, "password": password}
            });
            if(response == 'success'){
                let user = await $.ajax({
                    url: "/user",
                    type: "Get",
                });
                if(user.success){
                    window.location.assign("/");      // go to home url
                }
                else{
                    submitButton.show();
                    loadingSpinner.hide();
                    login_form[0].reset();
                }
            } else {
                if(response == "USER_NOT_FOUND"){
                    submitButton.show();
                    loadingSpinner.hide();
                    login_form[0].reset();
                }
                else if(response == "PASSWORD_NOT_MATCH"){
                    submitButton.show();
                    loadingSpinner.hide();
                    login_form[0][1].value = "";
                }
                else{
                    submitButton.show();
                    loadingSpinner.hide();
                    login_form[0].reset();
                }
            }
        }
        login_form[0].classList.add('was-validated');
    });
})(window.jQuery);