from werkzeug.security import generate_password_hash
from database import get_db_connection

conn = get_db_connection()
if conn is None:
    print('Không thể kết nối DB')
    exit(1)

cursor = conn.cursor(dictionary=True)

cursor.execute(
    "SELECT id,password_hash FROM users"
)

users = cursor.fetchall()

for user in users:
    try:
        current = user['password_hash']
        # Thực hiện hash (chú ý: chỉ chạy khi bạn chắc chắn)
        hashed = generate_password_hash(current)
        cursor2 = conn.cursor()
        cursor2.execute("""
            UPDATE users
            SET password_hash=%s
            WHERE id=%s
        """, (hashed, user['id']))
        cursor2.close()
    except Exception as e:
        print(f"Bỏ qua user {user['id']} do lỗi: {e}")

conn.commit()
cursor.close()
conn.close()

print('DONE')
