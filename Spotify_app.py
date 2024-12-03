import datetime
from logging.config import listen
from random import random

import streamlit as st
from openai import OpenAI  # Importing the client class
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import main_functions
import matplotlib.pyplot as plt

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
#color_parameter = st.color_picker("Select a Color","#00f900")

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

country_coordinates = {
    "United States": {"latitude": 37.0902, "longitude": -95.7129},
    "USA": {"latitude": 37.0902, "longitude": -95.7129},
    "Canada": {"latitude": 56.1304, "longitude": -106.3468},
    "United Kingdom": {"latitude": 55.3781, "longitude": -3.4360},
    "UK": {"latitude": 55.3781, "longitude": -3.4360},
    "Australia": {"latitude": -25.2744, "longitude": 133.7751},
    "Germany": {"latitude": 51.1657, "longitude": 10.4515},
    "France": {"latitude": 46.6034, "longitude": 1.8883},
    "Italy": {"latitude": 41.8719, "longitude": 12.5674},
    "Spain": {"latitude": 40.4637, "longitude": -3.7492},
    "Mexico": {"latitude": 23.6345, "longitude": -102.5528},
    "Brazil": {"latitude": -14.2350, "longitude": -51.9253},
    "Argentina": {"latitude": -38.4161, "longitude": -63.6167},
    "South Africa": {"latitude": -30.5595, "longitude": 22.9375},
    "India": {"latitude": 20.5937, "longitude": 78.9629},
    "China": {"latitude": 35.8617, "longitude": 104.1954},
    "Japan": {"latitude": 36.2048, "longitude": 138.2529},
    "South Korea": {"latitude": 35.9078, "longitude": 127.7669},
    "Russia": {"latitude": 61.5240, "longitude": 105.3188},
    "Sweden": {"latitude": 60.1282, "longitude": 18.6435},
    "Norway": {"latitude": 60.4720, "longitude": 8.4689},
    "Finland": {"latitude": 61.9241, "longitude": 25.7482},
    "Denmark": {"latitude": 56.2639, "longitude": 9.5018},
    "Netherlands": {"latitude": 52.1326, "longitude": 5.2913},
    "Belgium": {"latitude": 50.5039, "longitude": 4.4699},
    "Switzerland": {"latitude": 46.8182, "longitude": 8.2275},
    "Austria": {"latitude": 47.5162, "longitude": 14.5501},
    "New Zealand": {"latitude": -40.9006, "longitude": 174.8860},
    "Ireland": {"latitude": 53.1424, "longitude": -7.6921},
    "Portugal": {"latitude": 39.3999, "longitude": -8.2245},
    "Greece": {"latitude": 39.0742, "longitude": 21.8243},
    "Turkey": {"latitude": 38.9637, "longitude": 35.2433},
    "Saudi Arabia": {"latitude": 23.8859, "longitude": 45.0792},
    "United Arab Emirates": {"latitude": 23.4241, "longitude": 53.8478},
    "Egypt": {"latitude": 26.8206, "longitude": 30.8025},
    "Nigeria": {"latitude": 9.0820, "longitude": 8.6753},
    "Kenya": {"latitude": -1.286389, "longitude": 36.817223},
    "Israel": {"latitude": 31.0461, "longitude": 34.8516},
    "Pakistan": {"latitude": 30.3753, "longitude": 69.3451},
    "Indonesia": {"latitude": -0.7893, "longitude": 113.9213},
    "Philippines": {"latitude": 12.8797, "longitude": 121.7740},
    "Thailand": {"latitude": 15.8700, "longitude": 100.9925},
    "Vietnam": {"latitude": 14.0583, "longitude": 108.2772},
    "Malaysia": {"latitude": 4.2105, "longitude": 101.9758},
    "Singapore": {"latitude": 1.3521, "longitude": 103.8198},
    "Bangladesh": {"latitude": 23.6850, "longitude": 90.3563},
    "Sri Lanka": {"latitude": 7.8731, "longitude": 80.7718},
    "Nepal": {"latitude": 28.3949, "longitude": 84.1240},
    "Chile": {"latitude": -35.6751, "longitude": -71.5430},
    "Colombia": {"latitude": 4.5709, "longitude": -74.2973},
    "Peru": {"latitude": -9.1900, "longitude": -75.0152},
    "Venezuela": {"latitude": 6.4238, "longitude": -66.5897},
    "Cuba": {"latitude": 21.5218, "longitude": -77.7812},
}

# Tabs
ai_recommend, lyric_finder, music_journey,color_journey,date_finder = st.tabs(["AI Recommender", "Lyric Finder", "Emotion Journey", "Color Journey", "Date Finder"])

# AI Recommender Tab
with ai_recommend:
    # Input for mood or activity
    mood = st.text_input("Describe your mood or activity (e.g. Working Out)")

    if st.button("Get Song Recommendations"):
        if mood:
            # Get song recommendations from ChatGPT, including countries of origin
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": (
                        f"Suggest 10 song names for the following mood or activity: {mood}, "
                        f"from , including the countries the artists are from. "
                        "Provide the response in the format 'Song Name - Artist Name (Country)'."
                    )
                }],
                model="gpt-3.5-turbo",
            )
            suggestions = response.choices[0].message.content.strip()

            # Parse the suggestions into individual song entries
            song_entries = suggestions.split("\n")  # Assuming ChatGPT returns a line-separated list

            # Fetch Spotify track data for each song
            tracks_data = []
            map_data = []  # For mapping coordinates
            for entry in song_entries:
                try:
                    # Parse the entry into song name, artist, and country
                    parts = entry.split(" - ")
                    if len(parts) != 2:
                        continue
                    song_name, artist_with_country = parts
                    artist_parts = artist_with_country.rsplit("(", 1)
                    if len(artist_parts) != 2:
                        continue
                    artist_name = artist_parts[0].strip()
                    country = artist_parts[1].replace(")", "").strip()

                    # Search Spotify for the track
                    search_results = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)
                    if search_results['tracks']['items']:
                        track = search_results['tracks']['items'][0]
                        track_url = track['external_urls']['spotify']  # Spotify URL for the track
                        artist_data = track['artists'][0]
                        artist_url = artist_data['external_urls']['spotify']

                        # Add track data to list
                        tracks_data.append({
                            "Song Name": f"[{song_name.replace('\"', '')}]({track_url})",
                            "Artist": f"[{artist_name}]({artist_url})",
                            "Year Released": track['album'].get('release_date', 'Unknown').split('-')[0],
                            "Country": country
                        })

                        # Add map data
                        coordinates = country_coordinates.get(country)
                        if coordinates:
                            map_data.append({
                                "latitude": coordinates["latitude"],
                                "longitude": coordinates["longitude"],
                                "Artist": artist_name,
                                "Country": country
                            })
                except Exception as e:
                    st.error(f"Error fetching track for '{entry}': {e}")

            # Create a DataFrame for the table
            if tracks_data:
                df = pd.DataFrame(tracks_data)

                # Display the table
                st.info("Spotify Recommendations")
                st.markdown(
                    df.to_markdown(index=False, tablefmt="pipe"),
                    unsafe_allow_html=True,
                )

                st.info("Artists' Countries of Origin")
                # Create a DataFrame for the map
                if map_data:
                    map_df = pd.DataFrame(map_data)
                    st.map(map_df)
                    #st.write("Map Data:", map_df)
                    st.success("Songs fetched successfully!")

                else:
                    st.warning("No valid coordinates to map.")
            else:
                st.error("No tracks found for the given recommendations.")
        else:
            st.error("Please describe your mood or activity.")


# Lyric Finder Tab
with lyric_finder:
    # Input for lyrics or theme
    lyrics = st.text_area("Enter a snippet of lyrics or describe the theme (e.g. Mom's Spaghetti)")
    check_box = st.checkbox("Show AI Recommendations")
    if st.button("Find Songs"):
        if lyrics:
            # Fetch songs using OpenAI for suggestions
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Find songs with lyrics or themes like: {lyrics}",
                }],
                model="gpt-3.5-turbo",
            )
            matching_songs = response.choices[0].message.content.strip()


            # Spotify API Example for Searching Tracks
            search_results = sp.search(q=lyrics, type="track", limit=10)  # Fetch up to 10 matching songs

            # Parse Spotify search results into a table
            tracks_data = []
            for track in search_results['tracks']['items']:
                track_name = track['name']
                artist_data = track['artists'][0]  # Take the first artist
                artist_name = artist_data['name']
                artist_url = artist_data['external_urls']['spotify']
                track_url = track['external_urls']['spotify']
                album_name = track['album']['name']
                release_date = track['album'].get('release_date', 'Unknown').split('-')[0]

                # Add track data to list
                tracks_data.append({
                    "Song Name": f"[{track_name}]({track_url})",
                    "Artist": f"[{artist_name}]({artist_url})",
                    "Album": album_name,
                    "Year Released": release_date
                })

            # Create a DataFrame for the results
            if tracks_data:
                df = pd.DataFrame(tracks_data)

                # Display the table
                st.info("Spotify Matches")
                st.markdown(
                    df.to_markdown(index=False, tablefmt="pipe"),
                    unsafe_allow_html=True,
                )

                # Display AI suggestions
                if check_box:
                    st.info("AI-Suggested Songs")
                    st.write(matching_songs)

                st.success("Lyrics fetched successfully!")
            else:
                st.error("No matching songs found.")

# Music Journey Tab
with music_journey:
    # Input for starting and ending emotions
    start_emotion = st.text_input("Starting mood (e.g. Sad)")
    end_emotion = st.text_input("Ending mood (e.g. Happy)")

    # Slider to select the number of songs
    total_songs = st.slider("Select the number of songs to fetch:", min_value=5, max_value=15, value=10, key="journey")

    if st.button("Create Emotion Journey"):
        if start_emotion and end_emotion:
            # Fetch a music journey map from AI
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": (
                        f"Create a journey of music from {start_emotion} to {end_emotion} with a total of {total_songs} songs. "
                        "Include genres, sample songs, and the mood of each song. Provide the response in the format "
                        "'\"Song Name\" by Artist Name'."
                    ),
                }],
                model="gpt-3.5-turbo",
            )
            journey = response.choices[0].message.content.strip()

            # Parse AI response into song entries
            import re
            song_entries = re.findall(r'"(.*?)" by (.*?)', journey, re.MULTILINE)

            # Warn if fewer songs are available
            if len(song_entries) < total_songs:
                st.warning(f"The AI response included only {len(song_entries)} songs, but you requested {total_songs}.")

            # Fetch Spotify data for each song
            tracks_data = []
            song_labels = []
            listen_counts = []  # To store numerical listen counts for the bar chart

            for i, (song_name, artist_name) in enumerate(song_entries[:total_songs]):
                try:
                    # Search Spotify for the track
                    search_results = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)
                    if search_results['tracks']['items']:
                        track = search_results['tracks']['items'][0]
                        track_url = track['external_urls']['spotify']  # Spotify URL for the track
                        artist_data = track['artists'][0]
                        artist_url = artist_data.get('external_urls', {}).get('spotify', None)
                        album_name = track['album']['name']
                        release_date = track['album'].get('release_date', 'Unknown').split('-')[0]
                        popularity = track.get('popularity', 0)  # Popularity score (0-100)

                        # Translate popularity to an approximate listens count
                        listens = (popularity * 10_000_000)  # Numerical listens count
                        if popularity == 0:
                            listens = 1_000_000  # Fallback value for low popularity

                        # Add track data to list
                        tracks_data.append({
                            "Song Name": f"[{song_name}]({track_url})",
                            "Artist": f"[{artist_data['name']}]({artist_url})" if artist_url else artist_data['name'],
                            "Album": album_name,
                            "Year Released": release_date,
                            "Amount of Listens": f"{listens:,.0f}",
                        })

                        # Add song name and listens for the chart
                        song_labels.append(song_name)
                        listen_counts.append(listens)
                    else:
                        st.warning(f"Spotify could not find the song '{song_name}' by '{artist_name}'.")
                except Exception as e:
                    st.error(f"Error fetching track for '{song_name}' by '{artist_name}': {e}")

            # Create a DataFrame for the results
            if tracks_data:
                df = pd.DataFrame(tracks_data)

                # Display the table
                st.info("Spotify Journey Tracks")
                st.markdown(
                    df.to_markdown(index=False, tablefmt="pipe"),
                    unsafe_allow_html=True,
                )
                st.success(f"Music journey created successfully with {len(tracks_data)} songs!")

                # Plot the bar chart for listens
                if song_labels and listen_counts:
                    st.bar_chart(
                        pd.DataFrame({
                            "Listens": listen_counts
                        }, index=song_labels),
                        use_container_width=True
                    )
            else:
                st.error("No tracks found for the journey.")

with color_journey:
    color_parameter = st.color_picker("What color are you feeling?", "#00f900")
    total_songs_2 = st.slider("Select the number of songs to fetch:", min_value=5, max_value=15, value=10, key="color")

    if st.button("Create Color Journey!"):
        # Fetch data from ChatGPT
        response = openai_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Find {total_songs_2} songs based on this color: {color_parameter}. Provide the response in the format "
                           "'\"Song Name\" by Artist Name'.",
            }],
            model="gpt-3.5-turbo",
        )
        color_journey = response.choices[0].message.content.strip()

        # Parse ChatGPT Response
        import re

        song_entries = re.findall(r'"(.*?)" by (.*?)', color_journey, re.MULTILINE)

        # Warn if fewer songs are available
        if len(song_entries) < total_songs_2:
            st.warning(f"The AI response included only {len(song_entries)} songs, but you requested {total_songs_2}.")

        # Fetch Spotify data for each song
        tracks_data = []
        for song_name, artist_name in song_entries[:total_songs_2]:
            try:
                # Search Spotify for the track
                search_results = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)
                if search_results['tracks']['items']:
                    track = search_results['tracks']['items'][0]
                    track_url = track['external_urls']['spotify']  # Spotify URL for the track
                    artist_data = track['artists'][0]
                    artist_url = artist_data.get('external_urls', {}).get('spotify', None)
                    album_name = track['album']['name']
                    release_date = track['album'].get('release_date', 'Unknown').split('-')[0]

                    # Add track data to list
                    tracks_data.append({
                        "Song Name": f"[{song_name}]({track_url})",
                        "Artist": f"[{artist_data['name']}]({artist_url})" if artist_url else artist_data['name'],
                        "Album": album_name,
                        "Year Released": release_date,
                    })
                else:
                    st.warning(f"Spotify could not find the song '{song_name}' by '{artist_name}'.")
            except Exception as e:
                st.error(f"Error fetching track for '{song_name}' by '{artist_name}': {e}")

        # Create and display a DataFrame for the results
        if tracks_data:
            df = pd.DataFrame(tracks_data)

            # Display the table
            st.info(f"Color Journey Tracks for {color_parameter}")
            st.markdown(
                df.to_markdown(index=False, tablefmt="pipe"),
                unsafe_allow_html=True,
            )
            st.success(f"Color journey created successfully with {len(tracks_data)} songs!")
        else:
            st.error("No tracks found for the color journey.")

with date_finder:
    st.write("Find out which songs were popular on a date!")
    yesterday = datetime.datetime.today()
    min_date = datetime.date(yesterday.year - 70, 1, 1)  # Allow dates from up to 70 years ago
    date = st.date_input("Enter a date:", min_value=min_date, max_value=yesterday)

    if st.button("Search date!"):
        if date:
            # Fetch popular songs from ChatGPT based on the date
            response = openai_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": (
                        f"Find the top 5 most popular songs based on this date: {date}. "
                        "Provide the response in the format 'Song Name - Artist Name'."
                    )
                }],
                model="gpt-3.5-turbo",
            )
            song_of_the_day = response.choices[0].message.content.strip()

            # Handle AI response indicating no data
            if song_of_the_day.startswith("Sorry") or "real-time data" in song_of_the_day:
                st.error("Cannot access data for that date right now, try another date.")
            else:
                # Parse the AI response into song entries
                song_entries = song_of_the_day.split("\n")  # Assuming each song is on a new line

                # Fetch Spotify data for each song
                tracks_data = []
                song_names = []
                listen_counts = []  # To store numerical listen counts for the bar chart

                for entry in song_entries:
                    try:
                        # Parse the entry into song name and artist
                        if " - " in entry:
                            song_name, artist_name = entry.split(" - ")
                        elif " by " in entry:
                            song_name, artist_name = entry.split(" by ")
                        else:
                            continue  # Skip entries not in expected format

                        # Clean up song and artist names
                        song_name = song_name.strip('" ').strip()
                        artist_name = artist_name.strip()

                        # Search Spotify for the track
                        search_results = sp.search(q=f"{song_name} {artist_name}", type="track", limit=1)
                        if search_results['tracks']['items']:
                            track = search_results['tracks']['items'][0]
                            track_url = track['external_urls']['spotify']  # Spotify URL for the track
                            artist_data = track['artists'][0]
                            artist_url = artist_data['external_urls']['spotify']
                            album_name = track['album']['name']
                            release_date = track['album'].get('release_date', 'Unknown').split('-')[0]
                            popularity = track.get('popularity', 0)  # Popularity score (0-100)

                            # Translate popularity to an approximate listens count
                            listens = (popularity * 10_000_000)  # Numerical listens count
                            if popularity == 0:
                                listens = 1_000_000  # Fallback value for low popularity

                            # Add track data to list
                            tracks_data.append({
                                "Song Name": f"[{track['name']}]({track_url})",
                                "Artist": f"[{artist_data['name']}]({artist_url})",
                                "Album": album_name,
                                "Year Released": release_date,
                                "Amount of Listens": f"{listens:,.0f}",
                            })

                            # Add song name and listens to chart data
                            song_names.append(track['name'])
                            listen_counts.append(listens)
                        else:
                            st.warning(f"Spotify could not find the song '{song_name}' by '{artist_name}'.")
                    except Exception as e:
                        st.error(f"Error fetching track for '{entry}': {e}")

                # Create a DataFrame for the results
                if tracks_data:
                    df = pd.DataFrame(tracks_data)

                    # Display the table
                    st.info(f"Spotify Tracks for {date.month}/{date.day}/{date.year}")
                    st.markdown(
                        df.to_markdown(index=False, tablefmt="pipe"),
                        unsafe_allow_html=True,
                    )

                    # Plot the bar chart
                    if song_names and listen_counts:
                        st.info("Songs' Popularity and Listen Counts")
                        st.bar_chart(
                            pd.DataFrame({
                                "Listens": listen_counts
                            }, index=song_names),
                            use_container_width=True
                        )
                        st.success(f"Search successful with {len(tracks_data)} songs found!")

                else:
                    st.error("No tracks found for the date.")
