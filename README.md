MedTrack: A Cloud-Enabled Healthcare Management System
Project Description
MedTrack is a cloud-based healthcare management system designed to streamline patient-doctor interactions. It enables patients to book appointments, manage medical histories, and receive diagnoses online. Built using Flask for backend development, AWS EC2 for hosting, and DynamoDB for data management, the system ensures secure and efficient healthcare management.

Features
User Registration & Authentication (Doctors & Patients)
Appointment Booking System
Secure Data Storage with AWS DynamoDB
Real-time Notifications
IAM-Based Role Management for Secure Access
Cloud Hosting on AWS EC2
Flask Backend with Boto3 Integration
Responsive Web Pages for Easy Navigation

Tech Stack
Backend: Flask (Python)
Database: AWS DynamoDB
Hosting: AWS EC2
Security: AWS IAM (Identity & Access Management)
Version Control: Git/GitHub
Frontend: HTML, CSS

Setup & Installation
Prerequisites
AWS Account (For EC2, DynamoDB, IAM)
Python3 & pip
Flask Framework
Boto3 for AWS Integration
Git for Version Control

Installation Steps

Clone the Repository
git clone cd MedTrack
Set up a Virtual Environment
python3 -m venv venv source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Configure AWS Credentials
Set up AWS IAM roles for secure access. Update config.py with AWS access credentials.
Run the Application Locally
python app.py Access the application at http://127.0.0.1:5000/
Deployment on AWS EC2

Launch EC2 Instance
Choose Amazon Linux 2 or Ubuntu as the AMI.
Open ports for HTTP (80) & SSH (22).
Connect to EC2 Instance
ssh -i <your-key.pem> ec2-user@
Set Up the Environment
sudo yum update -y
sudo yum install python3 -y
sudo pip3 install virtualenv
python3 -m venv venv
source venv/bin/activate
pip install flask boto3
Deploy the Flask Application
python app.py
Access the Web App
http://:5000
Project Workflow

AWS Account Setup & IAM Configuration
DynamoDB Table Creation
Flask Backend Development
EC2 Instance Deployment
Testing & Debugging
Production Deployment
User Guide
For Patients:
Register/Login
Book Appointments
View Medical History
Receive Diagnosis Reports

For Doctors:
Login to the Dashboard
View Patient Appointments
Submit Diagnoses & Treatment Plans

Database Schema
Users Table
Appointments Table

Testing
Functional Testing: User registration, login, appointment booking
Database Testing: Data retrieval from DynamoDB
Security Testing: AWS IAM Role-Based Access

Conclusion
MedTrack is a scalable, secure, and efficient cloud-based healthcare management system. By leveraging AWS services, it enhances patient-doctor interactions, streamlining the process of appointment booking and medical data management.
