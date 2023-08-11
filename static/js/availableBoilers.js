(async function ($) {
    let error = $("#error");
    let data = $("#data");
    let loadingSpinner = $("#loadingSpinner");
    let pageTitle = $("#pageTitle");

    // initial setup
    error.hide();
    pageTitle.hide();
    data.empty();

    // check to see if user is authenticated
    let authenticated = await $.ajax({
        url: "/authenticated",
        type: "Get"
    });
    if(!authenticated.success){
        error.text("Not logged in!");
        error.show();
    }

    // ajax call to python backend
    let response = await $.ajax({
        url: "/available-boilers-data",
        type: "Get"
    });
    loadingSpinner.hide();
    pageTitle.show();
    if(response.success == undefined){
        response = JSON.parse(response);
        for(let i=0; i<response.length; i++){
            if(JSON.stringify(response[i]).length != 0){
            
                // new bootstrap card approach
                card = $(`<div class="card col-sm-6 col-lg-4 col-xl-3"></div>`);
                card.append(`<img class="card-img-top mx-auto my-3 boiler-img" src="${response[i].image}" alt="Boiler Image" loading="lazy" decoding="async">`);
                cardBody = $(`<div class="card-body text-center d-flex flex-column"></div>`);
                cardBody.append(`<h3 class="card-title bold">${response[i].name}</h3>`);
                cardBody.append(`<p class="card-text normal">State: ${response[i].state}</br>Status: ${response[i].status}</p>`);
                let data_url = `/diagnostics/${response[i].name}/${response[i].id}`
                cardBody.append(`<a href="${data_url}" class="btn btn-primary mt-auto" style="padding:8px 24px;" role="button" aria-label="Run Diagnostics Button">Run diagnostics &raquo</a>`);
                
                card.append(cardBody);
                data.append(card);
            }
        }
    } else {
        error.text("Cannot retrieve available boilers!");
        error.show();
    }
})(window.jQuery);