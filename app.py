#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy import desc, or_, and_
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db, app
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # Test if value is String or Date to avoid error
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
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
  # Challenge - Show Recent Listed Artists and Recently Listed Venues on the homepage
  venues = Venue.query.order_by(desc(Venue.id)).limit(10).all()
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  return render_template('pages/home.html', recent_artists=artists, recent_venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  # List of venues to be render
  venues_list = []
  # Get distincts cities and state from all venues
  cities_and_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  # Get actual datetime
  date_of_today = datetime.now()
  # print(cities_and_states)

  if cities_and_states:
    for city_and_state in cities_and_states:
      city = city_and_state[0]
      state = city_and_state[1]
      # Instance of venue's data to render
      city_and_state_data = {"city": city, "state": state, "venues": []}
      # Getting all venues from specific city and state
      venues = Venue.query.filter_by(city=city, state=state).all()

      for venue in venues:
          # Upcoming shows from actual venue
          upcoming_shows = (
              Show.query.filter_by(venue_id=venue.id)
              .filter(Show.start_time > date_of_today)
              .all()
          )
          # Adding actual venue's data
          venue_data = {
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows),
          }

          city_and_state_data["venues"].append(venue_data)

      # Adding venues from specific city and state to final list of venues
      venues_list.append(city_and_state_data)
  
  return render_template('pages/venues.html', areas=venues_list)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  form_data = request.form.get('search_term')
  search_list = form_data.split(',')

  # Challenge - Implement Search Venues by City and State
  if len(search_list) != 1:
    query = Venue.query\
    .with_entities(Venue.id, Venue.name)\
    .group_by(Venue.id, Venue.name)\
    .filter(or_(Venue.name.ilike('%'+ search_list[0] +'%'),
                and_(Venue.city.ilike('%'+ search_list[0].strip() +'%'),
                Venue.state.ilike('%'+ search_list[1].strip() +'%'))
              ))
  else:
    query = Venue.query\
    .with_entities(Venue.id, Venue.name)\
    .group_by(Venue.id, Venue.name)\
    .filter(Venue.name.ilike('%'+ search_list[0] +'%'))

  datas = query.all()
  venues = []
  # Set the counter for all the instances returned
  counter = 0
  for data in datas:
    counter+=1
    venues.append({
      "id": data[0],
      "name": data[1],
    })

  response={
    "count": counter,
    "data": venues,
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # If no result, execution is stopped with 404 error
  venue = Venue.query.get_or_404(venue_id)
  shows_query = Show.query.join(Venue, Venue.id == Show.venue_id)\
    .with_entities(
      Show.venue_id, Show.artist_id, Show.start_time, Venue.name.label('venue_name')
    ).filter(Show.venue_id == venue_id)
  
  now = datetime.now()
  past_shows = shows_query.filter(Show.start_time < now)
  upcoming_shows = shows_query.filter(Show.start_time > now)
  past_shows_list = []
  upcoming_shows_list = []

  # List of past shows for current venue
  if past_shows:
    for show in past_shows:
      artist = Artist.query.get(show.artist_id)
      past_shows_list.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      })
  
  # List of upcoming shows for current venue
  if upcoming_shows:
    for show in upcoming_shows:
      artist = Artist.query.get(show.artist_id)
      upcoming_shows_list.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      })
      
  # Convertion of genres from string to list to display on user's screen
  string_genres = venue.genres
  stringToList = string_genres.split(',')
      
  datas = ({
    "id": venue.id,
    "name": venue.name,
    "genres": stringToList,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(upcoming_shows_list),
  })

  return render_template('pages/show_venue.html', venue=datas)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  # renders form. do not touch.
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error = False
  try:
    # Trying to commit new Venue on db
    # Parse genres list as string to facilitate saving in database
    list_genres = request.form.getlist('genres')
    listToString = ','.join(list_genres)
    venue = Venue()

    # Set attributes for new venue to add in db
    setattr(venue, 'name', request.form.get('name'))
    setattr(venue, 'city', request.form.get('city'))
    setattr(venue, 'state', request.form.get('state'))
    setattr(venue, 'address', request.form.get('address'))
    setattr(venue, 'phone', request.form.get('phone'))
    setattr(venue, 'genres', listToString)
    setattr(venue, 'image_link', request.form.get('image_link'))
    setattr(venue, 'facebook_link', request.form.get('facebook_link'))
    setattr(venue, 'website_link', request.form.get('website_link'))
    setattr(venue, 'seeking_talent', True if request.form.get('seeking_talent') in ('y', True, 't', 'True') else False)
    setattr(venue, 'seeking_description', request.form.get('seeking_description'))

    db.session.add(venue)
    db.session.commit()
  except:
    # If we get an exception, we rollback all updates made on db
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # Closing session at the end
    db.session.close()

  # If there is an error, it's displayed an error message, otherwise
  # A success message is displayed
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.', 'danger')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!', 'success')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')
  return redirect(url_for('venues'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  error = False
  venue_del = {}
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    show = Show.query.filter_by(venue_id=venue_id).first()
    venue_del['name'] = venue.name
    db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  print(venue_del)
  if error:
    flash('An error occurred. Venue '+ venue_del['name'] +' could not be deleted.', 'danger')
  else:
    # on successful db insert, flash success
    flash('Venue '+ venue_del['name'] +' was successfully deleted!', 'success')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  form_data = request.form.get('search_term')
  search_list = form_data.split(',')
  
  # Challenge - Implement Search Artists by City and State
  if len(search_list) != 1:
    query = Artist.query\
    .with_entities(db.func.count(Artist.id), Artist.id, Artist.name)\
    .group_by(Artist.name, Artist.id)\
    .filter(or_(Artist.name.ilike('%'+ search_list[0] +'%'),
                and_(Artist.city.ilike('%'+ search_list[0].strip() +'%'),
                Artist.state.ilike('%'+ search_list[1].strip() +'%'))
              ))
  else:
    query = Artist.query\
    .with_entities(Artist.id, Artist.name)\
    .group_by(Artist.name, Artist.id)\
    .filter(Artist.name.ilike('%'+ search_list[0] +'%'))
  
  datas = query.all()
  artists = []
  # Set the counter for all the instances returned
  counter = 0
  for data in datas:
    counter+=1
    artists.append({
      "id": data[0],
      "name": data[1],
    })

  response={
    "count": counter,
    "data": artists,
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  # If no result, execution is stopped with 404 error
  artist = Artist.query.get_or_404(artist_id)

  shows_query = Show.query.join(Artist, Artist.id == Show.artist_id)\
    .with_entities(
      Show.venue_id, Show.artist_id, Show.start_time, Artist.name.label('artist_name')
    ).filter(Show.artist_id == artist_id)
  
  now = datetime.now()
  past_shows = shows_query.filter(Show.start_time < now)
  upcoming_shows = shows_query.filter(Show.start_time > now)
  past_shows_list = []
  upcoming_shows_list = []
  
  # List of past shows for current artist
  if past_shows:
      for show in past_shows:
        venue = Venue.query.get(show.venue_id)
        past_shows_list.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_time
        })
  
  # List of upcoming shows for current artist
  if upcoming_shows:
    for show in upcoming_shows:
      venue = Venue.query.get(show.venue_id)
      upcoming_shows_list.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time
      })

  # Convertion of genres from string to list to display in form
  string_genres = artist.genres
  stringToList = string_genres.split(',')
      
  datas = ({
    "id": artist.id,
    "name": artist.name,
    "genres": stringToList,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": len(past_shows_list),
    "upcoming_shows_count": len(upcoming_shows_list),
  })

  return render_template('pages/show_artist.html', artist=datas)
 

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # If no result, execution is stopped with 404 error
  artist = Artist.query.get_or_404(artist_id)

  # Convertion of genres from string to list to display in form
  string_genres = artist.genres
  stringToList = string_genres.split(',')

  form = ArtistForm(
    id = artist.id,
    name = artist.name,
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    genres = stringToList,
    image_link = artist.image_link,
    facebook_link = artist.facebook_link,
    website_link = artist.website_link,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description
  )

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  try:
    # Trying to update data of venue_id and commit updated values on db
    # If no result, execution is stopped with 404 error
    artist = Artist.query.get_or_404(artist_id)

    # Trying to Update an Artist on db
    list = request.form.getlist('genres')
    listToString = ','.join(list)

    # Update attributes for the editing artist to update in db
    setattr(artist, 'name', request.form.get('name'))
    setattr(artist, 'city', request.form.get('city'))
    setattr(artist, 'state', request.form.get('state'))
    setattr(artist, 'phone', request.form.get('phone'))
    setattr(artist, 'genres', listToString)
    setattr(artist, 'image_link', request.form.get('image_link'))
    setattr(artist, 'facebook_link', request.form.get('facebook_link'))
    setattr(artist, 'website_link', request.form.get('website_link'))
    setattr(artist, 'seeking_talent', True if request.form.get('seeking_talent') in ('y', True, 't', 'True') else False)
    setattr(artist, 'seeking_description', request.form.get('seeking_description'))
    
    db.session.commit()
  except:
    # If we get an exception, we rollback all updates made on db
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # Closing session at the end
    db.session.close()

  # If there is an error, it's displayed an error message, otherwise
  # A success message is displayed
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.', 'danger')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!', 'success')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # If no result, execution is stopped with 404 error
  venue = Venue.query.get_or_404(venue_id)

  # Convertion of genres from string to list to display in form
  string_genres = venue.genres
  stringToList = string_genres.split(',')

  form = VenueForm(
    id = venue.id,
    name = venue.name,
    city = venue.city,
    state = venue.state,
    address = venue.address,
    phone = venue.phone,
    genres = stringToList,
    image_link = venue.image_link,
    facebook_link = venue.facebook_link,
    website_link = venue.website_link,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description
  )

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  try:
    # Trying to update data of venue_id and commit updated values on db
    # If no result, execution is stopped with 404 error
    venue = Venue.query.get_or_404(venue_id)

    # Parse genres list as string to facilitate saving in database
    list_genres = request.form.getlist('genres')
    listToString = ','.join(list_genres)

    # Update attributes for the editing venue to update in db
    setattr(venue, 'name', request.form.get('name'))
    setattr(venue, 'city', request.form.get('city'))
    setattr(venue, 'state', request.form.get('state'))
    setattr(venue, 'address', request.form.get('address'))
    setattr(venue, 'phone', request.form.get('phone'))
    setattr(venue, 'genres', listToString)
    setattr(venue, 'image_link', request.form.get('image_link'))
    setattr(venue, 'facebook_link', request.form.get('facebook_link'))
    setattr(venue, 'website_link', request.form.get('website_link'))
    setattr(venue, 'seeking_talent', True if request.form.get('seeking_talent') in ('y', True, 't', 'True') else False)
    setattr(venue, 'seeking_description', request.form.get('seeking_description'))

    db.session.commit()
  except:
    # If we get an exception, we rollback all updates made on db
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # Closing session at the end
    db.session.close()

  # If there is an error, it's displayed an error message, otherwise
  # A success message is displayed
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.', 'danger')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!', 'success')

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # renders form. do not touch.
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try:
    # Trying to commit new Artist on db
    list = request.form.getlist('genres')
    listToString = ','.join(list)

    # Set attributes for new artist to add in db
    artist = Artist()
    setattr(artist, 'name', request.form.get('name'))
    setattr(artist, 'city', request.form.get('city'))
    setattr(artist, 'state', request.form.get('state'))
    setattr(artist, 'phone', request.form.get('phone'))
    setattr(artist, 'genres', listToString)
    setattr(artist, 'image_link', request.form.get('image_link'))
    setattr(artist, 'facebook_link', request.form.get('facebook_link'))
    setattr(artist, 'website_link', request.form.get('website_link'))
    setattr(artist, 'seeking_talent', True if request.form.get('seeking_talent') in ('y', True, 't', 'True') else False)
    setattr(artist, 'seeking_description', request.form.get('seeking_description'))
    
    db.session.add(artist)
    db.session.commit()
  except:
    # If we get an exception, we rollback all updates made on db
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # Closing session at the end
    db.session.close()

  # If there is an error, it's displayed an error message, otherwise
  # A success message is displayed
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be created.', 'danger')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully created!', 'success')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  datas = []
  shows_query = Show.query.join(Venue, Venue.id == Show.venue_id)\
    .join(Artist, Artist.id == Show.artist_id)\
    .with_entities(
      Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time
    )
    
  for show in shows_query:
    datas.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=datas)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  try:
    # Trying to commit new Show on db
    # artist = Artist.query.get(request.form.get('artist_id'))
    # venue = Venue.query.get(request.form.get('venue_id'))
    artist = request.form.get('artist_id')
    venue = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    show = Show(venue_id=venue, artist_id=artist, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    # If we get an exception, we rollback all updates made on db
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # Closing session at the end
    db.session.close()

  # If there is an error, it's displayed an error message, otherwise
  # A success message is displayed
  if error:
    flash('An error occurred. Show could not be listed.', 'danger')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!', 'success')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('shows'))

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
