# app.py
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# --- Flask App Initialization & Config ---
app = Flask(__name__)
CORS(app)

# --- IMPORTANT: Paths updated for Render's persistent disk ---
PERSISTENT_STORAGE_PATH = '/data'
DOWNLOAD_FOLDER = os.path.join(PERSISTENT_STORAGE_PATH, 'downloads')
COOKIES_FILE_PATH = os.path.join(PERSISTENT_STORAGE_PATH, 'cookies.txt')

# Create directories on the persistent disk if they don't exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


# --- API Route for Cookie Upload ---
@app.route('/api/upload-cookies', methods=['POST'])
def upload_cookies():
    data = request.get_json()
    if not data or 'cookieContent' not in data:
        return jsonify({"error": "No cookie content provided"}), 400

    try:
        # Save the received content to the cookies.txt file on the persistent disk
        with open(COOKIES_FILE_PATH, 'w') as f:
            f.write(data['cookieContent'])
        return jsonify({"message": "Cookies updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save cookies: {str(e)}"}), 500


# --- API Route for Conversion ---
@app.route('/api/convert', methods=['POST'])
def convert_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL not provided"}), 400

    youtube_url = data['url']
    unique_id = str(uuid.uuid4())
    # Output template now points to the persistent download folder
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

    if os.path.exists(COOKIES_FILE_PATH):
        ydl_opts['cookiefile'] = COOKIES_FILE_PATH

    try:
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

# --- Download Route & Main ---
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Ensure local dev uses a local folder
    PERSISTENT_STORAGE_PATH = '.' 
    DOWNLOAD_FOLDER = os.path.join(PERSISTENT_STORAGE_PATH, 'downloads')
    COOKIES_FILE_PATH = os.path.join(PERSISTENT_STORAGE_PATH, 'cookies.txt')
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
    
    app.run(host='0.0.0.0', port=5000, debug=True)
