import requests
import json
import os
from datetime import datetime, timedelta, timezone


class UnauthenticatedException(Exception):
    pass


class Boiler:
    def __init__(self, id, nuro="", sola="", description=""):
        self.id = id
        self.nuro = nuro
        self.sola = sola
        self.description = description


    def __str__(self):
        return "<" + self.id + ": " + self.description + " " + self.nuro + " " + self.sola + ">"


    def __repr__(self):
        return self.__str__()


class NuroConnect:
    def __init__(self, endpoint="https://app.nuroconnect.com"):
        self.endpoint = endpoint

        self.auth = None
        self.user = None
        self.expiry = None

        self.sites = None

        self.username = None


    def login(self, username, password):
        payload = {"email": username, "password": password}
        r = requests.post(self.endpoint + "/api/users/login", data=payload, verify=False)
        if r.ok:
            response = r.json()
            if 'id' in response and 'userId' in response and 'created' in response:
                self.auth = response['id']
                self.user = response['userId']
                self.expiry = datetime.strptime(response['created'], "%Y-%m-%dT%H:%M:%S.%f%z") + timedelta(seconds=response['ttl'])
                self.username = username
                return {
                    'success': True,
                    'id': response['id'],
                    'userId': response['userId'],
                    'username': username
                }
        try:
            response = r.json()
            return {'success': False, 'error': response['error']['message']}
        except: 
            return {'success': False}


    def logout(self):
        self.auth = None
        self.user = None
        self.expiry = None
        self.username = None


    def isAuthenticated(self):
        if self.auth is not None and self.user is not None and self.expiry is not None:
            return datetime.now(timezone.utc) < self.expiry
        return False


    def getSites(self, id, userId):
        params = {"filter": '{"include":"boilers"}'}
        headers = {"authorization": id}
        r = requests.get(self.endpoint + "/api/users/" + userId + "/sites", params=params, headers=headers, verify=False)
        if r.ok:
            response = r.json()
            self.sites = {}
            for site in response:
                self.sites[site['id']] = site

            return self.sites


    def listBoilers(self, sites):
        boilers = []

        if sites is not None:
            for id in sites:
                for boilerInfo in sites[id]['boilers']:

                    boiler = Boiler(boilerInfo['id'])
                    if 'nuroSN' in boilerInfo:
                        boiler.nuro = boilerInfo['nuroSN']
                    if 'solaSN' in boilerInfo:
                        boiler.sola = boilerInfo['solaSN']
                    if 'description' in boilerInfo:
                        boiler.description = boilerInfo['description']
                    boilers.append(boiler)

        return boilers


    def getBoilerInfo(self, id, boilerID):
        headers = {"authorization": id}
        r = requests.get(self.endpoint + "/api/Boilers/" + boilerID, headers=headers, verify=False)
        if r.ok:
            return r.json()


    def getLatestBoilerData(self, boilerID, limit=1):
        if self.isAuthenticated():
            params = {"filter": '{"order":"receivedDate DESC", "limit": ' + str(limit) + '}'}
            headers = {"authorization": self.auth}
            r = requests.get(self.endpoint + "/api/Boilers/" + boilerID + "/boilerRecords", params=params, headers=headers, verify=False)
            if r.ok:
                return r.json()
        else:
            raise UnauthenticatedException()

    def getLatestBoilerDataRaw(self, boilerID, limit=1):
        if self.isAuthenticated():
            params = {"filter": '{"order":"receivedDate DESC", "limit": ' + str(limit) + '}'}
            headers = {"authorization": self.auth}
            r = requests.get(self.endpoint + "/api/Boilers/" + boilerID + "/boilerRecords", params=params, headers=headers, verify=False)
            if r.ok:
                return r.text
        else:
            raise UnauthenticatedException()

    def getBoilerData(self, id, boilerID, startTime, endTime, interval):
        params = {
            "filter": '{"where": {"receivedDate":{"gte":"' + str(startTime) + '","lt":"' + str(endTime) + '"}}, "order":"receivedDate DESC", "skip": 0, "limit": 360, "interval": ' + str(interval) + '}'
        }
        headers = {"authorization": id}
        r = requests.get(self.endpoint + "/api/Boilers/" + boilerID + "/records", params=params, headers=headers, verify=False)
        if r.ok:
            return r.text

    def getBoilerImage(self, model):
        ### nuro connect api call to dynamically get boiler models ###
        # headers = {"authorization": self.auth}
        # r = requests.get('https://app.nuroconnect.com/api/BoilerModels', headers=headers, verify=False)
        # if r.ok:
        #     r = r.json()
        #     # search for model in boiler model list
        #     for i in range(len(r)):
        #         if(r[i]['modelKey'] == model):
        #             return f"https://app.nuroconnect.com/api/BoilerImages/view/{r[i]['imageFile']}.png"
    
        ### static method of getting boiler models ###
        with open(os.getcwd() + '/static/txt/boilerModels.txt') as f:
            json_data = json.load(f)
            for i in range(len(json_data)):
                if(json_data[i]['modelKey'] == model):
                    return f"https://app.nuroconnect.com/api/BoilerImages/view/{json_data[i]['imageFile']}.png"

    def getBoilerState(self, state):
        ### nuro connect api call to dynamically get boiler states ###
        # headers = {"authorization": self.auth}
        # r = requests.get('https://app.nuroconnect.com/api/BoilerStates', headers=headers, verify=False)        
        # if r.ok:
        #     r = r.json()
        #     return r[state]['text']

        ### static method of getting boiler states ###
        with open(os.getcwd() + '/static/txt/boilerStates.txt') as f:
            json_data = json.load(f)
            return json_data[state]['text']

    def getBoilerStatus(self, status):
        ### nuro connect api call to dynamically get boiler statuses ###
        # headers = {"authorization": self.auth}
        # r = requests.get('https://app.nuroconnect.com/api/BoilerStatuses', headers=headers, verify=False)        
        # if r.ok:
        #     r = r.json()
        #     return r[status]['text']
        
        ### static method of getting boiler statuses ###
        with open(os.getcwd() + '/static/txt/boilerStatuses.txt') as f:
            json_data = json.load(f)
            return json_data[status]['text']

    def experimental(self):
        if self.isAuthenticated():
            # params = {
            #     "filter": '{"where": {"receivedDate":{"gte":"' + str(startTime) + '","lt":"' + str(endTime) + '"}}, "order":"receivedDate DESC", "skip": 0, "limit": 360, "interval": ' + str(interval) + '}'
            # }
            boilerID = '0d134902-b2f6-4c6b-8820-5c5071df80d0'
            siteID = '51d97a7a-4e1f-4388-a6e9-7c4582f16c15'
            headers = {"authorization": self.auth}
            r = requests.get(self.endpoint + "/#!/boiler-details/" + siteID + "/" + boilerID, headers=headers, verify=False)

            if r.ok:
                return r.text
        else:
            raise UnauthenticatedException()

    def getUser(self, id, userId):
        headers = {"authorization": id}
        r = requests.get(self.endpoint + "/api/users/" + userId, headers=headers, verify=False)
        if r.ok:
            return r.json()