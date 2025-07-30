from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return 'YouTube Direct Link API is Running'

@app.route('/get-url', methods=['GET'])
def get_url():
    youtube_url = request.args.get("url")

    if not youtube_url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    try:
        # yt_dlp will handle all YouTube URL formats automatically
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_url = info.get('url')
            return jsonify({
                "title": info.get("title"),
                "url": video_url
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
