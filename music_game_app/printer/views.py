from django.shortcuts import render
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def printer(request):
    load_dotenv()
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

    if request.method == "POST":
        playlist_id = request.POST.get("playlist-input-id")
        results = sp.playlist(playlist_id=playlist_id)
    else:
        results = sp.playlist(playlist_id="37i9dQZF1DX36edUJpD76c")

    context={"results": results}
    return render(request, "printer.html", context)
