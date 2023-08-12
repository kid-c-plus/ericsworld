"""
Python SQLAlchemy model file defining GIF files and full text
    search terms.
"""
from sqlalchemy.sql import func

from app import flaskapp, db, appconfig, constants

# association table for tying tokenized search terms to the hashed
# GIFs matching those terms, including the weight of those 
# matches (number of times this term has referred to this GIF)

class SearchAssociation(db.Model):
    """
    Definition of many-to-many relationship between terms and GIFs.
        Necessary to include the extra "weight" field given to
        the association
    """
    term_value = db.Column(
        db.ForeignKey("term.value"),
        primary_key=True
    )
    gif_sha = db.Column(
        db.ForeignKey("gif.sha"),
        primary_key=True
    )
    weight = db.Column(db.Integer, default=1)

    term = db.relationship("Term", back_populates="gifs")
    gif = db.relationship("Gif", back_populates="terms")

class Term(db.Model):
    """
    Definition of tokenized search term data model.
    """
    value = db.Column(db.String(32), unique=True, primary_key=True)
    gifs = db.relationship(
        "SearchAssociation",
        back_populates="term"
    )

class Gif(db.Model):
    """
    Definition of GIF item, stored locally with name given by SHA.
    """
    sha = db.Column(db.String(64), unique=True, primary_key=True)
    terms = db.relationship(
        "SearchAssociation",
        back_populates="gif"
    )

