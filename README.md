Project Description
The Secure Student Management System with Digital Audit Trail is a web-based application developed using Python Flask. The system securely manages student records and maintains digital audit logs of user activities. It implements role-based access control, secure authentication, password hashing using bcrypt, dashboard analytics, student ID card generation, PDF/CSV export, and audit trail monitoring.
________________________________________
Software Requirements
•	Python 3.10 or above 
•	Flask 
•	SQLite 
•	HTML 
•	CSS 
•	Bootstrap 
•	bcrypt 
•	Pandas 
•	ReportLab 
________________________________________


Required Python Libraries
Install all dependencies using:
pip install -r requirements.txt
________________________________________
Database
Database Name:
student_management.db
The database contains the following tables:
•	users 
•	students 
•	audit_logs 
________________________________________
Installation Steps
1.	Download the project folder. 
2.	Install Python. 
3.	Install all required libraries. 
4.	Keep student_management.db in the project folder. 
5.	Open the project in VS Code. 
6.	Run the Flask application. 
________________________________________
Running the Project
Execute the following command:
python app.py
Open the browser and visit:
http://127.0.0.1:5000
________________________________________



Default User Roles
The application supports three user roles:
•	Admin 
•	Faculty 
•	Student 
________________________________________
Features
•	Secure Login 
•	Session Authentication 
•	Password Hashing using bcrypt 
•	Role-Based Access Control (RBAC) 
•	Student Record Management 
•	Dashboard Analytics 
•	Student ID Card Generation 
•	Audit Logs 
•	PDF Report Generation 
•	CSV Export 
•	Dark/Light Mode 
•	Custom 404 Error Page 
________________________________________
Security Features
•	Password Hashing (bcrypt) 
•	Session Management 
•	Role-Based Access Control 
•	Input Validation 
•	Audit Trail Logging 
•	Custom Error Handling 
________________________________________
