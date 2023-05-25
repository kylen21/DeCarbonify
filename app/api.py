import requests
import random
from constants import *

def api_request(json, url):
    
    authorization_headers = {"Authorization": f"Bearer: {MY_API_KEY}"}
    response = requests.post(url, json=json, headers=authorization_headers).json()
    return response

def flight_emissions(origin_airport, destination_airport, bypass_API=False):
    """API Request for emission data based on origin and destination flight"""
    
    if bypass_API:
        return [random.randint(500, 1000), 'kg']
    
    legs = []
    legs.append(
        {
            "from": origin_airport,
            "to": destination_airport,
            "passengers": 1,
            "class": "economy"
        }
    )

    trips = {"legs": legs}

    json_body = trips
    url = "https://beta3.api.climatiq.io/travel/flights"
    ret = api_request(json_body, url)['legs'][0]
    
    results = [ret['co2e'], ret['co2e_unit']]
    return results

def dist_emissions(dist, activity_id, bypass_API=False):
    """API Request for emission data based on distance traveled by transportation type"""
    
    #Avoid API call for testing:
    if bypass_API:
        return [random.randint(1, 100), 'kg']
    
    #Check for biking/walking
    if activity_id is None:
        return [0, "kg"]
    
    emission_factor = {
        "uuid": activity_id
    }
    
    parameters = {
        "distance": dist,
        "distance_unit": "km"
    }
    
    json = {
        "emission_factor": emission_factor,
        "parameters": parameters
    }
    
    url = "https://beta3.api.climatiq.io/estimate"
    
    ret = api_request(json, url)
    return [ret["co2e"], ret["co2e_unit"]]

def cost_emissions(cost, activity_id, bypass_API=False):
    """API Request for emission data based on USD spent on clothing/apparel product or food"""
    
    #Avoid API call for testing:
    if bypass_API:
        return [random.randint(1, 100), 'kg']
    
    emission_factor = {
        "uuid": activity_id
    }
    
    parameters = {
        "money": cost,
        "money_unit": "usd"
    }
    
    json = {
        "emission_factor": emission_factor,
        "parameters": parameters
    }
    
    url = "https://beta3.api.climatiq.io/estimate"
    
    ret = api_request(json, url)
    return [ret["co2e"], ret["co2e_unit"]]