let analyzeData_form = $("#analyzeData_form");
let boiler_id_input = $("#boiler_id_input");
let start_time_input = $("#start_time_input");
let end_time_input = $("#end_time_input");
let error = $("#error");
let data = $("#data");
let response;
let keys;
let loadingSpinner = $("#loadingSpinner");
let modalBtn = $("#modal-btn");
let binDisplay = false;
let crosshair;
let popoverList;

function showSummary(){
    let errorModal = new bootstrap.Modal(document.getElementById("error-modal"), {});
    errorModal.show();
}

(async function ($) {
    // initial setup
    error.hide();
    data.empty();
    loadingSpinner.hide();
    modalBtn.hide();

    // check if user is authenticated
    let authenticated = await $.ajax({
        url: "/authenticated",
        type: "Get"
    });
    if(!authenticated.success){
        error.text("Not logged in!");
        error.show();
    }

    // analyzeData form submission
    analyzeData_form.submit(async function(e){
        e.preventDefault();
        error.hide();
        modalBtn.hide();
        data.empty();

        let boiler_id = boiler_id_input.val();
        let start_time = start_time_input.val();
        let end_time = end_time_input.val();
        let select = analyzeData_form.find("#selectInterval option:selected").val();
        analyzeData_form[0].reset();
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
            loadingSpinner.show();
            response = await $.ajax({
                url: "/analyze-data-post",
                type: "Post",
                data: {
                    "boiler_id": boiler_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "interval": select
                }
            });
            dailyWeather = await $.ajax({
                url: "/analyze-weather-post",
                type: "Post"
            });
            loadingSpinner.hide();
            
            if(response.success == undefined){
                response = JSON.parse(response);
                keys = Object.keys(response);
                let graphDisplay = "none";
                let binDisplay = "none";
                
                // register chart plugins
                registerPlugins();
                
                // add html for all tests
                for(let i = 0; i < keys.length; i++){
                
                    let test = $("<div class='container border test-wrapper my-3 mx-auto'></div>");
                    
                    let title;
                    if(response[keys[i]].status == "green"){      // green
                        title = $("<div class='row border bg-success'></div>");
                    }
                    else if(response[keys[i]].status == "red"){     // red
                        title = $("<div class='row border bg-danger'></div>");
                    }
                    else if(response[keys[i]].status == "yellow"){      // yellow
                        title = $("<div class='row border bg-warning'></div>");
                    }
                    else{
                        title = $("<div class='row border bg-light'></div>");
                    }
                    
                    title.append(
                        `<div class="col-4 col-sm-6 col-md-8 col-lg-2 col-xl-3 col-xxl-5 my-1"><h3 class="bold">Test ${i+1}</h3></div>`
                    );
                    title.append(
                        `<div class="col-4 col-xxl-3 d-none d-lg-block"><button id="${keys[i]}binButton" aria-label="Generate Binary Graph" 
                        onclick="createTestGraph(${i}, this)" class="btn btn-secondary my-1" style="visibility:hidden" value="${binDisplay}" 
                        data-chart-name="${keys[i]}Graph" data-bin-btn="${keys[i]}binButtonMenu">Generate Binary Graph</button></div>`
                    );
                    title.append(
                        `<div class="col-5 col-xl-4 col-xxl-3 d-none d-lg-block"><button id="${keys[i]}genButton" onclick="createTestGraph(${i}, this)" 
                        aria-label="Generate Timeline Graph" class="btn btn-secondary my-1" value="${graphDisplay}" data-chart-name="${keys[i]}Graph" 
                        data-bin-name="${keys[i]}binButton" data-bin-menu="${keys[i]}binButtonMenu" data-gen-btn="${keys[i]}genButtonMenu">Generate Timeline Graph</button></div>`
                    );
                    
                    title.append(
                        `<div class="col-5 col-sm-4 col-md-3 d-block d-lg-none"><div class="dropdown"><button class="btn btn-secondary dropdown-toggle my-1" 
                        aria-label="Graph Features Dropdown Button" style="padding: 10px 20px;" type="button" id="${keys[i]}graphMenuButton" 
                        data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Options</button><ul class="dropdown-menu dropdown-menu-end"
                        aria-labelledby="${keys[i]}graphMenuButton" id="${keys[i]}graphMenu"><li><button id="${keys[i]}genButtonMenu" style="width: 100%; text-align: center;" onclick="createTestGraph(${i}, this)" 
                        class="dropdown-item" value="${graphDisplay}" data-chart-name="${keys[i]}Graph" data-bin-name="${keys[i]}binButton" data-bin-menu="${keys[i]}binButtonMenu" 
                        data-gen-btn="${keys[i]}genButton">Generate Timeline Graph</button></li><li><button id="${keys[i]}binButtonMenu" style="width: 100%; text-align: center;" onclick="createTestGraph(${i}, this)" 
                        class="dropdown-item disabled" value="${binDisplay}" data-chart-name="${keys[i]}Graph" data-bin-btn="${keys[i]}binButton">Generate Binary Graph</button>
                        </li></ul></div></div>`
                    );
                    
                    title.append(
                        `<div hidden><div id="${keys[i]}popupInfo" data-name="popover-options">Press "Generate Timeline Graph" to show the data for Test ${i+1}<div class="row">
                        <div class="col-6"></div><div class="col-6"><button onclick="getPopup(${i}, 'next')" aria-label="Next Button" class="popup-page-btn">
                        <i class="fa-solid fa-chevron-right" role="img" aria-hidden="true" style="color: #ffffff;"></i></button></div></div></div></div>`
                    )
                    title.append(
                        `<div class="col-3 col-sm-2 col-md-1 d-flex align-items-center"><button type="button" id="${keys[i]}popup-btn" aria-label="Help Popup" 
                        class="popup btn btn-secondary" data-bs-toggle="popover" data-bs-placement="top" data-bs-container="body" data-value="0"><i class="fa-solid fa-question" 
                        role="img" aria-hidden="true"></i></button></div>`
                    )
                    
                    let info = $("<div class='row gx-0'></div>");
                    info.append(
                        `<div class="col-6 col-md-4 px-2"><p>${response[keys[i]].title}</p></div>`
                    );
                    info.append(
                        `<div class="col-6 col-md-4 d-flex"><div class="me-auto px-2">${((response[keys[i]].warning_ct / response[keys[i]].total_ct) * 100).toFixed(2)}% warnings
                        <span class="fa-stack percent-info" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true" title="${response[keys[i]].warning_ct} out of ${response[keys[i]].total_ct} points">
                        <i class="fa-solid fa-circle fa-stack-1x text-secondary" role="img" aria-hidden="true"></i><i class="fa-solid fa-info fa-2xs text-light fa-stack-1x" 
                        role="img" aria-hidden="true"></i></span></div><div class="ms-auto">${((response[keys[i]].error_ct / response[keys[i]].total_ct) * 100).toFixed(2)}% errors
                        <span class="fa-stack percent-info" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true" title="${response[keys[i]].error_ct} out of ${response[keys[i]].total_ct} points">
                        <i class="fa-solid fa-circle fa-stack-1x text-secondary" role="img" aria-hidden="true"></i><i class="fa-solid fa-info fa-2xs text-light fa-stack-1x" 
                        role="img" aria-hidden="true"></i></span></div></div>`
                    )
                    info.append(
                        `<div class="col-12 col-md-4"><div class="dataset-info" id="${keys[i]}dataInfo"></div></div>`
                    );
                    
                    let graph = $(`<div class="row"><div class="chart-wrapper mx-auto disabled" id="${keys[i]}chartWrap"><canvas id="${keys[i]}Graph" width="0" height="0"></canvas></div></div>`);

                    test.append(title);
                    test.append(info);
                    test.append(graph);
                    data.append(test)
                }
                
                // add daily weather data
                if(dailyWeather.success == undefined){
                    dailyWeather = JSON.parse(dailyWeather);
                    let weatherKeys = Object.keys(dailyWeather);
                    let weatherTable = $("<div class='container border test-wrapper mt-3 mb-5 mx-auto'></div>");
                    let title = $("<div class='row border bg-secondary'></div>");
                    title.append(
                        `<div class="col my-1 py-2"><h3 class="bold">Daily Weather Data</h3></div>`
                    );
                    let table = $("<div class='row border d-none d-md-flex'></div>");
                    let dropdown = $("<div class='row border d-flex d-md-none bg-light'></div>");
                    let columns = Object.keys(dailyWeather[weatherKeys[0]]);
                    let columnLabels = { "wdir": { "title": "Wind Direction", "units": "\xB0" }, "tavgF_day": { "title": "Avg Temp", "units": "\xB0F" }, 
                        "tminF_day": { "title": "Min Temp", "units": "\xB0F" }, "tmaxF_day": { "title": "Max Temp", "units": "\xB0F" }, 
                        "prcpIN_day": { "title": "Precipitation", "units": "in" }, "wspdMPH_day": { "title": "Wind Speed", "units": "mph" },
                        "presPSI_day": { "title": "Pressure", "units": "psi" }, "hdd": {"title": "HDD", "units": ""} }
                    let keepColumns = Object.keys(columnLabels)
                    
                    let row = '<div class="row py-2 border-bottom ms-0 fs-5"><div class="col bold">Date</div>';
                    for(let i = 0; i < columns.length; i++){
                        if(keepColumns.includes(columns[i])){
                            row += `<div class="col bold overflow" onclick="showOverflow(this)">${columnLabels[columns[i]]["title"]}</div>`;
                        }
                    }
                    row += '</div>';
                    table.append(row);
                    
                    let accordion = `<div class="accordion accordion-flush bg-light" id="weather-accordion">`;
                    for(let i = 0; i < weatherKeys.length; i++){
                        let date = weatherKeys[i].split("T")[0];
                        let yyyy_mm_dd = date.split("-");
                        let year = yyyy_mm_dd[0].split("");
                        let item = `<div class="accordion-item"><h5 class="accordion-header" id="date${date}-header"><button class="accordion-button bg-light collapsed" 
                            type="button" data-bs-toggle="collapse" data-bs-target="#date${date}" aria-expanded="false" aria-controls="date${date}">
                            <p class="h5 bold">${yyyy_mm_dd[1]}/${yyyy_mm_dd[2]}/${year[2]}${year[3]}</p></button></h5><div id="date${date}" 
                            class="accordion-collapse collapse" aria-labeledby="date${date}-header"><div class="accordion-body"><ul>`;
                        row = `<div class="row py-2 border-bottom ms-0"><div class="col">${yyyy_mm_dd[1]}/${yyyy_mm_dd[2]}/${year[2]}${year[3]}</div>`;
                        for(let j = 0; j < columns.length; j++){
                            if(keepColumns.includes(columns[j])){
                                let value = dailyWeather[weatherKeys[i]][columns[j]].toFixed(2);
                                item += `<li><b>${columnLabels[columns[j]]["title"]}</b>: ${value} ${columnLabels[columns[j]]["units"]}</li>`
                                row += `<div class="col">${value} ${columnLabels[columns[j]]["units"]}</div>`
                            }
                        }
                        item += "</ul></div></div></div>"
                        row += "</div>";
                        table.append(row);
                        accordion += item;
                    }
                    
                    accordion += "</div>"
                    dropdown.append(accordion);
                    weatherTable.append(title);
                    weatherTable.append(table);
                    weatherTable.append(dropdown)
                    data.append(weatherTable);
                }
                
                let errorModal = new bootstrap.Modal(document.getElementById("error-modal"), {});
                let redErrors = "";
                let yellowErrors = "";
                let hasRed = false;
                let hasYellow = false;
                
                for(let i = 0; i < keys.length; i++){
                    if(response[keys[i]].status == "red"){
                        redErrors += `<li>${response[keys[i]].errorMsg} (Test ${i + 1})</li>`
                        hasRed = true;
                    }
                    else if(response[keys[i]].status == "yellow"){
                        yellowErrors += `<li>${response[keys[i]].errorMsg} (Test ${i + 1})</li>`
                        hasYellow = true;
                    }
                }
                
                if(hasRed || hasYellow){
                    if(!hasRed){
                        redErrors = `<li>No red tests -- all tests under 25% error</li>`
                    }
                    if(!hasYellow){
                        yellowErrors = `<li>No yellow tests -- all tests over 25% error</li>`
                    }
                
                    redErrors = `<div class="accordion-item"><h5 class="accordion-header" id="red-header"><button class="accordion-button bg-danger bold" type="button" 
                    style="font-size: 1.15rem; padding: 14px 20px;" data-bs-toggle="collapse" data-bs-target="#red-panel" aria-expanded="true" aria-controls="red-panel" 
                    aria-label="Toggle Red Errors">Red Errors</button></h5><div id="red-panel" class="accordion-collapse collapse show" aria-labelledby="red-header"><div class="accordion-body">` + redErrors;

                    yellowErrors = `<div class="accordion-item"><h5 class="accordion-header" id="yellow-header"><button class="accordion-button collapsed bg-warning bold" 
                    type="button" style="font-size: 1.15rem; padding: 14px 20px;" data-bs-toggle="collapse" data-bs-target="#yellow-panel" aria-expanded="false" 
                    aria-controls="yellow-panel" aria-label="Toggle Yellow Errors">Yellow Errors</button></h5><div id="yellow-panel" 
                    class="accordion-collapse collapse" aria-labelledby="yellow-header"><div class="accordion-body">` + yellowErrors;
                }
                
                if(!hasRed && !hasYellow){
                    redErrors = `<h5 class="bold">No errors -- all tests passed</h5>`
                }
                else{
                    redErrors = '<div class="accordion accordian-flush">' + redErrors + "</div></div></div>";
                    yellowErrors += "</div></div></div></div>"
                }
                
                document.getElementById("error-modal-body").innerHTML = redErrors + yellowErrors;
                errorModal.show();
                modalBtn.show();
                
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
                
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
                
            } else {
                error.text("Selected time interval or boiler has no data to analyze!");
                error.show();
            }
        }
    });
})(window.jQuery);

// call graph function based on button press
async function createTestGraph(testNum, button){
    if(button.id == keys[testNum] + "binButton" || button.id == keys[testNum] + "binButtonMenu"){
        createBinaryGraph(testNum, button);
    }
    else{
        createTimelineGraph(testNum, button);
    }
}