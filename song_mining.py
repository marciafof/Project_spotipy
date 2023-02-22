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
    list_songs_in_playlist = sp.playlist_tracks(playlist_id,limit = limit)
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
    track_id_list = [ x["track"]["id"] for x in tracks_in_playlist if x["track"]]
    clean_track_id_list = [x for x in track_id_list if x != None]
    #Divide into chunks to comply with audio_features
    if len(track_id_list) > 100:
        tracks_id_list_chunks = list(divide_chunks(clean_track_id_list,100)) #100 is the limit spotify give us
        list_of_dfs = []
        nchunk = 1
        for chunk_tracks in tracks_id_list_chunks:
            print(f"Treating chunk {nchunk} of playlist of size {len(tracks_id_list_chunks)}")
            df_chunk = get_tracks_audio_features(chunk_tracks)
            list_of_dfs.append(df_chunk)
            nchunk += 1
        return pd.concat(list_of_dfs,axis=0)
    else:
        df_tracks_features = get_tracks_audio_features(clean_track_id_list)
        return df_tracks_features

def get_recommendations_genre(genre= ["pop"], country="US",limit=100):
    """ The max elements that we can get from this function is 100 so no need for Next"""
    genre_recommendations = sp.recommendations(seed_genres=genre,limit=limit,country=country)
    return genre_recommendations["tracks"]

def get_playlists_by_category(category_id, category_name="name",limit=20):
    playlists_dic = sp.category_playlists(category_id=category_id, limit=limit)
    list_of_playlists_info = [ x["id"] for x in playlists_dic["playlists"]["items"] if x["id"]]
    for nlist, playlist_id in enumerate(list_of_playlists_info):
        print(f"Getting info from category: {category_name} playlist n° {nlist}")
        df_nlist = get_audio_features_from_playlist(playlist_id)
        df_nlist.to_csv(f"data/by_playlist/{category_name}_{playlist_id}.csv",index=False)
    return list_of_playlists_info

def get_categories_ids(country=None, limit=10):
    cats_global= sp.categories(country=country, limit=limit)
    list_of_categories_id = [ x["id"] for x in cats_global["categories"]["items"] if x["id"]]
    list_of_categories_names = [ x["name"] if x["name"] else None for x in cats_global["categories"]["items"] ]
    return list_of_categories_id, list_of_categories_names

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
#%% RATE LIMIT PER API
time_window = 30 #in seconds

#%% OBTAIN LIST OF GENRES
dic_genres = sp.recommendation_genre_seeds()
list_genres = list(dic_genres["genres"])

#%% Get tracks recommendations and features by genre
get_by_genre = False
id_dfs = str(1)
if get_by_genre:
    for genre_i in list_genres[2:]:
        print(f"Getting recommendations for genre {genre_i}")
        tracks_recommended = get_recommendations_genre(genre=[genre_i], country="US")
        track_id_list = [ x["id"] for x in tracks_recommended ]
        clean_track_id_list = [x for x in track_id_list if x != None]
        df_features_recommended = get_tracks_audio_features(clean_track_id_list)
        if not os.path.isdir(f"data/by_genre/{genre_i}"):
            os.mkdir(f"data/by_genre/{genre_i}")
        df_features_recommended.to_csv(f"data/by_genre/{genre_i}/{id_dfs}.csv",index=False)

#%% Get tracks recommendations and playlist_id
get_by_playlist = False
if get_by_playlist:
    playlist_list = ["5C9lZdpSpngIBd2fy7vJlx"]
    playlist_list_names = [r"partyhits_24_7"]
    for ielem, playlist_id in enumerate(playlist_list):
        print(f"Getting features from playlist {playlist_list_names[ielem]}")
        df_features_playlist = get_audio_features_from_playlist(playlist_id)
        df_features_playlist.to_csv(f"data/by_playlist/{playlist_list_names[ielem]}.csv",index=False)
#%% Get playlist by category
import random
get_playlists_basedon_category = True
if get_playlists_basedon_category:
    ncat = 5
    nlists = 2
    #df_categories = pd.read_csv("data/list_of_categories.txt")
    #list_of_cat = df_categories.iloc[:,0].to_list()
    #choice_of_cat = random.choices(list_of_cat,k=ncat)
    list_of_categories,list_of_categories_names = get_categories_ids(country=None, limit=ncat)
    for categorie_id, categorie_name in zip(list_of_categories,list_of_categories_names) :
        print(categorie_name)
        list_of_playlists_info = get_playlists_by_category(categorie_id,category_name = categorie_name,limit=nlists)
        for list_name in list_of_playlists_info:
            print(list_name)
#%%Building 
#playlist_global = sp.playlist_tracks("37i9dQZEVXbNG2KDcFcKOF", limit = 50)