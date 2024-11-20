from django.shortcuts import render
from django.http import FileResponse
from dotenv import load_dotenv
from django.shortcuts import render
import io
from reportlab.pdfgen import canvas  # pip install reportlab
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .utils.helpers import *
from .utils.printer import *


def dashboard(request):
    load_dotenv()
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

    if request.method == "POST":
        user_input = request.POST.get("playlist-input-id")
        playlist_id = get_playlist_id_from_url(user_input)
    else:
        playlist_id="37i9dQZF1DX36edUJpD76c"
    
    results = sp.playlist(playlist_id=playlist_id)

    playlist_dict = create_dict(results)

    request.session['playlist_dict'] = playlist_dict

    context={"playlist_id": playlist_id, "results": results, "playlist_dict": playlist_dict}
    return render(request, "dashboard.html", context)


def display_pdf(request):
    if request.method == "POST":
        playlist_id = request.POST.get("playlist-id")
        print(playlist_id)
    
    sp = SpotifyAPI()
    print(f"\nFetching tracks from playlist...")
    tracks = sp.get_playlist_tracks(playlist_id)
    
    if tracks:
        print(f"\nSuccessfully found {len(tracks)} tracks")
        print("\nGenerating cards PDF...")
        buffer = create_game_cards(tracks)
        return FileResponse(buffer, as_attachment=False, filename='your_pdf.pdf')
    else:
        print("No tracks found")
    
    
