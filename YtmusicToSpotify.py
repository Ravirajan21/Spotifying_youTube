import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Load configuration from JSON file
with open('configs.json') as config_file:
    config = json.load(config_file)

sp_config = config['spotify']
yt_config = config['youtube']
playlist_config = config['playlist']

# Spotify setup
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=sp_config['client_id'],
                                                    client_secret=sp_config['client_secret'],
                                                    redirect_uri=sp_config['redirect_uri'],
                                                    scope='playlist-modify-public'))

# YouTube setup
yt_scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
yt_flow = InstalledAppFlow.from_client_secrets_file(yt_config['client_secrets_file'], yt_scopes)
yt_credentials = yt_flow.run_local_server()
youtube = build('youtube', 'v3', credentials=yt_credentials)

# Function to get tracks from YouTube playlist
def get_youtube_tracks(youtube_playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=youtube_playlist_id,
        maxResults=50
    )
    response = request.execute()
    tracks = []
    for item in response['items']:
        title = item['snippet']['title']
        tracks.append(title)
    return tracks

# Function to create a Spotify playlist and add tracks
def create_spotify_playlist_from_youtube(youtube_playlist_id, playlist_name):
    # Get tracks from YouTube
    yt_tracks = get_youtube_tracks(youtube_playlist_id)

    # Create Spotify playlist
    user_id = spotify.me()['id']
    playlist = spotify.user_playlist_create(user=user_id, name=playlist_name, public=True)

    sp_track_ids = []
    for track in yt_tracks:
        results = spotify.search(q=track, type='track', limit=1)
        if results['tracks']['items']:
            sp_track_ids.append(results['tracks']['items'][0]['id'])

    # Add tracks to Spotify playlist
    spotify.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=sp_track_ids)

youtube_playlist_id = playlist_config['youtube_playlist_id']
create_spotify_playlist_from_youtube(youtube_playlist_id, "My YouTube Playlist on Spotify")
