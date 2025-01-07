from flask import Flask, request, jsonify, url_for, redirect, render_template, session,flash
import os
import mysql.connector as mc 

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = mc.connect(host="localhost", port=3306, user="admint", password="12341234", database="resumes")
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username and password are required!', 'error')
        return redirect(url_for('login_form'))
    
    query = "SELECT * FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    
    if not user or user['password'] != password:
        flash('Invalid username or password!', 'error')
        return redirect(url_for('login_form'))
    
    session['username'] = username
    flash('Login successful!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        flash('You have been logged out.', 'success')
    else:
        flash('You are not logged in.', 'info')
    return redirect(url_for('index'))

@app.route('/getsession')
def getsession():
    if 'username' in session:
        return session['username']
    return 'Not logged in!'

if __name__ == '__main__':
    app.run(debug=True)

