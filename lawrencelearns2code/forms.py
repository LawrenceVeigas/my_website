from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from lawrencelearns2code.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired(), Length(2,20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Account already exits with this email address')
            

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired(), Length(2,20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data!=current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use.')

class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(2,50)])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Post')

