from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/gurmukh/Developer/Athenos/Flask/database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vansh27102005@gmail.com'
app.config['MAIL_PASSWORD'] = 'dtma rcoj byyx rruo'
app.config['MAIL_DEFAULT_SENDER'] = 'vansh27102005@gmail.com'
mail = Mail(app)

# In-memory database (replace with a real database in production)
users = []
otp_store = {}
pending_registrations = {}

# Helper function to generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=4))


# Helper function to generate reset token
def generate_reset_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return self.username

class Subject(db.Model):
    __tablename__ = 'subjects'
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String(80), unique=True, nullable=False)

class Chapter(db.Model):
    __tablename__ = 'chapters'
    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    chapter_name = db.Column(db.String(80), nullable=False)

class Module(db.Model):
    __tablename__ = 'modules'
    module_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    module_name = db.Column(db.String(80), nullable=False)
    video_url = db.Column(db.String(200))

class StudentModuleProgress(db.Model):
    __tablename__ = 'student_module_progress'
    student_username = db.Column(db.String(80), db.ForeignKey('users.username'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), primary_key=True)
    current_difficulty = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)
    mastery = db.Column(db.Boolean, default=False)

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

# Define the TestAttempt model
class TestAttempt(db.Model):
    __tablename__ = 'test_attempts'
    attempt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

@app.route('/')
def index():
    return render_template("startup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user
        user = next((user for user in users if user['email'] == email), None)
        if not user:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

        # Check password
        if not bcrypt.check_password_hash(user['password'], password):
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

        # Authentication successful - create session
        session['user'] = {
            'email': user['email'],
            'user_type': user['user_type']
        }

        # Redirect to dashboard
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')

        # Validate form data
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Check if user already exists
        if any(user['email'] == email for user in users):
            flash('User already exists', 'error')
            return redirect(url_for('register'))

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store pending registration
        pending_registrations[email] = {
            'email': email,
            'password': hashed_password,
            'user_type': user_type
        }

        # Generate OTP
        otp = generate_otp()

        # Store OTP with expiry (5 minutes)
        otp_store[email] = {
            'otp': otp,
            'expiry': datetime.now() + timedelta(minutes=5)
        }

        # Send OTP via email
        try:
            msg = Message('Your Registration Verification Code',
                          recipients=[email])
            msg.html = f'''
                <h1>Registration Verification Code</h1>
                <p>Your 4-digit verification code is: <strong>{otp}</strong></p>
                <p>This code will expire in 5 minutes.</p>
            '''
            mail.send(msg)

            # Save email in session for next step
            session['pending_registration'] = {'email': email}

            # Redirect to verification page
            return redirect(url_for('verify_otp'))
        except Exception as e:
            print(e)
            flash('Failed to send verification email', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_registration' not in session:
        flash('No pending registration', 'error')
        return redirect(url_for('register'))

    email = session['pending_registration']['email']

    if request.method == 'POST':
        otp = request.form.get('otp')

        stored_otp = otp_store.get(email)

        # Check if OTP exists and is valid
        if not stored_otp or stored_otp['otp'] != otp:
            flash('Invalid verification code', 'error')
            return redirect(url_for('verify_otp'))

        # Check if OTP has expired
        if stored_otp['expiry'] < datetime.now():
            del otp_store[email]
            flash('Verification code has expired', 'error')
            return redirect(url_for('register'))

        # Registration successful - add user from pending registrations
        new_user = pending_registrations[email]
        users.append(new_user)

        # Clean up
        del pending_registrations[email]
        del otp_store[email]
        session.pop('pending_registration', None)

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('verify_otp.html', email=email)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        # Check if user exists
        user = next((user for user in users if user['email'] == email), None)
        if not user:
            # Don't reveal if user exists for security reasons
            flash('If your email is registered, you will receive a password reset link', 'success')
            return redirect(url_for('login'))

        # Generate reset token
        reset_token = generate_reset_token()
        reset_expiry = datetime.now() + timedelta(hours=1)

        # In a real app, store this token in the database
        # Here we're just demonstrating the flow

        # Send password reset email
        try:
            reset_link = url_for('reset_password', token=reset_token, email=email, _external=True)
            msg = Message('Password Reset Link',
                          recipients=[email])
            msg.html = f'''
                <h1>Password Reset Request</h1>
                <p>Click the link below to reset your password:</p>
                <p><a href="{"http://127.0.0.1:5000/register"}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
            '''
            mail.send(msg)

            flash('Password reset link sent to your email', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Failed to send reset email', 'error')
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    token = request.args.get('token')

    if not email or not token:
        flash('Invalid password reset link', 'error')
        return redirect(url_for('login'))

    # In a real app, validate the token from database
    # For demo purposes, we'll just show the reset form

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('reset_password', token=token, email=email))

        # Find the user
        user = next((user for user in users if user['email'] == email), None)
        if user:
            # Update password
            user['password'] = bcrypt.generate_password_hash(password).decode('utf-8')
            flash('Password has been reset successfully', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found', 'error')
            return redirect(url_for('login'))

    return render_template('reset_password.html', email=email, token=token)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'student':
        # Check if the student has any module progress
        has_progress = StudentModuleProgress.query.filter_by(student_username=current_user.username).first()
        if not has_progress:
            return redirect(url_for('enroll_courses'))

        subjects = Subject.query.all()
        progress = {}
        for subject_obj in subjects:  # Iterate through Subject objects
            chapters = Chapter.query.filter_by(subject_id=subject_obj.subject_id).all()
            total_modules = sum(len(Module.query.filter_by(chapter_id=chapter.chapter_id).all()) for chapter in chapters)
            completed_modules = sum(1 for chapter in chapters for module in Module.query.filter_by(chapter_id=chapter.chapter_id).all()
                                    for progress_entry in StudentModuleProgress.query.filter_by(student_username=current_user.username, module_id=module.module_id, completed=True).all())
            progress[subject_obj.subject_name] = (completed_modules, total_modules) if total_modules > 0 else (0, 1)

        return render_template('student_dashboard.html', progress=progress, subjects=subjects) # Pass the subjects list
    else:  # teacher
        students = User.query.filter_by(user_type='student').all()
        student_data = []
        for student in students:
            completed_modules = StudentModuleProgress.query.filter_by(student_username=student.username, completed=True).count()
            modules = StudentModuleProgress.query.filter_by(student_username=student.username).all()
            avg_difficulty = sum(p.current_difficulty for p in modules) / len(modules) if modules else 0
            test_attempts = db.session.query(db.func.avg(TestAttempt.score)).filter_by(student_username=student.username).scalar() or 0
            student_data.append({
                'username': student.username,
                'completed_modules': completed_modules,
                'avg_difficulty': round(avg_difficulty, 2),
                'avg_score': round(test_attempts, 2)
            })
        return render_template('teacher_dashboard.html', student_data=student_data)

@app.route('/enroll/courses', methods=['GET', 'POST'])
@login_required
def enroll_courses():
    if current_user.user_type != 'student':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    subjects = Subject.query.all()
    if request.method == 'POST':
        selected_subject_ids = request.form.getlist('subjects')
        enrolled_count = 0
        for subject_id_str in selected_subject_ids:  # Iterate through the list of selected subject IDs
            try:
                subject_id = int(subject_id_str)
                subject = Subject.query.get(subject_id)
                if subject:
                    chapters = Chapter.query.filter_by(subject_id=subject.subject_id).all()
                    for chapter in chapters:
                        modules = Module.query.filter_by(chapter_id=chapter.chapter_id).all()
                        for module in modules:
                            # Check if the student is already enrolled in this module
                            enrollment = StudentModuleProgress.query.filter_by(
                                student_username=current_user.username,
                                module_id=module.module_id
                            ).first()
                            if not enrollment:
                                new_enrollment = StudentModuleProgress(
                                    student_username=current_user.username,
                                    module_id=module.module_id
                                )
                                db.session.add(new_enrollment)
                                enrolled_count += 1
            except ValueError:
                flash(f'Invalid subject ID: {subject_id_str}')
                db.session.rollback()
                return redirect(url_for('enroll_courses'))
        db.session.commit()
        if enrolled_count > 0:
            flash(f'Successfully enrolled in {enrolled_count} modules.')
        return redirect(url_for('dashboard'))
    return render_template('enroll_courses.html', subjects=subjects)

@app.route('/teacher/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.user_type != 'teacher':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    subjects = Subject.query.all()

    if request.method == 'POST':
        subject_option = request.form.get('subject_option')
        subject = None

        if subject_option == 'new':
            new_subject_name = request.form.get('new_subject_name')
            if new_subject_name:
                if Subject.query.filter_by(subject_name=new_subject_name).first():
                    flash('Subject already exists.')
                    return render_template('create_course.html', subjects=subjects)
                subject = Subject(subject_name=new_subject_name)
                db.session.add(subject)
                db.session.commit()
                flash(f'Subject "{new_subject_name}" created successfully.')
            else:
                flash('Please enter a name for the new subject.')
                return render_template('create_course.html', subjects=subjects)
        else:
            subject_id = int(subject_option)
            subject = Subject.query.get(subject_id)
            if not subject:
                flash('Invalid subject selected.')
                return render_template('create_course.html', subjects=subjects)

        if subject:
            chapter_names = request.form.getlist('chapter_name[]')
            module_names_list = request.form.getlist('module_name[][]')
            video_urls_list = request.form.getlist('video_url[][]')

            for i, chapter_name in enumerate(chapter_names):
                if chapter_name:
                    chapter = Chapter(subject_id=subject.subject_id, chapter_name=chapter_name)
                    db.session.add(chapter)
                    db.session.commit()  # Commit chapter to get its ID

                    if i < len(module_names_list):
                        module_names = module_names_list[i]
                        video_urls = []
                        if i < len(video_urls_list):
                            video_urls = video_urls_list[i]

                        for j, module_name in enumerate(module_names):
                            if module_name:
                                video_url = video_urls[j] if j < len(video_urls) else None
                                module = Module(chapter_id=chapter.chapter_id, module_name=module_name, video_url=video_url)
                                db.session.add(module)
            db.session.commit()
            flash('Course structure saved successfully.')
            return redirect(url_for('dashboard'))

    return render_template('create_course.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
@login_required
def subject_portal(subject_id):
    if current_user.user_type != 'student':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    modules_data = []
    for chapter in chapters:
        modules = Module.query.filter_by(chapter_id=chapter.chapter_id).all()
        for module in modules:
            progress = StudentModuleProgress.query.filter_by(student_username=current_user.username, module_id=module.module_id).first()
            if not progress:
                progress = StudentModuleProgress(student_username=current_user.username, module_id=module.module_id, current_difficulty=1)
                db.session.add(progress)
                db.session.commit()
            modules_data.append({
                'module_id': module.module_id,  # Add the module_id here
                'module_name': module.module_name,
                'video_url': module.video_url,
                'difficulty': progress.current_difficulty,
                'completed': progress.completed,
                'mastery': progress.mastery
            })
    return render_template('subject_portal.html', modules=modules_data)

@app.route('/take_test/<int:module_id>', methods=['GET', 'POST'])
@login_required
def take_test(module_id):
    if current_user.user_type != 'student':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    module = Module.query.get(module_id)
    progress = StudentModuleProgress.query.filter_by(student_username=current_user.username, module_id=module_id).first()
    if request.method == 'POST':
        score = sum(1 for q in Question.query.filter_by(module_id=module_id, difficulty_level=progress.current_difficulty).all()
                    if request.form.get(f'q{q.question_id}') == q.answer) / 10  # Assuming 10 questions
        test_attempt = TestAttempt(student_username=current_user.username, module_id=module_id, score=score)
        db.session.add(test_attempt)
        if score >= 0.8:
            progress.current_difficulty = min(progress.current_difficulty + 1, 5)
            if progress.current_difficulty == 4 and score >= 0.8:
                progress.completed = True
            if progress.current_difficulty == 5 and score >= 0.8:
                progress.mastery = True
        elif score <= 0.5:
            progress.current_difficulty = max(progress.current_difficulty - 1, 1)
        db.session.commit()
        flash(f'Test score: {score*100}%')
        return redirect(url_for('subject_portal', subject_id=Chapter.query.get(module.chapter_id).subject_id))
    questions = Question.query.filter_by(module_id=module_id, difficulty_level=progress.current_difficulty).limit(10).all()
    return render_template('take_test.html', questions=questions, module_id=module_id)

@app.route('/logout')
@login_required  # Ensure only logged-in users can access this
def logout():
    logout_user()  # If you're using Flask-Login
    return redirect(url_for('login'))

# Context processor to make URL generation helper available to all templates
@app.context_processor
def utility_processor():
    def url_for_static(route):
        return url_for('static', filename=route)

    return {
        'url_for_static': url_for_static
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Sample data
        if not Subject.query.first():
            subjects = ['Mathematics', 'Science']
            for s in subjects:
                subject = Subject(subject_name=s)
                db.session.add(subject)
            db.session.commit()
            math = Subject.query.filter_by(subject_name='Mathematics').first()
            chapter = Chapter(subject_id=math.subject_id, chapter_name='Algebra')
            db.session.add(chapter)
            db.session.commit()
            module = Module(chapter_id=chapter.chapter_id, module_name='Linear Equations', video_url='https://example.com/video1')
            db.session.add(module)
            db.session.commit()
            question = Question(module_id=module.module_id, difficulty_level=1, question_text='What is 2+2?', answer='4')
            db.session.add(question)
            db.session.commit()
    app.run(debug=True)
