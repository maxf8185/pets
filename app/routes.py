from flask import render_template, redirect, url_for, request
import sqlalchemy as sa
from flask_login import logout_user, current_user, login_required, login_user

from app import app, db
from app.models import Pet, User


@app.route('/')
@login_required
def index():
    pets = db.session.scalars(sa.select(Pet)).all()
    return render_template('index.html', pets=pets)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return '<h1>log out please</h1>'
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if not user or not user.check_password(password):
            return '<h1>User not valid</h1>'
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return '<h1>Logged out</h1>'
