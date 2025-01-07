from flask import Flask, request, url_for, redirect, render_template, session, flash
import os
import mysql.connector as mc 

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = mc.connect(host="localhost", port=3306, user="admint", password="12341234", database="resumes")
cursor = db.cursor()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

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

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Username and password are required!', 'error')
        return redirect(url_for('register_form'))
    
    query = "SELECT * FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    
    if user:
        flash('Username already exists!', 'error')
        return redirect(url_for('register_form'))
    
    query = "INSERT INTO User (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))
    db.commit()
    
    session['username'] = username
    flash('Registration successful!', 'success')
    return redirect(url_for('index'))

@app.route('/vacancies')
def vacancies():
    return render_template('vacancies.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/about_company/<int:company_id>')
def about_company(company_id):
    cursor.execute("SELECT * FROM CompanyInfo WHERE company_id = %s", (company_id,))
    company = cursor.fetchone()

    cursor.execute("SELECT * FROM CompanyIntroduction WHERE company_id = %s", (company_id,))
    introduction = cursor.fetchone()
    
    cursor.execute("SELECT * FROM BusinessPhilosophy WHERE company_id = %s", (company_id,))
    philosophy = cursor.fetchone()

    cursor.execute("SELECT * FROM CompanyBenefits WHERE company_id = %s", (company_id,))
    benefits = cursor.fetchall()
    
    cursor.execute("SELECT * FROM JobOpenings WHERE company_id = %s", (company_id,))
    jobs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM ContactInfo WHERE company_id = %s", (company_id,))
    contact = cursor.fetchone()

    return render_template('about_company.html',
                           company=company, 
                           introduction=introduction, 
                           philosophy=philosophy, 
                           benefits=benefits, 
                           jobs=jobs, 
                           contact=contact)

@app.route('/cv')
def cv():
    # 連接資料庫並查詢履歷資料
    cursor = db.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC LIMIT 1")  # 假設只顯示最新的履歷
    resume = cursor.fetchone()
    
    # 如果找到了履歷資料，傳遞資料給前端
    if resume:
        return render_template('cv.html', resume=resume)
    else:
        return render_template('cv.html', resume=None)

@app.route('/uploadCV')
def uploadCV():
    return render_template('uploadCV.html')

@app.route('/submit_cv', methods=['POST'])
def submit_cv():
    # 取得表單資料
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    contact_info = request.form['contact_info']
    transport = ', '.join(request.form.getlist('transport'))  # 取得所有選中的交通工具
    school_name = request.form['school_name']
    education_level = request.form['education_level']
    department = request.form['department']
    study_status = request.form['study_status']
    work_experience = request.form['work_experience']

    # 檢查是否有空值
    if not first_name or not last_name or not contact_info or not school_name or not education_level or not department or not study_status or not work_experience:
        flash('所有欄位皆為必填！', 'error')
        return redirect(url_for('cv'))

    # 插入資料到資料庫
    query = """
    INSERT INTO resumes (first_name, last_name, contact_info, transport, school_name, education_level, department, study_status, work_experience)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (first_name, last_name, contact_info, transport, school_name, education_level, department, study_status, work_experience))
    db.commit()

    flash('履歷提交成功！', 'success')
    return redirect(url_for('cv'))

@app.route('/editCV', methods=['GET', 'POST'])
def edit_cv():
    if request.method == 'GET':
        # 查詢最新履歷資料
        cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC LIMIT 1")
        resume = cursor.fetchone()
        
        if resume:
            return render_template('editCV.html', resume=resume)
        else:
            flash('目前沒有履歷可以修改！', 'error')
            return redirect(url_for('cv'))
    
    if request.method == 'POST':
        print(request.form)
        # 接收用戶提交的修改後的履歷資料
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_info = request.form['contact_info']
        transport = ', '.join(request.form.getlist('transport'))
        school_name = request.form['school_name']
        education_level = request.form['education_level']
        department = request.form['department']
        study_status = request.form['study_status']
        work_experience = request.form['work_experience']
        resume_id = request.form['resume_id']

        # 檢查是否有空值
        if not all([first_name, last_name, contact_info, school_name, education_level, department, study_status, work_experience]):
            flash('所有欄位皆為必填！', 'error')
            return redirect(url_for('edit_cv'))

        # 更新資料庫
        query = """
        UPDATE resumes
        SET first_name = %s, last_name = %s, contact_info = %s, transport = %s,
            school_name = %s, education_level = %s, department = %s,
            study_status = %s, work_experience = %s
        WHERE id = %s
        """
        cursor.execute(query, (first_name, last_name, contact_info, transport,
                               school_name, education_level, department,
                               study_status, work_experience, resume_id))
        db.commit()

        flash('履歷修改成功！', 'success')
        return redirect(url_for('cv'))

@app.route('/uploadCV')
def uploadCV():
    return render_template('uploadCV.html')


if __name__ == '__main__':
    app.run(debug=True)

'''
TODO: 
1. Create a simple login page with username and password [kung done]
2. Create a session for the user [tim ]
3. Create a logout function [tim] (if user is in session -> logout; button in navbar)
4. Create a registration page [tim partial]
5. Create a database to store the user information [kung in progress]
6. Create a function to check if the user is in the database [tim ]
7. Create a function to check if the username is correct [tim ]
8. Create a function to check if the password is correct [tim ]
9. Create a function to search for vacancies or companies in navbar [tim ]
10. Create CV template [chiao done]
11. Create a function to render the CV template [chiao in progress]

.
|
|-  index.html [tim done]
|-  register.html [tim partial]
|-  companies.html [tim partial]
|   |-  about_company.html (by clicking on the company button in companies.html,
|   |   it will redirect to this page. 
|   |   fetch the data from the database then render it, show link to company website, (user should be logged in) show vacancies available & details)
|   |   [tim ]
|-  vacancies.html [tim ]
|-  cv.html [chiao in progress] (provide a cv template for the user to fill in)
|-  login.html [kung done]


'''

