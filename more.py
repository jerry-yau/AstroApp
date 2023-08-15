import os
import sqlite3
import requests
from functools import wraps
from flask import request, redirect, url_for, session

def login_required(f):
    """
    Requires login for routes
    Based on https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["user_id"] is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function 

def retrieve_geo():
    """Look up NASA DONKI Geomagnetic Storm history"""

    try:
        NASA_API = os.environ.get("NASA_API_KEY")
        url = f"https://api.nasa.gov/DONKI/GST?api_key={NASA_API}"
        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException:
        return None

    if not result.content:
        empty = "No events in the last 30 days."
        return empty

    try:
        result_parsed = result.json()
        latest_result = result_parsed[len(result_parsed) - 1]
        output = {}
        output['EventID'] = latest_result['gstID']
        output['link'] = latest_result['link']
        return output
        
    except KeyError:
        return None
    
def retrieve_CME():
    """Look up NASA DONKI CME history"""

    try:
        NASA_API = os.environ.get("NASA_API_KEY")
        url = f"https://api.nasa.gov/DONKI/CME?api_key={NASA_API}"
        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException:
        return None
    
    if not result.content:
        empty = "No events in the last 30 days."
        return empty

    try:
        result_parsed = result.json()
        latest_result = result_parsed[len(result_parsed) - 1]
        output = {}
        output['EventID'] = latest_result['activityID']
        output['link'] = latest_result['link']
        return output
    except KeyError:
        return None
    
def retrieve_HSS():
    """Look up NASA DONKI HSS history"""

    try:
        NASA_API = os.environ.get("NASA_API_KEY")
        url = f"https://api.nasa.gov/DONKI/HSS?api_key={NASA_API}"
        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException:
        return None
    
    if not result.content:
        empty = "No events in the last 30 days."
        return empty

    try:
        result_parsed = result.json()
        output = {}
        output['EventID'] = result_parsed[0]['hssID']
        output['link'] = result_parsed[0]['link']
        return output
        
    except KeyError:
        return None

def retrieve_weather(lat=51.51,lon=-0.13):
    """Look up weather information given latitude and longitude, otherwise London"""

    try:
        WEATHER_API = os.environ.get("WEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API}"
        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException:
        return None
    
    if not result.content:
        empty = "N/A"
        return empty
    
    try:
        result_parsed = result.json()
        output = result_parsed
        return output
    except KeyError:
        return None

def place_to_coord(search, country):
    """Converts place names to coordinates"""
    
    try:
        WEATHER_API = os.environ.get("WEATHER_API_KEY")
        if country == "Select country":
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={search}&limit=5&appid={WEATHER_API}"
        else:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={search},{country}&limit=5&appid={WEATHER_API}"
        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException:
        return None
    
    try:
        result_parsed = result.json()
        if result_parsed:
            output = result_parsed[0]
            return output
        else:
            return None
    except KeyError:
        return None

def retrieve_moon(date, loc):
    """Retrieves moon info: current phase, next phase, rise/set/transit"""

    try:
        url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={date}&coords={loc[0]},{loc[1]}"
        url2 = f"https://aa.usno.navy.mil/api/moon/phases/date?date={date}&nump=1"
        result = requests.get(url)
        result2 = requests.get(url2)
        result.raise_for_status()
        result2.raise_for_status()
    except requests.RequestException:
        return None
    
    try:
        parsed = result.json()
        parsed2 = result2.json()
        output = {}
        output['phase'] = parsed['properties']['data']['curphase']
        output['moondata'] = parsed['properties']['data']['moondata']
        output['nextphase'] = parsed2['phasedata'][0]
    except KeyError:
        return None

    return output

def retrieve_twilight(lat,lon):
    """Retrieves twilight information"""
    try:
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date=today&formatted=0"
        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException:
        return None
    
    try:
        parsed = result.json()
        output = {}
        output['sunrise'] = parsed['results']['sunrise']
        output['sunset'] = parsed['results']['sunset']
        output['astro_start'] = parsed['results']['astronomical_twilight_begin']
        output['civil_start'] = parsed['results']['civil_twilight_begin']
        output['nautical_start'] = parsed['results']['nautical_twilight_begin']
        output['nautical_end'] = parsed['results']['nautical_twilight_end']
        output['civil_end'] = parsed['results']['civil_twilight_end']
        output['astro_end'] = parsed['results']['astronomical_twilight_end']
    except KeyError:
        return None
    
    return output

def retrieve_sidereal(loc, date, update_time):
    """Retrieves sidereal times."""

    try:
        url = f"https://aa.usno.navy.mil/api/siderealtime?date={date}&coords={loc[0]},{loc[1]}&reps=1&intv_mag=5&intv_unit=minutes%20&time={update_time}"
        result = requests.get(url)
        result.raise_for_status()
    except:
        return None
    
    try:
        parsed = result.json()
        output = {}
        output['apparent'] = parsed['properties']['data'][0]['last']
        output['mean'] = parsed['properties']['data'][0]['lmst']
    except:
        return None
    
    return output

def login_connect(username, password):
    # Connect to Database
    with sqlite3.connect("data.db") as db_con:
        db = db_con.cursor()
        db.execute("SELECT * FROM accounts WHERE username = ? AND password = ?", (username, password))
        result = db.fetchall()
        if len(result) != 1:
            print('Account not identified.')
            return redirect('/login') 
           
    session["user_id"] = result[0][0]

    return result