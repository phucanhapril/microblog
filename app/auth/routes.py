from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, \
     ResetPasswordRequestForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=form.username.data).first()
        if _user is None or not _user.check_password(form.password.data):
            flash('invalid username or password ;-(')
            return redirect(url_for('auth.login'))
        login_user(_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # Check that next is not set to an absolute URL with a foreign domain
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title="log in", form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        _user = User(username=form.username.data, email=form.email.data)
        _user.set_password(form.password.data)
        db.session.add(_user)
        db.session.commit()
        flash("you're in")
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', title='join', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(email=form.email.data).first()
        if _user:
            send_password_reset_email(_user)
        flash("if ur legit, you'll receive a reset link in your inbox")
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_pw_request.html',
        title='reset password',
        form=form
    )

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    _user = User.verify_reset_password_token(token) # this is weird naming?
    if not _user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        _user.set_password(form.password.data)
        db.session.commit()
        flash('your password has been reset')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_pw.html', form=form)
