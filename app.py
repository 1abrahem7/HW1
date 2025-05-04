from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import hashlib
import re

app = Flask(__name__)
from flask import session
app.secret_key = 'your_secret_key'


db_config = {
    'user': 'root',
    'password': 'Asdf0123***',
    'host': '127.0.0.1',
    'database': 'users_db'
}

# وظيفة لتشفير كلمات المرور
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password_hash))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['username'] = username
                if user[3]:  # إذا هو أدمن
                    session['role'] = 'admin'
                    return redirect(url_for('admin'))  # يذهب إلى صفحة الأدمن
                else:
                    session['role'] = 'user'
                    return redirect(url_for('welcome'))  # المستخدم العادي يذهب إلى صفحة الترحيب
            else:
                message = "Invalid username or password."

        except mysql.connector.Error as err:
            message = f"Database error: {err}"

    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'], role=session.get('role'))
    else:
        return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))  # فقط الأدمن يستطيع الدخول

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, first_name, last_name, id_number, credit_card_number, valid_date, cvc, is_admin FROM users")
        users = cursor.fetchall()
        conn.close()

        return render_template('admin.html', users=users)

    except mysql.connector.Error as err:
        return f"Database error: {err}"


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        id_number = request.form['id_number']
        credit_card_number = request.form['credit_card_number']
        valid_date = request.form['valid_date']
        cvc = request.form['cvc']

        # التحقق بالـ Regex
        if not re.match(r'^[A-Za-z]+$', first_name):
            message = "First name must contain letters only."
        elif not re.match(r'^[A-Za-z]+$', last_name):
            message = "Last name must contain letters only."
        elif not re.match(r'^\d{9}$', id_number):
            message = "ID must be exactly 9 digits."
        elif not re.match(r'^(\d{4} \d{4} \d{4} \d{4}|\d{16})$', credit_card_number):
            message = "Credit Card must be 16 digits, grouped or ungrouped."
        elif not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', valid_date):
            message = "Valid date must be in MM/YY format."
        elif not re.match(r'^\d{3}$', cvc):
            message = "CVC must be exactly 3 digits."
        else:
            password_hash = hash_password(password)

            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, is_admin, first_name, last_name, id_number, credit_card_number, valid_date, cvc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (username, password_hash, False, first_name, last_name, id_number, credit_card_number, valid_date, cvc))
                conn.commit()
                conn.close()
                message = f"User {username} registered successfully!"
                return redirect(url_for('login'))  # إعادة التوجيه إلى صفحة الدخول بعد تسجيل ناجح
            except mysql.connector.errors.IntegrityError:
                message = "Username already exists. Please choose another one."
            except mysql.connector.Error as err:
                message = f"Database error: {err}"

    return render_template('register.html', message=message)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(debug=True)
