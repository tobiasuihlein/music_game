from django.shortcuts import render
from django.http import FileResponse, HttpResponse
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
        playlist_id="37i9dQZF1DX4jP4eebSWR9"
    
    try:
        results = sp.playlist(playlist_id=playlist_id)
    except:
        print("error in retrieving playlist / invalid URL")
        return HttpResponse("<h1>Error: Invalid URL</h1>")

    playlist_dict = create_dict(results)

    request.session['playlist_dict'] = playlist_dict
    request.session.set_expiry(0)

    context={"playlist_id": playlist_id, "results": results, "playlist_dict": playlist_dict}
    return render(request, "dashboard.html", context)


def display_pdf(request):
    if request.method == "POST":
        playlist_id = request.POST.get("playlist-id")
        print(playlist_id)

    if 'playlist_dict' in request.session:
        playlist_dict = request.session['playlist_dict']
    else:
        print("No playlist in session data")
        return HttpResponse("<h1>Error: Playlist not in Session Data</h1>")

    tracks = playlist_dict['track_items']
    
    if tracks:
        buffer = create_game_cards(playlist_name=playlist_dict['playlist_name'], all_songs=tracks, card_size_in_mm=60)
        buffer = reorder_pdf(buffer)
        return FileResponse(buffer, as_attachment=False, filename='your_pdf.pdf')
    else:
        print("No tracks found")
        return HttpResponse("<h1>Error: List of Tracks is Emtpy</h1>")
        
    
    
