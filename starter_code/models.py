from app import app
from app import db
from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy(app)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(500), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
            return f'<Venue name={self.name}, city={self.city}, state={self.state}, address={self.address}>'

   

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (done)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show', backref='Artists', lazy=True)

    def __repr__(self):
            return f'<Artist name={self.name}, city={self.city}, state={self.state}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (done)

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime)

  def __repr__(self):
            return f'<Show artist_id={self.artist_id}, venue_id={self.venue_id}, start_time={self.start_time}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.(done)