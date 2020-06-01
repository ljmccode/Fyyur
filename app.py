#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from babel import dates
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist, Show
import sys
import babel

# #----------------------------------------------------------------------------#
# # App Config.
# #----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    location = ""
    data = []

    venues = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
    for venue in venues:
        num_upcoming_shows = len(venue.shows.filter(Show.start_time > datetime.now()).all())

        # If venue location matches, append
        if location == venue.city + venue.state:
            data[len(data) - 1]["venues"].append({
                "id": venue.id,
                "name":  venue.name,
                "num_upcoming_shows": num_upcoming_shows
            })
        # else append data with new city, state
        else:
            location = venue.city + venue.state
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name":  venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                }]
               
            })
    return render_template('pages/venues.html', areas=data)
   

@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    data = venue.dictionary()

    past = list(filter(lambda x: x.start_time < datetime.now(), venue.shows))
    upcoming = list(filter(lambda x: x.start_time >= datetime.now(), venue.shows))
    past_shows = list(map(lambda x: x.show_artist(), past))
    upcoming_shows= list(map(lambda x: x.show_artist(), upcoming))

    # add upcoming/past show info to data dictionary
    data["past_shows"]= past_shows
    data["upcoming_shows"]= upcoming_shows
    data["num_past_shows"]= len(past_shows)
    data["num_upcoming_shows"]= len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form=VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error=False
    data=request.form

    try:
        new_venue=Venue(
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('state'),
            address=data.get('address'),
            phone=data.get('phone'),
            image_link=data.get('image_link'),
            facebook_link=data.get('facebook_link'),
            genres=data.getlist('genres'),
            website=data.get('website'),
            seeking_talent=bool(data.get('seeking_talent')),
            seeking_description=data.get('seeking_description')
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + data['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error=True
        flash('An error occurred. Venue ' +
              data['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    artists = Artist.query.all()
    
    data = []
    
    for artist in artists:
        data.append(artist)

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response={
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    data = artist.dictionary()

    past = list(filter(lambda x: x.start_time < datetime.now(), artist.shows))
    upcoming = list(filter(lambda x: x.start_time >= datetime.now(), artist.shows))
    past_shows = list(map(lambda x: x.show_venue(), past))
    upcoming_shows= list(map(lambda x: x.show_venue(), upcoming))

    # add upcoming/past show info to data dictionary
    data["past_shows"]= past_shows
    data["upcoming_shows"]= upcoming_shows
    data["num_past_shows"]= len(past_shows)
    data["num_upcoming_shows"]= len(upcoming_shows)
   
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form=ArtistForm()
    artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form=VenueForm()
    venue={
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form=ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error=False
    data=request.form

    try:
        new_artist=Artist(
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('state'),
            phone=data.get('phone'),
            image_link=data.get('image_link'),
            facebook_link=data.get('facebook_link'),
            genres=data.getlist('genres'),
            website=data.get('website'),
            seeking_venue=bool(data.get('seeking_venue')),
            seeking_description=data.get('seeking_description')
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + data['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error=True
        # on unsuccessful db insert, flash an error
        flash('An error occurred. Artist' +
              data['name'] + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    shows = Show.query.all()
    data = list(map(Show.show_dict, shows))
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form=ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error=False
    data=request.form

    try:
        new_show=Show(
            artist_id=data.get('artist_id'),
            venue_id=data.get('venue_id'),
            start_time=data.get('start_time')
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash("New show was successfully listed!")
    except():
        db.session.rollback()
        error=True
        flash('An error occurred. New show could not be listed.')
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler=FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
