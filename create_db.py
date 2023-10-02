import os
from dotenv import load_dotenv

load_dotenv()

import mysql.connector
import MySQLdb

mydb = MySQLdb.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USERNAME"),
    passwd=os.getenv("DB_PASSWORD"),
    db=os.getenv("DB_NAME"),
    autocommit=True,
    ssl_mode="VERIFY_IDENTITY",
    ssl={"CAFile": "/etc/ssl/cert.pem"},
)


my_cursor = mydb.cursor()

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
