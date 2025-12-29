from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required

from blueprintapp.app import db
from blueprintapp.blueprints.admin.models import Teacher, Discipline
from blueprintapp.blueprints.reviews.models import TeacherReview, DisciplineReview

reviews = Blueprint("reviews", __name__, template_folder="templates", static_folder="templates/reviews/assets")

@reviews.route("/add_review")
@login_required
def add_review():
    return render_template("reviews/add_review.html")



@reviews.route("/add_teacher", methods=["GET", "POST"])
@login_required
def add_teacher():
    teachers = Teacher.query.all()
    disciplines = Discipline.query.all()
    
    if request.method == "GET":
        return render_template("reviews/add_teacher.html", teachers=teachers, disciplines=disciplines)
    elif request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        discipline_id = request.form.get("discipline_id")

        teacher = Teacher.query.get(teacher_id)
        name = teacher.name
        surname = teacher.surname

        discipline = Discipline.query.get(discipline_id)
        discipline_name = discipline.name

        teach_disciplines = [d.id for d in teacher.disciplines]

        if int(discipline_id) not in teach_disciplines:
            return render_template("reviews/add_teacher.html", teachers=teachers, disciplines=disciplines, error="Teacher is not assigned to this discipline.")

        difficulty = request.form.get("difficulty")
        rating = request.form.get("rating")
        feedback = request.form.get("feedback")

        new_teacher_review = TeacherReview(
            user_id=current_user.id,
            teacher_id=teacher_id,
            discipline_id=discipline_id,
            name=name,
            surname=surname,
            discipline_name=discipline_name,
            difficulty=difficulty,
            rating=int(rating),
            feedback=feedback
        )

        db.session.add(new_teacher_review)
        db.session.commit()

        return redirect(url_for("reviews.add_teacher"))



@reviews.route("/add_discipline", methods=["GET", "POST"])
@login_required
def add_discipline():
    disciplines = Discipline.query.all()

    if request.method == "GET":
        return render_template("reviews/add_discipline.html", disciplines=disciplines)
    elif request.method == "POST":
        discipline_id = request.form.get("discipline_id")

        discipline = Discipline.query.get(discipline_id)

        name = discipline.name

        difficulty = request.form.get("difficulty")
        rating = request.form.get("rating")
        feedback = request.form.get("feedback")

        new_discipline_review = DisciplineReview(
            user_id=current_user.id,
            discipline_id=discipline_id,
            name=name,
            difficulty=difficulty,
            rating=rating,
            feedback=feedback
        )

        db.session.add(new_discipline_review)
        db.session.commit()

        return redirect(url_for("reviews.add_discipline"))



@reviews.route("/search_reviews")
@login_required
def search_reviews():
    return render_template("reviews/search_reviews.html")



@reviews.route("/search_teacher", methods=["GET", "POST"])
@login_required
def search_teacher():
    teachers = Teacher.query.all()
    disciplines = Discipline.query.all()
    reviews = TeacherReview.query.all()

    if request.method == "GET":
        return render_template("reviews/search_teacher.html", teachers=teachers, disciplines=disciplines, reviews=reviews)
    elif request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        discipline_id = request.form.get("discipline_id")

        difficulty = request.form.get("difficulty")
        rating = request.form.get("rating")
        time = request.form.get("time")

        reviews = get_reviews(teacher_id, discipline_id, difficulty, rating, time)

        return render_template("reviews/search_teacher.html", teachers=teachers, disciplines=disciplines, reviews=reviews)



@reviews.route("/search_discipline", methods=["GET", "POST"])
@login_required
def search_discipline():
    disciplines = Discipline.query.all()
    reviews = DisciplineReview.query.all()

    if request.method == "GET":
        return render_template("reviews/search_discipline.html", disciplines=disciplines, reviews=reviews)
    elif request.method == "POST":
        discipline_id = request.form.get("discipline_id")

        faculty = request.form.get("faculty")
        type = request.form.get("type")
        difficulty = request.form.get("difficulty")
        rating = request.form.get("rating")
        time = request.form.get("time")

        reviews = get_reviews(discipline_id=discipline_id, difficulty=difficulty, rating=rating, time=time, faculty=faculty, type=type, call=1)

        return render_template("reviews/search_discipline.html", disciplines=disciplines, reviews=reviews)



@reviews.route("/ratings", methods=["GET", "POST"])
@login_required
def ratings():
    if request.method == "GET":
        return render_template("reviews/ratings.html")

    elif request.method == "POST":
        rank_type = request.form.get("rank_type")

        if rank_type == "teacherRank":
            teachers = Teacher.query.order_by(Teacher.avg_rating.desc()).limit(10).all()
            return render_template("reviews/ratings.html", teachers=teachers)

        elif rank_type == "disciplineRank":
            disciplines = Discipline.query.order_by(Discipline.avg_rating.desc()).limit(10).all()
            return render_template("reviews/ratings.html", disciplines=disciplines)



def get_reviews(teacher_id=None, discipline_id=None, difficulty=None, rating=None, time=None, faculty=None, type=None, call=0):
    models = {0: TeacherReview, 1: DisciplineReview}
    model = models[call]

    query = model.query

    filters = []

    if teacher_id and call == 0:
        filters.append(model.teacher_id == int(teacher_id))
    if discipline_id:
        filters.append(model.discipline_id == int(discipline_id))

    if faculty or type:
        query = query.join(model.discipline)
        if faculty:
            filters.append(Discipline.faculty == faculty)
        if type:
            filters.append(Discipline.type == type)

    if difficulty:
        filters.append(model.difficulty == difficulty)
    if rating:
        filters.append(model.rating >= int(rating))

    if filters:
        query = query.filter(*filters)

    if time == "new":
        query = query.order_by(model.time.desc())
    elif time == "old":
        query = query.order_by(model.time.asc())

    return query.all()



@reviews.route("/delete_teacher_review", methods=["POST"])
@login_required
def delete_teacher_review():
    review_id = request.form.get("review_id")
    review = TeacherReview.query.get(review_id)

    if review:
        db.session.delete(review)
        db.session.commit()

        return redirect(url_for("auth.profile"))
    


@reviews.route("/delete_discipline_review", methods=["POST"])
@login_required
def delete_discipline_review():
    review_id = request.form.get("review_id")
    review = DisciplineReview.query.get(review_id)

    if review:
        db.session.delete(review)
        db.session.commit()

        return redirect(url_for("auth.profile"))