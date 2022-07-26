from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#debug = DebugToolbarExtension(app)
RESPONSES_KEY = "responses"

@app.get("/")
def generate_landing():
    """Generate app landing page"""

    return render_template (
        "base.html",
        )

@app.post("/")
def handle_get_request_and_render_form():
    """Upload to aws"""
    def upload(local_file, bucket, s3_file):
        s3 = boto3.client(
            "s3",
            aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_KEY
        )


    return redirect (
        "/"
    )
