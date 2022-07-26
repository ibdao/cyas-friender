from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
import boto3, botocore
import os
from botocore.exceptions import ClientError

from forms import UploadForm

app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
BUCKET = "friender-bucket-r26-jason"

s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)

#debug = DebugToolbarExtension(app)
RESPONSES_KEY = "responses"


@app.get("/")
def generate_landing():
    """Generate app landing page"""

    return render_template(
        "base.html",
    )


@app.post("/")
def upload_file():
    if "user_file" not in request.files:
        return "No user_file key in request.files"
    file = request.files["user_file"]
    if file.filename == "":
        return "Please select a file"
    if file:
        file.filename = secure_filename(file.filename)
        output = send_to_s3(file, app.config["S3_BUCKET"])
        return str(output)
    else:
        return redirect("/")
