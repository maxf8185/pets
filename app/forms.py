from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, IntegerField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app import app, db
import sqlalchemy as sa
from app.models import Category


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmed_password = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')
    #
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class PetForm(FlaskForm):
    name = StringField("Ім'я улюбленця", validators=[DataRequired()])
    description = TextAreaField("Опис", validators=[DataRequired()])
    age = IntegerField("Вік", validators=[DataRequired()])
    breed = StringField("Порода", validators=[DataRequired()])
    country = StringField("Країна", validators=[DataRequired()])
    category = SelectField("Категорія", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Відправити")

    def __init__(self, *args, **kwargs):
        super(PetForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name) for category in db.session.query(Category).order_by(Category.name).all()
        ]