from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional, List
from sqlalchemy import Column, DateTime
from datetime import datetime


user_pet_likes = sa.Table(
    'user_pet_likes',
    db.Model.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('pet_id', sa.Integer, sa.ForeignKey('pet.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    username: so.MappedColumn[str] = so.mapped_column(sa.String(60), unique=True)
    email: so.MappedColumn[str] = so.mapped_column(sa.String(128), unique=True, index=True)
    password_hash: so.MappedColumn[Optional[str]] = so.mapped_column(sa.String(60))
    user_pets: so.Mapped[List['Pet']] = so.relationship('Pet', back_populates='author')
    liked_pets: so.Mapped[List['Pet']] = so.relationship('Pet', secondary=user_pet_likes, back_populates='likers')

    def __repr__(self):
        return f'User: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Category(db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    name: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    pets: so.Mapped[List['Pet']] = so.relationship('Pet', back_populates='category')


class Pet(db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    name: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    description: so.MappedColumn[str] = so.mapped_column(sa.Text)
    age: so.MappedColumn[int]
    breed: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    country: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    category: so.Mapped[Category] = so.relationship('Category', back_populates='pets')
    category_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Category.id))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    author: so.Mapped[User] = so.relationship('User', back_populates='user_pets')
    likers: so.Mapped[List[User]] = so.relationship('User', secondary=user_pet_likes, back_populates='liked_pets')
    likes: so.MappedColumn[int] = so.mapped_column(sa.Integer, default=0)
    creation_date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Pet: {self.name}'
