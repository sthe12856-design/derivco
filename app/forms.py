from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    role_title = StringField('Role / Title', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=300)])
    github_url = StringField('GitHub URL', validators=[Optional(), Length(max=200)])
    avatar_url = StringField('Profile Picture URL', validators=[Optional(), Length(max=300)])
    avatar_upload = FileField('Upload Profile Picture', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')


class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    stage = SelectField('Current Stage', choices=[
        ('planning', 'Planning'),
        ('building', 'Building'),
        ('testing', 'Testing'),
        ('done', 'Done'),
    ])
    support_needed = TextAreaField('Support / Help Needed', validators=[Optional()])
    submit = SubmitField('Save Project')


class MilestoneForm(FlaskForm):
    title = StringField('Milestone Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Add Milestone')


class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post Comment')


class HandRaiseForm(FlaskForm):
    message = TextAreaField('Message (optional)', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Raise Hand 🤚')
