# SongScores

SongScores is a project I've been thinking about for a long time. I'm a big fan of getting my Spotify Wrapped every year, and I wanted to try creating my own version, inspired by what I've seen in them in the past.

From a birds-eye view, what it does is take a list of playlist ids and then return a numeric rating for each one where the rating indicates how "indie"/obscure your songs on that playlist are. 

Right now, you need your own Spotify API developer credentials to run this. You can generate them by following the instructions [here](https://developer.spotify.com/documentation/web-api/tutorials/getting-started). 

You can run `song_scores.py` from the command line like any normal Python script, with `sys.argv[1]` corresponding to a comma-separated list of playlist ids like this: `'id1, id2, ..., idn'`. You'll need to update the 2nd and 3rd arguments in the `main()` function in `song_scores` to contain your client id and secret; however you decide to do that securely is up to you.

To find the playlist ids, open Spotify in a browser, open a playlist, and click on the url. The playlist id is the string of numbers and letters following the last slash, like this: 
<pre>
https://open.spotify.com/playlist/<b>5439HoBFYizp8yk82qOJJS<b>
</pre>

*Note: This will not work with playlists that are not public on Spotify. It will return an error instead.*