import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

def get_db_connection():
    """Hàm khởi tạo và trả về kết nối tới MySQL (dùng biến môi trường)"""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            port=int(os.environ.get("DB_PORT"))
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("====== LỖI KẾT NỐI DATABASE ======")
        print(e)
        print("==================================")
        return None