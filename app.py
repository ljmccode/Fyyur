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
from models import db, Venue, Artist, Show
import sys
import babel

# #----------------------------------------------------------------------------#
# # App Config.
# #----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

# Show Venue List
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

# Create Venue Page
@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form=VenueForm()
    return render_template('forms/new_venue.html', form=form)

# Create Venue
@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
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

# View Venue Page
@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    data = venue.dictionary()

    past = list(filter(lambda x: x.start_time < datetime.now(), venue.shows))
    upcoming = list(filter(lambda x: x.start_time >= datetime.now(), venue.shows))
    past_shows = list(map(lambda x: x.show_info(), past))
    upcoming_shows= list(map(lambda x: x.show_info(), upcoming))

    # add upcoming/past show info to data dictionary
    data["past_shows"]= past_shows
    data["upcoming_shows"]= upcoming_shows
    data["num_past_shows"]= len(past_shows)
    data["num_upcoming_shows"]= len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

# Search Venue
@ app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    results =  Venue.query.order_by(Venue.id).filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    
    response = {}
    response['count'] = len(results)
    response['data'] = results
   
    return render_template('pages/search_venues.html', results=response)

# Update Venue Form
@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form=VenueForm()
    venue = Venue.query.get(venue_id).dictionary()
  
    return render_template('forms/edit_venue.html', form=form, venue=venue)

# Update Venue
@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    data=request.form
    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

    try:
        venue.name=data.get('name'),
        venue.city=data.get('city'),
        venue.state=data.get('state'),
        venue.address=data.get('address'),
        venue.phone=data.get('phone'),
        venue.image_link=data.get('image_link'),
        venue.facebook_link=data.get('facebook_link'),
        venue.genres=data.getlist('genres'),
        venue.website=data.get('website'),
        
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + data['name'] + ' was successfully updated!')
    except():
        db.session.rollback()
        error=True
        # on unsuccessful db insert, flash an error
        flash('An error occurred. Venue' +
              data['name'] + ' could not be updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))

# Delete Venue
@ app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
    try:
        shows = Show.query.filter_by(venue_id=venue_id)
        for show in shows:
            show.delete()

        venue = Venue.query.get(venue_id)
        venue.delete()
        flash('Venue deleted!')
        return render_template('pages/home.html')
    except():
        error=True
        db.session.rollback()
        flash('An error occured. Venue could not be deleted')
    return None

#----------------------------------------------------------------------------#
#  Artists
#----------------------------------------------------------------------------#

# Show Artist List
@ app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    
    for artist in artists:
        data.append(artist)
    return render_template('pages/artists.html', artists=data)

# Create Artist Form
@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form=ArtistForm(meta={"csrf": False})
    return render_template('forms/new_artist.html', form=form)

#Create Artist
@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form=ArtistForm(meta={"csrf": False})

    if not form.validate_on_submit():
        errors = form.errors
        for error in errors.values():
            flash( error[0] )
        return redirect(url_for('create_artist_form'))
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

# View Artist Page
@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = artist.dictionary()

    # establish if show is past/upcoming
    past = list(filter(lambda x: x.start_time < datetime.now(), artist.shows))
    upcoming = list(filter(lambda x: x.start_time >= datetime.now(), artist.shows))
    past_shows = list(map(lambda x: x.show_info(), past))
    upcoming_shows= list(map(lambda x: x.show_info(), upcoming))

    # add upcoming/past show info to data dictionary
    data["past_shows"]= past_shows
    data["upcoming_shows"]= upcoming_shows
    data["num_past_shows"]= len(past_shows)
    data["num_upcoming_shows"]= len(upcoming_shows)
   
    return render_template('pages/show_artist.html', artist=data)

# Search Artist
@ app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    results =  Artist.query.order_by(Artist.id).filter(Artist.name.ilike('%{}%'.format(search_term))).all()

    response = {}
    response['count'] = len(results)
    response['data'] = results
   
    return render_template('pages/search_artists.html', results=response)

# Update Artist Form
@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form=ArtistForm()
    artist = Artist.query.get(artist_id).dictionary()

    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Update Artist
@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    data=request.form
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

    try:
        artist.name=data.get('name'),
        artist.city=data.get('city'),
        artist.state=data.get('state'),
        artist.phone=data.get('phone'),
        artist.image_link=data.get('image_link'),
        artist.facebook_link=data.get('facebook_link'),
        artist.genres=data.getlist('genres'),
        artist.website=data.get('website'),
        
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + data['name'] + ' was successfully updated!')
    except():
        db.session.rollback()
        error=True
        # on unsuccessful db insert, flash an error
        flash('An error occurred. Artist' +
              data['name'] + ' could not be updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))

#----------------------------------------------------------------------------#
#  Shows
#----------------------------------------------------------------------------#

# View Shows
@ app.route('/shows')
def shows():
    shows = Show.query.all()
    data = list(map(Show.show_info, shows))
    return render_template('pages/shows.html', shows=data)

#Create Show Form
@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form=ShowForm()
    return render_template('forms/new_show.html', form=form)

#Create Show
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

#----------------------------------------------------------------------------#
#  Error Handling
#----------------------------------------------------------------------------#

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
