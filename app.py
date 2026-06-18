from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates', static_folder='static')
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
        cursor.execute("""SELECT 
                       id,
                       sku,
                       product_name,
                       category,
                       import_price,
                       unit,
                       stock_quantity
                    FROM products
                """)
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
        category = data.get('category')
        unit = data.get('unit')
        stock_quantity = data.get('stock_quantity')
        import_price = data.get('import_price')
        
        # Kiểm tra tính hợp lệ dữ liệu
        if not product_name or stock_quantity is None or import_price is None:
            return jsonify({"message": "Thiếu dữ liệu bắt buộc"}), 400
            
        cursor = conn.cursor()

        # Sinh SKU trước khi insert để tránh lỗi khi cột `sku` là NOT NULL UNIQUE
        cursor.execute("""
            SELECT MAX(id) as max_id
            FROM products
        """)
        row = cursor.fetchone()
        last_id = (row[0] if row and row[0] is not None else 0)
        sku = f"SP-{str(last_id + 1).zfill(3)}"

        # Thực thi câu lệnh INSERT dữ liệu thực tế vào MySQL (bao gồm sku)
        sql = """
        INSERT INTO products
        (sku, product_name, category, unit, stock_quantity, import_price)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (sku, product_name, category, unit, stock_quantity, import_price)
        cursor.execute(sql, values)
        conn.commit()  # Lưu dữ liệu vào MySQL

        cursor.close()
        conn.close()

        return jsonify({"message": "Thêm sản phẩm thành công!", "status": "success"}), 201
        
    except Exception as e:
        print(f"Lỗi khi thêm sản phẩm vào DB: {str(e)}")
        return jsonify({"message": "Lỗi xử lý cơ sở dữ liệu"}), 500
    
# =======================================================
# API LẤY CHI TIẾT 1 SẢN PHẨM
# =======================================================

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):

    conn = get_db_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM products
            WHERE id = %s
        """, (product_id,))

        product = cursor.fetchone()

        cursor.close()
        conn.close()

        if not product:
            return jsonify({"error": "Không tìm thấy sản phẩm"}), 404

        return jsonify(product)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =======================================================
# API XÓA SẢN PHẨM
# =======================================================

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM products
            WHERE id = %s
        """, (product_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Xóa sản phẩm thành công"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
# =======================================================
# API CẬP NHẬT SẢN PHẨM
# =======================================================

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):

    conn = get_db_connection()

    try:

        data = request.get_json()

        product_name = data.get('product_name')
        category = data.get('category')
        unit = data.get('unit')
        stock_quantity = data.get('stock_quantity')
        import_price = data.get('import_price')

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE products
            SET
                product_name = %s,
                category = %s,
                unit = %s,
                stock_quantity = %s,
                import_price = %s
            WHERE id = %s
        """, (
            product_name,
            category,
            unit,
            stock_quantity,
            import_price,
            product_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Cập nhật thành công"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

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
# 4. API DASHBOARD
# =======================================================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():

    conn = get_db_connection()

    if conn is None:
        return jsonify({"error": "Không thể kết nối Database"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        total_products = cursor.fetchone()['total_products']

        cursor.execute("SELECT COUNT(*) as total_agencies FROM agencies")
        total_agencies = cursor.fetchone()['total_agencies']

        cursor.execute("""
    SELECT COUNT(*) as low_stock
    FROM products
    WHERE stock_quantity < 200
""")
        low_stock = cursor.fetchone()['low_stock']

        # Tổng tồn kho (tổng số lượng trên tất cả sản phẩm)
        cursor.execute("SELECT SUM(stock_quantity) as total_stock FROM products")
        total_stock = cursor.fetchone()['total_stock'] or 0

        cursor.close()
        conn.close()

        return jsonify({
            "total_products": total_products,
            "total_agencies": total_agencies,
            "low_stock": low_stock,
            "total_stock": total_stock
        })

    except Exception as e:
        print(e)
        return jsonify({"error": "Lỗi server"}), 500
    
# =======================================================
# API ĐĂNG NHẬP
# =======================================================

@app.route('/api/login', methods=['POST'])
def login():

    conn = get_db_connection()

    try:

        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        cursor = conn.cursor(dictionary=True)

        # Lấy user theo username rồi kiểm tra mật khẩu phía server (an toàn hơn trong SQL)
        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = %s
        """, (username,))

        user = cursor.fetchone()

        # Nếu không tìm thấy user
        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Sai tài khoản hoặc mật khẩu"
            }), 401

        # Kiểm tra mật khẩu: ưu tiên compare hash nếu có
        stored_hash = user.get('password_hash') if isinstance(user, dict) else None
        if stored_hash:
            try:
                from werkzeug.security import check_password_hash
                if not check_password_hash(stored_hash, password):
                    cursor.close()
                    conn.close()
                    return jsonify({
                        "success": False,
                        "message": "Sai tài khoản hoặc mật khẩu"
                    }), 401
            except Exception:
                if stored_hash != password:
                    cursor.close()
                    conn.close()
                    return jsonify({
                        "success": False,
                        "message": "Sai tài khoản hoặc mật khẩu"
                    }), 401
        else:
            # fallback: compare plaintext password field if exists
            if user.get('password') != password:
                cursor.close()
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "Sai tài khoản hoặc mật khẩu"
                }), 401

        # Trả về thông tin user (loại bỏ trường mật khẩu)
        response_user = {
            "id": user.get('id'),
            "username": user.get('username'),
            "fullname": user.get('fullname'),
            "role": user.get('role')
        }

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "user": response_user
        })

    except Exception as e:

        return jsonify({
            "error":str(e)
        }),500
    
# =======================================================
# API DANH SÁCH USER
# =======================================================

@app.route('/api/users', methods=['GET'])
def get_users():
    # Kiểm tra quyền gọi API tạm thời theo header 'Role'
    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Không có quyền"}), 403

    conn = get_db_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                username,
                fullname,
                role
            FROM users
            ORDER BY id ASC
        """)

        users = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(users)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    # Tạo user mới (chỉ admin)
    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Không có quyền"}), 403

    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    role_new = data.get('role') or 'staff'

    if not username or not password or not fullname:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users
            (username, password_hash, fullname, role)
            VALUES(%s,%s,%s,%s)
        """, (
            username,
            password_hash,
            fullname,
            role_new
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Tạo user thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route(
    '/api/users/reset/<int:user_id>',
    methods=['PUT']
)
def reset_password(user_id):

    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Không có quyền"}), 403

    new_hash = generate_password_hash("123456")

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET password_hash=%s
            WHERE id=%s
        """,(new_hash,user_id))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message":
            "Reset thành công"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# =======================================================
# API XÓA USER
# =======================================================

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    role = request.headers.get('Role')
    if role != 'admin':
        return jsonify({"error": "Không có quyền"}), 403

    conn = get_db_connection()

    try:
        # Kiểm tra xem user có phải admin không
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT role
            FROM users
            WHERE id=%s
        """, (user_id,))

        row = cursor.fetchone()
        if row and row.get('role') == 'admin':
            cursor.close()
            conn.close()
            return jsonify({"error": "Không được xóa Admin"}), 403

        # Thực hiện xóa
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM users
            WHERE id = %s
        """, (user_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Xóa user thành công"
        })

    except Exception as e:
        return jsonify({
            "error":str(e)
        }),500

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