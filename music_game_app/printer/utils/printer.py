import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import io
import qrcode
import shutil


class QRCodeGenerator:
    def __init__(self):
        self.temp_dir = "temp_codes"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

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

def create_game_cards(playlist_name, all_songs, card_size_in_mm):

    songs = []
    for song in all_songs:
        if song['preview_url']:
            songs.append(song)

    # Card dimensions (50mm x 50mm)
    card_size = card_size_in_mm*mm
    padding = 5*mm
    id_margin = 3.5*mm
    
    # Initialize QR Code generator
    code_generator = QRCodeGenerator()
    
    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f"{playlist_name} Music Cards")
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
            c.setFont("Helvetica", 10)
            artist_text = truncate_text(', '.join(song['artists']), 80)
            artist_lines = []
            current_line = ""
            words = artist_text.split()
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 10) <= 0.85*card_size:
                    current_line = test_line
                else:
                    artist_lines.append(current_line)
                    current_line = word
            if current_line:
                artist_lines.append(current_line)

            title_text = truncate_text(song['title'], 80)
            title_lines = []
            current_line = ""
            words = title_text.split()
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 10) <= 0.85*card_size:
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
                10  # Additional padding
            )

            # Initialize starting y position to center content
            content_y = y + (card_size + total_height) / 2

            # Draw artist lines
            c.setFont("Helvetica", 10)
            for i, line in enumerate(artist_lines):
                artist_width = c.stringWidth(line, "Helvetica", 10)
                artist_x = x + (card_size - artist_width) / 2
                c.drawString(artist_x, content_y - (i * 15) + 15, line)

            # Adjust vertical position based on number of artist lines
            content_y -= (len(artist_lines) * 10 + 10)

            # Add year
            c.setFont("Helvetica-Bold", 20)
            year_width = c.stringWidth(str(song['release_year']), "Helvetica-Bold", 20)
            year_x = x + (card_size - year_width) / 2
            c.drawString(year_x, content_y, str(song['release_year']))

            # Add title
            content_y -= 25
            c.setFont("Helvetica", 10)
            for i, line in enumerate(title_lines):
                title_width = c.stringWidth(line, "Helvetica", 10)
                title_x = x + (card_size - title_width) / 2
                c.drawString(title_x, content_y - (i * 15), line)

            # Add small ID with increased margin
            c.setFont("Helvetica", 6)
            c.drawString(x + id_margin, y + id_margin, str(song_index + 1))
        
        if page < (len(songs) - 1) // (cards_per_row * cards_per_col):
            c.showPage()
    
    code_generator.cleanup()
    c.save()
    buffer.seek(0)
    return buffer