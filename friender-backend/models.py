from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Like (db.Model):
    __tablename__='likes'

    user_liking_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )

    user_being_liked_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )


class Dislike (db.Model):
    __tablename__='dislikes'

    user_not_liking_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )

    user_not_being_liked_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )


class User(db.Model):

    __tablename__='users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )


    location = db.Column(
        db.Text,
        nullable=False
    )

    friend_radius = db.Column(
        db.Integer,
        nullable=False
    )

    hobbies = db.Column(
        db.Text,
        nullable=False
    )

    interests = db.Column(
        db.Text,
        nullable=False
    )

    img_url = db.Column(
        db.Text,
        nullable=True
    )


    # like = db.relationship(
    #     "User",
    #     secondary="like",
    #     primaryjoin=(Like.user_being_liked_id == id),
    #     secondaryjoin=(Like.user_liking_id == id),
    #     backref="liking",
    # )

    # dislike = db.relationship(
    #     "User",
    #     secondary="dislike",
    #     primaryjoin=(Dislike.user_not_being_liked_id == id),
    #     secondaryjoin=(Dislike.user_not_liking_id == id),
    #     backref="disliking",
    # )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls,
               username,
               first_name,
               last_name,
               location,
               friend_radius,
               hobbies,
               interests,
               password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            location=location,
            friend_radius=friend_radius,
            hobbies=hobbies,
            interests=interests,
        )

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    #comparing two users to each other, self and other_user
    #checking to see if they are in each other's liked list
    def is_liking(self, other_user):
        found_user_list = [
            user for user in self.liking if user == other_user]
        return len(found_user_list) == 1

    def is_liked_by(self, other_user):
        found_user_list = [
            user for user in self.like if user == other_user]
        return len(found_user_list) == 1

    def is_disliking(self, other_user):
        found_user_list = [
            user for user in self.disliking if user == other_user]
        return len(found_user_list) == 1

    def is_disliked_by(self, other_user):
        found_user_list = [
            user for user in self.dislike if user == other_user]
        return len(found_user_list) == 1






def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
