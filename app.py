from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import qrcode
from qrcode_generator import qr_shop
import os
from database import shop_database, ads_db, video_database
import random

app = Flask(__name__)

# Set the upload folder for video
UPLOAD_FOLDER = 'static/ads_video'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/insert_shop')
def insert_shop():
   return render_template('shop_info.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    data = request.get_json()

    database_update = shop_database(data)

    qr_dir = qr_shop(data)
    qr_name = qr_dir.split("/")[-1]
    
    if os.path.exists(qr_dir):
        return jsonify({"qrFilePath": qr_name}), 200  # Return the file name/path as JSON
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/upload_ads')
def upload_ads():
    return render_template('upload_ads.html')

@app.route('/uploadAds', methods=['POST'])
def upload_file():
    if 'media' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    media_file = request.files['media']
    if media_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Validate file type
    allowed_extensions = {'mp4', 'avi', 'mov', 'jpg', 'png', 'jpeg', 'gif'}
    file_extension = media_file.filename.rsplit('.', 1)[1].lower()
    if file_extension not in allowed_extensions:
        return jsonify({"error": "Unsupported file type"}), 400

    # Save the media file
    media_path = os.path.join(app.config['UPLOAD_FOLDER'], media_file.filename)
    media_file.save(media_path)

    # Extract other form data (excluding the file)
    form_data = request.form.to_dict()  # This will contain the form data except the file

    # Pass form data and media path to your database function or logic
    ads_db(form_data, media_path)

    response = {
        "message": "Media file and form data received successfully",
        "form_data": form_data,
        "media_path": media_path
    }

    return jsonify(response)

@app.route('/popup')
def popup():
    return render_template('video.html')

@app.route('/get_video', methods=['GET'])
def get_video():
    # Decide which video to serve
    video = video_database()
    return jsonify(video)

@app.route('/wifi_shop/<shop_code>')
def wifi_shop(shop_code):
    wifi_qr = f"/static/wifi/{shop_code}.png"
    return render_template('video.html', wifi_qr=wifi_qr)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)