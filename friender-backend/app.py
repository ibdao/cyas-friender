from flask import Flask, request, render_template, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
import boto3
import os
import uuid
from botocore.exceptions import ClientError
from psycopg2 import IntegrityError
from werkzeug.utils import secure_filename
from models import db, connect_db, User, Like, Dislike
from forms import CSRFProtection, SignUpForm, LoginForm, PhotoForm

app = Flask(__name__)

# configure our environmental and global variables
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['S3_KEY'] = os.environ['S3_KEY']
app.config['S3_SECRET'] = os.environ['S3_SECRET']
app.config['S3_BUCKET'] = os.environ['S3_BUCKET']
BASE_URL = os.environ['BASE_URL']
CURR_USER_KEY = "curr_user"

s3 = boto3.client(
    "s3",
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
)

# CONNECT OUR APP TO OUR PSQL DATABASE
connect_db(app)
# db.drop_all()
db.create_all()

# debug = DebugToolbarExtension(app)


# ROUTES

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask g.
        - Do this before every endpoint request.
    """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_protection():
    """Add cross-site request forgery protection through WTForms.
        - Run this before every endpoint request.
    """

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.get("/")
def generate_landing():
    """Generate app landing page
        - Logged in users will see a list of other users.
        - Not logged in users will be given the opetion to sign up or log in.
        - g.user will not see users that have been disliked or liked
    """

    if g.user == None:
        return render_template("home-anon.html")
    else:
        dislikes_id = [u.id for u in g.user.disliking]
        likes_id = [u.id for u in g.user.liking]

        users = [user for user in User
                 .query
                 .filter(User.id.notin_(dislikes_id))
                 .filter(User.id.notin_(likes_id))
                 .all()
                 if user.id != g.user.id
                 ]

        return render_template("home.html", users=users)


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    """Handle signup form.
        - Display it and allow a user to create a profile.
        - Adds user to database upon submission.
        - Redirects to the add profilephoto page.
    """

    form = SignUpForm()

    if form.validate_on_submit():
        try:

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

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("signup.html", form=form)

        do_login(user)

        return redirect(f"/profilephoto/{user.id}")
    else:
        return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Display login form for a returning user and allow user to submit
    login form to log in. Redirect home."""

    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(
            form.username.data,
            form.password.data
        )
        if user:
            do_login(user)
            flash(f"Hello, {user.username}", "success")
            return redirect('/')
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)


@app.post("/logout")
def logout():
    """Allow user to log out. Remove from session.
        - Redirect to login form.
    """

    form = g.csrf_form
    if not form.validate_on_submit():
        flash("Access unauthorized", 'danger')
        return redirect("/")

    do_logout()

    return redirect("/login")


@app.route("/profilephoto/<int:user_id>", methods=["GET", "POST"])
def submit_a_photo(user_id):
    """Shows the submitphoto page.
        - Updates database with photo url.
        - Updates AWS bucket with photo file.
        - In AWS and database, photo file name is given a UUID.
        - Redirects to user detail page.
    """
    if not g.user:
        flash("Access unauthorized", 'danger')
        return redirect("/")

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
    """Currently shows photo of user visited
        - TODO: Create a more complete details page for the user.
    """
    if not g.user:
        flash("Access unauthorized", 'danger')
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template("/users/detail.html", user=user)


@app.get('/user/<int:user_id>/friends')
def user_friends(user_id):
    """Shows a user's friends list.
        - This is where two users have liked each other.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    friends = [friend for friend in user.liking if user in friend.liking]

    return render_template("friends.html", friends=friends)


@app.get('/pending/<int:liked_user_id>')
def likes(liked_user_id):
    """This updates the likes table in database
        - Redirects home.
    """

    liked_user = User.query.get_or_404(liked_user_id)
    g.user.liking.append(liked_user)
    db.session.commit()

    return redirect("/")


@app.get('/disliking/<int:disliked_user_id>')
def dislikes(disliked_user_id):
    """This updates the dislikes table in database.
        - Redirects home.

    """

    disliked_user = User.query.get_or_404(disliked_user_id)
    g.user.disliking.append(disliked_user)
    db.session.commit()

    return redirect("/")
