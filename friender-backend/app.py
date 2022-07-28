from flask import Flask, request, render_template, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
import boto3
import os
import uuid
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from models import db, connect_db, User, Like, Dislike
from forms import SignUpForm, LoginForm, PhotoForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['S3_KEY'] = os.environ['S3_KEY']
app.config['S3_SECRET'] = os.environ['S3_SECRET']
app.config['S3_BUCKET'] = os.environ['S3_BUCKET']
BASE_URL = os.environ['BASE_URL']

s3 = boto3.client(
    "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)

connect_db(app)
# db.drop_all()
db.create_all()

# debug = DebugToolbarExtension(app)

CURR_USER_KEY = "curr_user"


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id



@app.get("/")
def generate_landing():
    """Generate app landing page for non-logged in users"""

    if g.user == None:
        return render_template("home-anon.html")
    else:
        users = User.query.all()
        return render_template("home.html", users=users)


@app.route("/signup", methods=["GET","POST"])
def signup_page():
    """Submit signup form and create user
        Takes user to upload profile photo page
    """

    form = SignUpForm()

    if form.validate_on_submit():

        user = User.signup(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            location=form.location.data,
            friend_radius=form.friend_radius.data,
            hobbies=form.hobbies.data,
            interests=form.interests.data,
            password=form.password.data,
        )


        db.session.commit()

        do_login(user)

        return redirect(f"/profilephoto/{user.id}")
    else:
        return render_template("signup.html", form=form)



@app.route("/profilephoto/<int:user_id>", methods=["GET", "POST"])
def submit_a_photo(user_id):
    """ Submit Profile photo page
        Renders photo form
        Takes a file from user, uploads to AWS
        and updates database with file name
    """

    user = User.query.get_or_404(user_id)
    filename = secure_filename(str(uuid.uuid1()))

    form = PhotoForm()

    if form.validate_on_submit():
        img = form.file.data

        if img:
            s3.upload_fileobj(
                img,
                app.config["S3_BUCKET"],
                filename,
                ExtraArgs={'ACL': 'public-read'}
            )

            url = f"{BASE_URL}/{filename}"
            user.img_url = url

            db.session.commit()
            return redirect(f'/user/{user.id}')
    else:
        return render_template("submitphoto.html", form=form)

@app.get('/user/<int:user_id>')
def user_detail_page(user_id):
    user = User.query.get_or_404(user_id)

    return render_template("/users/detail.html", user=user)

def likes(evt):
    liked_user = User.query.get_or_404(evt.target.user.id)
    g.user.liking.append(liked_user)
    db.session.commit()

    return redirect("/")
