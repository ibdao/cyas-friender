from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length

class CSRFProtection(FlaskForm):
    """CSRFProtection form, intentionally left blank."""


class SignUpForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    location = StringField('Zipcode', validators=[DataRequired()])
    friend_radius = StringField('Friend radius')
    hobbies = TextAreaField('Hobbies')
    interests = TextAreaField('Interests')
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class PhotoForm(FlaskForm):
    file = FileField('file')
