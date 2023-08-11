// returns testNum from chart canvas
function getTestNum(chart){
    var canvas = chart.canvas.id;
    var testName = canvas.replace('Graph', "");
    var testNum = (parseInt(testName.replace('test', "")) - 1).toString()
    return testNum;
}

// applies popup html based on next/previous button press
function getPopup(testNum, direction){
    var popup = document.getElementById(keys[testNum] + "popupInfo");
    var popupBtn = document.getElementById(keys[testNum] + "popup-btn");
    
    var val = parseInt(popupBtn.dataset.value);
    const buttons = `<div class="row"><div class="col-6"><button onclick="getPopup(${testNum}, 'previous')" class="popup-page-btn" aria-label="Next Button">
        <i class="fa-solid fa-chevron-left" style="color: #ffffff;" role="img" aria-hidden="true"></i></button></div><div class="col-6">
        <button onclick="getPopup(${testNum}, 'next')" class="popup-page-btn" aria-label="Previous Button">
        <i class="fa-solid fa-chevron-right" style="color: #ffffff;" role="img" aria-hidden="true"></i></button></div></div>`;
    const firstButtons = `<div class="row"><div class="col-6"></div><div class="col-6">
        <button onclick="getPopup(${testNum}, 'next')" class="popup-page-btn" aria-label="Next Button">
        <i class="fa-solid fa-chevron-right" style="color: #ffffff;" role="img" aria-hidden="true"></i></button></div></div>`;
    const lastButtons = `<div class="row"><div class="col-6"><button onclick="getPopup(${testNum}, 'previous')" class="popup-page-btn" aria-label="Previous Button">
        <i class="fa-solid fa-chevron-left" style="color: #ffffff;" role="img" aria-hidden="true"></i></button></div></div>`;
    var htmlIndex;
    
    var htmlLabels = [
        'Press "Generate Timeline Graph" to show the data for Test ' + (testNum + 1) + firstButtons,
        'Hover the legend labels for information on individual datasets' + buttons,
        'Click the legend labels to hide specific datasets' + buttons,
        'Scroll or drag to zoom; Ctrl + drag to pan; Press refresh button to reset' + buttons,
        'Press "Generate Binary Graph" to show the pass/fail/ warning graph' + buttons,
        'Press "?" to disable help and information popups' + lastButtons
    ]
    
    if(direction == "next"){
        htmlIndex = val + 1;
    }
    else if(direction == "previous"){
        htmlIndex = val - 1;
    }
    else if(direction == "start"){
        htmlIndex = 0;
        if(popup){
            popoverList[testNum].hide();
        }
    }
    else{
        return;
    }
    popupBtn.dataset.value = htmlIndex.toString();
    popoverList[testNum]._config.content.innerHTML = htmlLabels[htmlIndex];
}