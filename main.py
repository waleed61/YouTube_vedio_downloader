from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ YouTube Direct Link API is Running'

@app.route('/get-url')
def get_url():
    youtube_url = request.args.get("url")

    if not youtube_url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'noplaylist': True,
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/115.0.0.0 Safari/537.36'
                )
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return jsonify({
                "title": info.get("title"),
                "url": info.get("url")
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
