from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required

from blueprintapp.app import db
from blueprintapp.blueprints.admin.models import Teacher, Discipline

admin = Blueprint("admin", __name__, template_folder="templates") #static_folder="templates/admin/assets"