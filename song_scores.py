import pandas as pd
import numpy as np
import requests
import config
BASE_URL = 'https://api.spotify.com/v1/'
FRIENDS = config.friends
AUTH_URL = 'https://accounts.spotify.com/api/token'
CLIENT_ID = config.id_
CLIENT_SECRET = config.secret

### TODO -- add type hints to functions


def main():
    access_token, headers = auth_stuff()

    playlist = get_all_playlist_ids(FRIENDS[2], headers)

    artist_ids = playlist_processor(playlist)

    return


def auth_stuff():
    
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    auth_response_data = auth_response.json()

    # save the access token
    access_token_ = auth_response_data['access_token']

    headers_ = {
        'Authorization': f'Bearer {access_token_}'#.format(token=access_token)
    }

    return access_token_, headers_  # does this need the access_token_ to be returned?

### Roadmap

# - with a user's id, get a list of their playlists
# - take a playlist from the preceding list (or an individual track?) and get the artist # of followers and popularity; the artist's top tracks; the track's popularity (do this for each track in the playlist)
#  - calculate indieness metric (maybe like 1/log(followers) * track popularity or something like that) for each track
#   - aggregate all indieness scores (some sort of average, maybe the median?)


def get_all_playlist_ids(user, headers_):
    # for now, user should be an element in the FRIENDS list
    returned = requests.get(f'{BASE_URL}users/{user}/playlists', headers=headers_)

    # get a list of their playlist ids (will be used soon to call dat aon their songs that compose each playlist)
    all_playlists = []
    for i in range(0, len(returned.json()['items'])):
        all_playlists.append(returned.json()['items'][i]['id'])

    print('swag')

    playlist = requests.get(f'{BASE_URL}playlists/{all_playlists[0]}/tracks', headers=headers_)

    return playlist

def playlist_processor(playlist_info):
    # playlist info will be what's returned from the api call
    songs = playlist_info.json()['items']

    song_ids = []
    artist_ids_ = {}
    for i in range(0, len(songs)):
        song_ids.append(songs[i]['track']['id'])  # add all the song ids to a list
        # print(songs[i]['track']['name'])
        artists = songs[i]['track']['artists']  # add all the artist ids to a list
        artist_id_values = []
        # artist_key = songs[i]
        for j in range(0, len(artists)):  # double-check this - should it be len(artists) or len(songs)
            # print(artists[j]['name'])
            artist_id_values.append(artists[j]['id'])
            artist_ids_[songs[i]['track']['id']] = artist_id_values
    print('swag')

    # artists[1]['id'
    return artist_ids_

    # songs[0]['track']['artists']
    # for spong in songs

if __name__=='__main__':
    main()
