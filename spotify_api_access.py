# %%
import requests

# %%
CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'
AUTH_URL = 'https://accounts.spotify.com/api/token'

# %%
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# %%
# convert the response to JSON
auth_response_data = auth_response.json()

# %%
# save the access token
access_token = auth_response_data['access_token']

# %%
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# %%
# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

# %%
# Track ID from the URI
track_id = '2takcwOaAZWiXQijPHIx7B'

# %%
# actual GET request with proper header
r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)

# %%
r = r.json()
r

# %%
artist_id = '06HL4z0CvFAxyc27GXpf02'

# %%
# pull all artists albums
r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums', 
                 headers=headers, 
                 params={'include_groups': 'album', 'limit': 50})
d = r.json()

# %%
for album in d['items']:
    print(album['name'], ' --- ', album['release_date'])

# %%
data = []   # will hold all track info
albums = [] # to keep track of duplicates

# loop over albums and get all tracks
for album in d['items']:
    album_name = album['name']

    albums.append(album_name) # use upper() to standardize
    
    # pull all tracks from this album
    r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', 
        headers=headers)
    tracks = r.json()['items']

    for track in tracks:
        # get audio features (key, liveness, danceability, ...)
        f = requests.get(BASE_URL + 'audio-features/' + track['id'], 
            headers=headers)
        f = f.json()
        
        # combine with album info
        f.update({
            'track_name': track['name'],
            'album_name': album_name,
            'release_date': album['release_date'],
            'album_id': album['id']
        })
        
        data.append(f)

# %%
import pandas as pd

df = pd.DataFrame(data)

# %%
df['release_date'] = pd.to_datetime(df['release_date'])
df = df.sort_values(by='release_date')
df


