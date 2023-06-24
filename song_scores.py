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

    playlist = get_all_playlist_ids(FRIENDS[0], headers)

    song_ids, album_ids, artist_ids = playlist_processor(playlist)

    # album_ids = get_all_album_ids(song_and_artist_ids.keys(), headers)

    song_popularities = get_popularities(song_ids, headers, 'tracks', 50)
    
    # artist_popularities = get_popularities(artist_ids, headers, 'artists', 50)  # keeps failing because of too many artists being requested

    album_popularities = get_popularities(album_ids, headers, 'albums', 20)

    # quick check to see song popularity relative to album popularity on this album
    ### TODO -- come up with a good way of quantifying the relationship between albums and songs
    summ = sum((np.array(song_popularities) - np.array(album_popularities)) > 5)

    print('swag')

    return song_popularities


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

    playlist_ = requests.get(f'{BASE_URL}playlists/{all_playlists[8]}/tracks', headers=headers_)

    return playlist_


def playlist_processor(playlist_info):
    # playlist info will be what's returned from the api call in get_all_playlist_ids
    songs = playlist_info.json()['items']

    ### TODO -- maybe make this two lists instead of a dictionary? 
    # That way you can have a get_artist_popularity function and a get_song-popularity function and it seems to make more sense
    song_ids = []
    album_ids = []
    artist_ids = []
    # song_and_artist_ids_ = {}
    for i in range(0, len(songs)):
        song_ids.append(songs[i]['track']['id'])  # add all the song ids to a list
        album_ids.append(songs[i]['track']['album']['id'])  # add all the album ids to a list
        artists = songs[i]['track']['artists']  # add all the artist ids to a list
        artist_id_subsets = []
        
        for j in range(0, len(artists)):  # double-check this - should it be len(artists) or len(songs)
            artist_id_subsets.append(artists[j]['id'])
        
        artist_ids.append(artist_id_subsets)

    return song_ids, album_ids, artist_ids


def nest_id_lists(id_list: list, members: int):
    if len(id_list) > members:  # if the list is longer than `members` items, figure out how many API calls to make
        if len(id_list) % members != 0:
            how_many_times = (len(id_list) / members) + 1
        else:
            how_many_times = len(id_list) / members
        
        start = 0
        end = members

        nested_list = []

        for i in range(0, int(how_many_times)):
            nested_list.append(list(id_list)[start:end])
            start += members  # increment to get the next values starting at previous end
            if end + members > len(id_list):
                end = len(id_list)
            else:
                end += members
        
        song_ids_ = nested_list

    else:
        song_ids_ = []
        song_ids_.append(id_list)

    return song_ids_


def get_all_album_ids(song_list: list, headers_):
    # a separate function to get the album_ids for eventually calculating album popularity

    ids_new = nest_id_lists(song_list, 20)
    for list_ in ids_new:
        subset_of_ids = str(list_).strip('[\'').strip('\']').replace('\', \'', ',')
        album_id_raw = requests.get(f'{BASE_URL}tracks/?ids={subset_of_ids}', headers=headers_).json()
        album_id_clean = album_id_raw['tracks'][0]['id']

    return


def get_popularities(id_list: list, headers_: dict, endpoint: str, batch_size: int):
    #  endpoint should be either 'tracks', 'artists', or 'albums'
    if endpoint not in ['tracks', 'artists', 'albums']:
        print('Incorrect value entered for endpoint parameter. Make sure it is either "tracks", "artists", or "albums".')

    ids_new = nest_id_lists(id_list, batch_size)

    popularity_list = []

    for list_ in ids_new:
        subset_of_ids = str(list_).strip('[\'').strip('\']').replace('\', \'', ',').replace('\'], [\'', '\',\'')

        popularities_raw = requests.get(f'{BASE_URL}{endpoint}/?ids={subset_of_ids}', headers=headers_)
        for j in range(0, len(list_)):
            popularity_list.append(popularities_raw.json()[endpoint][j]['popularity'])
    print('swag')

    # popularities_ = ''
    return popularity_list


if __name__=='__main__':
    main()
