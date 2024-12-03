from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Set the upload folder for video
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/uploadAds', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected video file"}), 400

    # Save the video file
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
    video_file.save(video_path)

    # Extract other form data (excluding the video)
    form_data = request.form.to_dict()  # This will contain the form data except the file

    # You can also add custom logic to manipulate the form data here
    response = {
        "message": "Video and form data received successfully",
        "form_data": form_data
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
