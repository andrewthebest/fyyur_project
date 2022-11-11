from flask_sqlalchemy import SQLAlchemy
from flask import Flask
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column('start_time', db.DateTime, nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(250), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000), nullable=True)
    shows = db.relationship('Show', backref='Venue', lazy=True, cascade='all, delete-orphan')

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  genres = db.Column(db.String(250), nullable=False)
  image_link = db.Column(db.String(500), nullable=False)
  facebook_link = db.Column(db.String(120), nullable=True)
  website_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(1000), nullable=True)
  shows = db.relationship('Show', backref='Artist', lazy=True)

db.create_all()
  # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.