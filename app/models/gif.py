"""
Python SQLAlchemy model file defining GIF files and full text
    search terms.
"""
from sqlalchemy.sql import func

from app import flaskapp, db, appconfig, constants

# association table for tying tokenized search words to the hashed
# GIFs matching those words, including the weight of those 
# matches (number of times this word has referred to this GIF)

word_gif_association_table = db.Table(
    "word_gif_associaton_table",
    db.Model.metadata,
    db.Column(
        "word_value", db.String(32),
        db.ForeignKey("word.value")
    ),
    db.Column(
        "gif_sha", db.String(64),
        db.ForeignKey("gif.sha")
    ),
    db.Column("weight"), db.Integer, default=1)
)

class Word(db.Model):
    """
    Definition of tokenized search word data model.
    """
    value = db.Column(db.String(32), unique=True, primary_key=True)
    gifs = db.relationship(
        "Gif",
        secondary=word_gif_association_table,
        lazy=True,
        back_populates="words"
    )

class Gif(db.Model):
    sha = db.Column(db.String(64), unique=True, primary_key=True)
    words = db.relationship(
        "Word",
        secondary=word_gif_association_table,
        lazy=True,
        back_populates="gifs"
    )

