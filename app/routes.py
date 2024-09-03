from flask import render_template, redirect, url_for, request, abort, flash
import sqlalchemy as sa
from flask_login import logout_user, current_user, login_required, login_user
from app import app, db
from .forms import RegistrationForm, LoginForm, PetForm, CategoryForm
from app.models import Pet, User, Category


@app.route('/')
@login_required
def index():
    pets = db.session.scalars(sa.select(Pet)).all()
    return render_template('index.html', pets=pets)


@app.route('/profile')
@login_required
def profile():
    user_pets = current_user.user_pets
    return render_template('profile.html', user_pets=user_pets)


@app.route('/pet/edit/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = db.session.scalar(sa.select(Pet).where(Pet.id == pet_id))
    if not pet:
        flash('Pet not found', category='danger')
        return redirect(url_for('index'))
    form = PetForm(obj=pet)
    if form.validate_on_submit():
        pet.name = form.name.data
        pet.description = form.description.data
        pet.age = form.age.data
        pet.breed = form.breed.data
        pet.country = form.country.data
        category = db.session.scalar(sa.select(Category).where(Category.id == form.category.data))
        if category:
            pet.category = category
        else:
            flash('Category not found', category='danger')
        db.session.commit()
        flash('You successfully edited the pet', category='success')
        return redirect(url_for('index'))
    return render_template('edit_pet.html', form=form)


@app.route('/pet/new', methods=['GET', 'POST'])
@login_required
def new_pet():
    form = PetForm()
    if form.validate_on_submit():
        category = db.session.get(Category, form.category.data)
        pet = Pet(name=form.name.data, description=form.description.data,
                  age=form.age.data, breed=form.breed.data,
                  country=form.country.data, category=category,
                  user_id=current_user.id)
        db.session.add(pet)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_pet.html', form=form)


@app.route('/delete_pet/<int:pet_id>', methods=['POST'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


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


@app.route('/category/new', methods=['POST', 'GET'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('create_category.html', form=form)


@app.route('/category/<int:category_id>')
def category_posts(category_id):
    category = db.session.scalar(sa.select(Category).where(Category.id == category_id))
    posts_list = db.session.scalars(category.posts.select())
    return render_template('posts.html', posts=posts_list)


@app.route('/category')
def category():
    categories = db.session.scalars(sa.select(Category))
    return render_template('categories.html', categories=categories)