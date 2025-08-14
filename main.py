from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return '✅ YouTube Direct Link API is Running'

@app.route('/info', methods=['POST'])
def get_info():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
            'forcejson': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            formats = info.get('formats', [])

            # Filter formats with both video and audio streams
            video_formats = []
            for fmt in formats:
                try:
                    if (fmt.get('vcodec') != 'none' and 
                        fmt.get('acodec') != 'none' and 
                        fmt.get('height') is not None):

                        # Get resolution
                        height = int(fmt['height'])

                        # Only consider resolutions up to 1080p
                        if height > 1080:
                            continue

                        # Get FPS
                        fps = fmt.get('fps', 30)
                        if not fps:
                            fps = 30

                        # Get bitrate
                        tbr = fmt.get('tbr', 0)
                        if not tbr:
                            tbr = 0

                        video_formats.append({
                            'height': height,
                            'fps': fps,
                            'tbr': tbr,
                            'format_id': fmt.get('format_id', ''),
                            'url': fmt.get('url', ''),
                            'ext': fmt.get('ext', 'mp4'),
                            'quality': f"{height}p"
                        })
                except:
                    continue

            # Sort by resolution descending
            video_formats.sort(key=lambda x: x['height'], reverse=True)

            # Remove duplicates - keep highest quality per resolution
            unique_videos = {}
            for fmt in video_formats:
                height = fmt['height']
                if height not in unique_videos:
                    unique_videos[height] = fmt

            # Get top 5 unique resolutions
            top_videos = list(unique_videos.values())
            top_videos.sort(key=lambda x: x['height'], reverse=True)
            top_videos = top_videos[:5]

            # Extract best audio format (audio only)
            audio_formats = []
            for fmt in formats:
                try:
                    if (fmt.get('acodec') != 'none' and 
                        fmt.get('vcodec') == 'none'):

                        tbr = fmt.get('tbr', 0)
                        if not tbr:
                            tbr = 0

                        audio_formats.append({
                            'format_id': fmt.get('format_id', ''),
                            'url': fmt.get('url', ''),
                            'ext': fmt.get('ext', 'mp3'),
                            'tbr': tbr,
                            'quality': f"{tbr:.0f}kbps",
                        })
                except:
                    continue

            # Sort audio by bitrate descending
            audio_formats.sort(key=lambda x: x['tbr'], reverse=True)
            best_audio = audio_formats[0] if audio_formats else None

            # Sanitize description
            description = info.get('description', '')
            sanitized_description = re.sub(r'\[.*?\]|\n', ' ', description)
            if len(sanitized_description) > 500:
                sanitized_description = sanitized_description[:500] + '...'

            return jsonify({
                "title": info.get("title", "Untitled Video"),
                "uploader": info.get("uploader", "Unknown Uploader"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"),
                "tags": info.get("tags", [])[:8],
                "description": sanitized_description,
                "formats": {
                    "video": top_videos,
                    "audio": best_audio
                }
            })

    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
