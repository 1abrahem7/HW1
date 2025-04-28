import mysql.connector
from mysql.connector import errorcode
import hashlib

# إعدادات الاتصال بـ MySQL
config = {
    'user': 'root',
    'password': 'Asdf0123***    ',
    'host': '127.0.0.1',
}

# تشفير كلمة المرور
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

try:
    # الاتصال بدون قاعدة بيانات أولاً
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # إنشاء قاعدة البيانات
    cursor.execute("CREATE DATABASE IF NOT EXISTS users_db")
    print("[✔] Database created or already exists.")

    # استخدام القاعدة
    conn.database = 'users_db'

    # إنشاء جدول المستخدمين مع أعمدة إضافية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            id_number VARCHAR(20) NOT NULL,
            credit_card_number VARCHAR(20) NOT NULL,
            valid_date VARCHAR(7) NOT NULL,
            cvc VARCHAR(4) NOT NULL
        )
    ''')
    print("[✔] Users table created or already exists.")

    # حذف كل المستخدمين السابقين (لو كانوا موجودين لإعادة الإنشاء بشكل نظيف)
    cursor.execute('DELETE FROM users')

    # إضافة المستخدمين
    users_data = [
        # username, password, is_admin, first_name, last_name, id_number, credit_card_number, valid_date, cvc
        ('admin', 'admin123', True, 'Israeli', 'Israeli', '123456789', '1234 5567 8901 2345', '12/32', '123'),
        ('user1', 'pass1', False, 'Ahmed', 'Salem', '234567890', '5678 1234 5678 1234', '11/30', '456'),
        ('user2', 'pass2', False, 'Mona', 'Ali', '345678901', '9012 3456 7890 1234', '10/29', '789'),
        ('user3', 'pass3', False, 'Yousef', 'Hassan', '456789012', '3456 7890 1234 5678', '09/28', '101'),
        ('user4', 'pass4', False, 'Sara', 'Fahad', '567890123', '7890 1234 5678 9012', '08/27', '202'),
        ('user5', 'pass5', False, 'Laila', 'Samir', '678901234', '2345 6789 0123 4567', '07/26', '303'),
        ('user6', 'pass6', False, 'Omar', 'Zayed', '789012345', '6789 0123 4567 8901', '06/25', '404'),
        ('user7', 'pass7', False, 'Nour', 'Kamal', '890123456', '0123 4567 8901 2345', '05/24', '505'),
        ('user8', 'pass8', False, 'Huda', 'Nabil', '901234567', '4567 8901 2345 6789', '04/23', '606'),
        ('user9', 'pass9', False, 'Ali', 'Sami', '012345678', '8901 2345 6789 0123', '03/22', '707'),
    ]

    for user in users_data:
        username, password, is_admin, first_name, last_name, id_number, credit_card_number, valid_date, cvc = user
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin, first_name, last_name, id_number, credit_card_number, valid_date, cvc)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (username, password_hash, is_admin, first_name, last_name, id_number, credit_card_number, valid_date, cvc))

    conn.commit()
    print("[✔] 10 users added successfully.")

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("[✖] Access denied: Check your username or password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("[✖] Database does not exist.")
    else:
        print(err)
