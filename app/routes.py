from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import EditProfileForm, EmptyForm, LoginForm, RegistrationForm
from app.models import User

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'dave'},
            'body': 'beautiful day in brooklyn!'
        },
        {
            'author': {'username': 'miri'},
            'body': 'looking for 5 woodchucks...'
        },
    ]
    return render_template('index.html', title='home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=form.username.data).first()
        if _user is None or not _user.check_password(form.password.data):
            flash('invalid username or password ;-(')
            return redirect(url_for('login'))
        login_user(_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # Check that next is not set to an absolute URL with a foreign domain
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="log in", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        _user = User(username=form.username.data, email=form.email.data)
        _user.set_password(form.password.data)
        db.session.add(_user)
        db.session.commit()
        flash("you're in")
        return redirect(url_for('login'))
    return render_template('register.html', title='join', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    _user = User.query.filter_by(username=username).first_or_404()
    posts = [{'author': _user, 'body': 'test'}]
    form = EmptyForm()
    return render_template('user.html', user=_user, posts=posts, form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=username).first()
        if _user is None:
            flash('{} has not been invited to the party'.format(username))
            return redirect(url_for('index'))
        if _user == current_user:
            flash("nice try, but you can't follow yourself")
            return redirect(url_for('user', username=username))
        current_user.follow(_user)
        db.session.commit()
        flash("you're now following {}!".format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=username).first()
        if _user is None:
            flash('{} has not been invited to the party'.format(username))
            return redirect(url_for('index'))
        if _user == current_user:
            flash("thou cannot unfollow oneself")
            return redirect(url_for('user', username=username))
        current_user.unfollow(_user)
        db.session.commit()
        flash('unfollowed {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('user', username=username))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('updates saved successfully')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title="edit profile", form=form)
