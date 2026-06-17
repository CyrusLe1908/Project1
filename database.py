import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Hàm khởi tạo và trả về kết nối tới MySQL trong XAMPP"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',         # Tài khoản mặc định của XAMPP
            password='',         # Mật khẩu mặc định của XAMPP để trống
            database='npp_manager',
            port=3306            
        )
        if connection.is_connected():
            return connection
    except Error as e:
        # Bỏ dấu # ở đây để Terminal hiển thị rõ nguyên nhân nếu lỗi
        print("====== LỖI KẾT NỐI DATABASE ======")
        print(e)
        print("==================================")
        return None