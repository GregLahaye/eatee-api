import os
import time

import googlemaps
from flask import Flask, request, jsonify
from googlemaps.places import places_nearby

app = Flask(__name__)


@app.route('/api/restaurants')
def get_restaurants():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    location = (latitude, longitude)
    radius = request.args.get('radius')

    response = places_nearby(client=google_maps, type='restaurant', location=location, radius=radius, open_now=True)
    restaurants = response['results']
    if 'next_page_token' in response:
        next_page_token = response['next_page_token']
        restaurants.extend(get_next_page(page_token=next_page_token))

    return jsonify({'restaurants': restaurants})


def get_next_page(page_token):
    time.sleep(2)
    response = places_nearby(client=google_maps, page_token=page_token)
    restaurants = response['results']
    if 'next_page_token' in response:
        next_page_token = response['next_page_token']
        restaurants.extend(get_next_page(page_token=next_page_token))

    return restaurants


if 'GOOGLE_MAPS_API_KEY' in os.environ:
    google_maps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])
else:
    raise ValueError('Must provide GOOGLE_MAPS_API_KEY as an environment variable')

if __name__ == '__main__':
    app.run()
