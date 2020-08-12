from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('bio', validators=[Length(min=0, max=140)])
    submit = SubmitField('save')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('ur gonna need a more unique username')

class EmptyForm(FlaskForm):
    submit = SubmitField('save')

class PostForm(FlaskForm):
    post = TextAreaField(
        'scream into the abyss',
        validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField('post')

class SearchForm(FlaskForm):
    q = StringField('search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        # Search is submitted with a GET request so query values are in the URL
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
