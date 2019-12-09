import mysql.connector


db = mysql.connector.connect(
    host='localhost',
    user='youruser',#put your name user mysql 
    password='<your password>',#put your password user mysql 
    database='<your database name>'#put your database here
)

cursor = db.cursor()
