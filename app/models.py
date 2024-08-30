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
    username: so.MappedColumn[str] = so.mapped_column(sa.String(60), unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), unique=True, index=True)
    password_hash: so.MappedColumn[Optional[str]] = so.mapped_column(sa.String(60))
    user_pets: so.Mapped['Pet'] = so.relationship(back_populates='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.username


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Category(db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    name: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    pets: so.WriteOnlyMapped['Pet'] = so.relationship(back_populates='category')


class Pet(db.Model):
    id: so.MappedColumn[int] = so.mapped_column(primary_key=True)
    name: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    description: so.MappedColumn[str] = so.mapped_column(sa.Text)
    age: so.MappedColumn[int]
    breed: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    country: so.MappedColumn[str] = so.mapped_column(sa.String(60))
    category_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Category.id))
    category: so.Mapped[Category] = so.relationship(back_populates='pets')
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    author: so.Mapped[User] = so.relationship(back_populates='user_pets')

    def __repr__(self):
        return f'Pet: {self.topic}'

