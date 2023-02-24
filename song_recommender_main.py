# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 00:53:49 2023

@author: marci
"""

import os
import config
import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt


#%% START SESSIONS WE NEED IT TO GET SPOTIFY API RESULTS
from spotipy.oauth2 import SpotifyClientCredentials
#Initialize SpotiPy with user credentias
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,
                                                           client_secret= config.client_secret))

#%%
def load(filename = "filename.pickle"): 
    try: 
        with open(filename, "rb") as f: #rb in this cas is reading permission
            return pickle.load(f) 
        
    except FileNotFoundError: # if we don't add this error it will give an error and the running will stop
        print("File not found!") 
def get_tracks_audio_features(track_id_list):
    """ Get track's audio features in a dataframe format
    using the audio_features functions from spotipy.

    Returns a pandas dataframe with the following columns in this order:
        - danceability
        - energy
        - loudness
        - speechiness
        - acousticness
        - instrumentalness
        - liveness
        - valence
        - tempo
        - id
        - duration_ms

    Input: 
        track_id_list : list of track/s id/s

    Return:
        pd.Dataframe 
    """
    columns = ["danceability","energy","loudness","speechiness","acousticness",
        "instrumentalness","liveness","valence","tempo","id","duration_ms"]
    #Extract audio features through the spotipy wrapper using audio_features
    #This is equivalent to only One request
    tracks_features = sp.audio_features(track_id_list)
    #Create the pandas dataframeusing json normalize
    df_track_features = pd.json_normalize(tracks_features)
    #Sometimes the output has no data, so we check. If no data we return an empty dataframe
    if df_track_features.shape[0] > 0:
        try:
            #Select only the mentioned columns
            df_track_features = df_track_features[["danceability","energy",
            "loudness","speechiness","acousticness", 
            "instrumentalness","liveness","valence","tempo","id","duration_ms"]]
            return df_track_features
        except KeyError:
            print("Problem with columns of created dataframe. Selected columns not found")
            print(df_track_features.columns)
            return pd.DataFrame()

def search_for_song(track_title,track_artist=None, market=None):
    if track_artist != None:
        track_artist = track_artist.replace(" ","%20")
        querystr = fr"%20track:{track_title}%20artist:{track_artist}"
        results = sp.search(q=querystr,limit=3,market=market,type="track") 
    else:
        querystr = track_title
        results = sp.search(q=querystr,limit=3,market=None) #top 3 limits and market great britan
    
    track_ids = [];
    track_hlinks = [];
    for x in results["tracks"]["items"]:
        if x!= None:
            track_ids.append(x["id"])
            track_hlinks.append(x["external_urls"]["spotify"])
    return track_ids,track_hlinks

def scale_new_entry(track_id):
    columns_no_id = ["danceability","energy","loudness","speechiness","acousticness",
        "instrumentalness","liveness","valence","tempo","duration_ms"]
    #Get audio track features
    df_track_features = get_tracks_audio_features([track_id])
    if df_track_features.shape[0]>0:
        df_track_features.set_index('id', inplace=True)
        
    saved_scaler = load("song_recom_scaler.pickle")
    scaled_user_input_song = saved_scaler.transform(df_track_features)
    df_scaled_user_input_song = pd.DataFrame(scaled_user_input_song, columns=columns_no_id)
    closest_cluster_label = saved_mode.predict(scaled_user_input_song)
    
