"""
Python SQLAlchemy file defining User. This is also the UserMixin for
    the Flask-Login module.
"""
from datetime import datetime
from sqlalchemy.sql import func
from werkzeug.security import (generate_password_hash, 
    check_password_hash)
from flask_login import UserMixin
from typing import Union
import secrets

from app import flaskapp, appconfig, db, constants, loginmanager

block_association_table = db.Table(
    "block_association_table",
    db.Model.metadata,
    db.Column(
        "blocker_id", db.String(32), db.ForeignKey("user.user_id")),
    db.Column(
        "blocked_id", db.String(32), db.ForeignKey("user.user_id"))
)

class User(UserMixin, db.Model):
    """
    Definition of User data model.
    """
    __tablename__ = "user"

    user_id = db.Column(db.String(32), primary_key=True)
    # I need a secondary User ID just used to generate
    # login cookies, so that it can be changed when a user's
    # login session must be invalidated (e.g. they become banned)
    login_id = db.Column(db.String(32), unique=True)
    
    # refer to constants.py for list of account status integers
    status = db.Column(db.Integer, 
            default=constants.INVITED_USER, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    status_updated_time = db.Column(
        db.DateTime, default=datetime.utcnow
    )

    # Phone number includes + and 1 to 3-digit country code
    phone_number = db.Column(
        db.String(14), unique=True, nullable=False
    )
    password_hash = db.Column(db.String(77))
    two_factor_auth = db.Column(db.Boolean, default=True)

    # Email address to be used only for password reset, in order to 
    # maintain true 2-Factor Auth (phone AND email)
    recovery_email = db.Column(db.String(320))
    # random token to be included as a URL parameter in case of
    # password reset. Stored as hash, because for the duration of
    # its validity it's near as stron as a password
    password_reset_token_hash = db.Column(db.String(77))
    pr_token_generated_time = db.Column(
        db.DateTime, default=datetime.fromtimestamp(0)
    )

    username = db.Column(db.String(20))
    # Profile Pic URI from set of available images
    profile_uri = db.Column(db.UnicodeText)

    heartscore = db.Column(db.Integer, default=0)

    inviting_user_id = db.Column(db.String(32),
        db.ForeignKey("user.user_id"))
    inviting_user = db.relationship(
        "User", remote_side="User.user_id", backref="invited_users")
    
    blocked_users = db.relationship(
        "User",
        secondary=block_association_table,
        primaryjoin=block_association_table.c.blocker_id==user_id,
        secondaryjoin=block_association_table.c.blocked_id==user_id,
        lazy=True,
        backref="blocked_by_users"
    )

    wisps = db.relationship("Wisp", back_populates="user", lazy=True)
    songs = db.relationship("Song", back_populates="user", lazy=True)

    def update_status(self, new_status: int):
        """
        Update status to provided value and set status updated time.
        :param new_status: new account status, from values in
            constants.py
        """
        self.status = new_status
        self.status_updated_time = func.now()
    
    def set_password(self, password: str):
        """
        Set a new hashed password.
        :param password: new password to hash and store
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Check submitted password against hash.
        :param password: submitted password to check
        :return: true if valid
        """
        return check_password_hash(self.password_hash, password)

    def generate_password_reset_token(self) -> Union[str, None]:
        """
        Generate and return a new token, or return None if the
            last token was generated within the configured timeout.
        :return: token if generated, None otherwise
        """
        token_delta = datetime.utcnow() - self.pr_token_generated_time
        if token_delta > appconfig["RESET_PROCESS_TIMEOUT"]:
            # uuid4 is random, uuid1 is based on system time
            new_token = secrets.token_hex(32)
            self.password_reset_token_hash = generate_password_hash(
                new_token
            )
            self.pr_token_generated_time = datetime.utcnow()
            return new_token
        else:
            return None

    def check_password_reset_token(self, token: str) -> bool:
        """
        Check submitted reset token against stored hash and creation
            timestamp.
        :param token: reset token to hash and compare
        :return: true if token matches hash and is not expired
        """
        token_delta = datetime.utcnow() - self.pr_token_generated_time
        if token_delta < appconfig["RESET_TOKEN_LIFESPAN"]:
            return check_password_hash(
                self.password_reset_token_hash,
                token
            )
        else:
            return False
    
    def heart_wisp(self, wisp):
        """
        Helper method for Hearting the provided Wisp. Increments
            poster's HeartScore
        :param wisp: Wisp to Heart
        """
        if (wisp.user != self and wisp not in self.hearted_wisps
                and wisp.status == constants.LIVE_WISP):
            self.hearted_wisps.append(wisp)
            wisp.user.heartscore += 1

    def unheart_wisp(self, wisp):
        """
        Helper method for UnHearting the provided Wisp. Decrements 
            poster's HeartScore
        :param wisp: Wisp to UnHeart
        """
        if (wisp.user != self and wisp in self.hearted_wisps
                and wisp.status == constants.LIVE_WISP):
            self.hearted_wisps.remove(wisp)
            wisp.user.heartscore -= 1

    def heart_song(self, song):
        """
        Helper method for Hearting the provided Song. Can be
            an autoplay song.
        :param song: Song to Heart
        """
        if (song.user != self and song not in self.hearted_songs
                and song.status == constants.PLAYING_SONG):
            if song in self.broken_hearted_songs:
                self.unbrokenheart_song(song)
            self.hearted_songs.append(song)
            if song.user:
                song.user.heartscore += 1

    def unheart_song(self, song):
        """
        Helper method for UnHearting the provided Song. Can be an
            autplay song. Checks to see if skip threshold reached.
        :param song: Song to UnHeart
        """
        if (song.user != self and song in self.hearted_songs
                and song.status == constants.PLAYING_SONG):
            self.hearted_songs.remove(song)
            if song.user:
                song.user.heartscore -= 1
            if (len(song.broken_hearted_users) - 
                    len(song.hearted_users) >=
                    appconfig["BROKENHEARTS_TO_SKIP"]):
                flaskapp.logger.error("Skipping song...")
                radiocontroller.skip_song()
    
    def brokenheart_song(self, song):
        """
        Helper method for BrokenHearting the provided Song. Can be
            an autoplay song.
        :param song: Song to BrokenHeart
        """
        if (song.user != self and song not in self.broken_hearted_songs
                and song.status == constants.PLAYING_SONG):
            if song in self.hearted_songs:
                self.unheart_song(song)
            self.broken_hearted_songs.append(song)
            if song.user:
                song.user.heartscore -= 1

    def unbrokenheart_song(self, song):
        """
        Helper method for UnBrokenHearting the provided Song. Can be an
            autplay song. Checks to see if skip threshold reached.
        :param song: Song to UnBrokenHeart
        """
        if (song.user != self and song in self.broken_hearted_songs
                and song.status == constants.PLAYING_SONG):
            self.broken_hearted_songs.remove(song)
            if song.user:
                song.user.heartscore += 1
    
    def __repr__(self):
        return "\n".join(
                f"{k}:\t{v}" for k, v in self.__dict__.items()
            )
    
    # Flask-Login settings
    def is_authenticated(self) -> bool:
        """
        Check if this user is an active account with authentication
        return: True if account status is ACTIVE_USER
        """
        return self.status == constants.ACTIVE_USER
    
    is_active = is_authenticated

    is_anonymous = False

    def get_id(self) -> str:
        """
        Return the login ID of this account.
        :return: login id field
        """
        return self.login_id

@loginmanager.user_loader
def load_user(login_id: str) -> User:
    return db.session.execute(db.select(User).filter_by(
        login_id=login_id
    )).scalar()

