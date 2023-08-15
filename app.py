import os
import sqlite3
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
import numpy as np
from datetime import datetime, timezone

from more import login_connect, login_required, retrieve_moon, retrieve_geo, retrieve_CME, retrieve_HSS, retrieve_weather, place_to_coord, retrieve_twilight, retrieve_sidereal

# Configures app and session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make sure API keys are set
if not os.environ.get("NASA_API_KEY"):
    raise RuntimeError("NASA_API_KEY not set")
if not os.environ.get("WEATHER_API_KEY"):
    raise RuntimeError("WEATHER_API_KEY not set")

# Database
if not os.path.isfile("data.db"):
    print("Database not found, creating now...")
    db_con = sqlite3.connect("data.db")
    db_con.close()

# Location
loc = [51.5074,-0.1278]

@app.route("/", methods=['POST', 'GET'])
def home():
    """Homepage of App that contains online information"""

    # Event updates
    Geostorm_event = retrieve_geo()
    if type(Geostorm_event) == dict:
        Geo_event_id = Geostorm_event['EventID']
        Geo_link = Geostorm_event['link']
    else:
        Geo_event_id = 0
        Geo_link = 0

    CME_event = retrieve_CME()
    if type(CME_event) == dict:
        CME_event_id = CME_event['EventID']
        CME_link = CME_event['link']
    else:
        CME_event_id = 0
        CME_link = 0

    HSS_event = retrieve_HSS()
    if type(HSS_event) == dict:
        HSS_event_id = HSS_event['EventID']
        HSS_link = HSS_event['link']
    else:
        HSS_event_id = 0
        HSS_link = 0

    # Weather status
    if request.method == "POST":

        query = request.form.get("search")
        country = request.form.get("country")

        result = place_to_coord(query, country)
        if result:
            lat = result['lat']
            long = result['lon']
            loc[0] = lat
            loc[1] = long
            weather_info = retrieve_weather(lat,long)
        else:
            weather_info = retrieve_weather(loc[0], loc[1])

    else:
        weather_info = retrieve_weather(loc[0], loc[1])

    now = datetime.now(timezone.utc)
    update_time = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    
    place = weather_info['name']
    coord_lon = weather_info['coord']['lon']
    coord_lat = weather_info['coord']['lat']
    weather = weather_info['weather'][0]['description']
    temp_now = round(weather_info['main']['temp'] - 273.15, 1)
    humidity = weather_info['main']['humidity']
    pressure = weather_info['main']['pressure']
    visibility = weather_info['visibility']
    cloudiness = weather_info['clouds']['all']
    wind_speed = weather_info['wind']['speed']

    # Lunar Info
    moon = retrieve_moon(date, loc)

    phen = "" # Formatting out
    times = ""
    for item in moon['moondata']:
        phen += item['phen'] + "/"
        times += item['time'] + ", "
    phen = phen[:-1]
    times = times[:-2]
    moon['phens'] = phen
    moon['times'] = times

    # Twilight Times
    twilights = retrieve_twilight(loc[0],loc[1])

    for key, value in twilights.items():
        converted = value[11:-6]

        twilights[key] = converted

    # Sidereal Time
    sidereal = retrieve_sidereal(loc, date, update_time)

    return render_template("index.html", Geo_event_id=Geo_event_id, Geo_link=Geo_link, CME_event_id=CME_event_id, CME_link=CME_link, HSS_event_id=HSS_event_id, HSS_link=HSS_link, place=place, coord_lon=coord_lon, coord_lat=coord_lat, weather=weather, temp_now=temp_now, humidity=humidity, pressure=pressure, vis=visibility, clouds=cloudiness, wind_speed=wind_speed, update_time=update_time, moon=moon, twilights=twilights, sidereal=sidereal, date=date)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Manage account details"""
    user_id = session['user_id']

    # Retrieve current account info
    with sqlite3.connect("data.db") as db_con:
        db = db_con.cursor()
        db.execute("SELECT * FROM accounts WHERE id = ?", (user_id, ))
        result = db.fetchall()
        if len(result) != 1:
            return redirect('/')
        
    username = result[0][1]
    password = result[0][2]
    name = result[0][3]
    city = result[0][4]

    if request.method == "POST":

        name_in = request.form.get("name")
        username_in = request.form.get("username")
        city_in = request.form.get("city")
        current = request.form.get("password-now")
        new = request.form.get("password-new")
        confirm = request.form.get("password-confirm")

        # Check if current password typed and correct
        if not current == password:
            print("Wrong password.")
            return redirect("/account")

        # Handle username & name & city
        if name_in:
            name = name_in
        
        if username_in:
            username = username_in

        if city_in:
            city = city_in

            # set new location
            city_coord = place_to_coord(city, None)
            loc[0] = city_coord['lat']
            loc[1] = city_coord['lon']
        
        # Handle passwords
        if (new == "") or (confirm == ""):
            pass
        elif (new == confirm):
            password = new
        else:
            print("Password mismatch!")
            return redirect("/account")

        # Write changes
        with sqlite3.connect("data.db") as db_con:
            db_cur = db_con.cursor()
            db_cur.execute("UPDATE accounts SET username = ?, password = ?, name = ?, city = ? WHERE id = ?", (username, password, name, city, user_id))
            print("Details updated.")

        return redirect("/")
     
    return render_template("account.html", name=name, username=username, city=city)

@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    """Takes user info and outputs results on page. Formula from https://spu.edu/ddowning/PHY1135/starelev.html"""

    if request.method == "POST":
        
        # Gathering parameters
        ra = request.form.get("RA")
        dec = request.form.get("dec")
        long = request.form.get("long")
        lat = request.form.get("lat")

        Dec = np.radians(float(dec))
        Lat = np.radians(float(lat))

        # Calculating hour angle
        Coord = [lat, long]
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        sidereal = retrieve_sidereal(Coord, today, time)
        local = sidereal['mean']
        
        (h,m,s) = local.split(':')
        lmst = float(h) + (float(m) / 60) + (float(s) / 3600)
        hour_angle_deg = (lmst - float(ra)) * 15 # Conversion factor from hours to degrees
        print(hour_angle_deg)

        if hour_angle_deg < 0:
            hour_angle_deg += 360
        elif hour_angle_deg > 360:
            hour_angle_deg -= 360

        print(local, lmst, hour_angle_deg)
        hour_angle_rad = np.radians(hour_angle_deg)
        
        # Calculate current altitude
        sin_alt = np.sin(Lat) * np.sin(Dec) + np.cos(Lat) * np.cos(Dec) * np.cos(hour_angle_rad)
        alt = np.degrees(np.arcsin(sin_alt))
        alt_out = round(alt, 2)

        # Max altitude
        sin_maxalt = np.sin(Lat) * np.sin(Dec) + np.cos(Lat) * np.cos(Dec)
        maxalt = np.degrees(np.arcsin(sin_maxalt))
        maxalt_out = round(maxalt, 2)

        return render_template("calculated.html", alt_out=alt_out, maxalt_out=maxalt_out)

    return render_template("calculate.html")

@app.route("/logbook", methods=["GET", "POST"])
def bookmark():
    """Bookmark function that saves their input in database and also access their saved information"""
    
    if session:
        user_id = session['user_id']

        if "save" in request.form and request.method == "POST":

            target = request.form.get("target_name")
            ra = request.form.get("RA")
            dec = request.form.get("dec")
            notes = request.form.get("notes")

            with sqlite3.connect("data.db") as db_con:
                db = db_con.cursor()
                db.execute("INSERT INTO bookmarks (user_id, target_name, RA, Dec, notes) VALUES (?, ?, ?, ?, ?);", (user_id, target, ra, dec, notes))
                db_con.commit()
                print("Item saved.")

            return redirect("/logbook")
        
        if "delete" in request.form and request.method == "POST":

            id = request.form.get("list")
            print(id)

            with sqlite3.connect("data.db") as db_con:
                db_cur = db_con.cursor()
                db_cur.execute("DELETE FROM bookmarks WHERE id = ?;", (id,))
                db_con.commit()
                print("Item deleted.")

            return redirect("/logbook")
            
        with sqlite3.connect("data.db") as db_con:
            db = db_con.cursor()
            db.execute("SELECT * FROM bookmarks WHERE user_id = ?", (user_id, ))
            result = db.fetchall()
            item_sum = len(result)
            print(f"Items found: {item_sum}")
            print(result)

        result_2 = []
        for item in result:
            new_dict = {}
            new_dict['id'] = item[0]
            new_dict['target_name'] = item[2]
            new_dict['ra'] = item[3]
            new_dict['dec'] = item[4]
            new_dict['notes'] = item[5]

            result_2.append(new_dict)
        
        return render_template("logbook.html", item_sum=item_sum, list=result_2)
    
    else:

        return render_template("logbook.html", item_sum=0, list=0)
    
@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact form to contact the owner of site. Currently saves information in a database."""

    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        purpose = request.form.get("purpose")
        message = request.form.get("message")
        confirm = request.form.get("data-check")
        promo = request.form.get("promo-check")

        if username == "":
            print("no username")
            username = None

        if promo == "on":
            promo_status = 1
        else:
            promo_status = 0

        # Access database
        with sqlite3.connect("data.db") as db_con:
            db = db_con.cursor()
            db.execute("INSERT INTO contact (name, username, email, purpose, message, promo) VALUES (?, ?, ?, ?, ?, ?);", (name, username, email, purpose, message, promo_status))
            db_con.commit()
            print("Form submitted.")

        return render_template("contact_submitted.html", name=name)

    # Get username
    if session:
        user_id = session['user_id']
        with sqlite3.connect("data.db") as db_con:
            db = db_con.cursor()
            db.execute("SELECT username FROM accounts WHERE id = ?", (user_id, ))
            result = db.fetchall()

        username = result[0][0]

        return render_template("contact.html", username=username)
    else:
        return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in or register to your account"""

    session.clear()
    
    if "login-submit" in request.form and request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Connect to Database
        out = login_connect(username,password)
        
        # set location
        city = out[0][4]
        coord = place_to_coord(city, None)
        loc[0] = coord['lat']
        loc[1] = coord['lon']

        return redirect("/")

    elif "register-submit" in request.form and request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        name = request.form.get("name")
        city = request.form.get("city")

        if password != confirm:
            return

        # Connect to Database
        with sqlite3.connect("data.db") as db_con:
            # Registration
            db = db_con.cursor()
            db.execute("INSERT INTO accounts (username, password, name, city) VALUES (?, ?, ?, ?)", (username, password, name, city))
            db_con.commit()
            print("New account created.")

        # Connect to Database
        out = login_connect(username, password)
        
        # set location
        city = out[0][4]
        coord = place_to_coord(city, None)
        loc[0] = coord['lat']
        loc[1] = coord['lon']

        return redirect('/')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    loc[0] = 51.5074
    loc[1] = -0.1278
    return redirect("/")