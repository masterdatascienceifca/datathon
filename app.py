# -*- coding: utf-8 -*-

import pandas as pd
from shapely.geometry import Point, shape
import flask

from flask import Flask
from flask import render_template
from flask import jsonify
import json
import ssl
import psycopg2

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

@app.route("/data2/")

#This is the function that should get infor from the back-end
def get_data2():
    latitude = flask.request.args.get('lat')
    longitude = flask.request.args.get('long')
    raw_data = '{"type": "FeatureCollection", "features": [{"type": "Feature","properties": {"marker-color": "#0015ff", "marker-size": "medium",        "marker-symbol": "square"      },"geometry": {"type": "Point", "coordinates": ["' + longitude + '", "' + latitude + '"]}}]}'
    json_data = json.loads(raw_data)
    return jsonify(json_data)

@app.route("/nearest/")

def get_nearest_coordinates():
    latitude = float(flask.request.args.get('lat'))
    longitude = float(flask.request.args.get('long'))
    radius = 10
    m = 0.00463 / 500                   #1m in coordinates
    r = (radius * m) ** 2                               #radius to coordinates for the formula
    conn = psycopg2.connect("dbname='gisdata' user='gisuser' host='193.146.75.168' password='Y8nmEHTYSZHCgc8d'")
    cur = conn.cursor()
    #query = """SELECT * from datathon_filtered WHERE (power((lon -""" + str(abs(longitude)) + """),2)+ power((lat - """ + str(abs(latitude)) + """),2)) <= power(""" + str(r) + """,2) AND securetype LIKE 'Opened'"""
    query = """SELECT * from datathon_filtered WHERE((ACOS(SIN(""" + str(latitude) + """ * PI() / 180) * SIN(lat * PI() / 180) + COS(""" + str(latitude) + """ * PI() / 180) * COS(lat * PI() / 180) * COS((""" + str(longitude) + """ - lon) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) <""" + str(radius) +""" and securetype LIKE 'Opened'"""
     
    print(query)
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)
    m = 0.00463 / 500                   #1m in coordinates
    r = (radius * m) ** 2                               #radius to coordinates for the formula
    lon = abs(longitude)
    lat = abs(latitude)
    
    result = {'features': [], 'type': 'FeatureCollection'}      #dict object
    myLoc={"style": {"color": "#33cc33"}, "properties": {"marker-size": "medium", "marker-symbol": "square", "fillColor": "#33cc33", "popupContent": "My Location"}, "geometry": {"type": "Point"}, "type": "Feature"}
    myLoc["geometry"]["coordinates"]=[longitude,latitude]
    result["features"].append(myLoc)
    for row in rows:
        result["features"].append(point_json(row[1],row[0]))    #add point to json
    conn.close()
    return jsonify(result)

def point_json(latitude,longitude):
	result={"style": {"color": "#33cc33"}, "properties": {"marker-size": "medium", "marker-symbol": "square", "fillColor": "#33cc33", "popupContent": "Open WiFi Network"}, "geometry": {"type": "Point"}, "type": "Feature"}
	result["geometry"]["coordinates"]=[longitude,latitude]
	return result

@app.route("/get_votes/")

def get_votes_coordinates():
    radius = 10
    m = 0.00463 / 500                   #1m in coordinates
    r = (radius * m) ** 2                               #radius to coordinates for the formula
    conn = psycopg2.connect("dbname='gisdata' user='gisuser' host='193.146.75.168' password='Y8nmEHTYSZHCgc8d'")
    cur = conn.cursor()
    query = """SELECT * from votes"""
    print(query)
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)

    result = {'features': [], 'type': 'FeatureCollection'}      #dict object
    for row in rows:
        result["features"].append(point_json(str(row[1]),str(row[0])))    #add point to json
    
    conn.close()
    return jsonify(result)

@app.route("/send_vote/")
def send_vote():
    latitude = float(flask.request.args.get('lat'))
    longitude = float(flask.request.args.get('long'))
    conn = psycopg2.connect("dbname='gisdata' user='gisuser' host='193.146.75.168' password='Y8nmEHTYSZHCgc8d'")
    cur = conn.cursor()
    query = """ INSERT INTO votes (lon, lat) VALUES (""" + str(longitude) + """, """ + str(latitude) + """);"""
    print(query)
    cur.execute(query)
    conn.commit()
    result = {'features': [], 'type': 'FeatureCollection'}      #dict object
    myLoc={"style": {"color": "#33cc33"}, "properties": {"marker-size": "medium", "marker-symbol": "square", "fillColor": "#33cc33", "popupContent": "Thanks for voting!"}, "geometry": {"type": "Point"}, "type": "Feature"}
    myLoc["geometry"]["coordinates"]=[longitude,latitude]
    result["features"].append(myLoc)
    conn.close()
    return jsonify(result)

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('./datathon.crt', './datathon.key')
    app.run(host='0.0.0.0',port=443,debug=True,ssl_context=context)
