from app import app
from flask import render_template, request, redirect, url_for, session
from app.services import convenors, reports, accounts


# Dashboard
@app.route("/convenor/dashboard/")
def convenor_dashboard():
    if "user_id" in session:
        user_id = session["user_id"]
        convenor = convenors.get_convenor_by_user_id(user_id)
        return render_template("/convenor/dashboard.html", convenor=convenor)
    else:
        return redirect(url_for('login'))
