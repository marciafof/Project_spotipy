import os
import config
import spotipy
import json
import pandas as pd

#%% START SESSIONS
from spotipy.oauth2 import SpotifyClientCredentials
#Initialize SpotiPy with user credentias
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,
                                                           client_secret= config.client_secret))

#%% FUNCTIONS 

# GETTING TRACKS OF PLAYLIST
def get_playlist_tracks_general(playlist_id, limit = 100):
    list_songs_in_playlist = sp.playlist_tracks(playlist_id,limit = limit, market="GB")
    tracks = list_songs_in_playlist['items']
    while list_songs_in_playlist['next']:
        list_songs_in_playlist = sp.next(list_songs_in_playlist)
        tracks.extend(list_songs_in_playlist['items'])
    return tracks

def get_tracks_audio_features(track_id_list):
    #track_id_joined = ",".join(track_id_list)
    tracks_features = sp.audio_features(track_id_list)
    df_track_features = pd.json_normalize(tracks_features)
    df_track_features = df_track_features[["danceability","energy",
    "loudness","speechiness","acousticness", 
    "instrumentalness","liveness","valence","tempo","id","duration_ms"]]
    return df_track_features

def get_audio_features_from_playlist(playlist_id, limit = 100):
    tracks_in_playlist = get_playlist_tracks_general(playlist_id, limit=limit)
    track_id_list = [ x["track"]["id"] for x in tracks_in_playlist ]
    df_tracks_features = get_tracks_audio_features(track_id_list)
    return df_tracks_features

def get_recommendations_genre(genre= ["pop"], country="US",limit=100):
    """ The max elements that we can get from this function is 100 so no need for Next"""
    genre_recommendations = sp.recommendations(seed_genres=genre,limit=limit,country=country)
    return genre_recommendations["tracks"]


#%% RATE LIMIT PER API
time_window = 30 #in seconds

#%% OBTAIN LIST OF GENRES
dic_genres = sp.recommendation_genre_seeds()
list_genres = list(dic_genres["genres"])

get_by_genre = True
id_dfs = str(1)
if get_by_genre:
    for genre_i in list_genres[2:]:
        print(f"Getting recommendations for genre {genre_i}")
        tracks_recommended = get_recommendations_genre(genre=[genre_i], country="US")
        track_id_list = [ x["id"] for x in tracks_recommended ]
        df_features_recommended = get_tracks_audio_features(track_id_list)
        if not os.path.isdir(f"data/by_genre/{genre_i}"):
            os.mkdir(f"data/by_genre/{genre_i}")
        df_features_recommended.to_csv(f"data/by_genre/{genre_i}/{id_dfs}.csv",index=False)
        
#%%Building 
#playlist_global = sp.playlist_tracks("37i9dQZEVXbNG2KDcFcKOF", limit = 50)