from flask import Flask

app = Flask(__name__)

from app import administrator_views
from app import chair_views
from app import convenor_views
from app import form_views
from app import report_views
from app import student_views
from app import supervisor_views
from app import views