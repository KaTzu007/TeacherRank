from blueprintapp.app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, select

from blueprintapp.blueprints.reviews.models import TeacherReview, DisciplineReview

teacher_discipline = db.Table(
    'teacher_discipline',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), primary_key=True),
    db.Column('discipline_id', db.Integer, db.ForeignKey('disciplines.id', ondelete='CASCADE'), primary_key=True)
)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)

    disciplines = db.relationship(
        "Discipline",
        secondary=teacher_discipline,
        back_populates="teachers"
    )

    reviews = db.relationship("TeacherReview", back_populates="teacher")

    def __repr__(self):
        return f"<Teacher {self.name} {self.surname}>"

    def get_id(self):
        return self.id

    def avg_rating_method(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)

    @hybrid_property
    def avg_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)

    @avg_rating.expression
    def avg_rating(cls):
        return (
            select(func.coalesce(func.avg(TeacherReview.rating), 0))
            .where(TeacherReview.teacher_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )


class Discipline(db.Model):
    __tablename__ = 'disciplines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    faculty = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)

    teachers = db.relationship(
        "Teacher",
        secondary=teacher_discipline,
        back_populates="disciplines"
    )

    reviews = db.relationship("DisciplineReview", back_populates="discipline")

    def __repr__(self):
        return f"<Discipline {self.name}>"

    def get_id(self):
        return self.id

    def avg_rating_method(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)

    @hybrid_property
    def avg_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)

    @avg_rating.expression
    def avg_rating(cls):
        return (
            select(func.coalesce(func.avg(DisciplineReview.rating), 0))
            .where(DisciplineReview.discipline_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )
