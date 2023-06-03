import os
from flask import Flask, render_template, request, redirect
import datetime
import re

app = Flask(__name__)

# Make sure API key is set
if not os.environ.get("NASA_API_KEY"):
    raise RuntimeError("NASA_API_KEY not set")

@app.route("/")
def home():
    """Homepage of App that contains relevant information"""

    return render_template("index.html")

@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    """Takes user info and outputs results on page"""

    return render_template("calculate.html")

@app.route("/bookmark", methods=["GET", "POST"])
def bookmark():
    """Bookmark function that saves their input in database and also access their saved information"""

    return render_template("bookmark.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact form to contact the owner of site. Currently saves information in a database."""

    if request.method == "POST":
        

        return render_template("contact_submitted.html")

    return render_template("contact.html")