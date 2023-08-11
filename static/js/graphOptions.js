// sets graph axis settings
function scalesOpt (testNum) {
    return { x: { type: "category", labels: response[keys[testNum]].labels, ticks: { maxTicksLimit: 8 } },
             "left": response[keys[testNum]].left,
             "right": response[keys[testNum]].right,
             "binY": { type: "category", labels: ["Status"], position: "left", display: false }
           }
}

// sets y-axis ticks using dynamic function
const ticks = { callback: function (value, index, values) {
                      // adds "Status" label if binary graph shown
                      if(index == values.length - 1 && binDisplay){
                          return "Status";
                      }
                      return value;
                  }
              }

// set graph's zoom settings
const zoomOpt = { limits: {
                     "left": { min: 'original', max: 'original' },
                     "right": { min: 'original', max: 'original' }
                  },
                  pan: { enabled: true, mode: 'x', modifierKey: "ctrl" },
                  zoom: { drag: { enabled: true, backgroundColor: 'rgba(0,255,255,0.3)' },
                          wheel: { enabled: true },
                          pinch: { enabled: true },
                          mode: 'x'
                        }
                }

// sets tooltip color based on pass/fail/warning status
function colorTooltip(tooltip){
    try{
        let length = tooltip.tooltipItems.length - 2;
        let color = "rgba(0, 166, 30, 0.8)";        // pass = green
        if(binDisplay){
            length -= 1;
        }
        for(let i = length; i >= 0; i--){
            if(tooltip.tooltipItems[i].dataset.pointBackgroundColor[tooltip.tooltipItems[i].dataIndex] == "#FF0000"){
                return "rgba(219, 4, 0, 0.8)";      // error = red
            }
            else if(tooltip.tooltipItems[i].dataset.pointBackgroundColor[tooltip.tooltipItems[i].dataIndex] == "#FFC107"){
                color = "rgba(255, 165, 0, 0.8)";       // warning = yellow
            }
        }
        return color;
    }
    catch{
        return "rgba(0, 0, 0, 0.8)";        // other = grey
    }
}

// sets tooltip label
function labelTooltip (tooltipItems){
    let length = tooltipItems.length - 2;
    let label = "";
    if(binDisplay){
        length -= 1;
    }
    for(let i = length; i >= 0; i--){
        if(tooltipItems[i].dataset.pointBackgroundColor[tooltipItems[i].dataIndex] == "#FF0000"){
            return "Error Point";       // red = error
        }
        else if(tooltipItems[i].dataset.pointBackgroundColor[tooltipItems[i].dataIndex] == "#FFC107"){
            label = "Warning Point";    // yellow = warning
        }
    }
    return label;       // other = no label
}

// adds y-values to tooltip
function valueTooltip (tooltipItem) {
    var label = tooltipItem.dataset.label;
    if(label == "Error Point" || label == "Pass/Fail" || label == "Warning Point" || label.includes("Threshold")){
        return "";
    }
    else{
        return tooltipItem.dataset.label + "\t" + tooltipItem.dataset.data[tooltipItem.dataIndex].toFixed(2);
    }
}

// sets legend labels      
const legendLabels = function (chart) {
    const labels = Chart.defaults.plugins.legend.labels.generateLabels(chart);
    const lineLabels = labels.filter((el, index) => el.text != "Pass/Fail" && (el.text != "Warning Point" || index == 1) && (el.text != "Error Point" || index == 0) && !el.text.includes("Threshold"));
    binData = labels.filter((el, index) => el.text == "Pass/Fail");
    
    // separate pass/fail/warning labels if binary graph shown
    if(binData.length > 0){
        lineLabels.push({
            text: "Pass",
            fillStyle: "#00A61E",
            strokeStyle: "#00A61E",
            hidden: binData[0].hidden,
            datasetIndex: labels.length - 1
        });
        lineLabels.push({
            text: "Fail",
            fillStyle: "#FF0000",
            strokeStyle: "#FF0000",
            hidden: binData[0].hidden,
            datasetIndex: labels.length - 1
        });
        lineLabels.push({
            text: "Warning",
            fillStyle: "#FFC107",
            strokeStyle: "#FFC107",
            hidden: binData[0].hidden,
            datasetIndex: labels.length - 1
       });
    }
    return lineLabels;
}

// hides/shows datasets on legend click
const displayDatasets = function (click, legendItem, legend) {
    let index = legendItem.datasetIndex;
    let testNum = getTestNum(legend.chart);
    let popupBtn = document.getElementById(keys[testNum] + "popup-btn");
    if(legend.chart.isDatasetVisible(index)){
        legend.chart.hide(index);
        if(index == 0){         // hide all warning datasets
            for(let i = (index + 1); i < legend.chart._metasets.length; i++){
                if(legend.chart._metasets[i].label == "Warning Point"){
                    legend.chart.hide(i);
                }
            }
        }
        else if(index == 1){        // hide all error datasets
            for(let i = (index + 1); i < legend.chart._metasets.length; i++){
                if(legend.chart._metasets[i].label == "Error Point"){
                    legend.chart.hide(i);
                }
            }
        }
        legendItem.hidden = true;
    }
    else{
        legend.chart.show(index);
        if(index == 0){         // show all warning datasets
            for(let i = (index + 1); i < legend.chart._metasets.length; i++){
                if(legend.chart._metasets[i].label == "Warning Point"){
                    legend.chart.show(i);
                }
            }
        }
        else if(index == 1){        // show all error datasets
            for(let i = (index + 1); i < legend.chart._metasets.length; i++){
                if(legend.chart._metasets[i].label == "Error Point"){
                    legend.chart.show(i);
                }
            }
        }
        legendItem.hidden = false;
    }
    if(popupBtn.dataset.value == "2"){
        getPopup(testNum, "next");
    }
    return;
}

// shows dataset info in textbox on legend hover
const showDataInfo = function (event, legendItem) {
    var testName = keys[getTestNum(event.chart)];
    var dataInfo = document.getElementById(testName + "dataInfo");
    var label = legendItem.text + " Threshold";
    var text = ""
    
    if(legendItem.text == "Warning Point"){
        text += "Warning points occur when the values are approaching test failure. ";
        text += "Hover the legend labels for specific thresholds."
    }
    else if(legendItem.text == "Error Point"){
        text += "Error points occur when the values fail the current test. ";
        text += ("(ie. " + response[testName].title + ")" );
    }
    else if(legendItem.text == "Pass"){
        text += "Passing status occurs when the values have optimal performance for the test. ";
    }
    else if(legendItem.text == "Fail"){
        text += "Failing status occurs when the values violate the current test. ";
    }
    else if(legendItem.text == "Warning"){
        text += "Warning status occurs when the values nearly fail the test. ";
        text += "Monitor these datasets to catch future test failures."
    }
    else{
        text += legendItem.text + " uses the " + response[testName].datasets[legendItem.datasetIndex].yAxisID + " axis. ";
        var threshold = response[testName].thresholdLabels[label];
        
        text += "The highlighted area shows the threshold for its warning points (" + threshold + "). ";
        showThreshold(event, legendItem, testName);
    }
    dataInfo.innerText = text;
    dataInfo.style.visibility = "visible";
}

// displays dataset warning threshold on legend hover
function showThreshold(event, legendItem, testName) {
    var index = legendItem.datasetIndex + 1;
    var label = legendItem.text + " Threshold";
    var type = response[testName].thresholdTypes[label];
    var fill = response[testName].thresholdFills[label];
    
    if(type == "custom" && fill == "none"){     // show all thresholds for datasets for custom type w/o threshold
        for(let i = 0; i < event.chart._metasets.length; i++){
            if(event.chart._metasets[i].label.includes("Threshold")){
                event.chart.show(i);
            }
        }
        return;
    }
    
    if(fill == "split" || fill == "all"){       // show all threshold datasets for split and all thresholds
        for(let i = index; i < event.chart._metasets.length; i++){
            if(event.chart._metasets[i].label.includes(legendItem.text) && event.chart._metasets[i].label.includes("Threshold")){
                event.chart.show(i);
            }
        }
        return;
    }
    
    if(fill == "none"){     // break if no fill
        return;
    }
    
    event.chart.show(index);    // else show dataset threshold
}

// hides dataset info in textbox after legend hover
const hideDataInfo = function (event, legendItem) {
    var testName = keys[getTestNum(event.chart)];
    var dataInfo = document.getElementById(testName + "dataInfo");
    dataInfo.style.visibility = "hidden";
    
    var popupBtn = document.getElementById(testName + "popup-btn");
    var label = legendItem.text;
    if(label != "Warning Point" && label != "Error Point" && label != "Pass" && label != "Fail" && label != "Warning"){
        hideThreshold(event, legendItem, testName);
        if(popupBtn.dataset.value == "1"){
            getPopup(getTestNum(event.chart), "next");
        }
    }
}

// hides dataset warning threshold after legend hover
function hideThreshold(event, legendItem, testName) {
    var index = legendItem.datasetIndex + 1;
    var label = legendItem.text + " Threshold";
    var type = response[testName].thresholdTypes[label];
    var fill = response[testName].thresholdFills[label];
    
    if(type == "custom" && fill == "none"){     // show all thresholds for datasets for custom type w/o threshold
        for(let i = 0; i < event.chart._metasets.length; i++){
            if(event.chart._metasets[i].label.includes("Threshold")){
                event.chart.hide(i);
            }
        }
        return;
    }
    
    if(fill == "split" || fill == "all"){       // show all threshold datasets for split and all thresholds
        for(let i = index; i < event.chart._metasets.length; i++){
            if(event.chart._metasets[i].label.includes(legendItem.text) && event.chart._metasets[i].label.includes("Threshold")){
                event.chart.hide(i);
            }
        }
        return;
    }
    
    if(fill == "none"){     // break if no fill
        return;
    }
    
    event.chart.hide(index);        // else show dataset threshold
}

// gets all legend settings
const getLegend = { labels: { generateLabels: legendLabels },
                    onClick: displayDatasets,
                    onHover: showDataInfo,
                    onLeave: hideDataInfo
                  }

// gets all tooltip settings       
const getTooltip = { position: "custom",
                     backgroundColor: colorTooltip,
                     callbacks: { beforeTitle: labelTooltip, label: valueTooltip }
                   }