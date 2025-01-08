from flask import Flask, request, url_for, redirect, render_template, session, flash
import os
import mysql.connector as mc 

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = mc.connect(host="localhost", port=3306, user="admint", password="12341234", database="devopFin")
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
        return redirect(url_for('login'))
    
    query = "SELECT * FROM User WHERE ID = '%s'" % username
    cursor.execute(query)
    user = cursor.fetchone()
    
    if not user or user[1] != password:
        flash('Invalid username or password!', 'error')
        return redirect(url_for('login'))
    
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
        return redirect(url_for('register'))
    
    query = "SELECT * FROM User WHERE ID = '%s'" % (username,)
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user != None:
        flash('Username already exists!', 'error')
        return redirect(url_for('register'))
    
    query = "INSERT INTO User (ID, pwd) VALUES ('%s', '%s')" % (username, password)
    cursor.execute(query)
    db.commit()
    
    session['username'] = username
    flash('Registration successful!', 'success')
    return redirect(url_for('index'))

@app.route('/vacancies')
def vacancies():
    if 'username' not in session:
        flash('Please login to view vacancies!', 'info')
        return redirect(url_for('login'))
    
    cursor.execute("SELECT * FROM JobOpenings")
    vacancies = cursor.fetchall()
    for i in range(len(vacancies)):
        query = "SELECT name FROM CompanyInformation WHERE company_id = '%s'" % (vacancies[i][1])
        cursor.execute(query)
        company_name = cursor.fetchone()
        vacancies[i] += company_name
    return render_template('vacancies.html', username=session['username'], vacancies=vacancies)

@app.route('/vacancies', methods=['POST'])
def search_vacancies():
    if 'username' not in session:
        flash('Please login to view vacancies!', 'info')
        return redirect(url_for('login'))
    
    keyword = request.form['search_vacancies']
    query = "SELECT * FROM JobOpenings WHERE job_title LIKE '%%%s%%'" % (keyword)
    cursor.execute(query)
    vacancies = cursor.fetchall()
    for i in range(len(vacancies)):
        query = "SELECT name FROM CompanyInformation WHERE company_id = '%s'" % (vacancies[i][1])
        cursor.execute(query)
        company_name = cursor.fetchone()
        vacancies[i] += company_name
    return render_template('vacancies.html', username=session['username'], keyword=keyword, vacancies=vacancies)

@app.route('/companies')
def companies():
    if 'username' in session:
        return render_template('companies.html', username=session['username'])
    return render_template('companies.html')

@app.route('/about_company/<int:company_id>')
def about_company(company_id):
    print("company_id: ", company_id)
    cursor.execute("SELECT * FROM CompanyInformation WHERE company_id = '%s'" % (company_id))
    company = cursor.fetchone()
    print("company: ", company)

    cursor.execute("SELECT * FROM CompanyIntroduction WHERE company_id = '%s'" % (company_id))
    introduction = cursor.fetchone()
    print("introduction: ", introduction)
    
    cursor.execute("SELECT * FROM BusinessPhilosophy WHERE company_id = '%s'" % (company_id))
    philosophy = cursor.fetchone()
    print("philosophy: ", philosophy)

    cursor.execute("SELECT * FROM CompanyBenefits WHERE company_id = '%s'" % (company_id))
    benefits = cursor.fetchall()
    print("benefits: ", benefits)
    
    cursor.execute("SELECT * FROM JobOpenings WHERE company_id = '%s'" % (company_id))
    jobs = cursor.fetchall()
    if 'username' not in session:
        jobs = [(0, 0, '', '登入後即可查看職缺', '', '', '', '', '')]
    print("jobs: ", jobs)
    
    cursor.execute("SELECT * FROM ContactInfo WHERE company_id = '%s'" % (company_id))
    contact = cursor.fetchone()
    print("contact: ", contact)

    if 'username' not in session:
        return render_template('about_company.html',
                               company=company, 
                               introduction=introduction, 
                               philosophy=philosophy, 
                               benefits=benefits,
                               jobs=jobs,  
                               contact=contact)
    return render_template('about_company.html',
                           company=company, 
                           introduction=introduction, 
                           philosophy=philosophy, 
                           benefits=benefits, 
                           jobs=jobs, 
                           contact=contact, username=session['username'])

@app.route('/cv')
def cv():
    # 連接資料庫並查詢履歷資料
    cursor = db.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC LIMIT 1")  # 假設只顯示最新的履歷
    resume = cursor.fetchone()
    
    if 'username' not in session:
        flash('Please login to view your CV!', 'info')
        return redirect(url_for('login'))
    # 如果找到了履歷資料，傳遞資料給前端
    if resume:
        return render_template('cv.html', resume=resume, username=session['username'])
    else:
        return render_template('cv.html', resume=None, username=session['username'])

@app.route('/uploadCV')
def uploadCV():
    if 'username' not in session:
        flash('Please login to upload your CV!', 'info')
        return redirect(url_for('login'))
    return render_template('uploadCV.html', username=session['username'])

@app.route('/submit_cv', methods=['POST'])
def submit_cv():
    username = session['username']
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
    query = '''INSERT INTO resumes (id, first_name, last_name, contact_info, transport, school_name, education_level, department, study_status, work_experience) 
    VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % (username, first_name, last_name, contact_info, transport, school_name, education_level, department, study_status, work_experience)
    cursor.execute(query)
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
            return render_template('editCV.html', resume=resume, username=session['username'])
        else:
            flash('目前沒有履歷可以修改！', 'error')
            return redirect(url_for('cv'))

    if request.method == 'POST':
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
        resume_id = request.form.get('resume_id')

        # 確保 resume_id 存在
        if not resume_id:
            flash('履歷 ID 丟失！', 'error')
            return redirect(url_for('edit_cv'))

        # 檢查是否有空值
        if not all([first_name, last_name, contact_info, school_name, education_level, department, study_status, work_experience]):
            flash('所有欄位皆為必填！', 'error')
            return render_template('editCV.html', first_name=first_name, last_name=last_name, contact_info=contact_info, 
                                   transport=transport, school_name=school_name, education_level=education_level, 
                                   department=department, study_status=study_status, work_experience=work_experience, 
                                   resume_id=resume_id)

        # 更新資料庫
        query = """
        UPDATE resumes
        SET first_name = '%s', last_name = '%s', contact_info = '%s', transport = '%s',
            school_name = '%s', education_level = '%s', department = '%s',
            study_status = '%s', work_experience = '%s'
        WHERE id = '%s'
        """  % (first_name, last_name, contact_info, transport,
                               school_name, education_level, department,
                               study_status, work_experience, resume_id)
        cursor.execute(query)
        db.commit()

        flash('履歷修改成功！', 'success')
        return redirect(url_for('cv'))


if __name__ == '__main__':
    app.run(debug=True)
