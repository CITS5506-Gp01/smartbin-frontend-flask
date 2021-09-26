from flask import Flask
from flask import render_template, url_for

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

user=os.getenv("user")
password=os.getenv("password")
host=os.getenv("host")
database=os.getenv("database")
port=os.getenv("port")



db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

cursor=db.cursor()


app = Flask(__name__)





#from app import routes

@app.route('/')
def index():
    query = ("SELECT * FROM devices")
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)


    return render_template('index.html',devices = devices)

#db.close()

@app.route('/device/<deviceid>/')
def entries(deviceid):

    query =  ("SELECT * FROM devices WHERE id = " + deviceid )
    cursor.execute(query)
    devices = []
    for device in cursor:
        devices.append(device)
    device = devices[0]


    query = ("SELECT * FROM distances WHERE device_id = " + deviceid )
    cursor.execute(query)
    entries = []
    for entry in cursor:
        entries.append(entry)



    return render_template("entries.html", device=device,entries= entries)