from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from qrcode_generator import qr_shop
import os
from database import shop_database, ads_db, read_ads_db, ad_info, get_location
from exposure import exposure_cal
from register_db import register_database
from login_db import login_database
from verify_ads import get_ads, update_ads

app = Flask(__name__)
app.secret_key = "weconnect"

# Set the upload folder for video
UPLOAD_FOLDER = 'static/assets/ads_media'
wifi_qr_dir = 'static/assets/wifi_qr'
shop_qr_dir = 'static/assets/shop_qr'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(wifi_qr_dir, exist_ok=True)
os.makedirs(shop_qr_dir, exist_ok=True)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/insert_shop')
def insert_shop():
    if 'username' in session:   
        return render_template('shop_info.html')
    else:
        flash("Please log in to access this page.", "warning")
        return render_template('index.html')
    
@app.route('/control_panel')
def control_panel():
    if 'username' in session:   
        return render_template('control_panel.html')
    else:
        flash("Please log in to access this page.", "warning")
        return render_template('index.html')

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
    if 'username' in session:   
        return render_template('upload_ads.html')
    else:
        flash("Please log in to access this page.", "warning")
        return render_template('index.html')

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
    return render_template('media.html')

# @app.route('/get_video', methods=['GET'])
def get_video(shop_code):
    # Decide which video to serve
    media = {
        "media_path": "/static/assets/ads_media/image.png",
        "url_link": "/upload"
    }
    shop_location = get_location(shop_code)
    if shop_location:
        all_ads = read_ads_db(shop_location)

        selected_ad = exposure_cal(all_ads)
        if selected_ad is None:
            return media
            
        media = ad_info(selected_ad, shop_location)

    return media
    
@app.route('/scan')
def wifi_shop():
    # Extract the shop code from the query parameter
    shop_code = request.args.get('qr')
    if not shop_code:
        return "Shop code is missing", 400
    
    media = get_video(shop_code)

    # Generate the path to the Wi-Fi QR code image
    wifi_qr = f"/static/assets/wifi_qr/{shop_code}.png"

    # Detect the device type based on the User-Agent header
    user_agent = request.headers.get('User-Agent', '').lower()
    if "iphone" in user_agent:
        gif_guide = "/static/assets/connection_guide/iphone_user.gif"
    elif "android" in user_agent:
        gif_guide = "/static/assets/connection_guide/android_user.gif"
    elif "harmonyos" in user_agent:
        gif_guide = "/static/assets/connection_guide/android_user.gif"
    elif "windows" in user_agent:
        gif_guide = "None"
    elif "mac" in user_agent:
        gif_guide = "None"
    else:
        gif_guide = "None"

    # Render the HTML template
    return render_template('media.html', wifi_qr=wifi_qr, user_guide=gif_guide, media=media)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    user_info = {
        "email": email,
        "username": username,
        "password": password
    }

    status = register_database(user_info)

    return status

@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    user_info = {
        "username": username,
        "password": password
    }

    status = login_database(user_info)

    if status["status"] == "success":
        session['username'] = username
        flash("Login successful!", "success")
        return redirect(url_for('control_panel'))
    else:
        return status['message']

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/ad_verify')
def ad_verify():
    if 'username' in session:   
        ads = get_ads()
        return render_template('ad_verify.html', tables=ads)
    else:
        flash("Please log in to access this page.", "warning")
        return render_template('index.html')

@app.route('/ads_verify', methods=['POST'])
def ads_verify():
    verify_form = request.form

    for table_data, _ in verify_form.items():
        status = update_ads(table_data)

    return redirect(url_for('ad_verify'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)