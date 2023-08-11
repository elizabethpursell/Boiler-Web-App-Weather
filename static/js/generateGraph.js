// adds all chart plugins
function registerPlugins(){
    // add zoom plugin -- sometimes doesn't register if only in base.html
    data.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.js" defer integrity="sha512-KacxtjMxwPjZfLXBoEAm2bKEzpZg71vwjVz4PTBuo/hEaijtBsrEwiWBXc+gC09Akd3lqeqMlOMMKNe1L3koRw==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>');
    
    // tooltip position plugin
    Chart.Tooltip.positioners.custom = function(elements, eventPosition){
        var tooltip = this;
        return {
            x: eventPosition.x,
            y: eventPosition.y
        };
    }
    
    // legend padding plugin
    Chart.register({
        id: "legendPadding",
        beforeInit(chart){
            const originalFit = chart.legend.fit;
            chart.legend.fit = function fit(){
                originalFit.bind(chart.legend)();
                this.height += 15;
            }
        }
    });
    
    // hoverCrosshair plugin
    Chart.register({
        id: "hoverCrosshair",
        events: ['mousemove'],
        beforeDatasetsDraw: drawCrosshair,
        afterEvent: getCoords
    });
    
    // showResetButton plugin
    Chart.register({
        id: "showResetButton",
        afterRender: displayButton,
        afterUpdate: displayButton
    });
}

// called on "Generate Timeline Graph" click
function createTimelineGraph(testNum, button){
    let graph = $(`#${keys[testNum]}Graph`);
    let graphElement = document.getElementById(button.dataset.chartName);
    let binElement = document.getElementById(button.dataset.binName);
    let binMenu = document.getElementById(button.dataset.binMenu);
    let genButton = document.getElementById(button.dataset.genBtn);
    let datasetInfo = document.getElementById(keys[testNum] + "dataInfo");
    let popupBtn = document.getElementById(keys[testNum] + "popup-btn");
    let chartWrap = document.getElementById(keys[testNum] + "chartWrap");
    let binData = [];
    
    for(let i = 0; i < popoverList.length; i++){
        popoverList[i].update();
    }

    // create new graph on first button press
    if(button.value == "none" && genButton.value == "none"){
        button.innerHTML = "Close Timeline Graph";
        genButton.innerHTML = "Close Timeline Graph";
        button.value = "shown";
        genButton.value = "shown";
        binElement.style.visibility = "visible";
        binMenu.classList.remove("disabled");
        chartWrap.classList.remove("disabled");
        datasetInfo.style.display = "inline-block";
        binDisplay = false;
        
        response[keys[testNum]].left["ticks"] = ticks;
        response[keys[testNum]].right["ticks"] = ticks;
        
        const myChart = new Chart(graph, {
            data: {
                labels: response[keys[testNum]].labels,
                datasets: response[keys[testNum]].datasets
            },
            options: {
                interaction: {intersect: false, mode: "index"},
                scales: scalesOpt(testNum),
                animation: { duration: false },
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: getLegend, tooltip: getTooltip, zoom: zoomOpt }
            }
        });
        
        if(popupBtn.dataset.value == "0"){
            getPopup(testNum, "next");
        }
    }
    
    // make graph visible
    else if(button.value == "hidden"){
        button.innerHTML = "Close Timeline Graph";
        genButton.innerHTML = "Close Timeline Graph";
        button.value = "shown";
        genButton.value = "shown";
        graphElement.style.display = "block";
        binElement.style.visibility = "visible";
        binMenu.classList.remove("disabled");
        chartWrap.classList.remove("disabled");
        datasetInfo.style.display = "inline-block";
        
        if(popupBtn.dataset.value == "0"){
            getPopup(testNum, "next");
        }
    }
    
    // hide graph
    else{
        button.innerHTML = "Generate Timeline Graph";
        genButton.innerHTML = "Generate Timeline Graph";
        button.value = "hidden";
        genButton.value = "hidden";
        graphElement.style.display = "none";
        binElement.style.visibility = "hidden";
        binMenu.classList.add("disabled");
        chartWrap.classList.add("disabled");
        datasetInfo.style.display = "none";
        
        getPopup(testNum, "start");
    }
    
    // add reset zoom button
    document.getElementById(keys[testNum] + "resetButton").addEventListener('click', (e) => {
        const chart = Chart.getChart(keys[testNum] + "Graph");
        chart.resetZoom();
        document.getElementById(keys[testNum] + "resetButton").style.display = "none";
        
        if(popupBtn.dataset.value == "3"){
            getPopup(testNum, "next");
        }
    });
}

// called on "Generate Binary Graph" click
function createBinaryGraph(testNum, button){
    const myChart = Chart.getChart(button.dataset.chartName);
    let popupBtn = document.getElementById(keys[testNum] + "popup-btn");
    let binButton = document.getElementById(button.dataset.binBtn);

    // add binary dataset to graph
    if(button.value == "none" || button.value == "hidden"){
        button.innerHTML = "Close Binary Graph";
        binButton.innerHTML = "Close Binary Graph";
        button.value = "shown";
        binButton.value = "shown";
        binDisplay = true;
        
        // create color-coded line segments to show error/warning/pass
        const errorData = response[keys[testNum]].binDatasets[0];
        const errorSeg = function(ctx){
            return ctx.p0.options.backgroundColor;
        }
        errorData["segment"] = {
            borderColor: ctx => errorSeg(ctx)
        };
        
        myChart.data.datasets.push(errorData);
        myChart.update();
        
        if(popupBtn.dataset.value == "4"){
            getPopup(testNum, "next");
        }
    }
    
    // remove binary dataset from graph
    else{
        button.innerHTML = "Generate Binary Graph";
        binButton.innerHTML = "Generate Binary Graph";
        button.value = "hidden";
        binButton.value = "hidden";
        binDisplay = false;
        myChart.data.datasets.pop();
        myChart.update();
    }
}

// hoverCrosshair plugin calls beforeDatasetsDraw
function drawCrosshair (chart, args, plugins){
    if(crosshair){
        const { ctx } = chart;
        ctx.save();
        crosshair.forEach((line, index) => {
            ctx.beginPath();
            ctx.lineWidth = 3;
            ctx.strokeStyle = "rgba(102, 102, 102, 1)";
            ctx.moveTo(line.startX, line.startY);
            ctx.lineTo(line.endX, line.endY);
            ctx.stroke();
        });
                                
        ctx.restore();
    }
}

// hoverCrosshair plugin calls afterEvent (after mousemove)
function getCoords (chart, args){
    const {ctx, chartArea: {left, right, top, bottom}} = chart;
    const xCoor = args.event.native.offsetX;
    const yCoor = args.event.native.offsetY;
    const x = args.event.x;
    const y = args.event.y;

    let inChartArea = (xCoor >= left) && (xCoor <= right) && (yCoor >= top) && (yCoor <= bottom);

    if(!inChartArea && crosshair){
        crosshair = undefined;
    }
    else if(inChartArea){
        crosshair = [{ startX: x, startY: top, endX: x, endY: bottom }];
        args.changed = true;
    }
    else{
        crosshair = undefined;
    }
}

// showResetButton plugin calls afterRender and afterUpdate
function displayButton (chart, args, plugins){
    var testName = keys[getTestNum(chart)];
    let resetButton = document.getElementById(testName + "resetButton");
    
    // create new reset button if needed
    if(!resetButton){
        resetButton = document.createElement("BUTTON");
        resetButton.id = testName + "resetButton";
        resetButton.innerHTML = '<i class="fa-solid fa-rotate-left white-font"></i>'
        resetButton.classList.add("btn");
        resetButton.classList.add("btn-secondary");
        resetButton.classList.add("my-1");
        resetButton.classList.add("reset-btn");
        resetButton.style.display = "none";
        chart.canvas.parentNode.appendChild(resetButton);
    }
    
    // set position of button
    resetButton.style.left = (chart.width - 60) + "px";
    resetButton.style.top = ((chart.height - 50) * -1) + "px";
    
    //check for two axes -- assign button position accordingly
    for(let i = 0; i < response[testName].datasets.length; i++){
        if(response[testName].datasets[i].yAxisID == "right"){
            resetButton.style.left = (chart.width - 120) + "px";
            resetButton.style.top = ((chart.height - 50) * -1) + "px";
            break;
        }
    }
    
    if(chart.isZoomedOrPanned() == false){
        resetButton.style.display = "none";
    }
    else{
        resetButton.style.display = "inline";
    }
}