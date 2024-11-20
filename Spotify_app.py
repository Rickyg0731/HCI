import datetime

import streamlit as st
from openai import OpenAI  # Importing the client class
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import main_functions

my_keys = main_functions.read_from_file("api_Keys.json")
# Spotify API Configuration
SPOTIFY_CLIENT_ID = my_keys["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET =  my_keys["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI =  my_keys["SPOTIFY_REDIRECT_URI"]
scope =  my_keys["scope"]
key = my_keys["open_ai_key"]

# OpenAI Client Configuration
openai_client = OpenAI(
    api_key=key
)

# Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=scope))

# Page Configuration
st.set_page_config(
    page_title="Spotify AI",
    page_icon="🎵",
    layout="wide",
)

# Add top banner
st.markdown(
    """
    <style>
    .top-banner {
        background-color: #1DB954;
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
    }
    .spotify-logo {
        height: 30px;
        vertical-align: middle;
    }
    </style>
    <div class="top-banner">
        <img src="https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_White.png" class="spotify-logo" />
        AI
    </div>
    """,
    unsafe_allow_html=True,
)

# Main Content
#st.subheader("Welcome to Spotify AI")

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Tabs
ai_recommend, lyric_finder, music_journey, color_journey, date_finder = st.tabs(["AI Recommender", "Lyric Finder", "Emotion Journey", "Color Journey", "Date Finder"])

# AI Recommender Tab
with ai_recommend:
    #st.write("AI Recommender")
    mood = st.text_input("Describe your mood or activity:")
    if st.button("Get Song Recommendations"):
        if mood:
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Suggest music genres or songs for the following mood or activity: {mood}",
                }],
                model="gpt-3.5-turbo",
            )
            suggestions = response.choices[0].message.content.strip()
            st.write(f"AI Suggestions: {suggestions}")

            # Spotify API Example for Recommendations
            recommended_tracks = sp.recommendations(seed_genres=["pop", "rock"], limit=5)
            st.write("Spotify Recommendations:")
            for track in recommended_tracks['tracks']:
                track_name = track['name']
                artists = ', '.join([artist['name'] for artist in track['artists']])
                track_preview_url = track.get('preview_url')  # Get the preview URL (if available)

                st.write(f"{track_name} by {artists}")

                if track_preview_url:
                    st.audio(track_preview_url, format="audio/mp3")
                else:
                    st.write("Preview not available for this track.")

# Lyric Finder Tab
with lyric_finder:
    #st.write("Lyric Finder")
    lyrics = st.text_area("Enter a snippet of lyrics or describe the theme:")
    if st.button("Find Songs"):
        if lyrics:
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Find songs with lyrics or themes like: {lyrics}",
                }],
                model="gpt-3.5-turbo",
            )
            matching_songs = response.choices[0].message.content.strip()
            st.write(f"AI Suggestions: {matching_songs}")

            # Spotify API Example for Searching Tracks
            search_results = sp.search(q=lyrics, type="track", limit=5)
            st.write("Spotify Matches:")
            for track in search_results['tracks']['items']:
                st.write(f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")

# Music Journey Tab
with music_journey:
   # st.write("Music Journey Map")
    start_emotion = st.text_input("Enter your starting emotion:")
    end_emotion = st.text_input("Enter your ending emotion:")
    if st.button("Create Emotion Journey"):
        if start_emotion and end_emotion:
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Create a journey of music from {start_emotion} to {end_emotion}. Include genres and sample songs.",
                }],
                model="gpt-3.5-turbo",
            )
            journey = response.choices[0].message.content.strip()
            st.write(f"AI Journey Map: {journey}")

            # Spotify Recommendations for Music Journey
            genres = ["chill", "dance", "acoustic"]
            journey_tracks = sp.recommendations(seed_genres=genres, limit=5)
            st.write("Spotify Journey Tracks:")
            for track in journey_tracks['tracks']:
                st.write(f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")

with color_journey:
    color_parameter = st.color_picker("What color are you feeling?", "#00f900")
    if color_parameter:
        response = openai_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Find songs based on this color: {color_parameter}. Include genres and sample songs.",
            }],
            model="gpt-3.5-turbo",
        )
        journey = response.choices[0].message.content.strip()

        genres = ["chill", "dance", "acoustic"]
        journey_tracks = sp.recommendations(seed_genres=genres, limit=5)
        st.write("Tracks based on your color:")
        for track in journey_tracks['tracks']:
            st.write(f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")

with date_finder:
    st.write("Find out which songs were popular on a date!")
    yesterday = datetime.datetime.today()
    min_date = datetime.date(yesterday.year - 70, 1, 1)
    date = st.date_input("Enter a date:", format="MM/DD/YYYY", min_value= min_date, max_value=yesterday)
    if date:
        response = openai_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Find the most popular songs based on this date: {date}. Only give me the name of the song and the artist.",
            }],
            model="gpt-3.5-turbo",
        )
        song_of_the_day = response.choices[0].message.content.strip()

        st.write(f"Top Song of {date.month}/{date.day}/{date.year}")
        song = sp.search(song_of_the_day)
        st.write(song_of_the_day)
#        st.write(f"Track: {song['tracks']['items'][0]['title']} by {song['tracks']['items'][0]['artists']}")
