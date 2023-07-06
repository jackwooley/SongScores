import pandas as pd
import numpy as np
import requests
import config
BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/api/token'
# FRIENDS = config.friends  # a list of user_ids
# CLIENT_ID = config.id_  # id, supplied from spotify for developers; replace with your own
# CLIENT_SECRET = config.secret  # secret, supplied from spotify for developers; replace with your own

### Roadmap
# - with a user's id, get a list of their playlists
# - take a playlist from the preceding list (or an individual track?) and get the artist # of followers and popularity; the artist's top tracks; the track's popularity (do this for each track in the playlist)
#  - calculate indieness metric (maybe like 1/log(followers) * track popularity or something like that) for each track
#   - aggregate all indieness scores (some sort of average, maybe the median?)

### TODO -- add type hints to functions


def main(user_id: str, client_id: str, client_secret: str):
    access_token, headers = auth_stuff(client_id, client_secret)

    playlist = get_all_playlist_ids(user_id, headers)

    song_ids_all, album_ids_all, artist_ids_all = [], [], []
    for i in playlist:
        song_ids, album_ids, artist_ids = playlist_processor(i, headers)
        song_ids_all.append(song_ids)
        album_ids_all.append(album_ids)
        artist_ids_all.append(artist_ids)

    metrics = []

    ### TODO -- basic functionality works but this loop needs lots of work to run correctly/successfully
    ### 
    for i in range(0, len(song_ids_all)):
        try:
            song_popularities = get_popularities(song_ids_all[i], headers, 'tracks', 50)
            
            artist_popularities = get_artist_popularities(artist_ids_all[i], headers)

            artist_followers = get_artist_follower_count(artist_ids_all[i], headers, 50)

            album_popularities = get_popularities(album_ids_all[i], headers, 'albums', 20)

            # TODO -- decide if it's worth it to run this one, or if it'll slow it down too much
            # artists_top_songs = get_artists_top_songs(artist_ids, headers, 20)

            ### TODO -- come up with a good way of quantifying the relationship between albums and songs
            # what's currently in here doesn't make much sense lol
            # something like the following might work:
            # the higher the better on the indie-ness scale (i.e., 0 = v mainstream, 100? = the most indie - not sure how to standardize scores though)
            # np.log(1/song_pop) + np.log(avg(1/artist_followers)) + np.log(1/album_popularities) + [check if song is in artist's most popular songs (this slows the program down significantly though)]

            # np.log(1/song_popularities[i]) + np.log(1/np.mean(np.array(artist_followers[i]))) + np.log(1/album_popularities[i])
            for j in range(0, len(song_ids)):
                jth_song_metric = np.log((song_popularities[j] + .1)) + np.log((artist_popularities[j] + .1))
                + np.log((np.mean(np.array(artist_followers[j])) + .1)) + np.log((album_popularities[j] + .1))
                metrics.append(jth_song_metric)
        except TypeError as te:
            print(f'iteration {i} had an error: {te=}')
    
    np.array(metrics)

    return np.mean(metrics)

    # song_vec = np.array(song_popularities) / 100
    # artist_vec = np.array(artist_popularities) / 100
    # artist_followers_vec = np.log(np.array(artist_followers).astype(float))
    # album_vec = np.array(album_popularities) / 100

    # relative_song_popularity_album = song_vec / album_vec  # relative to how popular the album is, how popular is the song?
    # relative_song_popularity_artist = song_vec / artist_vec  # relative to how popular the artist is, how popular is the song?
    # relative_song_popularity_followers = song_vec * (np.log(artist_followers_vec))
    
    # print('swag')

    # return song_popularities


def auth_stuff(client_id: str, client_secret: str):
    
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()

    # save the access token
    access_token_ = auth_response_data['access_token']

    headers_ = {
        'Authorization': f'Bearer {access_token_}'#.format(token=access_token)
    }

    return access_token_, headers_  # does this need the access_token_ to be returned?


def get_all_playlist_ids(user: str, headers_: dict)->list:
    # for now, user should be an element in the FRIENDS list
    returned = requests.get(f'{BASE_URL}users/{user}/playlists?limit=50', headers=headers_)

    # get a list of their playlist ids (will be used soon to call dat aon their songs that compose each playlist)
    all_playlists = []
    for i in range(0, len(returned.json()['items'])):
        all_playlists.append(returned.json()['items'][i]['id'])

    return all_playlists


def playlist_processor(playlist_id: str, headers_: dict):
    playlist_info = requests.get(f'{BASE_URL}playlists/{playlist_id}/tracks', headers=headers_)

    # playlist info will be what's returned from the api call in get_all_playlist_ids
    songs = playlist_info.json()['items']

    song_ids = []
    album_ids = []
    artist_ids = []
    # song_and_artist_ids_ = {}

    ### TODO -- error handling needs some love. this is a really sloppy fix rn.
    try:
        for i in range(0, len(songs)):
            song_ids.append(songs[i]['track']['id'])  # add all the song ids to a list
            album_ids.append(songs[i]['track']['album']['id'])  # add all the album ids to a list
            artists = songs[i]['track']['artists']  # add all the artist ids to a list
            artist_id_subsets = []  # leave this here for when u go back to fix the artist api calls
            # artist_ids.append(artists[0]['id'])  # this doesn't account for songs with more than 1 artist (like ones w features)

            for j in range(0, len(artists)):
                artist_id_subsets.append(artists[j]['id'])
            
            artist_ids.append(artist_id_subsets)
    
    except TypeError as te:
        print(f'iteration {i} caused a problem: {te=}')
        if len(song_ids) == i-1:
            song_ids[i] = None
        if len(album_ids) == i-1:
            album_ids[i] = None
        if len(artist_ids) == i-1:
            artist_ids[i] = None

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
    #  endpoint should be either 'tracks' or 'albums'
    try:
        ids_new = nest_id_lists(id_list, batch_size)
        popularity_list = []

        for list_ in ids_new:
            subset_of_ids = str(list_).strip('[\'').strip('\']').replace('\', \'', ',')#.replace('\'], [\'', '\',\'')
            popularities_raw = requests.get(f'{BASE_URL}{endpoint}/?ids={subset_of_ids}', headers=headers_)
            
            for j in range(0, len(list_)):
                popularity_list.append(popularities_raw.json()[endpoint][j]['popularity'])
    
    except KeyError as k:
        print(f'{k=}. Did you use the wrong endpoint?')

    return popularity_list


def get_artist_popularities(id_list: list, headers_: dict):
    
    popularity_list = []
    lengths = []
    starred = []

    for i in id_list:
        lengths.append(len(i))
        starred = [*starred, *i]

    raw_popularities = get_popularities(starred, headers_, 'artists', 20)  # artists api is rate-limited to 20 instead of 50

    start = 0
    end = 0
    for i in lengths:
        end += i
        popularity_list.append(raw_popularities[start:end])
        start = end

    for i in range(0, len(popularity_list)):
        if len(popularity_list[i]) != len(id_list[i]):
            print('bro')

    return popularity_list


def get_artist_follower_count(id_list: list, headers_: dict, batch_size: int):  # TODO -- NOT TESTED YET
    # almost identical to the get popularity one, but it returns # of an artist's followers as opposed to popularity

    clean_followers_list = []
    lengths = []
    starred = []

    for i in id_list:
        lengths.append(len(i))
        starred = [*starred, *i]

    ids_new = nest_id_lists(starred, batch_size)

    followers_list = []

    for list_ in ids_new:
        subset_of_ids = str(list_).strip('[\'').strip('\']').replace('\', \'', ',')#.replace('\'], [\'', '\',\'')
        followers_raw = requests.get(f'{BASE_URL}artists/?ids={subset_of_ids}', headers=headers_)
        for j in range(0, len(list_)):
            followers_list.append(followers_raw.json()['artists'][j]['followers']['total'])

    start = 0
    end = 0
    for i in lengths:
        end += i
        clean_followers_list.append(followers_list[start:end])
        start = end

    return clean_followers_list


def get_artists_top_songs(id_list: list, headers_: dict, batch_size: int):
    clean_top_songs = []
    lengths = []
    starred = []

    for i in id_list:
        lengths.append(len(i))
        starred = [*starred, *i]

    # ids_new = nest_id_lists(starred, batch_size)

    top_songs = []

    for artist in starred:
        # subset_of_ids = str(list_).strip('[\'').strip('\']').replace('\', \'', ',')#.replace('\'], [\'', '\',\'')
        top_songs_raw = requests.get(f'https://api.spotify.com/v1/artists/{artist}/top-tracks?market=US', headers=headers_)  #requests.get(f'{BASE_URL}artists/{starred[0]}/top-tracks', headers=headers_)
        for j in range(0, len(top_songs_raw.json()['tracks'])):
            top_songs.append(top_songs_raw.json()['tracks'][j]['album']['id'])

    start = 0
    end = 0
    for i in lengths:
        end += i
        clean_top_songs.append(top_songs[start:end])
        start = end

    return clean_top_songs

if __name__=='__main__':
    main(config.friends[0], config.id_, config.secret)
