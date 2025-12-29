from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required

from email_validator import validate_email, EmailNotValidError

import secrets

from blueprintapp.app import db, bcrypt
from blueprintapp.blueprints.auth.models import User
from blueprintapp.blueprints.reviews.models import TeacherReview, DisciplineReview

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="templates/auth/assets")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            valid = validate_email(email, check_deliverability=False)
            email = valid.email
        except EmailNotValidError as e:
            return render_template("auth/login.html", error="Invalid email format.")

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("auth/login.html", error="User not found. Please sign up first.")

        if bcrypt.check_password_hash(user.passwordHash, password):
            login_user(user)

            session['name'] = user.username
            session['email'] = user.email

            return redirect(url_for("core.index"))
        else:
            return render_template("auth/login.html", error="Incorrect password.")
    


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    elif request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            valid = validate_email(email, check_deliverability=False)
            email = valid.email
        except EmailNotValidError as e:
            return render_template("auth/signup.html", error="Invalid email format.")
        
        if User.query.filter_by(email=email).first():
            return render_template("auth/signup.html", error="This email is already registered.")

        if correct_password(password):
            passwordHash = bcrypt.generate_password_hash(password).decode('utf-8')

            verification_code = str(secrets.randbelow(10**6)).zfill(6)
            print(f"Verification code for {email}: {verification_code}")

            session['verification_code'] = verification_code
            session['name'] = name
            session['email'] = email
            session['passwordHash'] = passwordHash

            return redirect(url_for("auth.verification"))
        else:
            return render_template(
                "auth/signup.html", 
                error="Invalid password. It must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
                )
    


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("core.index"))



@auth.route("/verification", methods=["POST", "GET"])
def verification():
    if request.method == "GET":
        return render_template("auth/verification.html")
    elif request.method == "POST":
        code = ''.join([
            request.form.get(f'digit{i}', '') for i in range(6)
        ])
        
        if code == session.get('verification_code'):
            if session.get('purpose') == 'reset':
                user = User.query.filter_by(email=session['email']).first()
                session['name'] = user.username

                user.passwordHash = bcrypt.generate_password_hash(session['newpassword']).decode('utf-8')
                db.session.commit()

                session.pop('verification_code', None)
                session.pop('newpassword', None)
                session.pop('purpose', None)

                return redirect(url_for('auth.login'))

            user = User(username=session['name'], email=session['email'], passwordHash=session['passwordHash'])

            db.session.add(user)
            db.session.commit()

            login_user(user)
            
            session.pop('passwordHash', None)
            session.pop('verification_code', None)

            return redirect(url_for("core.index"))
        else:
            return render_template('auth/verification.html', error='Invalid code, please try again!')



@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot_password.html")
    elif request.method == "POST":
        session['email'] = request.form.get("email")
        session['newpassword'] = request.form.get("newpassword")

        try:
            valid = validate_email(session['email'], check_deliverability=False)
            session['email'] = valid.email
        except EmailNotValidError as e:
            return render_template("auth/forgot_password.html", error="Invalid email format.")

        user = User.query.filter_by(email=session['email']).first()

        if user:
            if correct_password(session['newpassword']):
                session['purpose'] = 'reset'

                verification_code = str(secrets.randbelow(10**6)).zfill(6)
                print(f"Verification code for {session['email']}: {verification_code}")

                session['verification_code'] = verification_code

                return redirect(url_for("auth.verification"))
            else:
                return render_template(
                            'auth/forgot_password.html', 
                            error="Invalid new password. It must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
                            )
        else:
            return render_template('auth/forgot_password.html', error='Email address not registered!')



@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    teachReviews = TeacherReview.query.filter_by(user_id = current_user.id).all()
    disReviews = DisciplineReview.query.filter_by(user_id = current_user.id).all()
    
    if request.method == "GET":
        return render_template("auth/profile.html", user=current_user, teachReviews=teachReviews, disReviews=disReviews)
    elif request.method == "POST":
        new_username = request.form.get("username").strip()
        new_password = request.form.get("new_password").strip()
        
        if new_username == "" and new_password:
            if correct_password(new_password):
                user = User.query.filter_by(id=current_user.id).first()
                user.passwordHash = bcrypt.generate_password_hash(new_password).decode('utf-8')

                db.session.commit()

                return render_template("auth/profile.html", user=current_user, error="Password updated successfully.", disReviews=disReviews, teachReviews=teachReviews)
            else:
                return render_template(
                    "auth/profile.html", 
                    user=current_user, 
                    error="Invalid password. It must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                    disReviews=disReviews,
                    teachReviews=teachReviews
                    )
        elif new_password == "" and new_username:
            if User.query.filter_by(username=new_username).first():
                return render_template("auth/profile.html", user=current_user, error="Username already taken.", disReviews=disReviews, teachReviews=teachReviews)

            user = User.query.filter_by(id=current_user.id).first()

            user.username = new_username

            db.session.commit()

            return render_template("auth/profile.html", user=current_user, error="Username updated successfully.", disReviews=disReviews, teachReviews=teachReviews)
        elif new_username and new_password:
            if correct_password(new_password):
                if User.query.filter_by(username=new_username).first():
                    return render_template("auth/profile.html", user=current_user, error="Username already taken.", disReviews=disReviews, teachReviews=teachReviews)

                user = User.query.filter_by(id=current_user.id).first()

                user.username = new_username
                user.passwordHash = bcrypt.generate_password_hash(new_password).decode('utf-8')

                db.session.commit()

                return render_template("auth/profile.html", user=current_user, error="Profile updated successfully.", disReviews=disReviews, teachReviews=teachReviews)
            else:
                return render_template(
                    "auth/profile.html", 
                    user=current_user, 
                    error="Invalid password. It must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                    disReviews=disReviews,
                    teachReviews=teachReviews
                    )
        elif new_username == "" and new_password == "":
            return render_template("auth/profile.html", user=current_user, error="No changes made.", disReviews=disReviews, teachReviews=teachReviews)



def correct_password(password):
    import re
    
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    
    return True