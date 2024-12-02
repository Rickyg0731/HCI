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
    "USA": {"latitude": 37.0902, "longitude": -95.7129},
    "Canada": {"latitude": 56.1304, "longitude": -106.3468},
    "United Kingdom": {"latitude": 55.3781, "longitude": -3.4360},
    "Australia": {"latitude": -25.2744, "longitude": 133.7751},
    "Germany": {"latitude": 51.1657, "longitude": 10.4515},
    # Add more countries as needed
}

# Tabs
ai_recommend, lyric_finder, music_journey = st.tabs(["AI Recommender", "Lyric Finder", "Emotion Journey"])

# AI Recommender Tab
with ai_recommend:
    # Input for mood or activity
    mood = st.text_input("Describe your mood or activity (e.g. Working Out)")

    # Date range input
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From (YYYY-MM-DD):")
    with col2:
        to_date = st.date_input("To (YYYY-MM-DD):")

    if st.button("Get Song Recommendations"):
        if mood:
            # Check if date range is valid
            if from_date > to_date:
                st.error("Invalid date range: 'From' date cannot be after 'To' date.")
            else:
                # Format the date range for the ChatGPT prompt
                formatted_from_date = from_date.strftime("%Y-%m-%d")
                formatted_to_date = to_date.strftime("%Y-%m-%d")

                # Get song recommendations from ChatGPT, including countries of origin
                response = openai_client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": (
                            f"Suggest 10 song names for the following mood or activity: {mood} that released from {from_date} to {to_date}, "
                            f"from {formatted_from_date} to {formatted_to_date}, including the countries the artists are from. "
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
                    st.success("Songs fetched successfully!")

                    # Create a DataFrame for the map
                    if map_data:
                        map_df = pd.DataFrame(map_data)
                        st.map(map_df)
                        st.write("Map Data:", map_df)
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
    total_songs = st.slider("Select the number of songs to fetch:", min_value=5, max_value=15, value=10)

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

            # Generate linear progression for mood values
            start_mood_values = list(range(10, 10 - total_songs, -1))  # Linearly decreases from 10
            end_mood_values = list(range(1, total_songs + 1))          # Linearly increases from 1

            # Fetch Spotify data for each song
            tracks_data = []
            song_labels = []
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

                        # Add track data to list
                        tracks_data.append({
                            "Song Name": f"[{song_name}]({track_url})",
                            "Artist": f"[{artist_data['name']}]({artist_url})" if artist_url else artist_data['name'],
                            "Album": album_name,
                            "Year Released": release_date,
                        })

                        # Add song label for the chart
                        song_labels.append(song_name)
                    else:
                        st.warning(f"Spotify could not find the song '{song_name}' by '{artist_name}'.")
                except Exception as e:
                    st.error(f"Error fetching track for '{song_name}' by '{artist_name}': {e}")

            # Create a DataFrame for the bar chart
            if tracks_data:
                bar_chart_data = pd.DataFrame({
                    "Starting Mood": start_mood_values[:len(song_labels)],
                    "Ending Mood": end_mood_values[:len(song_labels)]
                }, index=song_labels)

                # Display the table
                df = pd.DataFrame(tracks_data)
                st.info("Spotify Journey Tracks")
                st.markdown(
                    df.to_markdown(index=False, tablefmt="pipe"),
                    unsafe_allow_html=True,
                )
                st.success(f"Music journey created successfully with {len(tracks_data)} songs!")

                # Plot the bar chart for mood progression
                st.bar_chart(bar_chart_data, use_container_width=True)

                # Add a legend or information about starting and ending moods
                st.caption(f"Bar Chart shows the transition from Starting Mood ({start_emotion}) to Ending Mood ({end_emotion}).")
            else:
                st.error("No tracks found for the journey.")
