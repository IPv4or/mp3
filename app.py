# app.py
# --- Imports ---
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Configuration ---
DOWNLOAD_FOLDER = 'static/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# The location of the cookies file in the root directory
COOKIES_FILE_PATH = 'cookies.txt'


# --- API Route ---
@app.route('/api/convert', methods=['POST'])
def convert_video():
    """
    API endpoint to handle the conversion.
    Expects a JSON payload with a "url" key.
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL not provided"}), 400

    youtube_url = data['url']
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')

    # --- UPDATED SECTION ---
    # Configure yt-dlp options, now including cookie support
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'quiet': True,
    }

    # If cookies.txt exists in the project's root, add it to the options.
    if os.path.exists(COOKIES_FILE_PATH):
        ydl_opts['cookiefile'] = COOKIES_FILE_PATH
        print("INFO: Found and using cookies.txt") # For debugging on the server
    else:
        print("INFO: cookies.txt not found. Proceeding without authentication.")

    # --- END UPDATED SECTION ---

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            final_filename = f"{unique_id}.wav"
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], final_filename)

            if not os.path.exists(file_path):
                 raise FileNotFoundError("Converted file was not found after download.")
            
            download_url = f"/download/{final_filename}"
            
            return jsonify({
                "message": "Transmutation Complete",
                "downloadUrl": download_url,
                "title": info.get('title', 'Untitled')
            })

    except yt_dlp.utils.DownloadError as e:
        # Improved error message formatting
        error_text = str(e).split('ERROR: ')[-1]
        return jsonify({"error": f"{error_text}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# --- Download Route ---
@app.route('/download/<filename>')
def download_file(filename):
    """
    Serves the converted file for download.
    """
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)


# --- Main Entry Point ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

