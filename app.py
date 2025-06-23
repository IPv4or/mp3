# app.py
# --- Imports ---
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# --- Flask App Initialization ---
app = Flask(__name__)
# Enable CORS to allow our front-end to make requests to this server
CORS(app)

# --- Configuration ---
# The directory where converted WAV files will be stored temporarily.
# The 'static' folder is a common convention in Flask for serving files.
DOWNLOAD_FOLDER = 'static/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# --- API Route ---
@app.route('/api/convert', methods=['POST'])
def convert_video():
    """
    API endpoint to handle the conversion.
    Expects a JSON payload with a "url" key.
    e.g., {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    """
    # 1. Get the URL from the request
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL not provided"}), 400

    youtube_url = data['url']
    
    # 2. Generate a unique filename to avoid conflicts
    unique_id = str(uuid.uuid4())
    # We will let yt-dlp determine the final filename and then rename it.
    output_template = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')

    # 3. Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'quiet': True, # Suppress console output from yt-dlp
    }

    # 4. Run the download and conversion process
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            # The actual filename will be determined by yt-dlp
            # We know the ID and the extension will be .wav
            final_filename = f"{unique_id}.wav"
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], final_filename)

            if not os.path.exists(file_path):
                 # This is a fallback in case the output file naming is unexpected
                 raise FileNotFoundError("Converted file was not found after download.")
            
            # 5. Generate the download URL for the client
            # This URL points to our 'download' route below
            download_url = f"/download/{final_filename}"
            
            return jsonify({
                "message": "Transmutation Complete",
                "downloadUrl": download_url,
                "title": info.get('title', 'Untitled')
            })

    except yt_dlp.utils.DownloadError as e:
        # Handle errors from yt-dlp (e.g., invalid URL, private video)
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500
    except Exception as e:
        # Handle other unexpected errors
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
    # Running in debug mode is fine for development.
    # For production, use a proper WSGI server like Gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=True)

