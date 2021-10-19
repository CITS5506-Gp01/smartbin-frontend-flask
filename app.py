from flask import Flask,flash
from flask import render_template, url_for , request,redirect
import simplejson as json

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


#db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

print(" connected ")
#cursor=db.cursor(buffered=True)



app = Flask(__name__)
app.secret_key = os.getenv("secretkey")




#from app import routes

@app.route('/')
def index():
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT * FROM devices")
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)
    db.commit()
    db.close()

    return render_template('index.html',devices = devices,getlatestdistancevalue=getlatestdistancevalue,format=format)

@app.route('/Alert', methods=['GET','POST'])
def alert():
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
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
    db.close()
#db.close()

@app.route('/BatteryRemain1', methods=['GET','POST'])
def GetBatteryStatus():
    Max_Battery = round(getMaxBattery(1),2)
    Current_Battery = round(getCurrentBattery(1),2)
    print(Current_Battery)
    if Current_Battery >= 4.06:
        return "100%"
    elif Current_Battery <4.06 and Current_Battery >= 3.98:
        return "90%"
    elif Current_Battery <3.98 and Current_Battery >= 3.92:
        return "80%"
    elif Current_Battery <3.92 and Current_Battery >= 3.87:
        return "70%"
    elif Current_Battery <3.87 and Current_Battery >= 3.82:
        return "60%"
    elif Current_Battery <3.82 and Current_Battery >= 3.79:
        return "50%"
    elif Current_Battery <3.79 and Current_Battery >= 3.77:
        return "40%"
    elif Current_Battery <3.77 and Current_Battery >= 3.74:
        return "30%"
    elif Current_Battery <3.74 and Current_Battery >= 3.68:
        return "20%"
    elif Current_Battery <3.68 and Current_Battery >= 3.45:
        return "10%"
    else:
        return "Battery Low"

@app.route('/BatteryRemain2', methods=['GET','POST'])
def GetBatteryStatus2():
    Battery_Remain = 30
    if Battery_Remain >= 30:
        return "30%"

@app.route('/BatteryRemain3', methods=['GET','POST'])
def GetBatteryStatus3():
    Battery_Remain = 10
    if Battery_Remain >= 10:
        return "10%"

@app.route('/entries/<deviceid>/', methods=['GET', 'POST'])
def entries(deviceid):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query =  ("SELECT * FROM devices WHERE id = " + deviceid )
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)
    device = devices[0]
    maxdistance = device[3]


    query = ("SELECT * FROM records WHERE device_id = " + deviceid )
    cursor.execute(query)
    entries = []
    for entry in cursor:
        entries.append(entry)

    latestdistancevalue = getlatestdistancevalue(device[0])
    currentpercentage = None
    print(latestdistancevalue)
    if (latestdistancevalue):
        currentpercentage = format(((device[3] - latestdistancevalue)/device[3])*100,".2f")

    maxdistanceinentries = getMaxDistInEntries(deviceid)
    maxdistform = changemaxdistanceform()
    if maxdistform.validate_on_submit():
        newmaxdistance = maxdistform.maxDistance.data
        #print("new max distance " + str(newmaxdistance))
        query = "UPDATE devices SET max_distance = " + str(newmaxdistance) + " WHERE id = " + str(deviceid)
        cursor.execute(query)
        db.commit()
        db.close()
        return redirect(url_for('entries',deviceid=deviceid))
    print(maxdistance)

    latestlocation = getlocationdatafordevice(deviceid)



    '''
    datetimeform = testtdatetimeform()
    if datetimeform.validate_on_submit():

        return redirect(url_for('entries',deviceid=deviceid))

    '''
    
    db.commit()
    db.close()
    return render_template("entries.html", device=device,entries= entries,maxdistance=maxdistance,
    deviceid=deviceid,maxdistform=maxdistform,maxdistanceinentries=maxdistanceinentries,currentpercentage=currentpercentage,latestlocation = latestlocation)


@app.route("/api/drawplot/<deviceid>/<startdate>/<enddate>/")
def drawplot(deviceid,startdate,enddate):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor(buffered = True)

    fullstartdate = None
    fullenddate = None
    
    try:
        fullstartdate = splitjsdate(startdate)
        fullenddate = splitjsdate(enddate)
        if(fullstartdate >= fullenddate):
            fullstartdate = None
            fullenddate = None
    except:
        print("badinput")
    


    query = ("SELECT max_distance FROM devices WHERE id = "+ deviceid )
    cursor.execute(query)

    maxdistance = -1
    for entry in cursor:
        maxdistance = entry[0]

    #db.close()
    #print("max distance = " + str(maxdistance))
    #db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

    query = ("SELECT * FROM records WHERE device_id = " + deviceid )
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


    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    plt.ylim([0, maxdistance])

    if(fullstartdate and fullenddate):
        plt.xlim(fullstartdate,fullenddate)

    ax.plot(timings, distances, color="blue", marker='o')  # Plot some data on the axes.
    ax.plot(timings,maxdistancerepeated,color="red")
    if drawthresholds == True:
        ax.plot(timings, onethirdthresholdrepeated,color="green") 
        ax.plot(timings,twothirdsthresholdrepeated,color="orange")

 
    db.commit()
    db.close()

    html_str = mpld3.fig_to_html(fig)

    return html_str







@app.route("/api/drawtemperatureplot/<deviceid>/<startdate>/<enddate>/")
def drawtemperatureplot(deviceid,startdate,enddate):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor(buffered = True)
    fullstartdate = None
    fullenddate = None
    
    try:
        fullstartdate = splitjsdate(startdate)
        fullenddate = splitjsdate(enddate)
        if(fullstartdate >= fullenddate):
            fullstartdate = None
            fullenddate = None
    except:
        print("otherbadinput")
    
    #db.close()
    #print("max distance = " + str(maxdistance))
    #db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

    query = ("SELECT * FROM records WHERE device_id = " + deviceid )
    cursor.execute(query)

    temperatures = []
    timings = []
    
    
    for entry in cursor:
        temperature =  entry[4]
        timing = entry[2]
        if(temperature):
            if(temperature <= 85 and temperature >= -40):
                temperatures.append(temperature)
                timings.append(timing)


    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    
    #plt.ylim([-40, 85])
    if(fullstartdate and fullenddate):
        plt.xlim(fullstartdate,fullenddate)

    ax.plot(timings, temperatures, color="black", marker='o')  # Plot some data on the axes.
    db.commit()
    db.close()

    html_str = mpld3.fig_to_html(fig)

    return html_str


@app.route("/api/providelocationdata/",methods=["GET"])
def providelocationdata():
    
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor(buffered = True)
    query = ("SELECT * FROM records")
    cursor.execute(query)
    
    mainlist = []
    deviceidlist = []



    for entry in cursor:
        
        deviceid = entry[1]
        latitude = entry[6] 
        longtitude = entry[7]
        
        deviecename = deviceid

        if(latitude != 0 and longtitude != 0 and latitude and longtitude):
            if(deviceid not in deviceidlist):
                cursor2 = db.cursor(buffered = True)
                query2 = ("SELECT device_name FROM devices WHERE id = " + str(deviceid))
                cursor2.execute(query2)
                for entry2 in cursor2:
                    print(entry2)
                    devicename = entry2
                
                
                deviceidlist.append(deviceid)

                templist = []
                templist.append(devicename)
                templist.append(latitude)
                templist.append(longtitude)

                mainlist.append(templist)

            else:
                listindex = deviceidlist.index(deviceid)
                mainlist[listindex][1] = latitude
                mainlist[listindex][2] = longtitude



    print(mainlist)


    '''
        templist = []
        devicename = entry[1]
        latitude = entry[4]
        longtitude = entry[5]

        if(latitude and longtitude):
            templist.append(devicename)
            templist.append(latitude)
            templist.append(longtitude)
            
            mainlist.append(templist)
    '''
    
    db.commit()
    db.close()
    #return(jsonify(mainlist))
    return json.dumps(mainlist)


def getlocationdatafordevice(deviceid):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT * FROM records WHERE device_id = "+ str(deviceid))
    cursor.execute(query)
    
    deviceid = None
    latitude = None
    longtitude = None

    for entry in cursor:
        
        nextdeviceid = entry[1]
        nextlatitude = entry[6]
        nextlongtitude = entry[7]

        if(nextlatitude != 0 and nextlongtitude != 0 and nextlatitude and nextlongtitude):
            deviceid = nextdeviceid
            latitude = nextlatitude
            longtitude = nextlongtitude

    returnlist = [latitude,longtitude]
    return returnlist



    


def splitjsdate(stringdate):

    splitdatetime = stringdate.split("T")
    date = splitdatetime[0]
    time = splitdatetime[1]

    #print(date)
    #print(time)

    datesplit = date.split("-")
    year = int(datesplit[0])
    month = int(datesplit[1])
    day = int( datesplit[2])

    timesplit = time.split(":")
    hour = int(timesplit[0])
    minute = int(timesplit[1])

    #print(year+month+day+hour+minute)

    fulldatetime = datetime.datetime(year,month,day,hour,minute)
    #print(fulldatetime)
    return fulldatetime

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



# Additional support functions
def calculate_dis(MaxDistance,Current):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    current_hight = MaxDistance - Current
    percentage = current_hight / MaxDistance
    result = "{:.0%}".format(percentage)
    db.commit()
    db.close()
    return result


def check_device_current_distance(DeviceID):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT distance FROM records WHERE device_id = " + str(DeviceID) + " ORDER BY id DESC limit 1")
    cursor.execute(query)
    current = []
    for datas in cursor:
        current.append(datas)
    db.commit()
    db.close()

    return current[0][0]

def get_record_date(DeviceID):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT logged_datetime FROM records WHERE distance = (SELECT MIN(distance) FROM records WHERE device_id =" + str(DeviceID) + ")")
    cursor.execute(query)
    date = []
    for datas in cursor:
        date.append(datas)
    db.commit()
    db.close()

    return date[0][0]

def getMaxDistInEntries(deviceid):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT MAX(distance) FROM records WHERE device_id = " + str(deviceid))
    cursor.execute(query)
    current = []
    for entry in cursor:
       current.append(entry)
    db.commit()
    db.close()

    return current[0][0]

def getlatestdistancevalue(deviceid):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT * FROM records where device_id =" + str(deviceid) ) 
    cursor.execute(query)
    maxtime = datetime.datetime(1970, 1, 1)
    
    entry = None
    for item in cursor:      
        entrytime = item[2]
        if(entrytime > maxtime):
            maxtime = entrytime
            entry = item[3]

    db.commit() 
    db.close()
    return(entry)


def getMaxBattery(DeviceID):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT Max(battery) FROM records WHERE device_id = " + str(DeviceID))
    cursor.execute(query)
    current = []
    for datas in cursor:
        current.append(datas)
    db.commit()
    db.close()

    return current[0][0]


def getCurrentBattery(DeviceID):
    db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
    cursor=db.cursor()
    query = ("SELECT battery FROM records WHERE device_id = " + str(DeviceID) + " ORDER BY id DESC limit 1")
    cursor.execute(query)
    current = []
    for datas in cursor:
        current.append(datas)
    db.commit()
    db.close()

    return current[0][0]