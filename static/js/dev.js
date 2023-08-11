(async function ($) {
    let error = $("#error");
    let data = $("#data");
    let devButton = $("#devButton");

    // initial setup
    error.hide();
    data.empty();
    $('#devLink').addClass('active');

    // ajax call to python backend
    devButton.click(async function() {
        let response = await $.ajax({
            url: "/dev",
            type: "Get"
        });
        console.log(response);
    });   
})(window.jQuery);