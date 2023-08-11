from flask import Flask, render_template, request, make_response
from NuroConnect import NuroConnect
import json
#import time
import os
import sys
script_dir = os.path.dirname( __file__ )
analyze_dir = os.path.join(script_dir, 'static', 'py' )
sys.path.append(analyze_dir)
import analyzeRecentData

app = Flask(__name__)
nc = NuroConnect()
cache = {"boilers" : "none"}

@app.route('/')
def home():
    # check to see if user is already authenticated
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        firstName = request.cookies.get('firstName')
        lastName = request.cookies.get('lastName')
        company = request.cookies.get('company')
        resp = make_response(render_template('home.html', authenticated = True, firstName = firstName, lastName = lastName, company = company, pageName = "Home"))
        return resp
    else:
        resp = make_response(render_template('home.html', authenticated = False, pageName = "Logout"))
        return resp

@app.route('/logout')
def logout():
    authenticated = request.cookies.get('authenticated')
    resp = make_response(render_template('home.html', authenticated = False, pageName = "Logout"))
    if(authenticated == 'true'):
        nc.logout()
        # destroy authenticated cookies
        resp.set_cookie('authenticated', '', max_age=0)
        resp.set_cookie('id', '', max_age=0)
        resp.set_cookie('userId', '', max_age=0)
        resp.set_cookie('username', '', max_age=0)
        # destroy user cookies
        resp.set_cookie('firstName', '', max_age=0)
        resp.set_cookie('lastName', '', max_age=0)
        resp.set_cookie('email', '', max_age=0)
        resp.set_cookie('title', '', max_age=0)
        resp.set_cookie('company', '', max_age=0)
        # destroy cache
        cache["boilers"] = "none"
    return resp

# @app.route('/recent-data-get')
# def recentDataGet():
#     if(nc.isAuthenticated()):
#         return render_template('recentData.html')
#     else:
#         return render_template('home.html')

# @app.route('/data-get')
# def dataGet():
#     if(nc.isAuthenticated()):
#         return render_template('data.html')
#     else:
#         return render_template('home.html')

@app.route('/diagnostics/<boiler_name>/<boiler_id>')
def analyzeDataRender(boiler_name, boiler_id):
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        firstName = request.cookies.get('firstName')
        lastName = request.cookies.get('lastName')
        company = request.cookies.get('company')
        return render_template('analyzeData.html', authenticated = True, firstName = firstName, lastName = lastName, company = company, boiler_name = boiler_name, boiler_id = boiler_id, pageName = "Diagnostics")
    else:
        return render_template('home.html', authenticated = False, pageName = "Logout")

# @app.route('/dev-get')
# def devGet():
#     if(nc.isAuthenticated()):
#         return render_template('dev.html')
#     else:
#         return render_template('home.html')

@app.route('/profile')
def profile():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        firstName = request.cookies.get('firstName')
        lastName = request.cookies.get('lastName')
        email = request.cookies.get('email')
        title = request.cookies.get('title')
        company = request.cookies.get('company')
        return render_template(
            'profile.html',
            authenticated = True,
            firstName = firstName,
            lastName = lastName,
            email = email,
            title = title,
            company = company,
            pageName = "My Profile"
        )
    else:
        return render_template('home.html', authenticated = False, pageName = "Logout")
    
@app.route('/help')
def help():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        firstName = request.cookies.get('firstName')
        lastName = request.cookies.get('lastName')
        email = request.cookies.get('email')
        title = request.cookies.get('title')
        company = request.cookies.get('company')
        return render_template(
            'help.html',
            authenticated = True,
            firstName = firstName,
            lastName = lastName,
            email = email,
            title = title,
            company = company,
            pageName = "Help"
        )
    else:
        return render_template('home.html', authenticated = False, pageName = "Logout")

# @app.route('/dev')
# def dev():
#     if(nc.isAuthenticated()):
#         return nc.experimental()
#     else:
#         return {"success": False}

@app.route('/available-boilers')
def availableBoilersGet():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        firstName = request.cookies.get('firstName')
        lastName = request.cookies.get('lastName')
        company = request.cookies.get('company')
        return render_template('availableBoilers.html', authenticated = True, firstName = firstName, lastName = lastName, company = company, pageName = "Available Boilers")
    else:
        return render_template('home.html', authenticated = False, pageName = "Logout")

@app.route('/authenticated')
def authenticated():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        return {"success": True}
    else:
        return {"success": False}

@app.route('/user')
def user():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        firstName = request.cookies.get('firstName')
        lastName = request.cookies.get('lastName')
        return {"success": True, "firstName": firstName, "lastName": lastName}
    else:
        return {"success": False}

# @app.route('/recent-data-post', methods=['POST'])
# def recentDataPost():
#     if(nc.isAuthenticated()):
#         boiler_id = request.form.get('boiler_id')
#         boiler_info = nc.getBoilerInfo(boiler_id)
#         if(boiler_info['status'] == 16): # status = 16 seems to mean boiler is disconnected
#             return {"success": False}
#         result = nc.getLatestBoilerDataRaw(boiler_id, 10)
#         if(result == None):
#             return {"success": False}
#         else:
#             return result
#     else:
#         return {"success": False}

# @app.route('/data-post', methods=['POST'])
# def dataPost():
#     if(nc.isAuthenticated()):
#         boiler_id = request.form.get('boiler_id')
#         start_time = request.form.get('start_time')
#         end_time = request.form.get('end_time')
#         interval = request.form.get('interval')
#         boiler_info = nc.getBoilerInfo(boiler_id)
#         if(boiler_info['status'] == 16): # status = 16 seems to mean boiler is disconnected
#             return {"success": False}
#         result = nc.getBoilerData(boiler_id, start_time, end_time, interval)
#         if(result == None):
#             return {"success": False}
#         else:
#             return result
#     else:
#         return {"success": False}

@app.route('/analyze-data-post', methods=['POST'])
def analyzeDataPost():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        # retrieve boiler data
        boiler_id = request.form.get('boiler_id')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        interval = request.form.get('interval')

        # get boiler info
        id = request.cookies.get('id')
        boiler_info = nc.getBoilerInfo(id, boiler_id)
        if(boiler_info['status'] == 16): # status = 16 seems to mean boiler is disconnected
            return {"success": False}

        # get boiler raw data
        rawData = nc.getBoilerData(id, boiler_id, start_time, end_time, interval)
        if rawData == None or rawData == "[]":
            return {"success": False}

        # get weather data for site
        userId = request.cookies.get('userId')
        nc.getSites(id, userId)
        coords = nc.getSiteCoords(boiler_info["siteId"])
        if coords != None:
            dailyWeather = nc.getDailyWeather(start_time, end_time, boiler_info["siteId"])
            hourlyWeather = nc.getHourlyWeather(start_time, end_time, boiler_info["siteId"])

        # clean and analyze boiler data
        result = {}
        cleanData = analyzeRecentData.cleanRawData(rawData, interval)
        result["test1"] = analyzeRecentData.test1(cleanData)
        result["test2"] = analyzeRecentData.test2(cleanData)
        result["test3"] = analyzeRecentData.test3(cleanData)
        result["test4"] = analyzeRecentData.test4(cleanData)
        result["test5"] = analyzeRecentData.test5(cleanData)
        result["test6"] = analyzeRecentData.test6(cleanData)
        result["test7"] = analyzeRecentData.test7(cleanData)
        result["test8"] = analyzeRecentData.test8(cleanData)
        result["test9"] = analyzeRecentData.test9(cleanData)
        result["test10"] = analyzeRecentData.test10(cleanData)
        result["test11"] = analyzeRecentData.test11(cleanData)
        result["test12"] = analyzeRecentData.test12(cleanData)
        result["test13"] = analyzeRecentData.test13(cleanData)
        try:
            result["test14"] = analyzeRecentData.test14(cleanData, dailyWeather)
        except:
            print("Test 14 failed -- graph not displayed")
        return json.dumps(result)
    else:
        return {"success": False}
    
@app.route('/analyze-weather-post', methods=['POST'])
def analyzeWeatherPost():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        # get weather data for site
        try:
            return nc.__dict__["dailyWeather"].to_json(orient="index", date_format="iso")
        except:
            return {"success": False}
    else:
        return {"success": False}

@app.route('/available-boilers-data', methods=['GET'])
def availableBoilersData():
    authenticated = request.cookies.get('authenticated')
    if(authenticated == 'true'):
        if cache["boilers"] == "none":
            id = request.cookies.get('id')
            userId = request.cookies.get('userId')
            sites = nc.getSites(id, userId)
            boilersList = nc.listBoilers(sites)
    
            for i in range(len(boilersList)):
                boiler_id = boilersList[i].id
                boiler_info = nc.getBoilerInfo(id, boiler_id)
                boiler_image = nc.getBoilerImage(boiler_info['model'])
                boiler_state = nc.getBoilerState(boiler_info['state'])
                boiler_status = nc.getBoilerStatus(boiler_info['status'])
    
                data = {
                    'name': boiler_info['name'],
                    'state': boiler_state,
                    'status': boiler_status,
                    'image': boiler_image,
                    'id': boiler_id
                }
    
                boilersList[i] = data
    
            boilers = json.dumps(boilersList)
            cache["boilers"] = boilers;
            return boilers
        else:
            return cache["boilers"]
    else:
        return {"success": False}

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    result = nc.login(email, password)
    if(result['success']):
        resp = make_response('success')
        # set authenticated cookies
        resp.set_cookie('authenticated', 'true')
        resp.set_cookie('id', result['id'])
        resp.set_cookie('userId', result['userId'])
        resp.set_cookie('username', result['username'])
        # set user cookies
        user = nc.getUser(result['id'], result['userId'])
        resp.set_cookie('firstName', user['firstName'])
        resp.set_cookie('lastName', user['lastName'])
        resp.set_cookie('email', user['email'])
        resp.set_cookie('title', user['titledata']['text'])
        resp.set_cookie('company', user['company'])
        return resp
    else:
        try:
            return make_response(result['error'])
        except:
            return 'failure'

if __name__ == "__main__":
    app.run(debug=True)
