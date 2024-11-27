FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/music_game_app
ENV DJANGO_SETTINGS_MODULE=music_game_app.settings.staging_local

# Collect static files to serve
RUN mkdir -p /app/staticfiles
RUN chmod -R 755 /app/staticfiles
RUN python music_game_app/manage.py collectstatic --noinput

# Update the wsgi path
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "music_game_app.wsgi:application"]