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
            df_track_features = df_track_features[columns]
            return df_track_features
        except KeyError:
            print("Problem with columns of created dataframe. Selected columns not found")
            print(df_track_features.columns)
            return pd.DataFrame()

def search_for_song(track_title,track_artist=None, market=None):
    """ 
    This is the function that searches the track to laucnh the recommendation.
    The track is searched using track title and the artist's name if wanted.
    
    The query outputs 3 possible track choices ( this is limit by the parameter limit=3)
    
    Input:
        track_title : str (song's name)
        track_artist: Optional str (name of artist)
        market: str (from list of ISO codes, if None then we get a general result)
        
    Return:
        track_ids: list ( list containing query results track IDs used to search in spotify API)
        track_hlinks: list ( list containing query results Hyperlink that can be used to embed the song)
    
    """
    if track_artist != None:
        track_artist = track_artist.replace(" ","%20") #We replace the space with this character according to Spotify's documentation
        querystr = fr"%20track:{track_title}%20artist:{track_artist}" #Building the query string
        results = sp.search(q=querystr,limit=3,market=market,type="track") 
    else:
        querystr = track_title
        results = sp.search(q=querystr,limit=3,market=None) #top 3 limits
    #We build the lists with the results
    track_ids = [];
    track_hlinks = [];
    for x in results["tracks"]["items"]:
        if x!= None:
            track_ids.append(x["id"])
            track_hlinks.append(x["external_urls"]["spotify"])
    return track_ids,track_hlinks

def scale_predict_new_entry(track_id, 
                            scaler_path="model_ui/song_recom_scaler.pickle",
                            model_path="model_ui/song_recom_model.pickle",
                            data_path = "model_ui/labeled_db_for_recommendation.csv"):
    """ 
    Function to scale new entry according to the model's scaler produced in the training.
    The new entry is a track id that is used as an input for the get audio features function.
    
    The audio features from the track_id are return as a dataframe and scaled using the
    scaler.transform.
    
    The transform 
    
    """
    audio_features_selected =  ["danceability","energy","loudness","speechiness","acousticness",
    "instrumentalness","liveness","valence","tempo"]
    #Get audio track features
    df_track_features = get_tracks_audio_features([track_id])
    if df_track_features.shape[0]>0:
        df_track_features.set_index('id', inplace=True)
        
    #Scaling the new track id
    saved_scaler = load(scaler_path)
    scaled_user_input_song = saved_scaler.transform(df_track_features)
    df_scaled_user_input_song = pd.DataFrame(scaled_user_input_song, columns=audio_features_selected)
    #Opening the model for prediction
    saved_model = load(model_path)
    
    #Predicting label with saved model
    closest_cluster_label = saved_model.predict(df_scaled_user_input_song)
    
    #Choosing song from our database that matches the characteristics of new song
    df_recommentation = pd.read_csv(data_path)
    
    #Select songs from same cluster
    cluster_df = df_recommentation[df_recommentation["cluster"] == int(closest_cluster_label)]

    # Select a random song from the cluster
    random_song = cluster_df.sample(n=1)
    random_song.reset_index(inplace = True)
    id_recommended_song = random_song.id[0]
    
    #id_recommended_song = "3e9HZxeyfWwjeyPAMmWSSQ" #just for test
    
    return id_recommended_song
