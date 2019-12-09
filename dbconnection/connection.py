import mysql.connector


db = mysql.connector.connect(
    host='localhost',
    user='steven',
    password='HatakeKakashi8294403049&',
    database='alumnos'
)

cursor = db.cursor()