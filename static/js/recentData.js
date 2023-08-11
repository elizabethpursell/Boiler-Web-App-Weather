(async function ($) {
    let recentData_form = $("#recentData_form");
    let boiler_id_input = $("#boiler_id_input");
    let error = $("#error");
    let data = $("#data");

    // initial setup
    error.hide();
    data.empty();

    // recentData form submission
    recentData_form.submit(async function(e){
        e.preventDefault();
        error.hide();
        data.empty();

        let boiler_id = boiler_id_input.val();
        recentData_form[0].reset();
        let valid = true;

        // input handling
        if(!boiler_id){
            error.text("Must supply boiler ID!");
            error.show();
            valid = false;
        }

        // ajax call to python backend
        if(valid){
            let response = await $.ajax({
                url: "/recent-data-post",
                type: "Post",
                data: {"boiler_id": boiler_id}
            });
            if(response.success == undefined){
                response = JSON.parse(response);
                for(let i=0; i<response.length; i++){
                    if(JSON.stringify(response[i]).length != 0){
                        data.append(
                            `<div class="col-lg-6 border"><pre>${JSON.stringify(response[i], undefined, 4)}</pre></div>`
                        );
                    }
                }
            } else {
                error.text("Cannot retrieve data from the supplied boiler ID!");
                error.show();
            }
        }
    });
})(window.jQuery);