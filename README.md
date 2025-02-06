# Spotify QR Code Card Generator

A Django-based web application that transforms Spotify playlists into printable playing card PDFs, inspired by the music guessing game Hitster. The app generates cards displaying artist, song title, and release year on one side, and a QR Code of the song's preview link, which can be scanned using a companion web application for playback. The app is usable without Spotify account.

## Features

- Spotify playlist integration
- Automatic fetching of song previews and metadata
- Generation of playing cards
- PDF export functionality for printing
- Companion web app for scanning and playing preview clips

## Technologies Used

- Backend: Django
- Frontend: HTML, CSS, JavaScript
- APIs: Spotify Web API
- PDF Generation: PyPDF2
- QR Code Generation: qrcode
- Data Processing: pandas, numpy
- Visualization: matplotlib, seaborn

## Usage

1. Navigate to the application in your web browser
2. Enter a Spotify playlist URL
3. Wait for the app to fetch and analyze the songs
4. Preview the generated cards
5. Export to PDF for printing
6. Use the companion web app ([scanner-url]) to scan the printed cards and play preview clips

## Educational Purpose

This project is created solely for educational purposes to demonstrate:
- Integration with external APIs
- Backend development with Django
- Frontend development with vanilla JavaScript
- PDF and QR code generation
- Data processing and visualization
- Multi-app integration (main app + scanner)

## Acknowledgments

- Inspired by the Hitster music guessing game
- Built using the Spotify Web API
