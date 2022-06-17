import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host = 'yh-db.ckdh7nnfozjl.ap-northeast-2.rds.amazonaws.com',
        database='recipe_db',
        user='recipe_user',
        password='recipe1234'
    )
    
    return connection
    