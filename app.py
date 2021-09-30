from flask import Flask,flash
from flask import render_template, url_for , request

import mysql.connector
from dotenv import load_dotenv
import os
import matplotlib
matplotlib.use('Agg') 
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
    query = ("SELECT * FROM devices")
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)
    for items in devices:
        device_maxDistance = items[3]
        current_mindistance = check_device_current_distance(items[0]) # Check each device's current recorded min distance
        volume_percentage = calculate_dis(device_maxDistance,current_mindistance)
        record_date = get_record_date(items[0])
        if volume_percentage >= "{:.0%}".format(30): # Need to change later, Test Flash
            Message = "Alert! The Bin: {0} volume has reached {1}. Recorded at: {2}".format(items[1],volume_percentage,record_date)
            Infor = "Clean actions required"
            flash( Message)
            flash(Infor)
        elif volume_percentage >= "{:.0%}".format(50):
            Message = "Alert! The Bin: {0} volume has reached {1}. Recorded at: {2}".format(items[1],volume_percentage,record_date)
            flash(Message)
        elif volume_percentage >= "{:.0%}".format(70):
            Message = "Alert! The Bin: {0} volume has reached {1}. Recorded at: {2}".format(items[1],volume_percentage,record_date)
            Infor = "Clean actions required"
            flash(Message)
            flash(Infor)
        elif volume_percentage >= "{:.0%}".format(90):
            Message = "Warning! The Bin: {0} is almost full, please empty the bin ASAP".format(items[1])
            flash(Message)
        else:
            Message = "Nothing to worry about"
            flash(Message)

    

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



# Additional support functions

def calculate_dis(MaxDistance,Current):
    current_hight = MaxDistance - Current
    percentage = current_hight / MaxDistance
    result = "{:.0%}".format(percentage)
    return result


def check_device_current_distance(DeviceID):
    query = ("SELECT MIN(distance) FROM distances WHERE device_id = " + str(DeviceID))
    cursor.execute(query)
    current = []
    for datas in cursor:
        current.append(datas)
    return current[0][0]

def get_record_date(DeviceID):
    query = ("SELECT logged_datetime FROM distances WHERE distance = (SELECT MAX(distance) FROM distances WHERE device_id =" + str(DeviceID) + ")")
    cursor.execute(query)
    date = []
    for datas in cursor:
        date.append(datas)
    return date[0][0]