from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
import boto3
import os
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from models import db, connect_db, User, Like, Dislike

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['S3_KEY'] = os.environ['S3_KEY']
app.config['S3_SECRET'] = os.environ['S3_SECRET']
app.config['S3_BUCKET'] = os.environ['S3_BUCKET']

s3 = boto3.client(
    "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)

connect_db(app)

#debug = DebugToolbarExtension(app)

@app.get("/")
def generate_landing():
    """Generate app landing page"""

    return render_template(
        "base.html",
    )


@app.post("/")
def upload_file():
    img = request.files['file']
    if img:
        filename = secure_filename(img.filename)
        s3.upload_fileobj(
            img,
            app.config["S3_BUCKET"],
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )

    return redirect("/")
