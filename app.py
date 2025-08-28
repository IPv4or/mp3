# app.py
import os
import uuid
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# --- Flask App Initialization & Config ---
app = Flask(__name__)
CORS(app)

# Use the local ephemeral filesystem for downloads
DOWNLOAD_FOLDER = 'static/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


# --- API Route for Conversion (Now handles cookies) ---
@app.route('/api/convert', methods=['POST'])
def convert_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL not provided"}), 400

    youtube_url = data['url']
    # Get cookie content from the request, default to None if not provided
    cookie_content = data.get('cookieContent')
    
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'quiet': True,
    }

    cookie_file_path = None
    try:
        # If cookie content was sent, write it to a temporary file
        if cookie_content:
            # Create a temporary file that will be automatically deleted
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_cookie_file:
                temp_cookie_file.write(cookie_content)
                cookie_file_path = temp_cookie_file.name
            ydl_opts['cookiefile'] = cookie_file_path

        # --- Perform the download ---
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            final_filename = f"{unique_id}.mp3"
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], final_filename)

            if not os.path.exists(file_path):
                 raise FileNotFoundError("Converted file was not found after download.")
            
            download_url = f"/download/{final_filename}"
            return jsonify({ "message": "Transmutation Complete", "downloadUrl": download_url, "title": info.get('title', 'Untitled') })

    except yt_dlp.utils.DownloadError as e:
        error_str = str(e).lower()
        if '429' in error_str or 'too many requests' in error_str:
            return jsonify({"error": "YouTube rate limit exceeded."}), 429
        else:
            error_text = str(e).split('ERROR: ')[-1]
            return jsonify({"error": f"{error_text}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        # Clean up the temporary cookie file if it was created
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)


# --- Download Route & Main ---
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
