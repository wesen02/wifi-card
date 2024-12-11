from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from qrcode_generator import qr_shop
import os
from database import shop_database, ads_db, read_ads_db, ad_info
from exposure import exposure_cal

app = Flask(__name__)

# Set the upload folder for video
UPLOAD_FOLDER = 'static/assets/ads_media'
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

    _ = shop_database(data)

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
    # video = video_database()
    all_ads = read_ads_db()
    selected_ad = exposure_cal(all_ads)
    
    if selected_ad == None:
        return jsonify(None)
        
    media = ad_info(selected_ad)

    return jsonify(media)

@app.route('/scan')
def wifi_shop():
    # Extract the shop code from the query parameter
    shop_code = request.args.get('qr')
    if not shop_code:
        return "Shop code is missing", 400

    # Generate the path to the Wi-Fi QR code image
    wifi_qr = f"/static/assets/wifi_qr/{shop_code}.png"

    device=None

    # Detect the device type based on the User-Agent header
    user_agent = request.headers.get('User-Agent', '').lower()
    if "iphone" in user_agent:
        gif_guide = "/static/assets/connection_guide/iphone_user.gif"
    elif "android" in user_agent:
        gif_guide = "/static/assets/connection_guide/android_user.gif"
    elif "harmonyos" in user_agent:
        gif_guide = "None"
    elif "windows" in user_agent:
        gif_guide = "None"
    elif "mac" in user_agent:
        gif_guide = "None"
    else:
        gif_guide = "None"

    # Render the HTML template
    return render_template('video.html', wifi_qr=wifi_qr, user_guide=gif_guide, device=device)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)