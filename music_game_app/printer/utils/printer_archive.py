import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Image
import requests
from dotenv import load_dotenv
import base64
import json
import io
from PIL import Image as PILImage
import qrcode

load_dotenv()

class SpotifyAPI:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.token = self.get_token()

    def get_token(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
        
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        result = requests.post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        return json_result["access_token"]

    def get_track_info(self, track_id):
        """Get detailed track info including preview URL"""
        track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        track_result = requests.get(track_url, headers=headers)
        track_json = json.loads(track_result.content)
        
        if "error" in track_json:
            raise Exception(f"Track fetch error: {track_json['error']['message']}")
        
        # Get album info for release date
        album_id = track_json["album"]["id"]
        album_url = f"https://api.spotify.com/v1/albums/{album_id}"
        
        album_result = requests.get(album_url, headers=headers)
        album_json = json.loads(album_result.content)
        
        if not track_json.get("preview_url"):
            raise Exception("No preview URL available")
            
        return {
            "id": track_json["id"],
            "title": track_json["name"],
            "artist": track_json["artists"][0]["name"],
            "preview_url": track_json["preview_url"],
            "year": album_json["release_date"][:4],
            "spotify_url": track_json["external_urls"]["spotify"]
        }
    

    def get_playlist_tracks(self, playlist_id):
        """Fetch all tracks from a playlist"""
        valid_tracks = []
        offset = 0
        limit = 100  # Maximum allowed by Spotify API
        
        while True:
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {
                "offset": offset,
                "limit": limit,
                "fields": "items(track(id,name,artists,album(release_date))),next"
            }
            
            result = requests.get(url, headers=headers, params=params)
            json_result = json.loads(result.content)
            
            if "error" in json_result:
                print(f"Error fetching playlist: {json_result['error']['message']}")
                return []
            
            # Process each track
            for item in json_result["items"]:
                if item["track"] and item["track"]["id"]:
                    try:
                        track_info = self.get_track_info(item["track"]["id"])
                        valid_tracks.append(track_info)
                        #print(f"✓ Added: {track_info['title']} by {track_info['artist']} ({track_info['year']})")
                    except Exception as e:
                        track_name = item["track"]["name"]
                        artist_name = item["track"]["artists"][0]["name"]
                        #print(f"✗ Skipped: {track_name} by {artist_name} - {str(e)}")
            
            # Check if we've got all tracks
            if len(json_result["items"]) < limit:
                break
                
            offset += limit
        
        return valid_tracks


class QRCodeGenerator:
    def __init__(self):
        self.temp_dir = "temp_codes"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def generate_qr_code(self, preview_url, track_id):
        """Generate QR code for the preview URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(preview_url)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        png_path = os.path.join(self.temp_dir, f"{track_id}.png")
        qr_image.save(png_path)
        
        return png_path

def truncate_text(text, max_length):
    """Truncate text and add ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def create_game_cards(songs):

    print(songs[0])

    # Card dimensions (50mm x 50mm)
    card_size = 50*mm
    padding = 5*mm
    id_margin = 3.5*mm
    
    # Initialize QR Code generator
    code_generator = QRCodeGenerator()
    
    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Calculate cards per page
    cards_per_row = int(width // card_size)
    cards_per_col = int(height // card_size)
    
    # Calculate margins to center cards on page
    margin_x = (width - (cards_per_row * card_size)) / 2
    margin_y = (height - (cards_per_col * card_size)) / 2
    
    # Front pages (QR Codes) - Remains exactly the same as before
    for page in range((len(songs) - 1) // (cards_per_row * cards_per_col) + 1):
        for i in range(cards_per_row * cards_per_col):
            song_index = page * (cards_per_row * cards_per_col) + i
            
            if song_index >= len(songs):
                break
                
            # Calculate position
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = margin_x + (col * card_size)
            y = height - margin_y - ((row + 1) * card_size)
            
            song = songs[song_index]
            
            # Draw card border
            c.rect(x, y, card_size, card_size)
            
            try:
                # Generate QR code for preview URL
                code_path = code_generator.generate_qr_code(song["preview_url"], song["id"])
                
                # Calculate dimensions for the QR code
                code_width = card_size - (2 * padding)
                code_height = code_width  # QR codes are square
                
                # Center the code vertically and horizontally
                code_x = x + padding
                code_y = y + padding
                
                # Draw the QR code
                c.drawImage(code_path, code_x, code_y, width=code_width, height=code_height)
                
                # Add small ID
                c.setFont("Helvetica", 6)
                c.drawString(x + id_margin, y + id_margin, str(song_index + 1))
                
            except Exception as e:
                print(f"Error processing QR code for {song['title']}: {str(e)}")
        
        if page < (len(songs) - 1) // (cards_per_row * cards_per_col):
            c.showPage()
    
    # Back pages (song information) - Modified order of content
    c.showPage()
    
    for page in range((len(songs) - 1) // (cards_per_row * cards_per_col) + 1):
        for i in range(cards_per_row * cards_per_col):
            song_index = page * (cards_per_row * cards_per_col) + i
            
            if song_index >= len(songs):
                break
            
            # Calculate position with margins - reverse columns for proper back printing
            row = i // cards_per_row
            col = cards_per_row - 1 - (i % cards_per_row)  # Reverse column order
            
            x = margin_x + (col * card_size)
            y = height - margin_y - ((row + 1) * card_size)
            
            song = songs[song_index]
            
            # Draw card border
            c.rect(x, y, card_size, card_size)
            
 
            # Add artist first (with line breaks)
            c.setFont("Helvetica", 8)
            artist_text = truncate_text(song['artist'], 40)
            artist_lines = []
            current_line = ""
            words = artist_text.split()
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 8) <= 40*mm:
                    current_line = test_line
                else:
                    artist_lines.append(current_line)
                    current_line = word
            if current_line:
                artist_lines.append(current_line)

            title_text = truncate_text(song['title'], 60)
            title_lines = []
            current_line = ""
            words = title_text.split()
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 8) <= 40*mm:
                    current_line = test_line
                else:
                    title_lines.append(current_line)
                    current_line = word
            if current_line:
                title_lines.append(current_line)

            # Calculate total content height
            total_height = (
                len(artist_lines) * 10 +  # Artist height (10 points per line)
                0 +  # Year height (increased for larger font)
                len(title_lines) * 10 +  # Title height (10 points per line)
                20  # Additional padding
            )

            # Initialize starting y position to center content
            content_y = y + (card_size + total_height) / 2

            # Draw artist lines
            c.setFont("Helvetica", 8)
            for i, line in enumerate(artist_lines):
                artist_width = c.stringWidth(line, "Helvetica", 8)
                artist_x = x + (card_size - artist_width) / 2
                c.drawString(artist_x, content_y - (i * 10) + 10, line)

            # Adjust vertical position based on number of artist lines
            content_y -= (len(artist_lines) * 10 + 10)

            # Add year
            c.setFont("Helvetica-Bold", 20)
            year_width = c.stringWidth(str(song['year']), "Helvetica-Bold", 20)
            year_x = x + (card_size - year_width) / 2
            c.drawString(year_x, content_y, str(song['year']))

            # Add title
            content_y -= 20
            c.setFont("Helvetica", 8)
            for i, line in enumerate(title_lines):
                title_width = c.stringWidth(line, "Helvetica", 8)
                title_x = x + (card_size - title_width) / 2
                c.drawString(title_x, content_y - (i * 10), line)

            # Add small ID with increased margin
            c.setFont("Helvetica", 6)
            c.drawString(x + id_margin, y + id_margin, str(song_index + 1))
        
        if page < (len(songs) - 1) // (cards_per_row * cards_per_col):
            c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer