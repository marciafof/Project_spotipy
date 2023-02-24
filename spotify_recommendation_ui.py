import os
import numpy as np
import pandas as pd
import plotly.express as px

import streamlit as st
import streamlit.components.v1 as components

import song_recommender_main as song_recom
#%%
def play_song_from_spotify(track_id):
    html_song = f"""<iframe style="border-radius:12px" 
    src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" 
    width="100%" height="352" 
    frameBorder="0" allowfullscreen="" 
    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
    return html_song

def show_recommended_song(track_id):
    recomended_trackid = song_recom.scale_predict_new_entry(track_id)
    placeholder_recommendation = st.empty()
    with placeholder_recommendation:
        components.html (play_song_from_spotify(recomended_trackid), height=400)
#%% Setting up page config
st.set_page_config(page_title="Song Recommendation", layout="centered")
#%%Creating main title of body
st.markdown("""
<style>
h1 {
    text-align: center;
    color: #1db954;
}
</style>
""", unsafe_allow_html=True)

main_title = "BEST song recommendation system"
#%% Description of app
st.markdown(
            f"<h1>{main_title}</h1>",
            unsafe_allow_html=True)

st.markdown("""This is an app where you can get recommendations of songs based on a single input""")
#%% Requests input
mystyletext = '''
    <style>
        p {
            text-align: center;
        }
    </style>
    '''
st.markdown(mystyletext, unsafe_allow_html=True)

st.markdown("""Please insert your first <span style="color:#1db954">**song's title**</span>, 
and the  <span style="color:#1db954">**artist's**</span> name if possible""",unsafe_allow_html=True)

# st.markdown("""<style>

# .stTextInput{font-size:105%; font-weight:bold; color:#1db954;} </style>""", unsafe_allow_html=True)
#%% Create text input boxes
st.markdown('''
<style>

    label {
    justify-content: center;
    text-align: center;
    color: #1db954 !important;
}
</style>
''', unsafe_allow_html=True)

with st.form(key='columns_in_form'):

    col_title, col_artist= st.columns(2)
    
    with col_title:
        track_title = st.text_input(label="**Song's title**")
    with col_artist:
        track_artist = st.text_input(label="**Song's artist**")
    submitButton = st.form_submit_button(label = 'Go!')

#%% Call the function to look for tracks id
if "recommend" not in st.session_state:
    st.session_state.recommend = False
if "songoptions" not in st.session_state:
    st.session_state.songoptions = False
if "ncols" not in st.session_state:
    st.session_state.ncols = 1
if "chosentrack" not in st.session_state:
    st.session_state.chosentrack = None
if "newtrackid" not in st.session_state:
    st.session_state.newtrackid = None
    

#%%
if submitButton:
    if track_title and track_artist:
        st.write(track_title)
        st.write(track_artist)
        #Launch the function that searches for a song
        tracks_ids, tracks_hrefs = song_recom.search_for_song(track_title, track_artist)
        st.write(tracks_ids)
    elif track_title:
        st.write(track_title)
        tracks_ids, tracks_hrefs = song_recom.search_for_song(track_title, None)
        st.write(tracks_ids)
    st.session_state.newtrackid = tracks_ids
    ncols = len(tracks_ids)
    st.session_state.ncols = ncols
    st.session_state.songoptions=True
    st.session_state.recommend=False

if st.session_state.songoptions:
    if st.session_state.ncols == 1:
        
        placeholder_recommendation = st.empty()
        with placeholder_recommendation:
            components.html (play_song_from_spotify(tracks_ids[0]), height=400)
        agree = st.button('This is the song I am talking about')
        if agree:
            track_to_search = tracks_ids[0]
            st.session_state.recommend = True
    elif st.session_state.ncols == 2:
        col_1,col_2= st.columns(2)
        
    else:
        col_1,col_2,col_3 = st.columns(3)
       
    tracks_ids = st.session_state.newtrackid
    if st.session_state.ncols > 1:
        with col_1:
                placeholder_recommendation = st.empty()
                with placeholder_recommendation:
                    components.html (play_song_from_spotify(tracks_ids[0]), height=400)
                agree_id1 = st.button("I agree", key="opt1")
                if agree_id1:
                    st.session_state.recommend=True
                    st.session_state.chosentrack=tracks_ids[0]
        with col_2:
                 placeholder_recommendation = st.empty()
                 with placeholder_recommendation:
                     components.html (play_song_from_spotify(tracks_ids[1]), height=400)
                 agree_id2 = st.button("I agree", key="opt2")
                 if agree_id2:
                     st.session_state.recommend=True
                     st.session_state.chosentrack=tracks_ids[1]
        with col_3:
                 placeholder_recommendation = st.empty()
                 with placeholder_recommendation:
                     components.html (play_song_from_spotify(tracks_ids[2]), height=400)
                 agree_id3 = st.button("I agree", key="opt3")
                 if agree_id3:
                     st.session_state.recommend=True
                     st.session_state.chosentrack=tracks_ids[2]
                     
if st.session_state.recommend:
    track_to_search = st.session_state.chosentrack
    st.markdown(
    """<font size = 18px weight=700>
    <span style="color:#fffff">We found something you may like</span> </font>""",unsafe_allow_html=True)
    recomended_trackid = song_recom.scale_predict_new_entry(track_to_search)
    placeholder_recommendation = st.empty()
    with placeholder_recommendation:
        components.html (play_song_from_spotify(recomended_trackid), height=400)

