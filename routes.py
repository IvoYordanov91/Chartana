from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .forms import loginForm, registrationForm, uploadForm
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from .utils.preprocessing import parse_csv, count_nulls, count_duplicates
import os
import uuid
import pandas as pd
import numpy as np


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
    try:
        df = pd.read_csv('cleaned_marketing_campaigns.csv')
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        df['duration_days'] = (df['end_date'] - df['start_date']).dt.days
        df = df[df['duration_days'] >= 0]

        # Dataset date range
        min_date = df['start_date'].min().strftime('%Y-%m-%d')
        max_date = df['end_date'].max().strftime('%Y-%m-%d')

        # KPI Summary
        loss_count = df[df['net_profit'] < 0].shape[0]
        top_channel = df['channel'].value_counts().idxmax()
        best_type = df.groupby('type')['roi'].mean().idxmax()

        #Channel distribution:
        channel_distribution = (
        df['channel'].value_counts().rename_axis('channel').reset_index(name='count').to_dict(orient='records'))

        # Summary per channel with true ROI
        channel_totals = df.groupby('channel')[['budget', 'revenue']].sum()
        channel_totals['roi'] = (channel_totals['revenue'] / channel_totals['budget']).round(2)
        channel_totals['net_profit'] = (channel_totals['revenue'] - channel_totals['budget']).round(2)
        channel_summary = channel_totals.round(2).reset_index().to_dict(orient='records')

        #Top channel performers:
        top_profit_channel = channel_totals['net_profit'].idxmax()
        top_profit_value = round(channel_totals.loc[top_profit_channel, 'net_profit'], 2)

        top_roi_channel = channel_totals['roi'].idxmax()
        top_roi_value = round(channel_totals.loc[top_roi_channel, 'roi'], 2)

        #Quarterly analysis:
        # Create 'quarter' column like '2022-Q3'
        df['quarter'] = df['start_date'].dt.to_period('Q').astype(str)

        # Group by quarter and channel
        quarterly_summary = df.groupby(['quarter', 'channel']).agg({
        'budget': 'sum',
        'revenue': 'sum',
        'net_profit': 'sum'
        }).reset_index()

        # Compute true ROI
        quarterly_summary['roi'] = (quarterly_summary['revenue'] / quarterly_summary['budget']).round(2)

        # Optional: round all financial values
        quarterly_summary[['budget', 'revenue', 'net_profit']] = quarterly_summary[['budget', 'revenue', 'net_profit']].round(2)
        quarterly_data = quarterly_summary.to_dict(orient='records')
        channels = sorted(df['channel'].dropna().unique())

        # Group and collect top 5 campaigns by net profit per quarter
        top_campaigns_by_quarter = {}

        for q in sorted(df['quarter'].unique()):
            top_5 = (
                df[df['quarter'] == q].sort_values(by='net_profit', ascending=False).head(5)[['campaign_name', 'net_profit', 'roi', 'channel', 'type']].round(2).to_dict(orient='records')
            )
            top_campaigns_by_quarter[q] = top_5

        # Group and collect the top 5 worst campaign performers by net profit per quarter
        worst_campaigns_by_quarter = {}

        for q in sorted(df['quarter'].unique()):
            bottom_5 = (
            df[df['quarter'] == q].sort_values(by='net_profit', ascending=True).head(5)[['campaign_name', 'net_profit', 'roi', 'channel', 'type']].round(2).to_dict(orient='records')
            )
            worst_campaigns_by_quarter[q] = bottom_5

        #Calculate campaign duration vs ROI
        duration_roi_df = df[df['roi'].notna() & df['duration_days'].notna()]
        duration_vs_roi = duration_roi_df[['campaign_name', 'duration_days', 'roi']].round(2).to_dict(orient='records')
        #Calculate budget efficiency ration roi/budget
        df['roi_per_1000_dollars'] = (df['roi'] / df['budget']) * 1000
        df = df[df['roi_per_1000_dollars'].notna() & df['roi_per_1000_dollars'].apply(np.isfinite)]
        top_efficiency = (
            df[['campaign_name', 'roi', 'budget', 'roi_per_1000_dollars', 'channel']].sort_values(by='roi_per_1000_dollars', ascending=False).head(5).round(2).to_dict(orient='records')
        )
        #Calculate channel performance by audience type:
        audience_channel_roi = (
            df.groupby(['channel', 'target_audience'])['roi'].mean().reset_index().round(2).to_dict(orient='records')
        )
        #Calculate ROI and Net Profit by Quarter
        seasonality_by_channel = (
            df.groupby(['quarter', 'channel'])[['roi', 'net_profit']].mean().round(2).reset_index().sort_values(['quarter', 'channel']).to_dict(orient='records')
        )
        print('seasonality_summary:', seasonality_by_channel)


    except Exception as e:
        flash(str(e), 'danger')
    return render_template('dashboard.html', user=user, upload_form=upload_form,                   loss_count=loss_count, top_channel=top_channel, best_type=best_type,    channel_summary=channel_summary, min_date=min_date, max_date=max_date,top_profit_channel=top_profit_channel, top_profit_value=top_profit_value,  top_roi_channel=top_roi_channel, top_roi_value=top_roi_value, available_channels=channels, quarterly_data=quarterly_data, channel_distribution=channel_distribution, top_campaigns_by_quarter=top_campaigns_by_quarter, worst_campaigns_by_quarter=worst_campaigns_by_quarter, duration_vs_roi=duration_vs_roi, top_efficiency=top_efficiency, audience_channel_roi=audience_channel_roi, seasonality_by_channel=seasonality_by_channel)

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
        return render_template('preview.html', preview=preview, null_counts=null_counts_html)

    except Exception as e:
        flash(f"Error reading uploaded file: {e}", 'danger')
        return redirect(url_for('main_routes.show_dashboard'))

@main_routes.route('/data-cleanup')
def data_cleanup():
    if 'csv_file_path' not in session:
        flash('Please upload a dataset first.', 'warning')
        return redirect(url_for('main_routes.show_dashboard'))

    return render_template('dataCleanup.html')
