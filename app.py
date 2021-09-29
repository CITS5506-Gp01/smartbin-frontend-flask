from flask import Flask,flash
from flask import render_template, url_for , request

import mysql.connector
from dotenv import load_dotenv
import os

import matplotlib.pyplot as plt
import numpy as np
import mpld3




load_dotenv()

user=os.getenv("user")
password=os.getenv("password")
host=os.getenv("host")
database=os.getenv("database")
port=os.getenv("port")



db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

cursor=db.cursor()


app = Flask(__name__)
app.secret_key = os.getenv("secretkey")




#from app import routes

@app.route('/')
def index():
    flash(" TEST ") # TEST FLASHING MESSAGE
    query = ("SELECT * FROM devices")
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)
    

    return render_template('index.html',devices = devices)

#db.close()

@app.route('/entries/<deviceid>/')
def entries(deviceid):
    query =  ("SELECT * FROM devices WHERE id = " + deviceid )
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)
    device = devices[0]
    maxdistance = device[3]


    query = ("SELECT * FROM distances WHERE device_id = " + deviceid )
    cursor.execute(query)
    entries = []
    for entry in cursor:
        entries.append(entry)

    return render_template("entries.html", device=device,entries= entries,maxdistance=maxdistance,deviceid=deviceid)


@app.route("/api/drawplot/<deviceid>")
def drawplot(deviceid):

    query = ("SELECT max_distance FROM devices WHERE id = "+ deviceid )
    cursor.execute(query)

    maxdistance = -1
    for entry in cursor:
        maxdistance = int(entry[0])

    print("max distance = " + str(maxdistance))
    
    query = ("SELECT * FROM distances WHERE device_id = " + deviceid )
    cursor.execute(query)
    maxdistancerepeated= []
    distances = []
    timings = []

    for entry in cursor:
        distances.append(maxdistance - entry[3])
        timings.append(entry[2])
        maxdistancerepeated.append(maxdistance)


    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    plt.ylim([0, maxdistance+1])
    ax.plot(timings, distances)  # Plot some data on the axes.=
    ax.plot(timings,maxdistancerepeated)
    

    html_str = mpld3.fig_to_html(fig)

    return html_str


    
@app.route("/api/changemaxdistance/", methods=['POST'])
def changemaxdistance():
    r = request.get_json()
    maxdistance = r["maxdistance"]
    deviceid = r["deviceid"]
    print(maxdistance)

    query = "UPDATE devices SET max_distance = " + str(maxdistance) + " WHERE id = " + str(deviceid)
    
    cursor.execute(query)
    db.commit()

    print("device id = " + str(deviceid))

    return '',200
