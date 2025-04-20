import mysql.connector
from mysql.connector import errorcode
import hashlib

config = {
    'user': 'root',
    'password': 'Asdf0123***',
    'host': '127.0.0.1',
}

# تشفير كلمة المرور
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

try:
    # الاتصال بدون قاعدة بيانات أولًا لإنشاء قاعدة جديدة
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # إنشاء قاعدة بيانات إذا لم تكن موجودة
    cursor.execute("CREATE DATABASE IF NOT EXISTS users_db")
    print("[✔] Database created or already exists.")

    # التبديل لقاعدة البيانات
    conn.database = 'users_db'

    # إنشاء جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN NOT NULL
        )
    ''')
    print("[✔] Users table created or already exists.")

    # إدخال الأدمن
    admin_username = 'admin'
    admin_password = 'admin123'
    admin_hash = hash_password(admin_password)

    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (%s, %s, %s)
        ''', (admin_username, admin_hash, True))
        conn.commit()
        print("[✔] Admin user added successfully.")
    except mysql.connector.errors.IntegrityError:
        print("[i] Admin user already exists.")

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("[✖] Access denied: Check your username or password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("[✖] Database does not exist.")
    else:
        print(err)
