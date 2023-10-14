from app import app
from flask import render_template, request, session
from app.services import students, notification

# Dashboard
@app.route("/administrator/dashboard/")
def administrator_dashboard():
    unapproved_students = students.get_unapproved_students()

    return render_template("/administrator/dashboard.html",
                           unapproved_students=unapproved_students)