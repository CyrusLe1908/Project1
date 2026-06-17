from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db_connection

app = Flask(__name__)
# Kích hoạt CORS để cho phép gọi API từ cổng Live Server (Port 5500)
CORS(app)

# =======================================================
# 1. API LẤY DANH SÁCH SẢN PHẨM (GET)
# =======================================================
@app.route('/api/products', methods=['GET']) # Đã sửa từ list_users thành methods chuẩn của Flask
def get_products():
    """API lấy toàn bộ danh sách sản phẩm từ MySQL XAMPP"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Không thể kết nối Database"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Truy vấn đúng các trường cấu trúc Database thật của bạn
        cursor.execute("SELECT product_id, product_name, category_id, import_price, unit, stock_quantity FROM products")
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify(products)
    except Exception as e:
        print(f"Lỗi truy vấn sản phẩm: {str(e)}")
        return jsonify({"error": "Lỗi hệ thống phía Server"}), 500

# =======================================================
# 2. API THÊM MỚI SẢN PHẨM (POST)
# =======================================================
@app.route('/api/products', methods=['POST'])
def add_product():
    """API tiếp nhận gói dữ liệu JSON và thêm mới sản phẩm vào MySQL"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Không thể kết nối Database"}), 500
        
    try:
        # Nhận gói dữ liệu JSON do hàm fetch() của Frontend truyền lên
        data = request.get_json()
        
        product_name = data.get('product_name')
        category_id = data.get('category_id')
        unit = data.get('unit')
        stock_quantity = data.get('stock_quantity')
        import_price = data.get('import_price')
        
        # Kiểm tra tính hợp lệ dữ liệu
        if not product_name or stock_quantity is None or import_price is None:
            return jsonify({"message": "Thiếu dữ liệu bắt buộc"}), 400
            
        cursor = conn.cursor()
        # Thực thi câu lệnh INSERT dữ liệu thực tế vào MySQL
        sql = """
            INSERT INTO products (product_name, category_id, unit, stock_quantity, import_price) 
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (product_name, category_id, unit, stock_quantity, import_price)
        cursor.execute(sql, values)
        
        conn.commit()  # Lưu dữ liệu vào MySQL
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Thêm sản phẩm thành công!", "status": "success"}), 201
        
    except Exception as e:
        print(f"Lỗi khi thêm sản phẩm vào DB: {str(e)}")
        return jsonify({"message": "Lỗi xử lý cơ sở dữ liệu"}), 500

# =======================================================
# 3. API LẤY DANH SÁCH ĐẠI LÝ (GET)
# =======================================================
@app.route('/api/agencies', methods=['GET'])
def get_agencies():
    """API lấy toàn bộ danh sách đại lý từ MySQL XAMPP"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Không thể kết nối Database"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT agency_code, agency_name, representative, phone, level, debt FROM agencies")
        agencies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify(agencies)
    except Exception as e:
        print(f"Lỗi truy vấn đại lý: {str(e)}")
        return jsonify({"error": "Lỗi hệ thống phía Server"}), 500

# =======================================================
# KHỞI CHẠY SERVER FLASK
# =======================================================
if __name__ == '__main__':
    print("Đang kiểm tra kết nối tới MySQL XAMPP...")
    test_conn = get_db_connection()
    if test_conn:
        print("-> Kết nối MySQL thành công!")
        test_conn.close()
    else:
        print("-> CẢNH BÁO: Không thể kết nối MySQL. Vui lòng bật XAMPP!")
        
    print("Đang khởi động Flask Server tại cổng 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)