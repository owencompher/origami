from flask import Blueprint, session, flash, redirect, render_template, request, url_for
from flask_peewee.utils import get_object_or_404
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user
from flask_dance.contrib.discord import discord
from models import User, IntegrityError
from app import lm, now

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login(error=None):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = None

        try: user = User.get(User.username == username)
        except User.DoesNotExist: error = f"user {username} does not exist"

        if user:
            if not user.password: return redirect(url_for('discord.login'))
            if not check_password_hash(user.password, password):
                error = 'incorrect password'

        if error is None:
            if current_user.is_authenticated:
                logout_user()
                if discord.authorized: del session['oauth_token']
            login_user(user)
            session['oauth_token'] = discord.token
            #   flash('logged in')
            return redirect(request.args.get('next') or url_for('root.index'))

        flash(error)

    return render_template('auth/login.html', error=error)


@bp.route('/logout')
def logout():
    logout_user()
    if discord.authorized: del session['oauth_token']
    #   flash('logged out')
    return redirect(request.args.get('next') or url_for('root.index'))


@bp.route('/register', methods=('GET', 'POST'))
def register(error=None):
    if request.method == 'POST':
        username = request.form['username']
        #   email = request.form['email']
        password = request.form['password']
        error = None

        if not username:
            error = 'username is required'
        elif not password:
            error = 'password is required'

        if error is None:
            try:
                user = User(username=username, password=generate_password_hash(password), joined=now(), admin=False)
                user.save()
            except IntegrityError:
                error = f"user {username} is already registered"
            else:
                flash(f"registered user {username}")
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html', error=error)


@bp.route('/users/<username>', methods=('GET', 'POST'))
def user(username, error=None):
    user = get_object_or_404(User.select(User).where(User.username == username))
    duser = user.duid

    if request.method == 'POST':
        if not current_user.admin and not user == current_user: return lm.unauthorized()

        if 'username' in request.form:
            try:
                current_user.username = request.form['username']
                current_user.save()
            except IntegrityError:
                error = f"username {request.form['username']} is taken"

        if not error: return redirect(url_for('auth.user', username=current_user.username, error=error))

    return render_template('auth/user.html', user=user, duser=duser, error=error)


@lm.user_loader
def load_user(user_id): return User.get_or_none(user_id)
