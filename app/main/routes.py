from datetime import datetime
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import Post, User

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('your post has been sent to the void')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.following_posts().paginate(
        page,
        current_app.config['POSTS_PER_PAGE'],
        False
    )
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    # pylint: disable=bad-continuation
    return render_template('index.html',
        title='home',
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    _user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = _user.posts.order_by(
        Post.timestamp.desc()
    ).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.user', username=_user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=_user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template(
        'user.html',
        user=_user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form
    )

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=username).first()
        if _user is None:
            flash('{} has not been invited to the party'.format(username))
            return redirect(url_for('main.index'))
        if _user == current_user:
            flash("nice try, but you can't follow yourself")
            return redirect(url_for('main.user', username=username))
        current_user.follow(_user)
        db.session.commit()
        flash("you're now following {}!".format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=username).first()
        if _user is None:
            flash('{} has not been invited to the party'.format(username))
            return redirect(url_for('main.index'))
        if _user == current_user:
            flash("thou cannot unfollow oneself")
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(_user)
        db.session.commit()
        flash('unfollowed {}'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.user', username=username))

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('updates saved successfully')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title="edit profile", form=form)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,
        current_app.config['POSTS_PER_PAGE'],
        False
    )
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template(
        'index.html',
        title='explore',
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )
