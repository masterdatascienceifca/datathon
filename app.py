# -*- coding: utf-8 -*-

import pandas as pd
from shapely.geometry import Point, shape

from flask import Flask
from flask import render_template
from flask import jsonify
import json


data_path = './input/'
n_samples = 30000

def get_age_segment(age):
    if age <= 22:
        return '22-'
    elif age <= 26:
        return '23-26'
    elif age <= 28:
        return '27-28'
    elif age <= 32:
        return '29-32'
    elif age <= 38:
        return '33-38'
    else:
        return '39+'

def get_location(longitude, latitude, provinces_json):
    
    point = Point(longitude, latitude)

    for record in provinces_json['features']:
        polygon = shape(record['geometry'])
        if polygon.contains(point):
            return record['properties']['name']
    return 'other'


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data/")

#This is the function that should get infor from the back-end
def get_data():
    with open(data_path + 'datathon.geojson') as data_file:
        json_data = json.load(data_file)
    return jsonify(json_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
