#!/bin/bash

# Directory to monitor
WATCH_DIR="../static/ads_video/"

# Check if inotifywait is installed
if ! command -v inotifywait &>/dev/null; then
    echo "Error: inotifywait is not installed. Install it using 'sudo apt install inotify-tools' or your package manager."
    exit 1
fi

echo "Monitoring $WATCH_DIR for new .mp4 files..."

# List of supported file extensions
SUPPORTED_EXTENSIONS=("mp4" "avi" "mov" "jpg" "png" "jpeg" "gif")

# Monitor the directory for new files
inotifywait -m -e create --format "%f" "$WATCH_DIR" | while read -r NEW_FILE; do
    # Check if the new file is an .mp4
    # Get the file extension of the new file
    FILE_EXTENSION="${NEW_FILE##*.}"

    if [[ "${SUPPORTED_EXTENSIONS[*]}" == *"$FILE_EXTENSION"* ]]; then
        echo "New file detected: $NEW_FILE with extension .$FILE_EXTENSION"

        # Define paths
        FILE_PATH="${WATCH_DIR%/}/$NEW_FILE"
        TEMP_FILE="${FILE_PATH%.*}_temp.${FILE_EXTENSION}"

        echo "Processing file: $FILE_PATH"

        if [[ "$FILE_EXTENSION" == "mp4" || "$FILE_EXTENSION" == "avi" || "$FILE_EXTENSION" == "mov" ]]; then
            # Run ffmpeg for video files
            ffmpeg -y -i "$FILE_PATH" -c:v libx264 -crf 23 -preset medium -c:a aac "$TEMP_FILE"

            # Check if ffmpeg succeeded
            if [ $? -eq 0 ]; then
                echo "ffmpeg processing succeeded. Replacing the original file with the processed version."
                mv "$TEMP_FILE" "$FILE_PATH"
                python3 hash_video.py
            else
                echo "Error: ffmpeg processing failed."
                rm -f "$TEMP_FILE"
            fi
        elif [[ "$FILE_EXTENSION" == "jpg" || "$FILE_EXTENSION" == "png" || "$FILE_EXTENSION" == "jpeg" || "$FILE_EXTENSION" == "gif" ]]; then
            # Example processing for image files (e.g., compressing or resizing)
            echo "Processing image: $FILE_PATH"
            dimensions=$(identify -format "%w %h" "$FILE_PATH")
            width=$(echo "$dimensions" | cut -d' ' -f1)
            height=$(echo "$dimensions" | cut -d' ' -f2)

            # Determine if the image is vertical or horizontal
            if [ "$width" -gt "$height" ]; then
                # Horizontal or square image: constrain width
                convert "$FILE_PATH" -resize "1920x1080" "$TEMP_FILE"
            else
                # Vertical image: constrain height
                max_height=720
                convert "$FILE_PATH" -resize "1080x1920" "$TEMP_FILE"
            fi

            # Check if the `convert` command succeeded
            if [ $? -eq 0 ]; then
                echo "Image processing succeeded. Replacing the original file with the processed version."
                mv "$TEMP_FILE" "$FILE_PATH"
                python3 hash_video.py
            else
                echo "Error: Image processing failed."
                rm -f "$TEMP_FILE"
            fi
        fi

        # Call the Python script for further processing
    else
        echo "Unsupported file type: .$FILE_EXTENSION. Skipping processing."
    fi
done
