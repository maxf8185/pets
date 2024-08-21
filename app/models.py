from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional


user_pet = sa.Table(
    'user_pet',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('pet_id', sa.Integer, sa.ForeignKey('pet.id'), primary_key=True)
)



class User(UserMixin, db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    username: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    password_hash: so.MappedColumn[Optional[str]] = so.mapped_column(sa.String(60))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.username


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))



class Pet(db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    topic: so.MappedColumn[str] = so.mapped_column(sa.String(100))
    name: so.MappedColumn[str] = so.mapped_column(sa.String(30))

    def __repr__(self):
        return f'Pet: {self.topic}'
