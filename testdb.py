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

cursor.execute("SHOW TABLES")

for table_name in cursor:
   print(table_name)


query = ("SELECT * FROM devices")
cursor.execute(query)

for item in cursor:
   print(item)


query = ("SELECT * FROM distances WHERE device_id = " + str(1) )
cursor.execute(query)
for entry in cursor:
    print(entry)


db.close()