from blueprintapp.app import db
from datetime import date

class TeacherReview(db.Model):
    __tablename__ = "teacher_reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)

    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    discipline_name = db.Column(db.String(80), nullable=False)

    difficulty = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    time = db.Column(db.Date, default=date.today, onupdate=date.today, nullable=False)

    teacher = db.relationship("Teacher", backref="teacher_reviews")
    discipline = db.relationship("Discipline", backref="teacher_reviews")

    def __repr__(self):
        return f"<TeacherReview {self.name} {self.surname} - {self.discipline_name}>; {self.rating} stars; feedback: {self.feedback[:20]}..."

class DisciplineReview(db.Model):
    __tablename__ = "discipline_reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)

    name = db.Column(db.String(80), nullable=False)

    difficulty = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    time = db.Column(db.Date, default=date.today, onupdate=date.today, nullable=False)

    discipline = db.relationship("Discipline", backref="discipline_reviews")

    def __repr__(self):
        return f"<DisciplineReview {self.name} - {self.discipline_name}>; {self.rating} stars; feedback: {self.feedback[:20]}..."