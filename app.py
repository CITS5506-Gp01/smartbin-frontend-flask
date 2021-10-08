from flask import Flask,flash
from flask import render_template, url_for , request,redirect

import mysql.connector  

import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import mpld3
import time
import datetime

from forms import changemaxdistanceform 

''' 
from dotenv import load_dotenv
load_dotenv()
'''

user=os.getenv("user")
password=os.getenv("password")
host=os.getenv("host")
database=os.getenv("database")
port=os.getenv("port")



print(user)
print(password)
print(host)
print(database)
print(port)


db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

print(" connected ")
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
    db.commit()
    


    return render_template('index.html',devices = devices,getlatestdistancevalue=getlatestdistancevalue,format=format)

@app.route('/Alert', methods=['GET','POST'])
def alert():
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
        if volume_percentage >= "{:.0%}".format(30) and volume_percentage <= "{:.0%}".format(50): # Need to change later, Test Flash
            Message = "Alert! The Bin: {0} volume has reached {1}. Recorded at: {2} Pretty Clean!".format(items[1],volume_percentage,record_date)
            return Message
            #flash( Message)
            #flash(Infor)
        elif volume_percentage >= "{:.0%}".format(50) and volume_percentage <= "{:.0%}".format(70):
            Message = "Alert! The Bin: {0} volume has reached {1}. Recorded at: {2} Need attention!".format(items[1],volume_percentage,record_date)
            return Message
            #flash(Message)
        elif volume_percentage >= "{:.0%}".format(70) and volume_percentage <= "{:.0%}".format(90):
            Message = "Alert! The Bin: {0} volume has reached {1}. Recorded at: {2} Better to have a look! ".format(items[1],volume_percentage,record_date)
            Infor = "Clean actions required"
            return Message
            #flash(Message)
            #flash(Infor)
        elif volume_percentage >= "{:.0%}".format(90):
            Message = "Warning! The Bin: {0} is almost full, please empty the bin ASAP! ".format(items[1])
            return Message
            #flash(Message)
        else:
            Message = "Nothing to worry about"
            return Message
            #flash(Message)
    db.commit()
#db.close()

@app.route('/entries/<deviceid>/', methods=['GET', 'POST'])
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

    currentdistance = getlatestdistancevalue(deviceid)
    currentpercentage = format(((device[3] - getlatestdistancevalue(device[0]))/device[3])*100,".2f")

    maxdistanceinentries = getMaxDistInEntries(deviceid)
    maxdistform = changemaxdistanceform()
    if maxdistform.validate_on_submit():
        newmaxdistance = maxdistform.maxDistance.data
        #print("new max distance " + str(newmaxdistance))
        query = "UPDATE devices SET max_distance = " + str(newmaxdistance) + " WHERE id = " + str(deviceid)
        cursor.execute(query)
        db.commit()
        return redirect(url_for('entries',deviceid=deviceid))
    print(maxdistance)
    db.commit()
    return render_template("entries.html", device=device,entries= entries,maxdistance=maxdistance,
    deviceid=deviceid,maxdistform=maxdistform,maxdistanceinentries=maxdistanceinentries,currentpercentage=currentpercentage)


@app.route("/api/drawplot/<deviceid>")
def drawplot(deviceid):

    query = ("SELECT max_distance FROM devices WHERE id = "+ deviceid )
    cursor.execute(query)

    maxdistance = -1
    for entry in cursor:
        maxdistance = entry[0]

    #db.close()
    #print("max distance = " + str(maxdistance))
    #db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

    query = ("SELECT * FROM distances WHERE device_id = " + deviceid )
    cursor.execute(query)
    maxdistancerepeated= []
    onethirdthresholdrepeated = []
    twothirdsthresholdrepeated = []
    distances = []
    timings = []
    
    drawthresholds = True

    for entry in cursor:
        distances.append(maxdistance - entry[3])
        timings.append(entry[2])
        maxdistancerepeated.append(maxdistance)
        if drawthresholds == True:
            third = maxdistance/3
            onethirdthresholdrepeated.append(third)
            twothirds = third*2
            twothirdsthresholdrepeated.append(twothirds)





    print(distances)
    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    plt.ylim([0, maxdistance+1])
    ax.plot(timings, distances, color="blue", marker='o')  # Plot some data on the axes.
    ax.plot(timings,maxdistancerepeated,color="red")
    if drawthresholds == True:
        ax.plot(timings, onethirdthresholdrepeated,color="green") 
        ax.plot(timings,twothirdsthresholdrepeated,color="orange")

    
    
    db.commit()
    html_str = mpld3.fig_to_html(fig)

    return html_str


#changed impl to forms, but will keep this here just in case
'''
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
'''

'''
@app.route("/api/returnbinsthatarefillingup",methods = ["GET"])
def returnbinsthatarefillingup:
    print("todolol")
# Additional support functions
'''
def calculate_dis(MaxDistance,Current):
    current_hight = MaxDistance - Current
    percentage = current_hight / MaxDistance
    result = "{:.0%}".format(percentage)
    db.commit()
    return result


def check_device_current_distance(DeviceID):
    query = ("SELECT distance FROM distances WHERE device_id = " + str(DeviceID) + " ORDER BY id DESC limit 1")
    cursor.execute(query)
    current = []
    for datas in cursor:
        current.append(datas)
    db.commit()

    return current[0][0]

def get_record_date(DeviceID):
    query = ("SELECT logged_datetime FROM distances WHERE distance = (SELECT MIN(distance) FROM distances WHERE device_id =" + str(DeviceID) + ")")
    cursor.execute(query)
    date = []
    for datas in cursor:
        date.append(datas)
    db.commit()

    return date[0][0]

def getMaxDistInEntries(deviceid):
    query = ("SELECT MAX(distance) FROM distances WHERE device_id = " + str(deviceid))
    cursor.execute(query)
    current = []
    for entry in cursor:
       current.append(entry)
    db.commit()

    return current[0][0]

def getlatestdistancevalue(deviceid):
    entries = []
    query = ("SELECT * FROM distances where device_id =" + str(deviceid) ) 
    cursor.execute(query)
    maxtime = datetime.datetime(1970, 1, 1)
    
    entry = -1
    for item in cursor:      
        entrytime = item[2]
        if(entrytime > maxtime):
            maxtime = entrytime
            entry = item
    
    
    print(entry[3])
    db.commit() 
    return(entry[3])