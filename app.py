import os
import time

import firebase_admin
import googlemaps
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, request, jsonify
from googlemaps.places import places_nearby

app = Flask(__name__)


@app.route('/api/restaurants')
def get_restaurants():
    # round latitude and longitude to two decimal places
    latitude = int(float(request.args.get('latitude')) * 100) / 100
    longitude = int(float(request.args.get('longitude')) * 100) / 100
    # create location tuple
    location = (latitude, longitude)
    # set radius to default value if not valid
    radius = int(request.args.get('radius'))
    radius = radius if radius in VALID_RADII else DEFAULT_RADIUS

    # create key from latitude and longitude
    x = int((90 - float(latitude)) * 100) * 100000
    y = int((180 + float(longitude)) * 100)
    key = str(x + y)

    # query database
    results = ref.child(key).get()
    now = time.time()
    if results and (now - (results['timestamp'] / 1000)) < SECONDS_IN_WEEK:
        print('returning database results')

        restaurants = results['restaurants']
    else:
        print('querying places api for results')

        # query places api
        response = places_nearby(client=google_maps, type='restaurant', location=location, radius=radius, open_now=True)
        restaurants = response['results']

        # request results from next pages
        if 'next_page_token' in response:
            next_page_token = response['next_page_token']
            restaurants.extend(get_next_page(page_token=next_page_token))

        # save restaurants in database
        ref.child(key).set({'location': location, 'restaurants': restaurants, 'timestamp': {'.sv': 'timestamp'}})

    # return restaurants
    return jsonify({'restaurants': restaurants})


def get_next_page(page_token):
    # must wait two seconds before page token becomes valid
    time.sleep(2)

    # query places api
    response = places_nearby(client=google_maps, page_token=page_token)
    restaurants = response['results']

    # request results from next pages
    if 'next_page_token' in response:
        next_page_token = response['next_page_token']
        restaurants.extend(get_next_page(page_token=next_page_token))

    return restaurants


SECONDS_IN_WEEK = 604800

VALID_RADII = [1000, 2000, 5000, 10000, 20000]
DEFAULT_RADIUS = 5000

if 'GOOGLE_MAPS_API_KEY' in os.environ:
    google_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])
else:
    raise ValueError('Must provide GOOGLE_MAPS_API_KEY as an environment variable')

if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    # create database credentials
    cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    # initialize firebase app
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://eatee-api.firebaseio.com'
    })

    # create reference to database collection
    ref = db.reference('restaurants')
else:
    raise ValueError('Must provide GOOGLE_APPLICATION_CREDENTIALS as an environment variable')

if __name__ == '__main__':
    app.run()
