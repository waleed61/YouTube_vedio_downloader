import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for browser access

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Serve frontend at root
@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

# API endpoint for link extraction
@app.route('/get-url', methods=['POST'])
def extract_direct_url():
    # Validate input
    if not request.is_json:
        return jsonify({'error': 'Invalid request format. Send JSON with YouTube URL.'}), 400
        
    data = request.get_json()
    youtube_url = data.get('url', '').strip()
    
    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400
    
    # Configure yt-dlp with Render-friendly settings
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Get highest quality
        'quiet': True,
        'no_warnings': True,
        'simulate': True,  # Don't download, just extract
        'force_generic_extractor': True,
        'cachedir': False,  # Disable cache for Render's ephemeral storage
        'http_headers': {
            # Spoof Chrome browser headers
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.youtube.com/'
        }
    }
    
    try:
        logger.info(f"Processing URL: {youtube_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info without downloading
            info = ydl.extract_info(youtube_url, download=False)
            
            # Validate extracted data
            if not info or 'url' not in info:
                return jsonify({'error': 'Failed to extract video information'}), 500
                
            return jsonify({
                'title': info.get('title', 'Untitled'),
                'direct_url': info['url']
            })
            
    except yt_dlp.utils.DownloadError as e:
        # Handle specific YouTube errors
        error_msg = str(e).lower()
        if 'private' in error_msg:
            logger.warning(f"Private video error: {youtube_url}")
            return jsonify({'error': 'Private video - requires login'}), 403
        elif 'age restricted' in error_msg:
            logger.warning(f"Age-restricted video: {youtube_url}")
            return jsonify({'error': 'Age-restricted content - cannot extract'}), 403
        elif 'unavailable' in error_msg:
            logger.warning(f"Unavailable video: {youtube_url}")
            return jsonify({'error': 'Video unavailable or removed'}), 404
        elif 'too many requests' in error_msg:
            logger.error("YouTube rate limit exceeded")
            return jsonify({'error': 'YouTube rate limit exceeded - try again later'}), 429
        else:
            logger.error(f"Download error: {str(e)}")
            return jsonify({'error': f'YouTube extraction failed: {str(e)}'}), 500
            
    except Exception as e:
        # General error handling
        logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Gunicorn logger integration
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Start application (Render-compatible)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
