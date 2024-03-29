import mysql.connector
from dotenv import load_dotenv
import os
import datetime




load_dotenv()

user=str(os.getenv("user"))
password=str(os.getenv("password"))
host=str(os.getenv("host"))
database=str(os.getenv("database"))
port=os.getenv("port")

print(user)
print(password)
print(host)
print(database)
print(port)

db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)

cursor=db.cursor()

cursor.execute("SHOW TABLES")
print("tables")
for table_name in cursor:
   print(table_name)




print("devices")
query = ("SELECT * FROM devices")
cursor.execute(query)

for item in cursor:
   print(item)

'''

query = ("SELECT * FROM records WHERE device_id = " + str(1) )
cursor.execute(query)
for entry in cursor:
    print(entry)

'''

print("records")

query = ("SELECT * FROM records")
cursor.execute(query)

for item in cursor:
   print(item)








def getMaxDistInEntries(deviceid):
   query = ("SELECT MAX(distance) FROM records WHERE device_id = " + str(deviceid))
   cursor.execute(query)
   current = []
   for entry in cursor:
       current.append(entry)
   print(current[0][0])
   return current[0][0]

   db.commit()

getMaxDistInEntries(1)



'''
query = ("SELECT * FROM gps")
cursor.execute(query)

for item in cursor:
   print(item)
'''
#query = ("ALTER TABLE devices ADD COLUMN longtitude DECIMAL(8,5) NOT NULL;")
#cursor.execute(query)
'''
query = ("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'records'")
cursor.execute(query)
for item in cursor:
   print(item)

'''


def getlatestdistancevalue(deviceid):
   entries = []
   query = ("SELECT * FROM records where device_id =" + str(deviceid) ) 
   cursor.execute(query)
   maxtime = datetime.datetime(1970, 1, 1)
   
   entry = -1
   for item in cursor:      
      entrytime = item[2]

      if(entrytime > maxtime):
         maxtime = entrytime
         entry = item


   print(entry[3])
   return(entry[3])
   

getlatestdistancevalue(1)








def providelocationdata():
    
   db = mysql.connector.connect(user=user, password=password, host=host, database=database,port = port)
   cursor=db.cursor()
   query = ("SELECT * FROM records")
   cursor.execute(query)
   
   mainlist = []
   deviceidlist = []


   for entry in cursor:
      deviceid = entry[1]
      latitude = entry[6]
      longtitude = entry[7]

       
      if(latitude != 0 and longtitude != 0 and latitude and longtitude):
         if(deviceid not in deviceidlist):
               deviceidlist.append(deviceid)
               templist = []
               templist.append(deviceid)
               templist.append(latitude)
               templist.append(longtitude)
               mainlist.append(templist)

         else:
            listindex = deviceidlist.index(deviceid)
            mainlist[listindex][1] = latitude
            mainlist[listindex][2] = longtitude



   print(mainlist)
   print(deviceidlist)




providelocationdata()

cursor=db.cursor(buffered = True)
query = ("SELECT * FROM records")
cursor.execute(query)
    
mainlist = []
deviceidlist = []

for entry in cursor:
      
   deviceid = entry[1]
   latitude = entry[6] 
   longtitude = entry[7]
      
   if(latitude != 0 and longtitude != 0 and  latitude and longtitude):
      if(deviceid not in deviceidlist):
         deviecename = deviceid
         cursor2 = db.cursor(buffered = True)
         query2 = ("SELECT device_name FROM devices WHERE id = " + str(deviceid))
         cursor2.execute(query2)
         for entry2 in cursor2:
            print("cursor2")
            print(entry2)
            devicename = entry2
         
         
         deviceidlist.append(deviecename)
         templist = []
         templist.append(deviceid)
         templist.append(latitude)
         templist.append(longtitude)
         mainlist.append(templist)
      else:
         listindex = deviceidlist.index(deviceid)
         mainlist[listindex][1] = latitude
         mainlist[listindex][2] = longtitude







db.commit()


db.close()