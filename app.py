from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import hashlib

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
                if user[3]:  # is_admin
                    session['role'] = 'admin'
                else:
                    session['role'] = 'user'
                return redirect(url_for('welcome'))

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
                           (username, password_hash, False))
            conn.commit()
            conn.close()
            message = f"User {username} registered successfully!"

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
