from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .forms import loginForm, registrationForm, uploadForm
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def show_landing():
    return render_template('index.html')

@main_routes.route('/login', methods=['GET', 'POST'])

def login():
    login_form = loginForm()
    if request.method == 'POST' and login_form.validate_on_submit():
        # Process login form data here
        email = login_form.email.data
        password = login_form.password.data
        #Login Process
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main_routes.show_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('loginForm.html', login_form=login_form)

@main_routes.route('/registration', methods=['GET', 'POST'])
def registration():
    registration_form = registrationForm()
    if request.method == 'POST' and registration_form.validate_on_submit():
        # Process registration form data here
        name = registration_form.name.data
        email = registration_form.email.data
        date_birth = registration_form.date_birth.data
        password = registration_form.password.data
        #Register user:
        hashed_pw = generate_password_hash(password)
        user = User(
            name=name,
            email=email,
            password=hashed_pw,
            date_birth=date_birth
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('main_routes.login'))
    return render_template('registrationForm.html', registration_form=registration_form)

@main_routes.route('/documentation')
def show_docs():
    return render_template('documentation.html')

@main_routes.route('/dashboard', methods=['GET', 'POST'])
def show_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('main_routes.login'))

    user = User.query.get(session['user_id'])
    upload_form = uploadForm()

    if upload_form.validate_on_submit():
        file = upload_form.datafile.data
        sep = upload_form.separator.data
        # You can parse the CSV file with pandas here
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('main_routes.show_dashboard'))

    return render_template('dashboard.html', user=user, upload_form=upload_form)
