
# PGTracker - Postgraduate Monitoring System

## COMP639 Group Project 2 - Group 11

Web Application URL: https://pgtracker.pythonanywhere.com/

## Technology stack used
  
- Python3
- MySql
- Flask
- Jinja templates
- Bootstrap
- JavaScript

## Build and Run - Steps

1. Create Database connection
- Create new file connect.py in app/util/ folder
- Update connect.py - Replace the values with your details
```
dbuser = "root"  # YOUR MySQL USERNAME
dbpass = "<your_password>"  # "YOUR PASSWORD"
dbhost = "localhost"  # "YOUR HOST"
dbport = "3306" # "YOUR PORT"
dbname = "pgtracker" # "YOUR DATABASE NAME"
```

2. Run below command in your terminal to install required dependencies
```
pip install -r requirements.txt
```

3. Run below command in your terminal to build and run the application
```
flask --app run.py --debug run
```

4. Open the provided URL in your browser (most likely something like http://127.0.0.1:5000/)

