import pandas as pd
import numpy as np
import requests
import config
BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/api/token'
FRIENDS = config.friends  # a list of user_ids
CLIENT_ID = config.id_  # id, supplied from spotify for developers
CLIENT_SECRET = config.secret  # secret, supplied from spotify for developers

### Roadmap
# - with a user's id, get a list of their playlists
# - take a playlist from the preceding list (or an individual track?) and get the artist # of followers and popularity; the artist's top tracks; the track's popularity (do this for each track in the playlist)
#  - calculate indieness metric (maybe like 1/log(followers) * track popularity or something like that) for each track
#   - aggregate all indieness scores (some sort of average, maybe the median?)

### TODO -- add type hints to functions


def main():
    access_token, headers = auth_stuff()

    playlist = get_all_playlist_ids(FRIENDS[2], headers)

    song_and_artist_ids = playlist_processor(playlist)

    song_popularities = get_popularities(song_and_artist_ids.keys(), headers)
    
    artist_popularities = get_popularities(song_and_artist_ids.values(), headers)

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


def get_all_playlist_ids(user, headers_):
    # for now, user should be an element in the FRIENDS list
    returned = requests.get(f'{BASE_URL}users/{user}/playlists', headers=headers_)

    # get a list of their playlist ids (will be used soon to call dat aon their songs that compose each playlist)
    all_playlists = []
    for i in range(0, len(returned.json()['items'])):
        all_playlists.append(returned.json()['items'][i]['id'])

    print('swag')

    playlist_ = requests.get(f'{BASE_URL}playlists/{all_playlists[0]}/tracks', headers=headers_)

    return playlist_

def playlist_processor(playlist_info):
    # playlist info will be what's returned from the api call in get_all_playlist_ids
    songs = playlist_info.json()['items']

    ### TODO -- maybe make this two lists instead of a dictionary? 
    # That way you can have a get_artist_popularity function and a get_song-popularity function and it seems to make more sense
    song_ids = []
    song_and_artist_ids_ = {}
    for i in range(0, len(songs)):
        song_ids.append(songs[i]['track']['id'])  # add all the song ids to a list
        # print(songs[i]['track']['name'])
        artists = songs[i]['track']['artists']  # add all the artist ids to a list
        artist_id_values = []
        # artist_key = songs[i]
        for j in range(0, len(artists)):  # double-check this - should it be len(artists) or len(songs)
            # print(artists[j]['name'])
            artist_id_values.append(artists[j]['id'])
            song_and_artist_ids_[songs[i]['track']['id']] = artist_id_values
    print('swag')

    # artists[1]['id'
    return song_and_artist_ids_


def get_popularities(id_list: list, headers_: dict):

    ids_new = nest_id_lists(song_ids)
    
    for i in ids_new:
        ### TODO -- loop through new list of lists to get info on 50 tracks at a time
        song_pop_short = requests.get(f'{BASE_URL}tracks/{some_set_of_50_ids}', headers=headers_)
    popularities_ = ''
    return popularities_


def nest_id_lists(id_list: list):
    if len(id_list) > 50:  # if the list is longer than 50 members, figure out how many API calls to make
        if len(id_list) % 50 != 0:
            how_many_times = (len(id_list) / 50) + 1
        else:
            how_many_times = len(id_list) / 50
        
        start = 0
        end = 50

        nested_list = []

        for i in range(0, int(how_many_times)):
            nested_list.append(id_list[start:end])
            start += 50  # increment to get the next values starting at 
            if end + 50 > len(id_list):
                end = len(id_list)
            else:
                end += 50
        
        song_ids_ = nested_list

    else:
        song_ids_ = id_list

    return id_list


if __name__=='__main__':
    main()
