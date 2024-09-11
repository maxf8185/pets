from flask import render_template, redirect, url_for, request, abort, flash
import sqlalchemy as sa
from flask_login import logout_user, current_user, login_required, login_user
from app import app, db
from .forms import RegistrationForm, LoginForm, PetForm, CategoryForm, EditName, EditNamePet, EditAgePet, EditBreedPet, \
    EditCountryPet, EditCategoryPet, EditDescriptionPet, CommentForm
from app.models import Pet, User, Category, Country, user_pet_likes, Comment
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename


@app.route('/')
@login_required
def index():
    pets = db.session.scalars(sa.select(Pet)).all()
    return render_template('index.html', pets=pets)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form_name = EditName(obj=current_user)
    user_pets = current_user.user_pets
    if form_name.validate_on_submit():
        current_user.username = form_name.username.data
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html', form_name=form_name, user_pets=user_pets)


@app.route('/my_stories')
@login_required
def my_stories():
    user_pets = current_user.user_pets
    return render_template('my_stories.html', user_pets=user_pets)


@app.route('/comments_all')
@login_required
def comments_all():
    comments = db.session.scalars(sa.select(Comment)).all()
    return render_template('comments_all.html', comments=comments)


@app.route('/pet/profile/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def profile_pet(pet_id):
    pet = db.session.scalar(sa.select(Pet).where(Pet.id == pet_id))
    comments = db.session.scalars(sa.select(Comment).where(Comment.pet_id == pet_id)).all()
    if not pet:
        flash('Pet not found', category='danger')
        return redirect(url_for('profile_pet', pet_id=pet_id))
    form = PetForm(obj=pet)
    form_name = EditNamePet(obj=pet)
    form_age = EditAgePet(obj=pet)
    form_breed = EditBreedPet(obj=pet)
    form_country = EditCountryPet(obj=pet)
    form_category = EditCategoryPet(obj=pet)
    form_description = EditDescriptionPet(obj=pet)
    form_comment = CommentForm()

    if request.method == 'POST':
        # Обработка полей редактирования питомца
        if form_name.validate_on_submit():
            pet.name = form_name.name.data
        if form_description.validate_on_submit():
            pet.description = form_description.description.data
        if form_age.validate_on_submit():
            pet.age = form_age.age.data
        if form_breed.validate_on_submit():
            pet.breed = form_breed.breed.data
        if form_category.validate_on_submit():
            category = db.session.scalar(sa.select(Category).where(Category.id == form_category.category.data))
            if category:
                pet.category = category
        if form_country.validate_on_submit():
            country = db.session.scalar(sa.select(Country).where(Country.id == form_country.country.data))
            if country:
                pet.country = country
        if form_comment.validate_on_submit():
            # comment = Comment(text=form_comment.text.data, user_id=current_user.id, pet_id=pet_id)
            # db.session.add(comment)
            comment = Comment(text=form_comment.text.data, user_id=current_user.id, pet_id=pet_id)
            db.session.add(comment)
            try:
                db.session.commit()
                flash('Comment added successfully', category='success')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {e}', category='danger')
            return redirect(url_for('profile_pet', pet_id=pet_id))

        # Сохранение изменений в базе данных
        try:
            db.session.commit()
            flash('Changes saved successfully', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', category='danger')
            print(e)  # Печать ошибки для отладки

        return redirect(url_for('profile_pet', pet_id=pet.id))

    return render_template('profile_pet.html', timedelta=timedelta,
                           form=form, form_name=form_name, form_age=form_age,
                           form_breed=form_breed, form_country=form_country,
                           form_category=form_category, form_description=form_description, form_comment=form_comment,
                           pet=pet, comments=comments)


@app.template_filter('get_image')
def get_image(country):
    if hasattr(country, 'name'):
        country_name = country.name
    else:
        country_name = str(country)
    filename = f'{country_name.replace(" ", "_").lower()}.jpg'
    if os.path.exists(os.path.join(app.static_folder, 'flags', filename)):
        return f'flags/{filename}'
    return 'flags/flag.jpg'


@app.route('/pet/new', methods=['GET', 'POST'])
@login_required
def new_pet():
    form = PetForm()
    if form.validate_on_submit():
        category = db.session.get(Category, form.category.data)
        country = db.session.get(Country, form.country.data)
        pet = Pet(name=form.name.data, description=form.description.data,
                  age=form.age.data, breed=form.breed.data,
                  country=country, category=category,
                  user_id=current_user.id)
        db.session.add(pet)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_pet.html', form=form)


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
        category = db.session.scalar(sa.select(Category).where(Category.id == form.category.data))
        country = db.session.scalar(sa.select(Country).where(Country.id == form.country.data))
        if category:
            pet.category = category
        else:
            flash('Category not found', category='danger')
        if country:
            pet.category = category
        else:
            flash('Сountry not found', category='danger')
        db.session.commit()
        flash('You successfully edited the pet', category='success')
        return redirect(url_for('index'))
    return render_template('edit_pet.html', form=form)


@app.route('/delete_pet/<int:pet_id>', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if comment:
        try:
            db.session.delete(comment)
            db.session.commit()
            flash('Comment deleted successfully', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', category='danger')
    else:
        flash('Comment not found', category='danger')

    return redirect(url_for('profile_pet', pet_id=comment.pet_id))


@app.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if comment:
        if current_user in comment.likers:
            # User already liked the comment, so remove the like
            comment.likers.remove(current_user)
            comment.likes -= 1
        else:
            # User has not liked the comment, so add the like
            comment.likers.append(current_user)
            comment.likes += 1

        try:
            db.session.commit()
            flash('Like status updated successfully', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', category='danger')
    else:
        flash('Comment not found', category='danger')

    return redirect(url_for('profile_pet', pet_id=comment.pet_id))


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
@login_required
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
    posts_list = db.session.scalars(sa.select(Pet).where(Pet.category_id == category_id)).all()
    return render_template('posts.html', posts=posts_list)


@app.route('/category')
def category():
    categories = db.session.scalars(sa.select(Category)).all()
    return render_template('categories.html', categories=categories)


@app.route('/like_pet/<int:pet_id>', methods=['POST'])
def like_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)

    # Check if user has already liked the pet
    if current_user in pet.likers:
        # Remove like
        pet.likers.remove(current_user)
        pet.likes -= 1
    else:
        # Add like
        pet.likers.append(current_user)
        pet.likes += 1

    db.session.commit()

    # Redirect back to the same page
    return redirect(request.referrer or url_for('index'))


@app.route('/liked_pets')
@login_required
def liked_pets():
    # Отримання проголосованих петицій для користувача
    liked_pets = get_liked_pets_for_user(current_user.id)
    return render_template('liked_pets.html', liked_pets=liked_pets)


def get_liked_pets_for_user(user_id):
    # Отримати користувача за його ідентифікатором
    user = User.query.get(user_id)

    if user:
        # Повернути список петицій, за які користувач проголосував
        return user.liked_pets
    else:
        # Повернути пустий список, якщо користувач не знайдений
        return []


def time_since(creation_date):
    now = datetime.utcnow()
    diff = now - creation_date

    seconds = diff.total_seconds()
    minutes = int(seconds // 60)
    hours = int(minutes // 60)

    if seconds < 60:
        return f"{int(seconds)} с. тому"
    elif minutes < 60:
        return f"{minutes} хвил. тому"
    elif hours < 24:
        return f"{hours} год. тому"
    else:
        days = int(hours // 24)
        return f"{days} дн. тому"


@app.context_processor
def utility_processor():
    return dict(time_since=time_since)

