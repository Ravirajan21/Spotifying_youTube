import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify setup

client_credentials_manager = SpotifyClientCredentials(client_id='Your_Client_id', client_secret='Your_Client_Secret')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# YouTube setup
youtube_scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
youtube_flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', youtube_scopes)
youtube_credentials = youtube_flow.run_local_server()
youtube = build('youtube', 'v3', credentials=youtube_credentials)

# Function to get tracks from Spotify playlist
def get_spotify_tracks(spotify_playlist_id):
    results = spotify.playlist_tracks(spotify_playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append(f"{track['name']} {track['artists'][0]['name']}")
    return tracks

# Function to create a YouTube playlist and add tracks
def create_youtube_playlist_from_spotify(spotify_playlist_id, playlist_title):
    # Create YouTube playlist
    create_playlist_response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_title,
                "description": "Playlist migrated from Spotify",
                "tags": ["Spotify", "Music", "Migration"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    ).execute()

    playlist_id = create_playlist_response["id"]

    # Get tracks from Spotify
    tracks = get_spotify_tracks(spotify_playlist_id)

    # Search and add tracks to YouTube playlist
    for track in tracks:
        search_response = youtube.search().list(
            q=track,
            part="snippet",
            maxResults=1,
            type="video"
        ).execute()

        if search_response["items"]:
            video_id = search_response["items"][0]["id"]["videoId"]

            # Add video to playlist
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()

# Example usage
spotify_playlist_id = 'Playlist_id'
create_youtube_playlist_from_spotify(spotify_playlist_id, "My Spotify Playlist on YouTube")