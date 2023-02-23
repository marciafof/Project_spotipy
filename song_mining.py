import os
import config
import spotipy
import json
import pandas as pd
import glob
import re

#%% START SESSIONS
from spotipy.oauth2 import SpotifyClientCredentials
#Initialize SpotiPy with user credentias
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,
                                                           client_secret= config.client_secret))

#%% FUNCTIONS 

# GETTING TRACKS OF PLAYLIST
def get_playlist_tracks_general(playlist_id, limit = 100):
    """ Get tracks from playlist using the spotipy playlist_tracks
    Input:
            playlist_id : str (id of playlist)
            limit : int 100 is the maximum of songs 
                    per page but we can go through all the playlist
    
    Return:
            tracks: list (list of each dictionary from the items)
    """
    list_songs_in_playlist = sp.playlist_tracks(playlist_id,limit = limit)
    tracks = list_songs_in_playlist['items']
    while list_songs_in_playlist['next']:
        list_songs_in_playlist = sp.next(list_songs_in_playlist)
        tracks.extend(list_songs_in_playlist['items'])
    return tracks

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


def get_audio_features_from_playlist(playlist_id, limit = 100):
    """ Get audio geatures based on playlist id. 
    The first step is to get the tracks inside playlist using the
    get_playlist_tracks_general function.

    To get the audio features the list of tracks ids is divided in "chunks"
    of 100 items due to the limitations in the sp.audio_features requests.
    The "chunks" are created using the divide_chunks functions. 

    For each "chunk" we apply the get_tracks_audio_features.
    
    Input:
        playlist_id : str (id of playlist)
        limit : int (limit of tracks per page)

    Return:
        pd.Dataframe (Contains all the audio features of all tracks in playlist)
    """
    #First we extract the tracks of the playlist_id 
    tracks_in_playlist = get_playlist_tracks_general(playlist_id, limit=limit)
    #Get track id for each item in the dictionary in tracks_in_playlist if it contains elements 
    track_id_list = [ x["track"]["id"] for x in tracks_in_playlist if x["track"]]
    #Sometimes the id recovered is a None value and it creates issues when extracting audio_features
    #We clean the list
    clean_track_id_list = [x for x in track_id_list if x != None]
    #Divide into chunks to comply with audio_features if we have more than 100 ids in playlist
    if len(track_id_list) > 100:
        tracks_id_list_chunks = list(divide_chunks(clean_track_id_list,100)) #100 is the limit spotify give us
        list_of_dfs = [] #Initialize list to stores dataframes with audio features
        nchunk = 1
        #For each chunk of 100 items we get the tracks audio features and add it to a list of dataframes
        for chunk_tracks in tracks_id_list_chunks:
            print(f"Treating chunk {nchunk} of playlist of size {len(tracks_id_list_chunks)}")
            df_chunk = get_tracks_audio_features(chunk_tracks)
            list_of_dfs.append(df_chunk)
            nchunk += 1
        #Create One dataframe with all chunks
        return pd.concat(list_of_dfs,axis=0)
    else:
        #If the lists of ids is less than 100 we can get it directly from the function sp.audio features
        df_tracks_features = get_tracks_audio_features(clean_track_id_list)
        return df_tracks_features

def get_recommendations_genre(genre= ["pop"], country="US",limit=100):
    """ We can get a list of songs recommended by Spotify using the sp.recommendations
    The max elements that we can get from this function is 100 according to Spotify API
    
    Input:
        genre : list (list containing the name/s of genre/s)
        country: str or None (Code of the country used to get recommendations)
        limit: int ( Number of tracks I would like to get)
    
    Return:
        list: list of tracks dictionaries 
    """
    #Here I only put the genre recommendations
    genre_recommendations = sp.recommendations(seed_genres=genre,limit=limit,country=country)
    return genre_recommendations["tracks"]

def get_playlists_by_category(category_id, category_name="name",limit=20,country=None):
    """
    Get audio features from tracks in recommended playlists for the category_id from Spotify home page.
    First the playlists are recovered using sp.category_playlists for the category_id
    For each playlist we obtain the tracks and audio features by the get_audio_features_from_playlist function.
    We return a dataframe with the audio features for each playlist named using category_name and the number of playlist.

    Input:
        category_id: str (Category id used in Spotify api to get recommendations of playlists)
        category_name: str (Name of the category, it is only used to name the file output)
        limit: int (Number of playlists to be recommended)
        country: str (Code of the country if target marketed)

    Return:
        lists_of_playlists_info: lists of ids of playlists
    """
    #First we try to get playlists for the category_id.
    #Sometimes the category_id returns an error so we handle through Exception and return an empty list
    try:
        playlists_dic = sp.category_playlists(category_id=category_id, limit=limit,country=country)
    except Exception as e:
        print(e)
        print(f"Playlist for category {category_id} coudn't be recovered ")
        return []
    #If there items in playlists_dic is not empty we iterate through each item (playlist)
    if playlists_dic["playlists"]["items"]:
        #We create a list of playlist ids by checking that there is no None or empty values
        #list_of_playlists_info = [ x["id"] for x in playlists_dic["playlists"]["items"] if ((x!=None)|(x["id"] != None))] #Did not work in One line
        list_of_playlists_info = []
        for x in playlists_dic["playlists"]["items"]:
            if x == None:
                continue
            elif x["id"] == None:
                continue
            else:
                list_of_playlists_info.append(x["id"])
        
        #We iterate through each playlist_id
        for nlist, playlist_id in enumerate(list_of_playlists_info):
            print(f"Getting info from category: {category_name} playlist n° {nlist}")
            #We check if the playlist is not already in our database based on the playlist_id
            #In this case the path to look for the files is hard written (be careful if you change the directory of playlists)
            if len(glob.glob(fr"data\\by_playlist\\*_{playlist_id}.csv"))>0:
                print(f"Playlist {playlist_id} already save") #If file with playlist already exists we do not request the information.
                #TODO 
                #If the playlist is updated frequently maybe add an option to rewrite based on playlist_id
            else:
                #If file does not exist, we recover the audio features for the playlist and we save
                df_nlist = get_audio_features_from_playlist(playlist_id)
                df_nlist.to_csv(f"data\\by_playlist\\{category_name}_{playlist_id}.csv",index=False)
                #TODO
                #If we want to change the path of the saving folder maybe add an option
    else:
        #If nothing return for the playlist create an empty list for consistency of the output
        list_of_playlists_info = []
        #I return the playlists_id for possible use afterwards
    return list_of_playlists_info

def get_categories_ids(country=None, limit=10,offset=0):
    """ Get Spotify category id using the sp.categories function from Spotipy
    The country could be specified
    
    Input:
        country: str ( Country code )
        limit: int (Number of categories to look for. The max is 50)
        offset: int (First number of category to be return)

    Return:
        list_of_categories_id, list_of_categories_names

        list_of_categories_id: list ( list containing categories ids )
        list_of_categories_names: list ( list containing name associated to each category_id)
    """

    #If country=None then we get the "global" categories
    cats_global= sp.categories(country=country, limit=limit,offset=offset) 
    #Get the categories ids if the items are not None
    list_of_categories_id = [ x["id"] for x in cats_global["categories"]["items"] if x["id"] != None]
    #Get the name associated to each id
    list_of_categories_names = [ ]
    for x in cats_global["categories"]["items"]:
        #Some names contain characters such as &, or /, that are not well handled by windows.
        #I replaced them with "_" underscore
        if x["name"]:
            if re.search(r'[/&]', x["name"]):
                list_of_categories_names.append(re.sub(r'[/&]', '_',x["name"]))
            else:
                list_of_categories_names.append(x["name"])
        else:
            list_of_categories_names.append(None)#If no name is recover I return a None to keep the same number of elements as list_of_categories_id
    return list_of_categories_id, list_of_categories_names

def divide_chunks(l, n):
    """Function to divide a list l into n number of chunks"""
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
#import random
get_playlists_basedon_category = True
if get_playlists_basedon_category:
    ncat = 50 #Number of categories I want to return, Limit is 50
    nlists = 5 #Number of playlist by category, Limit is 50 playlists per category
    
    country = "LB" #by default None
    list_of_categories,list_of_categories_names = get_categories_ids(country=country, limit=ncat, offset=0)
    for categorie_id, categorie_name in zip(list_of_categories,list_of_categories_names) :
        print(categorie_name)
        list_of_playlists_info = get_playlists_by_category(categorie_id,category_name = categorie_name,limit=nlists, country=country)
        for list_name in list_of_playlists_info:
            print(list_name)
#%%Unitary tests
#playlist_global = sp.playlist_tracks("37i9dQZEVXbNG2KDcFcKOF", limit = 50)