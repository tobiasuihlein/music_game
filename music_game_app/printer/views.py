from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from dotenv import load_dotenv
from django.shortcuts import render
import os
import base64
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .utils.helpers import *
from .utils.printer import *


def index(request):
    return render(request, "index.html")


def dashboard(request):
    load_dotenv()
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

    if request.method == "POST":
        user_input = request.POST.get("playlist-input-id")
        playlist_id = get_playlist_id_from_url(user_input)
    else:
        # playlist_id="37i9dQZF1DX4jP4eebSWR9" # Hot Hits Deutschland
        # playlist_id="49jlHLZQ6fx6GvdmZKU1ll" # BRAVO Hits Party X-MAS
        playlist_id="26zIHVncgI9HmHlgYWwnDi" # Hitster Deutschland
    
    try:
        api_response = sp.playlist(playlist_id=playlist_id)
        playlist_name = api_response['name']
        result = api_response['tracks']
        track_items = result['items']
        while result['next']:
            result = sp.next(result)
            track_items.extend(result['items'])
        
    except:
        print("error in retrieving or creating playlist / invalid URL")
        return HttpResponse("<h1>Error in retrieving or creating playlist / Invalid URL</h1>")

    playlist_dict, distribution_chart_png = create_dict_and_chart(track_items, playlist_name)

    distribution_chart_base64 = base64.b64encode(distribution_chart_png).decode('utf-8')

    request.session['playlist_dict'] = playlist_dict
    request.session.set_expiry(0)

    context={"playlist_id": playlist_id, "playlist_dict": playlist_dict, "distribution_chart": distribution_chart_base64}
    return render(request, "dashboard.html", context)


def display_pdf(request):

    if 'playlist_dict' in request.session:
        playlist_dict = request.session['playlist_dict']
    else:
        print("No playlist in session data")
        return HttpResponse("<h1>Error: Playlist not in Session Data</h1>")
    
    if playlist_dict:
        buffer = create_game_cards(playlist_name=playlist_dict['playlist_name'], all_songs=playlist_dict['track_items'], card_size_in_mm=60)
        buffer = reorder_pdf(buffer)
        return FileResponse(buffer, as_attachment=False, filename='your_pdf.pdf')
    else:
        print("No tracks found")
        return HttpResponse("<h1>Error: List of Tracks is Emtpy</h1>")
        
    
    
