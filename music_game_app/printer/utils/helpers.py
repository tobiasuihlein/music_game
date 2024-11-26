import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import io
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import os

def get_playlist_id_from_url(url):
    """Extract playlist ID from Spotify URL"""
    if 'playlist/' in url:
        return url.split('playlist/')[1].split('?')[0]
    return url

def create_distribution_chart(df):

    df["release_year"] = df["release_year"].astype(int)
    df["is_available"] = df["preview_url"].notnull()
    years_range = max(df["release_year"]) - min(df["release_year"])

    width = 5
    height = years_range/8 + 2

    aspect = width / height

    fig = sns.displot(data=df, y="release_year", hue="is_available", 
                      height=height, aspect=aspect, discrete=True, multiple='stack', legend=False,
                      binwidth=1, shrink=0.8, edgecolor='none', palette=['#f87171', '#738cb5']) 
    fig.set_axis_labels("Count", "")

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return image_png

def create_dict_and_chart(track_items, playlist_name):
    title_list = []
    artist_list = []
    release_year_list = []
    preview_url_list = []
    id_list = []

    for track_item in track_items:
        title_list.append(track_item['track']['name'])
        artists = [artist['name'] for artist in track_item['track']['artists']]
        artist_list.append(artists)
        release_year_list.append(track_item['track']['album']['release_date'][0:4])
        preview_url_list.append(track_item['track']['preview_url'])
        id_list.append(track_item['track']['id'])

    df = pd.DataFrame({"title": title_list, "artists": artist_list, "release_year": release_year_list, "preview_url": preview_url_list, "id": id_list})

    distribution_chart_png = create_distribution_chart(df)

    playlist_dict = {}
    playlist_dict['track_items'] = df.to_dict('records')
    playlist_dict['total_songs'] = int(len(df))
    playlist_dict['available_songs'] = int(df['preview_url'].notna().sum())
    playlist_dict['playlist_name'] = playlist_name

    return playlist_dict, distribution_chart_png

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