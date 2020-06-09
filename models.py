from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default= False)
    seeking_description = db.Column(db.String(500), default= '')
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def __repr__(self):
        return f'<Venue Id: {self.id} Name: {self.name}>'

    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default= '')
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')

    def __repr__(self):
        return f'<Artist Id: {self.id} Name: {self.name}>'

    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
   
    def show_info(self):
        return {
            "id": self.id,
            "artist_id": self.artist_id,
            "venue_id": self.venue_id,
            "start_time": str(self.start_time),
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()