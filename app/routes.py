from flask import render_template, redirect, url_for, request, abort, flash
import sqlalchemy as sa
from flask_login import logout_user, current_user, login_required, login_user
from app import app, db
from .forms import RegistrationForm, LoginForm, PetForm
from app.models import Pet, User


@app.route('/')
# @login_required
def index():
    pets = db.session.scalars(sa.select(Pet)).all()
    return render_template('index.html', pets=pets)


@app.route('/profile')
@login_required
def profile():
    user_pets = db.session.scalars(current_user.user_pets.select())
    return render_template('profile.html', user_pets=user_pets)


@app.route('/pet/adopt/<int:pet_id>')
@login_required
def adopt_pet(pet_id):
    pet = db.session.scalar(sa.select(Pet).where(Pet.id == pet_id))
    user_pets = db.session.scalars(current_user.user_pets.select())
    if pet in user_pets:
        return '<h1>You have already adopted this pet</h1>'
    current_user.user_pets.add(pet)
    db.session.commit()
    return '<h1>You have adopted this pet successfully</h1>'


@app.route('/pet/edit/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    pet = db.session.scalar(sa.select(Pet).where(Pet.id == pet_id))
    form = PetForm(obj=pet)
    if form.validate_on_submit():
        pet.name = form.name.data
        pet.species = form.species.data
        pet.age = form.age.data
        pet.description = form.description.data
        db.session.commit()
        flash('You successfully edited the pet', category='success')
        return redirect(url_for('index'))
    return render_template('edit_pet.html', form=form)


@app.route('/pet/new', methods=['GET', 'POST'])
def new_pet():
    form = PetForm()
    if form.validate_on_submit():
        pet = Pet(name=form.name.data,  age=form.age.data, description=form.description.data)
        db.session.add(pet)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_pet.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data) or not user.is_active:
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
