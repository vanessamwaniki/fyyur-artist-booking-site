#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
import sys
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.(done)
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
migrate = Migrate(compare_type=True)

# TODO: connect to a local postgresql database (done)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import Artist, Venue, Show

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#



def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date=value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data = [] 
  locations = Venue.query.distinct(Venue.city, Venue.state).all() #query distinct locations
  location_details = {}
  for location in locations: 
    location_details = {
      'city' : location.city ,
      'state' : location.state ,
      'venues' : []
    }
    venues = Venue.query.filter_by(city=location.city, state=location.state).all() #query venues under the distict locations
    venue_details = []
    for venue in venues:
      venue_details.append ({
        'id' : venue.id,
        'name' : venue.name,
        'num_upcoming_shows' : db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).count()
      })
      location_details["venues"] = venue_details
      data.append(location_details)        

  # TODO: replace with real venues data. (done)
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. (done)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.(done)
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={}
  search_term = request.form.get('search_term', '')
  search_results = Venue.query.filter(Venue.name.match(f'%{search_term}%')).all()
  result_data=[]  
  result_data = [
    {
        "id": search_result.id,
        "name": search_result.name,
        "num_upcoming_shows": db.session.query(Show).join(Venue).filter(Show.venue_id == search_result.id).filter(Show.start_time > datetime.now()).count()
    }
      for search_result in search_results
  ]
  response = {
    'count': len(search_results), 
    'data': result_data
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


# shows the venue page with the given venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  # TODO: replace with real venue data from the venues table, using venue_id (done)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(', '),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "past_shows_count": [0],
    "upcoming_shows": [],
    "upcoming_shows_count": [0]
  }

  # join show and venue to query artist playing at a particular venue in particular show
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  upcoming_show = []
  past_show = []
  for show in upcoming_shows:
    upcoming_show_data = {
      "artist_id": show.artist_id ,
      "artist_name": show.Artists.name,
      "artist_image_link": show.Artists.image_link,
      "start_time": show.start_time
    }
    upcoming_show.append(upcoming_show_data)
    data["upcoming_shows"] = upcoming_show
    data["upcoming_shows_count"] = len(upcoming_show)
      
   
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  past_show = []
  for show in past_shows:
    past_show_data = {
      "artist_id": show.artist_id ,
      "artist_name": show.Artists.name,
      "artist_image_link": show.Artists.image_link,
      "start_time": show.start_time
    }
    past_show.append(past_show_data)
    data["past_shows"] = past_show
    data["past_shows_count"] = len(past_show)


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead (done)
  # TODO: modify data to be the data object returned from db insertion (done)
  
  form = VenueForm(request.form)
  try:
    venue_name = form.name.data
    check_registered = db.session.query(Venue.id).filter_by(name=venue_name).first() #check if venue already exists
    if check_registered:
      flash('Venue ' + venue_name + ' already exists!')
      return redirect(url_for(' create_venue_form'))
    else:
      add_venue = Venue(
        name = venue_name,
        city =form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=', '.join(form.genres.data),
        website_link=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(add_venue)
      db.session.commit() 
      # on successful db insert, flash success
      flash('Venue ' + venue_name + ' was successfully listed!')
      return redirect(url_for('show_venue', venue_id=add_venue.id))

  except:    
    # TODO: on unsuccessful db insert, flash an error instead.(done)
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + venue_name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
        db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using (done)
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.filter_by(id=venue_id).first()
  venue_name = venue.name
  try:
      venue.delete()
      db.session.commit()
      flash('Venue ' + venue_name + ' was successfully deleted!')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Venue ' + venue_name + ' could not be deleted!')
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database(done)
  data = []
  artists = Artist.query.all()
  artist_details = {}
  for artist in artists: 
    artist_details = {
      'id' : artist.id ,
      'name' : artist.name
    }
    data.append(artist_details)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(done)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={}
  search_term = request.form.get('search_term', '')
  search_results = Artist.query.filter(Artist.name.match(f'%{search_term}%')).all()
  result_data=[]  
  result_data = [
    {
        "id": search_result.id,
        "name": search_result.name,
        "num_upcoming_shows": db.session.query(Show).join(Artist).filter(Show.artist_id == search_result.id).filter(Show.start_time > datetime.now()).count()
    }
      for search_result in search_results
  ]
  
  response = {
    'count': len(search_results), 
    'data': result_data
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  # shows the artist page with the given artist_id (done)
  # TODO: replace with real artist data from the artist table, using artist_id (done)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(', '),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows" : [],
    "upcoming_shows_count": [0],
    "past_shows" : [],
    "past_shows_count" : [0]
  }

  # join show and artist to query the venues the artist is playing for a particular show
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_show = []
  past_show = []
  for show in upcoming_shows:
    upcoming_show_data = {
      "venue_id": show.venue_id ,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    }
    upcoming_show.append(upcoming_show_data)
    data["upcoming_shows"] = upcoming_show
    data["upcoming_shows_count"] = len(upcoming_show)
      
   
  past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  past_show = []
  for show in past_shows:
    past_show_data = {
      "venue_id": show.venue_id ,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time
    }
    past_show.append(past_show_data)
    data["past_shows"] = past_show
    data["past_shows_count"] = len(past_show)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edit_artist = Artist.query.filter_by(id=artist_id).first()
  artist={
    "id": edit_artist.id,
    "name": edit_artist.name,
    "genres": edit_artist.genres,
    "city": edit_artist.city,
    "state": edit_artist.state,
    "phone": edit_artist.phone,
    "website": edit_artist.website_link,
    "facebook_link": edit_artist.facebook_link,
    "seeking_venue": edit_artist.seeking_venue,
    "seeking_description": edit_artist.seeking_description,
    "image_link": edit_artist.image_link
  }
  form = ArtistForm(fromdata=None, data=artist) 
  
  # TODO: populate form with fields from artist with ID <artist_id> (done)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing (done)
  # artist record with ID <artist_id> using the new attributes
  edited_artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(request.form)
  artist_name = form.name.data
  try:
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(edited_artist)
    db.session.commit() 
    # on successful db edit, flash success
    flash('Artist ' + artist_name + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:    
    flash('Artist ' + artist_name + ' could not be updated.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  edit_venue = Venue.query.filter_by(id=venue_id).first()
  venue={
    "id": edit_venue.id,
    "name": edit_venue.name,
    "genres": edit_venue.genres,
    "address" : edit_venue.address,
    "city": edit_venue.city,
    "state": edit_venue.state,
    "phone": edit_venue.phone,
    "website": edit_venue.website_link,
    "facebook_link": edit_venue.facebook_link,
    "seeking_talent": edit_venue.seeking_talent,
    "seeking_description": edit_venue.seeking_description,
    "image_link": edit_venue.image_link
  }
  form = VenueForm(fromdata=None, data=venue) 
  
  # TODO: populate form with values from venue with ID <venue_id> (done)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing (done)
  # venue record with ID <venue_id> using the new attributes
  edited_venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm(request.form)
  venue_name = form.name.data
  try:
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(edited_venue)
    db.session.commit() 
    # on successful db edit, flash success
    flash('Venue ' + venue_name + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

  except:    
    flash('Venue ' + venue_name + ' could not be updated.')
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead (done)
  # TODO: modify data to be the data object returned from db insertion (done)
  form = ArtistForm(request.form)
  
  try:
    artist_name = form.name.data
    check_registered = db.session.query(Artist.id).filter_by(name=artist_name).first()
    if check_registered:
      flash('Artist ' + artist_name + ' already exists!')
      return redirect(url_for('create_artist_form'))
    else:
      add_artist = Artist(
        name = artist_name,
        city =form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=', '.join(form.genres.data),
        website_link=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(add_artist)
      db.session.commit() 
      # on successful db insert, flash success
      flash('Artist ' + artist_name + ' was successfully listed!')
      return redirect(url_for('show_artist', artist_id=add_artist.id))

  except:    
    # TODO: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Artist ' + artist_name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
        db.session.close()
  return render_template('pages/home.html')
 
  # return render_template('forms/new_artist.html', form=form)
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
#   # displays list of shows at /shows
#   # TODO: replace with real venues data.
  data = []
  shows = Show.query.order_by(Show.start_time.desc()).all()
  show_details = {}
  for show in shows: 
    show_details = {
      'venue_id' : show.venue_id ,
      'venue_name': show.venue.name ,
      'venue_image_link' : show.venue.image_link,
      'artist_id' : show.artist_id ,
      'artist_name': show.Artists.name ,
      'artist_image_link' : show.Artists.image_link,
      'start_time' : show.start_time
    } 
    data.append(show_details)
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form (done)
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
 
  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    check_artist_exists = db.session.query(Artist.id).filter_by(id=artist_id).first() #check if artist and venue exist before creating show
    check_venue_exists = db.session.query(Venue.id).filter_by(id=venue_id).first()
    if not check_artist_exists:
      flash('Artist ' + artist_id + ' doesnt exist!')
    elif not check_venue_exists:
      flash('Venue ' + venue_id + ' doesnt exist!') 
      return redirect(url_for('create_show'))
    else:
      add_show = Show(
        artist_id = artist_id,
        venue_id = venue_id,
        start_time = start_time
      )
      db.session.add(add_show)
      db.session.commit() 
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      return redirect(url_for('index'))

  except:    
    # TODO: on unsuccessful db insert, flash an error instead. (done)
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
        db.session.close()
  return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
