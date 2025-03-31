from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .forms import loginForm, registrationForm, uploadForm
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from .utils.preprocessing import parse_csv, count_nulls, count_duplicates
import os
import uuid


UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')

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
        #Preprocess csv file


        try:
            # Save the uploaded file with a unique filename
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)

            file_id = str(uuid.uuid4()) + ".csv"
            file_path = os.path.join(UPLOAD_DIR, file_id)
            file.save(file_path)

            session['csv_file_path'] = file_path
            session['csv_sep'] = sep

            flash('File uploaded successfully. Proceeding to preview.', 'success')
            return redirect(url_for('main_routes.preview_data'))

        except Exception as e:
            flash(str(e), 'danger')
    return render_template('dashboard.html', user=user, upload_form=upload_form)

@main_routes.route('/preview')
def preview_data():
    file_path = session.get('csv_file_path')
    sep = session.get('csv_sep', ',')

    if not file_path or not os.path.exists(file_path):
        flash('No file uploaded or file expired.', 'warning')
        return redirect(url_for('main_routes.show_dashboard'))

    try:
        df = parse_csv(open(file_path, 'rb'), sep)
        preview = df.head().to_html(classes='table table-bordered table-striped', index=False)
        null_counts = count_nulls(df)
        null_counts_frame = null_counts.to_frame(name="Missing Values")
        #percent_missing = percent_nulls(df, null_counts)
        null_counts_html = null_counts_frame.to_html(classes='table table-sm table-warning', index=True)
        duplicate_counts = count_duplicates(df)
        duplicate_counts_html = duplicate_counts.to_frame().to_html(classes='table table-sm table-secondary')
        flash('File uploaded and parsed successfully.', 'success')
        return render_template('preview.html', preview=preview, null_counts=null_counts_html, duplicate_counts=duplicate_counts_html)

    except Exception as e:
        flash(f"Error reading uploaded file: {e}", 'danger')
        return redirect(url_for('main_routes.show_dashboard'))

@main_routes.route('/data-cleanup')
def data_cleanup():
    if 'csv_file_path' not in session:
        flash('Please upload a dataset first.', 'warning')
        return redirect(url_for('main_routes.show_dashboard'))

    return render_template('dataCleanup.html')
