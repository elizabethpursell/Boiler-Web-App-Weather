(async function ($) {
    let data_form = $("#data_form");
    let boiler_id_input = $("#boiler_id_input");
    let start_time_input = $("#start_time_input");
    let end_time_input = $("#end_time_input");
    let error = $("#error");
    let data = $("#data");

    // initial setup
    error.hide();
    data.empty();

    // data form submission
    data_form.submit(async function(e){
        e.preventDefault();
        error.hide();
        data.empty();

        let boiler_id = boiler_id_input.val();
        let start_time = start_time_input.val();
        let end_time = end_time_input.val();
        let select = analyzeData_form.find("#selectInterval option:selected").val();
        data_form[0].reset();
        let valid = true;

        // input handling
        if(!boiler_id){
            error.text("Must supply boiler ID!");
            error.show();
            valid = false;
        }
        if(!start_time){
            error.text("Must supply start time!");
            error.show();
            valid = false;
        }
        if(!end_time){
            error.text("Must supply end time!");
            error.show();
            valid = false;
        }
        if(!select){
            error.text("Must select time interval!");
            error.show();
            valid = false;
        }

        start_time = start_time + ":00.000Z"
        end_time = end_time + ":00.000Z"
        // ajax call to python backend
        if(valid){
            let response = await $.ajax({
                url: "/data-post",
                type: "Post",
                data: {
                    "boiler_id": boiler_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "interval": select
                }
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