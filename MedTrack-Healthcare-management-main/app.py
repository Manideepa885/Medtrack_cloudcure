from flask import Flask, request, session, redirect, url_for, render_template, flash
import boto3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from config import Config  # Import Config class

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)                     # Load configurations from config.py
app.secret_key = app.config['SECRET_KEY']           # Use the secret key from config

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', 
                           region_name=app.config['AWS_REGION_NAME'],
                           aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

# Define DynamoDB tables
user_table = dynamodb.Table('UsersTable')
appointment_table = dynamodb.Table('AppointmentsTable')

# -------------------------------
# Helper Functions
# -------------------------------

# Check if user is logged in
def is_logged_in():
    return 'email' in session

# Get user role
def get_user_role(email):
    response = user_table.get_item(Key={'email': email})
    if 'Item' in response:
        return response['Item'].get('role')  # Either 'doctor' or 'patient'
    return None

# -------------------------------
# Routes
# -------------------------------

# Home Page
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Register User (Doctor/Patient)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():  # Check if already logged in
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])  # Hash password
        age = request.form['age']
        gender = request.form['gender']
        role = request.form['role']  # 'doctor' or 'patient'

        # Add user to DynamoDB
        user_table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': password,  # Store hashed password
                'age': age,
                'gender': gender,
                'role': role,
                'specialization': request.form['specialization'] if role == 'doctor' else None,
            }
        )
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login User (Doctor/Patient)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():  # If the user is already logged in, redirect to dashboard
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Get the selected role (doctor or patient)

        # Validate user credentials
        user = user_table.get_item(Key={'email': email}).get('Item')

        if user:
            # Check password and role
            if check_password_hash(user['password'], password):  # Use check_password_hash to verify hashed password
                if user['role'] == role:
                    session['email'] = email
                    session['role'] = role  # Store the role in the session
                    flash('Login successful.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid role selected.', 'danger')
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Email not found.', 'danger')

    return render_template('login.html')

# Logout User
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':  # Ensure it's a POST request for logout
        session.pop('email', None)
        session.pop('role', None)
        flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Dashboard for both Doctors and Patients
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))

    role = session['role']
    email = session['email']

    if role == 'doctor':
        # Show doctor dashboard with list of appointments
        response = appointment_table.scan(
            FilterExpression="#doctor_email = :email",
            ExpressionAttributeNames={"#doctor_email": "doctor_email"},
            ExpressionAttributeValues={":email": email}
        )
        appointments = response['Items']
        return render_template('doctor_dashboard.html', appointments=appointments)

    elif role == 'patient':
        # Show patient dashboard with list of their appointments
        response = appointment_table.scan(
            FilterExpression="#patient_email = :email",
            ExpressionAttributeNames={"#patient_email": "patient_email"},
            ExpressionAttributeValues={":email": email}
        )
        appointments = response['Items']
        return render_template('patient_dashboard.html', appointments=appointments)

# Book an Appointment (Patient)
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if not is_logged_in() or session['role'] != 'patient':
        flash('Only patients can book appointments.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_email = request.form['doctor_email']
        symptoms = request.form['symptoms']
        patient_email = session['email']

        # Create a new appointment
        appointment_id = str(uuid.uuid4())
        appointment_table.put_item(
            Item={
                'appointment_id': appointment_id,
                'doctor_email': doctor_email,
                'patient_email': patient_email,
                'symptoms': symptoms,
                'status': 'pending',
                'appointment_date': str(datetime.now()),
            }
        )
        flash('Appointment booked successfully.', 'success')
        return redirect(url_for('dashboard'))

    # Get list of doctors for selection
    response = user_table.scan(
        FilterExpression="#role = :role",
        ExpressionAttributeNames={"#role": "role"},
        ExpressionAttributeValues={":role": 'doctor'}
    )
    doctors = response['Items']
    return render_template('book_appointment.html', doctors=doctors)

# View Appointment (Doctor)
@app.route('/view_appointment/<appointment_id>', methods=['GET', 'POST'])
def view_appointment(appointment_id):
    if not is_logged_in() or session['role'] != 'doctor':
        flash('Only doctors can view appointments.', 'danger')
        return redirect(url_for('login'))

    # Fetch appointment details
    response = appointment_table.get_item(Key={'appointment_id': appointment_id})
    appointment = response.get('Item')

    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        treatment_plan = request.form['treatment_plan']
        prescription = request.form['prescription']

        # Update appointment with doctor's diagnosis and treatment plan
        appointment_table.update_item(
            Key={'appointment_id': appointment_id},
            UpdateExpression="set diagnosis = :d, treatment_plan = :t, prescription = :p, #s = :s",
            ExpressionAttributeValues={
                ':d': diagnosis,
                ':t': treatment_plan,
                ':p': prescription,
                ':s': 'completed'
            },
            ExpressionAttributeNames={
                '#s': 'status'  # Use #s as an alias for the reserved keyword 'status'
            }
        )
        flash('Diagnosis submitted successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('view_appointment.html', appointment=appointment)

# Submit Diagnosis (Doctor)
@app.route('/submit_diagnosis/<appointment_id>', methods=['POST'])
def submit_diagnosis(appointment_id):
    diagnosis = request.form['diagnosis']
    treatment_plan = request.form['treatment_plan']
    prescription = request.form['prescription']

    # Update the appointment in the database
    appointment_table.update_item(
        Key={'appointment_id': appointment_id},
        UpdateExpression="SET diagnosis = :d, treatment_plan = :t, prescription = :p, #status = :s",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ':d': diagnosis,
            ':t': treatment_plan,
            ':p': prescription,
            ':s': 'completed'
        }
    )

    flash('Diagnosis submitted successfully.', 'success')
    return redirect(url_for('dashboard'))

# -------------------------------
# Run the Flask app
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
