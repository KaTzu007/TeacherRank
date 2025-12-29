from blueprintapp.app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'User {self.id}; {self.username}; {self.email}'
    
    def get_id(self):
        return str(self.id)