import os
import numpy as np
import pandas as pd
import plotly.express as px

import streamlit as st
import streamlit.components.v1 as components

import song_recommender_main as song_recom
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
    submitButton = st.form_submit_button(label = 'Calculate')

#%% Call the function to look for tracks id
if submitButton:
    if track_title and track_artist:
        st.write(track_title)
        st.write(track_artist)
        
        tracks_ids, tracks_hrefs = song_recom.search_for_song(track_title, track_artist)
        st.write(tracks_ids)
    elif track_title:
        st.write(track_title)
        tracks_ids, tracks_hrefs = song_recom.search_for_song(track_title, None)
        st.write(tracks_ids)
    
    ncols = len(tracks_ids)
    
    if ncols == 1:
        placeholder_recommendation = st.empty()
        with placeholder_recommendation:
            components.html(
                """<iframe style="border-radius:12px" 
                src="https://open.spotify.com/embed/track/{tracks_ids[0]}?utm_source=generator" 
                width="100%" height="352" 
                frameBorder="0" allowfullscreen="" 
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
            , height=400)
        agree = st.checkbox('This is the song I am talking about')
        if agree:
            song_recom.scale_new_entry(tracks_ids[0])
    elif ncols == 2:
        col_1,col_2= st.columns(ncols)
        
    else:
        col_1,col_2,col_3 = st.columns(ncols)
    
    if ncols > 1:
        with col_1:
            placeholder_recommendation = st.empty()
            with placeholder_recommendation:
                components.html(
                    f"""<iframe style="border-radius:12px" 
                    src="https://open.spotify.com/embed/track/{tracks_ids[0]}?utm_source=generator"
                    width="100%" height="352" 
                    frameBorder="0" allowfullscreen="" 
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
                , height=400)
            agree_id1 = st.button('I agree',key="opt1")
            if agree_id1:
                song_recom.scale_new_entry(tracks_ids[0])
        with col_2:
            placeholder_recommendation = st.empty()
            with placeholder_recommendation:
                components.html(
                    f"""<iframe style="border-radius:12px" 
                    src="https://open.spotify.com/embed/track/{tracks_ids[1]}?utm_source=generator"
                    width="100%" height="352" 
                    frameBorder="0" allowfullscreen="" 
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
                , height=400)
            agree_id2 = st.button('I agree',key="opt2")
            if agree_id2:
                song_recom.scale_new_entry(tracks_ids[1])
        if ncols == 3:
            with col_3:
                placeholder_recommendation = st.empty()
                with placeholder_recommendation:
                    components.html(
                        f"""<iframe style="border-radius:12px" 
                        src="https://open.spotify.com/embed/track/{tracks_ids[2]}?utm_source=generator"
                        width="100%" height="352" 
                        frameBorder="0" allowfullscreen="" 
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
                    , height=400)
                agree_id3 = st.button('I agree',key="opt3")
                if agree_id3:
                    song_recom.scale_new_entry(tracks_ids[2])

        
#%% Show result
placeholder_recommendation = st.empty()
with placeholder_recommendation:
    components.html(
        """<iframe style="border-radius:12px" 
        src="https://open.spotify.com/embed/track/0yLdNVWF3Srea0uzk55zFn?utm_source=generator" 
        width="100%" height="352" 
        frameBorder="0" allowfullscreen="" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
    , height=400)
