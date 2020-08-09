from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('log in')

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password_confirm = PasswordField(
        'confirm password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('ur gonna need a more unique username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('this email is already registered')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    password_confirm = PasswordField(
        'confirm password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('reset')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('request password reset')

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
        'say some shiii',
        validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField('post')
