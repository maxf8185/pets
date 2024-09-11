from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, IntegerField, TextAreaField, PasswordField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app import app, db
import sqlalchemy as sa
from app.models import Category, Country


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirmed_password = PasswordField('Підтвердіть пароль', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Зареєструватись')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')


class EditName(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')


class PetForm(FlaskForm):
    name = StringField("Ім'я улюбленця", validators=[DataRequired()])
    description = TextAreaField("Історія", validators=[DataRequired()])
    age = IntegerField("Вік", validators=[DataRequired()])
    breed = StringField("Порода", validators=[DataRequired()])
    country = SelectField("Країна", coerce=int, validators=[DataRequired()])
    category = SelectField("Категорія", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Відправити")

    def __init__(self, *args, **kwargs):
        super(PetForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name) for category in db.session.query(Category).order_by(Category.name).all()
        ]
        self.country.choices = [
            (country.id, country.name) for country in db.session.query(Country).order_by(Country.name).all()
        ]


class EditNamePet(FlaskForm):
    name = StringField("Ім'я улюбленця", validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')


class EditAgePet(FlaskForm):
    age = IntegerField("Вік", validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')


class EditBreedPet(FlaskForm):
    breed = StringField("Порода", validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')


class EditCountryPet(FlaskForm):
    country = SelectField("Вид", coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')

    def __init__(self, *args, **kwargs):
        super(EditCountryPet, self).__init__(*args, **kwargs)
        self.country.choices = [
            (country.id, country.name) for country in db.session.query(Country).order_by(Country.name).all()
        ]


class EditDescriptionPet(FlaskForm):
    description = TextAreaField("Історія", validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')


class EditCategoryPet(FlaskForm):
    category = SelectField("Вид", coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зберегти зміни')

    def __init__(self, *args, **kwargs):
        super(EditCategoryPet, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name) for category in db.session.query(Category).order_by(Category.name).all()
        ]


class CategoryForm(FlaskForm):
    name = StringField("Ім'я категорії", validators=[DataRequired()])
    submit = SubmitField("Створити")


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField("Submit")
