import os
import logging
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
def serve_frontend():
    try:
        return send_file('static/index.html')
    except FileNotFoundError:
        logger.error("index.html not found in static folder")
        return "Frontend not available", 500

def normalize_youtube_url(url):
    """Convert any YouTube URL format to standard watch format"""
    # Mobile share link: https://youtu.be/VIDEO_ID
    youtu_be_match = re.match(r'https?://youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if youtu_be_match:
        return f'https://www.youtube.com/watch?v={youtu_be_match.group(1)}'
    
    # YouTube Shorts: https://www.youtube.com/shorts/VIDEO_ID
    shorts_match = re.match(r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})', url)
    if shorts_match:
        return f'https://www.youtube.com/watch?v={shorts_matche.group(1)}'
    
    # Mobile browser share link: https://www.youtube.com/watch?v=VIDEO_ID&feature=share
    feature_share_match = re.match(r'(https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11})&', url)
    if feature_share_match:
        return feature_share_match.group(1)
    
    # Already standard format
    if re.match(r'https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}', url):
        return url
    
    return None

@app.route('/get-url', methods=['POST'])
def extract_direct_url():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400
        
    data = request.get_json()
    youtube_url = data.get('url', '').strip()
    
    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400
    
    # Normalize URL to standard format
    normalized_url = normalize_youtube_url(youtube_url)
    if not normalized_url:
        return jsonify({'error': 'Invalid YouTube URL format'}), 400
    
    logger.info(f"Original URL: {youtube_url} -> Normalized URL: {normalized_url}")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'force_generic_extractor': True,
        'cachedir': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.youtube.com/'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(normalized_url, download=False)
            
            if not info or 'url' not in info:
                return jsonify({'error': 'Failed to extract video information'}), 500
            
            # Get best available format
            formats = info.get('formats', [])
            best_format = max(
                [f for f in formats if f.get('height')], 
                key=lambda x: x.get('height', 0), 
                default=None
            )
            
            return jsonify({
                'title': info.get('title', 'Untitled'),
                'direct_url': best_format['url'] if best_format else info['url'],
                'thumbnail': info.get('thumbnail', ''),
                'original_url': youtube_url,
                'normalized_url': normalized_url
            })
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if 'private' in error_msg:
            return jsonify({'error': 'Private video - requires login'}), 403
        elif 'age restricted' in error_msg:
            return jsonify({'error': 'Age-restricted content'}), 403
        elif 'unavailable' in error_msg:
            return jsonify({'error': 'Video unavailable or removed'}), 404
        elif 'too many requests' in error_msg:
            return jsonify({'error': 'YouTube rate limit exceeded - try again later'}), 429
        else:
            logger.error(f"Download error: {str(e)}")
            return jsonify({'error': f'YouTube extraction failed: {str(e)}'}), 500
            
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
