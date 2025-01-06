from flask import Flask, request, jsonify, url_for, redirect, render_template, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/getsession')
def getsession():
    if 'username' in session:
        return session['username']
    return 'Not logged in!'

if __name__ == '__main__':
    app.run(debug=True)

