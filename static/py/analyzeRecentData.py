import json
import pandas as pd

# formats test data
def cleanRawData(rawData, interval):
    rawData = json.loads(rawData)
    cleanData = []
    for i in range(len(rawData)):

        if(rawData[i]["receivedData"]["data"] != None):
            row = {}
            
            # date
            date = rawData[i]["receivedDate"]
            date = date.replace('T', ' ')
            date = date.replace('Z', '')
            row["date"] = date
    
            # supply
            supply = rawData[i]["receivedData"]["data"]["supply"]
            supply = int(supply) / 10
            row["supply"] = supply
    
            # inlet
            inlet = rawData[i]["receivedData"]["data"]["return"]
            inlet = int(inlet) / 10
            row["inlet"] = inlet
    
            # stack
            stack = rawData[i]["receivedData"]["data"]["stack"]
            stack = int(stack) / 10
            row["stack"] = stack
    
            # header
            header = rawData[i]["receivedData"]["data"]["header"]
            header = int(header) / 10
            row["header"] = header
    
            # hx
            hx = rawData[i]["receivedData"]["data"]["hx"]
            hx = int(hx) / 10
            row["hx"] = hx
    
            # oda
            oda = rawData[i]["receivedData"]["data"]["oda"]
            oda = int(oda) / 10
            row["oda"] = oda
    
            # flame
            flame = rawData[i]["receivedData"]["data"]["flame"]
            flame = int(flame) / 100
            row["flame"] = flame
    
            # fan
            fan = rawData[i]["receivedData"]["data"]["fan"]
            fan = int(fan) / 3
            row["fan"] = fan
    
            # firerate
            firerate = rawData[i]["receivedData"]["data"]["firerate"]
            firerate = int(firerate) / 2
            row["firerate"] = firerate
    
            # chsetpoint
            chsetpoint = rawData[i]["receivedData"]["data"]["chsetpoint"]
            chsetpoint = int(chsetpoint) / 10
            row["chsetpoint"] = chsetpoint
            
            # interval
            row["interval"] = interval
    
            cleanData.append(row)

    # create pandas dataframe and new columns
    cleanData = pd.DataFrame(cleanData)
    cleanData['date'] = pd.to_datetime(cleanData.date)
    cleanData.sort_values(by = 'date', ascending = True, inplace = True)
    cleanData['interval'] = cleanData["interval"].astype(float)
    cleanData["difference"] = cleanData['supply'].sub(cleanData['inlet'], axis = 0)
    cleanData['hx_diff'] = cleanData[["hx"]] - cleanData[["hx"]].shift(1)
    cleanData['stack_diff'] = cleanData[["stack"]] - cleanData[["stack"]].shift(1)
    cleanData['fan_diff'] = cleanData[["fan"]] - cleanData[["fan"]].shift(1)
    cleanData['flame_diff'] = cleanData[["flame"]] - cleanData[["flame"]].shift(1)
    cleanData['firerate_diff'] = cleanData[["firerate"]] - cleanData[["firerate"]].shift(1)
    cleanData['date_diff'] = cleanData[["date"]] - cleanData[["date"]].shift(1)

    return cleanData

# gets test datasets (error + warning + thresholds + data points)
def runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg):
    warningSet = pd.merge(warningSet, errorSet, indicator = True, how = "outer").query('_merge == "left_only"').drop('_merge', axis = 1)        # remove error points
    output = {}
    output["title"] = title
    output["error_ct"] = errorSet.shape[0]
    output["warning_ct"] = warningSet.shape[0]
    output["total_ct"] = data.shape[0]
    output["labels"] = data.date.astype(str).tolist()
    datasets = []
    
    if (round(((errorSet.shape[0] / data.shape[0]) * 100), 2) == 0):
        output["status"] = "green"
    elif (round(((errorSet.shape[0] / data.shape[0]) * 100), 2) > 25):
        output["status"] = "red"
    elif (round(((errorSet.shape[0] / data.shape[0]) * 100), 2) > 0):
        output["status"] = "yellow"
    else:
        output["status"] = "unknown"
        
    thresholdLabels = {}
    thresholdTypes = {}
    thresholdFills = {}
    for s in sets:
        thresholdLabels[testOptions[s]["title"] + " Threshold"] = testOptions[s]["thresholdLabel"]
        thresholdTypes[testOptions[s]["title"] + " Threshold"] = testOptions[s]["thresholdType"]
        thresholdFills[testOptions[s]["title"] + " Threshold"] = testOptions[s]["thresholdFill"]
    
    datasets, order, output = getErrorSets(output, data, datasets, errorSet, warningSet, sets, testOptions)
    output = getAxes(output, axisTitles, ["left", "right"])
    datasets = getDatasets(data, datasets, sets, testOptions, order)

    output["datasets"] = datasets
    output["thresholdLabels"] = thresholdLabels
    output["thresholdTypes"] = thresholdTypes
    output["thresholdFills"] = thresholdFills
    output["errorMsg"] = errorMsg
    return output

# gets test datasets + thresholds
def getDatasets(data, datasets, sets, testOptions, order):
    colors = ['#0099CC', '#6600CC', '#006600', '#FF9933', '#660033']
    for i in range(len(sets)):
        keySet = {}
        keySet["type"] = "line"
        keySet["label"] = testOptions[sets[i]]["title"]
        keySet["data"] = data[sets[i]].tolist()
        keySet["yAxisID"] = testOptions[sets[i]]["axisID"]
        keySet["borderColor"] = colors[i]
        keySet["pointBackgroundColor"] = colors[i]
        keySet["pointHoverRadius"] = 6
        keySet["pointHoverBorderWidth"] = 4
        keySet["pointHoverBackgroundColor"] = "transparent"
        keySet["order"] = order
        order += 1
        
        datasets.append(keySet)
        
        if testOptions[sets[i]]["thresholdFill"] != "none":
            thresholdList = getThreshold(data, sets[i], testOptions[sets[i]], order, colors[i])
            for t in thresholdList:
                datasets.append(t)
                
    return datasets

# gets test warning threshold
def getThreshold(data, setName, testOptions, order, color):
    thresholdList = []
    dates = data.date.astype(str).tolist()
    
    threshold = {}
    threshold["type"] = "line"
    threshold["label"] = testOptions["title"] + " Threshold"
    threshold["yAxisID"] = testOptions["axisID"]
    threshold["borderColor"] = "transparent"
    threshold["backgroundColor"] = color + "50"
    threshold["pointBackgroundColor"] = [color + "50"] * len(data[setName].tolist())
    threshold["pointRadius"] = 0
    threshold["pointHoverRadius"] = 0
    threshold["pointHoverBorderWidth"] = 0
    threshold["hidden"] = True
    
    if testOptions["thresholdType"] == "custom":
        threshold["data"] = testOptions["thresholdData"]
    elif testOptions["thresholdType"] == "exists":
        point1 = {"x": dates[0], "y": 0}
        point2 = {"x": dates[len(dates) - 1], "y": 0}
        threshold["data"] = [point1, point2]
    elif "2" in testOptions["title"]:
        point1 = {"x": dates[0], "y": (-1 * testOptions["warnVal"])}
        point2 = {"x": dates[len(dates) - 1], "y": (-1 * testOptions["warnVal"])}
        threshold["data"] = [point1, point2]
    else:
        point1 = {"x": dates[0], "y": testOptions["warnVal"]}
        point2 = {"x": dates[len(dates) - 1], "y": testOptions["warnVal"]}
        threshold["data"] = [point1, point2]

    if testOptions["thresholdFill"] == "above":
        threshold["fill"] = "end"
    elif testOptions["thresholdFill"] == "below" or "2" in testOptions["title"]:
        threshold["fill"] = "start"
    elif testOptions["thresholdFill"] == "between":
        threshold["fill"] = {"value": (-1 * testOptions["warnVal"])}
    elif testOptions["thresholdFill"] == "split":
        threshold["fill"] = "end"
        testOptions["title"] = testOptions["title"] + "2"
        thresholdList.append(getThreshold(data, setName, testOptions, order + 5, color)[0])
    elif testOptions["thresholdFill"] == "all":
        threshold["fill"] = "end"
        testOptions["title"] = testOptions["title"] + "2"
        thresholdList.append(getThreshold(data, setName, testOptions, order + 5, color)[0])
        
    threshold["order"] = order + 10
    thresholdList.append(threshold)
    return thresholdList

# gets test error/warning/binary datasets
def getErrorSets(output, data, datasets, errorSet, warningSet, sets, testOptions):
    binDatasets = []
    
    data.loc[:, "error"] = data["date"].apply(lambda x: "error" if x in set(errorSet["date"]) else "passed")
    data.loc[:, "warning"] = data["date"].apply(lambda x: "warning" if x in set(warningSet["date"]) else "none")
    
    binError = {}
    binError["type"] = "line"
    binError["borderWidth"] = 10
    binError["label"] = "Pass/Fail"
    binError["data"] = ["Status"] * len(data[sets[0]].tolist())
    binError["yAxisID"] = "binY"
    binError["order"] = 10
    binError["pointBackgroundColor"] = []
    binError["pointRadius"] = 0
    binError["pointHoverRadius"] = 0
    
    order = 0
    dates = data.date.astype(str).tolist()
    for s in sets:
        error, warning = setErrorOptions(testOptions[s], order)
        error, warning, binError = getErrorPoints(data, dates, s, error, warning, binError)
        
        datasets.append(warning)
        datasets.append(error)
        
        order += 2
    
    if errorSet.shape[0] == 0 and warningSet.shape[0] == 0:
        binError["borderColor"] = "#00A61E"
    elif errorSet.shape[0] == data.shape[0]:
        binError["borderColor"] = "#FF0000"
    elif warningSet.shape[0] == data.shape[0]:
        binError["borderColor"] = "#FFC107"
    binDatasets.append(binError)
    output["binDatasets"] = binDatasets

    return (datasets, order, output)

# sets the graph options for error/warning
def setErrorOptions(testOptions, order):
    error = {}
    error["type"] = "line"
    error["label"] = "Error Point"
    error["fill"] = False
    error["showLine"] = False
    error["data"] = []
    error["yAxisID"] = testOptions["axisID"]
    error["backgroundColor"] = "#FF0000"
    error["order"] = order
    error["pointBackgroundColor"] = []
    error["pointRadius"] = []
    
    warning = {}
    warning["type"] = "line"
    warning["label"] = "Warning Point"
    warning["fill"] = False
    warning["showLine"] = False
    warning["data"] = []
    warning["yAxisID"] = testOptions["axisID"]
    warning["backgroundColor"] = "#FFC107"
    warning["order"] = order + 1
    warning["pointBackgroundColor"] = []
    warning["pointRadius"] = []
    
    return error, warning

# sets the point values and colors for error/warning/binary
def getErrorPoints(data, dates, setName, error, warning, binError):
    # color-code warning points
    for i in range(data.shape[0]):
        point = {"x": dates[i], "y": data[setName].iloc[i]}
        error["data"].append(point)
        warning["data"].append(point)
            
        if data["error"].iloc[i] == "error":
            error["pointBackgroundColor"].append('#FF0000')
            error["pointRadius"].append(3)
            warning["pointBackgroundColor"].append("transparent")
            warning["pointRadius"].append(0)
            if len(binError) != data.shape[0]:
                binError["pointBackgroundColor"].append("#FF0000")
        elif data["warning"].iloc[i] == "warning":
            warning["pointBackgroundColor"].append("#FFC107")
            warning["pointRadius"].append(3)
            error["pointBackgroundColor"].append("transparent")
            error["pointRadius"].append(0)
            if len(binError) != data.shape[0]:
                binError["pointBackgroundColor"].append("#FFC107")
        else:
            warning["pointBackgroundColor"].append("transparent")
            warning["pointRadius"].append(0)
            error["pointBackgroundColor"].append("transparent")
            error["pointRadius"].append(0)
            if len(binError) != data.shape[0]:
                binError["pointBackgroundColor"].append("#00A61E")
                
    return error, warning, binError

# gets axis settings
def getAxes(output, axisTitles, axisPositions):
    for p in axisPositions:
        axis = {}
        axis["type"] = "linear"
        axis["position"] = p
        axis["display"] = "auto"
        axis["grace"] = "5%"
        title = {}
        title["text"] = axisTitles[p]
        title["display"] = True
        axis["title"] = title
        output[p] = axis
        
    return output

# call with checkDuration to remove points that are over duration limit
def underLimit(value, limit):
    return value > limit

# call with checkDuration to remove points that are under duration limit
def overLimit(value, limit):
    return value < limit

# used with duration tests
def checkDuration(checkSet, data, timeLimit, checkLimit):
    dates = data.date.tolist()
    removeDuration = False
    durationSet = []
    removeRows = []
    
    for i in range(checkSet.shape[0] - 1, 0, -1):       # reverse loop through errorSet
        index = dates.index(checkSet["date"].iloc[i])
        prevDate = dates[index - 1]
        if prevDate == checkSet["date"].iloc[i - 1]:      # consecutive points
            durationSet.append(i)
            if i == 1:
                durationSet.append(0)
            duration = pd.Timedelta(checkSet["date"].iloc[durationSet[0]] - checkSet["date"].iloc[i]).seconds / 60.0    # duration in min
            if(checkLimit(duration, timeLimit)):       # check duration condition
                removeDuration = True
            else:
                removeDuration = False
        else:
            if removeDuration:      # remove duration points if over 10 min
                removeRows += durationSet
            durationSet = [i]
            removeDuration = False

    if removeDuration:
        removeRows += durationSet
        
    checkSet = checkSet.drop([checkSet.index[j] for j in removeRows])
    return checkSet
        
def test1(data):
    errorSet = data[(data.hx >= data.supply) | (data.hx <= data.inlet)]
    warningSet = data[(data.supply > (data.hx + 5)) & (data.inlet < (data.hx - 5))]
    title = "Heat exchanger temperature is not between inlet and outlet temperature"
    sets = ["hx", "supply", "inlet"]
    testOptions = {
            "hx" : {
                    "title" : "Heat Exchanger Temperature",
                    "axisID" : "left",
                    "thresholdLabel" : "outlet > heat exchanger + 5 \N{DEGREE SIGN}F and inlet < heat exhanger - 5 \N{DEGREE SIGN}F",
                    "thresholdType" : "custom",
                    "thresholdFill" : "none"
                },
            "supply" : {
                    "title" : "Outlet Temperature",
                    "axisID" : "left",
                    "thresholdLabel" : "outlet > heat exchanger + 5 \N{DEGREE SIGN}F",
                    "thresholdType" : "custom",
                    "thresholdFill" : "above",
                    "thresholdData" : [y + 5 for y in data["hx"].tolist()]
                },
            "inlet" : {
                    "title" : "Inlet Temperature",
                    "axisID" : "left",
                    "thresholdLabel" : "inlet < heat exchanger - 5 \N{DEGREE SIGN}F",
                    "thresholdType" : "custom",
                    "thresholdFill" : "below",
                    "thresholdData" : [y - 5 for y in data["hx"].tolist()]
                }
        }
    axisTitles = {
            "left" : "Temperature (\N{DEGREE SIGN}F)",
            "right" : "Temperature (\N{DEGREE SIGN}F)"
        }
    errorMsg = "Faulty sensors or heat exchanger needs to be cleaned"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test2(data):
    errorSet = data[(data.fan > 0) & (data.difference < 0)]
    warningSet = data[(data.difference < 1) & (data.fan > 2000)]
    title = "Inlet/outlet temperature difference is negative while fan speed is positive"
    sets = ["difference", "fan"]
    testOptions = {
            "difference" : {
                    "title" : "Inlet and Outlet Temperature Difference [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "< 1 \N{DEGREE SIGN}F",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 1
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "> 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Temperature Difference (\N{DEGREE SIGN}F)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Faulty sensors or flow of water reversed"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test3(data):
    data = data.iloc[1:]        # skip first row because NAN (no difference found for first value)
    errorSet = data[(data.hx_diff == 0) & (data.stack_diff != 0)]
    warningSet = data[abs(data.hx_diff) < 3]
    title = "Exhaust temperature difference exists while heat exchanger temperature difference is 0"
    sets = ["stack_diff", "hx_diff"]
    testOptions = {
            "stack_diff" : {
                    "title" : "Exhaust Temperature Difference",
                    "axisID" : "left",
                    "thresholdLabel" : "any \N{DEGREE SIGN}F",
                    "thresholdType" : "exists",
                    "thresholdFill" : "all",
                },
            "hx_diff" : {
                    "title" : "Heat Exchanger Temperature Difference",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 \N{DEGREE SIGN}F and > -3 \N{DEGREE SIGN}F",
                    "thresholdType" : "abs",
                    "thresholdFill" : "between",
                    "warnVal" : 3
                }
        }
    axisTitles = {
            "left" : "Temperature Difference (\N{DEGREE SIGN}F)",
            "right" : "Temperature Difference (\N{DEGREE SIGN}F)"
        }
    errorMsg = "Faulty sensor"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test4(data):
    data = data.iloc[1:]        # skip first row because NAN (no difference found for first value)
    errorSet = data[((data.fan_diff > 0) & (data.flame_diff < 0)) | ((data.fan_diff < 0) & (data.flame_diff > 0))]
    warningSet = data[(abs(data.fan_diff) < 1000) & (abs(data.flame_diff) < 3)]
    title = "Fan speed difference and flame signal difference have opposite signs"
    sets = ["fan_diff", "flame_diff"]
    testOptions = {
            "fan_diff" : {
                    "title" : "Fan Speed Difference [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "< 1000 RPM and > -1000 RPM",
                    "thresholdType" : "abs",
                    "thresholdFill" : "between",
                    "warnVal" : 1000
                },
            "flame_diff" : {
                    "title" : "Flame Signal Difference [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "< 3 mA/V/% and > -3 mA/V/%",
                    "thresholdType" : "abs",
                    "thresholdFill" : "between",
                    "warnVal" : 3
                }
        }
    axisTitles = {
            "left" : "Fan Speed Difference (RPM)",
            "right" : "Flame Signal Difference (mA / V / %)"
        }
    errorMsg = "Faulty flame ignition rod, polarity is backwards, or faulty sensor"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test5(data):
    errorSet = data[(data.difference > 0) & (data.flame == 0)]
    warningSet = data[(data.difference > -1) & (data.flame < 3)]
    title = "Inlet/outlet temperature difference is positive while flame signal is 0"
    sets = ["difference", "flame"]
    testOptions = {
            "difference" : {
                    "title" : "Inlet and Outlet Temperature Difference",
                    "axisID" : "left",
                    "thresholdLabel" : "> -1 \N{DEGREE SIGN}F",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : -1
                },
            "flame" : {
                    "title" : "Flame Signal",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/%",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 3
                }
        }
    axisTitles = {
            "left" : ["Temperature Difference (\N{DEGREE SIGN}F)", "", "Flame Signal (mA / V / %)"],
            "right" : ["Temperature Difference (\N{DEGREE SIGN}F)", "", "Flame Signal (mA / V / %)"]
        }
    errorMsg = "Check valve position or pump operation"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test6(data):
    errorSet = data[(data.fan == 0) & (data.difference > 0)]
    warningSet = data[(data.difference > -1) & (data.fan < 2000)]
    title = "Inlet/outlet temperature difference is positive while fan speed is 0"
    sets = ["difference", "fan"]
    testOptions = {
            "difference" : {
                    "title" : "Inlet and Outlet Temperature Difference [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "> -1 \N{DEGREE SIGN}F",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : -1
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "< 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Temperature Difference (\N{DEGREE SIGN}F)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Faulty fan signal and/or fan failed"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test7(data):
    data = data.iloc[1:]        # skip first row because NAN (no difference found for first value)
    errorSet = data[((data.firerate_diff > 0) & (data.flame_diff < 0)) | ((data.firerate_diff < 0) & (data.flame_diff > 0))]
    warningSet = data[(abs(data.firerate_diff) < 3) | (abs(data.flame_diff) < 3)]
    title = "Firing rate difference and flame signal difference have opposite signs"
    sets = ["firerate_diff", "flame_diff"]
    testOptions = {
            "firerate_diff" : {
                    "title" : "Firing Rate Difference",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/% and > -3 mA/V/%",
                    "thresholdType" : "abs",
                    "thresholdFill" : "between",
                    "warnVal" : 3
                },
            "flame_diff" : {
                    "title" : "Flame Signal Difference",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/% and > -3 mA/V/%",
                    "thresholdType" : "abs",
                    "thresholdFill" : "between",
                    "warnVal" : 3
                }
        }
    axisTitles = {
            "left" : "Current Difference (mA / V / %)",
            "right" : "Current Difference (mA / V / %)"
        }
    errorMsg = "Faulty flame signal connections"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test8(data):
    errorSet = data[(data.fan > 0) & (data.firerate == 0)]
    warningSet = data[(data.firerate < 3) & (data.fan > 2000)]
    title = "Firing rate is 0 while fan speed is positive"
    sets = ["firerate", "fan"]
    testOptions = {
            "firerate" : {
                    "title" : "Firing Rate [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/%",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 3
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "> 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Firing Rate (mA / V / %)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Fan operating just before or just after ignition. If this is happening abruptly, flame sensor is faulty"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test9(data):
    errorSet = data[(data.fan > 0) & (data.flame == 0)]
    warningSet = data[(data.flame < 3) & (data.fan > 2000)]
    title = "Flame signal is 0 while fan speed is positive"
    sets = ["flame", "fan"]
    testOptions = {
            "flame" : {
                    "title" : "Flame Signal [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/%",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 3
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "> 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Flame Signal (mA / V / %)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Fan operating just before or just after ignition. If this is happening for prolonged periods of time, fan is faulty"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test10(data):
    errorSet = data[(data.firerate > 0) & (data.flame == 0)]
    warningSet = data[(data.firerate > -1) & (data.flame < 3)]
    title = "Firing rate is positive while flame signal is 0"
    sets = ["firerate", "flame"]
    testOptions = {
            "firerate" : {
                    "title" : "Firing Rate",
                    "axisID" : "left",
                    "thresholdLabel" : "> -1 mA/V/%",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : -1
                },
            "flame" : {
                    "title" : "Flame Signal",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/%",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 3
                }
        }
    axisTitles = {
            "left" : "Current (mA / V / %)",
            "right" : "Current (mA / V / %)"
        }
    errorMsg = "Faulty flame sensor or check wiring of ignition equipment"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test11(data):
    data = data.iloc[1:]        # skip first row because NAN (no difference found for first value)
    errorSet = data[(data['flame_diff'] > 0.2) & (data['fan'] == 0)]
    warningSet = data[(abs(data.flame_diff) > 3) & (data.fan < 2000)]
    title = "Drastic changes in flame signal difference while fan speed is zero"
    sets = ["flame_diff", "fan"]
    testOptions = {
            "flame_diff" : {
                    "title" : "Flame Signal Difference [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "> 3 mA/V/% or < -3 mA/V/%",
                    "thresholdType" : "abs",
                    "thresholdFill" : "split",
                    "warnVal" : 3
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "< 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Flame Signal Difference (mA / V / %)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Ignition equipment is faulty, dirty, or has bad connection. Check ignition rod and sensor"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)
    
def test12(data):
    errorSet = data[(data['flame'] > 0) & (data['fan'] != 0) & (data["interval"] <= 10)]
    if errorSet.shape[0] > 0:
        errorSet = checkDuration(errorSet, data, 10, underLimit)      # underDuration to check < 10min
    warningSet = data[(data['flame'] > 0) & (data["fan"] > 2000) & (data["interval"] <= 20)]
    if warningSet.shape[0] > 0:
        warningSet = checkDuration(warningSet, data, 20, underLimit)
    title = "Flame signal duration is less than 10 minutes at a time"
    sets = ["flame", "fan"]
    testOptions = {
            "flame" : {
                    "title" : "Flame Signal [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "> 0 mA/V/% for < 20 min",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : 0
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "> 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Flame Signal (mA / V / %)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Boiler is short cycling. Check boiler speed -- slow down response and/or prolong firing time"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)

def test13(data):
    errorSet = data[(data['fan'] > 0) & (data['flame'] == 0)]
    errorSet = checkDuration(errorSet, data, 1.5, overLimit)      # overDuration to check > 90sec
    warningSet = data[(data['fan'] > 2000) & (data['flame'] < 3)]
    warningSet = checkDuration(warningSet, data, .5, overLimit)
    title = "Flame signal is 0 and fan speed is positive for over 90 seconds at a time"
    sets = ["flame", "fan"]
    testOptions = {
            "flame" : {
                    "title" : "Flame Signal [left]",
                    "axisID" : "left",
                    "thresholdLabel" : "< 3 mA/V/% for > 30 sec",
                    "thresholdType" : "default",
                    "thresholdFill" : "below",
                    "warnVal" : 3
                },
            "fan" : {
                    "title" : "Fan Speed [right]",
                    "axisID" : "right",
                    "thresholdLabel" : "> 2000 RPM",
                    "thresholdType" : "default",
                    "thresholdFill" : "above",
                    "warnVal" : 2000
                }
        }
    axisTitles = {
            "left" : "Flame Signal (mA / V / %)",
            "right" : "Fan Speed (RPM)"
        }
    errorMsg = "Faulty fan"

    return runTest(data, errorSet, warningSet, title, sets, testOptions, axisTitles, errorMsg)