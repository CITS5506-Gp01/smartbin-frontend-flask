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

query = ("SELECT * FROM distances WHERE device_id = " + str(1) )
cursor.execute(query)
for entry in cursor:
    print(entry)

'''

print("distances")

query = ("SELECT * FROM distances")
cursor.execute(query)

for item in cursor:
   print(item)






def getMaxDistInEntries(deviceid):
   query = ("SELECT MAX(distance) FROM distances WHERE device_id = " + str(deviceid))
   cursor.execute(query)
   current = []
   for entry in cursor:
       current.append(entry)
   print(current[0][0])
   return current[0][0]

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
query = ("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'distances'")
cursor.execute(query)
for item in cursor:
   print(item)

'''


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
   return(entry[3])
   

getlatestdistancevalue(1)


db.commit()


db.close()