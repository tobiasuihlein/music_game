import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io

def get_playlist_id_from_url(url):
    """Extract playlist ID from Spotify URL"""
    if 'playlist/' in url:
        return url.split('playlist/')[1].split('?')[0]
    return url

def create_dict(api_response):
    title_list = []
    artist_list = []
    release_year_list = []
    preview_url_list = []
    id_list = []

    for track_item in api_response['tracks']['items']:
        title_list.append(track_item['track']['name'])
        artists = [artist['name'] for artist in track_item['track']['artists']]
        artist_list.append(artists)
        release_year_list.append(track_item['track']['album']['release_date'][0:4])
        preview_url_list.append(track_item['track']['preview_url'])
        id_list.append(track_item['track']['id'])

    df = pd.DataFrame({"title": title_list, "artists": artist_list, "release_year": release_year_list, "preview_url": preview_url_list, "id": id_list})

    playlist_dict = {}
    playlist_dict['track_items'] = df.to_dict('records')
    playlist_dict['total_songs'] = int(len(df))
    playlist_dict['available_songs'] = int(df['preview_url'].notna().sum())
    playlist_dict['playlist_name'] = api_response['name']

    return playlist_dict

def reorder_pdf(input_buffer):

    reader = PdfReader(input_buffer)
    writer = PdfWriter()

    writer.add_metadata(reader.metadata)

    page_count = len(reader.pages)
    for page_num in range(int(page_count/2)):
        writer.add_page(reader.pages[page_num])
        writer.add_page(reader.pages[page_num + int(page_count/2)])
    
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer