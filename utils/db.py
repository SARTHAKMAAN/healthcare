import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password@1",
        database="health_tracker"
<<<<<<< HEAD
    )
=======
    )
>>>>>>> 96cc0499af803d9666e1418f4ea418f22480aae5
