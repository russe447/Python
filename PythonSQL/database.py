import mysql.connector

config = {
    'user': 'root',
    'password': 'pass',
    'host': 'localhost'
}

db = mysql.connector.connect(**config)
cursor = db.cursor()

