from flask import Flask, render_template, request, Response, session, redirect, url_for, flash
from functools import wraps
import base64
import secrets
from models import Database

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
db = Database()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not all([username, password, email]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        success, message = db.register_user(username, password, email)
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, result = db.login_user(username, password)
        if success:
            session['user_id'] = result
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash(result, 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    user = db.get_user_by_id(session['user_id'])
    return render_template('home.html', 
                         progress=get_progress_data(),
                         user=user)

# Update all other routes to include @login_required
@app.route("/challenge1", methods=['GET', 'POST'])
@login_required
def challenge1():
    if request.method == 'POST':
        if request.form.get('code') == 'PYTHON_EXPLORER_2024':
            progress = db.get_user_progress(session['user_id'])
            progress['challenge1'] = True
            db.save_user_progress(session['user_id'], progress)
            session['progress'] = progress
            return render_template('success.html', 
                                progress=get_progress_data(),
                                challenge_num=1,
                                next_challenge='/challenge2')
        return render_template('error.html', 
                            progress=get_progress_data(),
                            challenge_num=1)

    return render_template('challenge1.html', progress=get_progress_data())

@app.route("/challenge2", methods=['GET', 'POST'])
@login_required
def challenge2():
    if request.method == 'POST':
        if request.form.get('code') == 'HEADER_HUNTER_42':
            progress = db.get_user_progress(session['user_id'])
            progress['challenge2'] = True
            db.save_user_progress(session['user_id'], progress)
            session['progress'] = progress
            return render_template('success.html', 
                                progress=get_progress_data(),
                                challenge_num=2,
                                next_challenge='/challenge3')
        return render_template('error.html', 
                            progress=get_progress_data(),
                            challenge_num=2)

    response = Response(render_template('challenge2.html', progress=get_progress_data()))
    response.headers['X-Secret-Code'] = 'HEADER_HUNTER_42'
    return response

@app.route("/challenge3", methods=['GET', 'POST'])
@login_required
def challenge3():
    if request.method == 'POST':
        if request.form.get('code') == 'MASTER_SCRAPER_99':
            progress = db.get_user_progress(session['user_id'])
            progress['challenge3'] = True
            db.save_user_progress(session['user_id'], progress)
            session['progress'] = progress
            return render_template('success.html', 
                                progress=get_progress_data(),
                                challenge_num=3,
                                next_challenge='/victory')
        return render_template('error.html', 
                            progress=get_progress_data(),
                            challenge_num=3)

    secret_message = base64.b64encode("MASTER_SCRAPER_99".encode()).decode()
    return render_template('challenge3.html', 
                         progress=get_progress_data(),
                         secret_message=secret_message)

@app.route("/victory")
@login_required
def victory():
    progress_data = get_progress_data()
    if progress_data['completed'] < progress_data['total']:
        return render_template('error.html', 
                            progress=progress_data,
                            message="🚫 Complete all challenges first!",
                            challenge_num=progress_data['completed'] + 1)
    
    return render_template('victory.html', progress=progress_data)

def get_progress_data():
    if 'user_id' not in session:
        return {
            'completed': 0,
            'total': 3,
            'percent': 0,
            'challenges': [
                {'number': i, 'complete': False, 'icon': '⏳'} 
                for i in range(1, 4)
            ]
        }
    
    progress = db.get_user_progress(session['user_id'])
    completed = sum(1 for value in progress.values() if value)
    total = len(progress)
    progress_percent = (completed / total) * 100 if total > 0 else 0
    
    challenges_status = []
    for i in range(1, total + 1):
        challenge_key = f'challenge{i}'
        challenges_status.append({
            'number': i,
            'complete': progress.get(challenge_key, False),
            'icon': '✅' if progress.get(challenge_key, False) else '⏳'
        })
    
    return {
        'completed': completed,
        'total': total,
        'percent': progress_percent,
        'challenges': challenges_status
    }

if __name__ == "__main__":
    app.run(debug=True) 