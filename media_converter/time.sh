#!/bin/bash

# Set the target time (24-hour format)
TARGET_TIME="15:30"

# Get the current time in HH:MM format
CURRENT_TIME=$(date +"%H:%M")

# Loop until the current time matches the target time
while [[ "$CURRENT_TIME" != "$TARGET_TIME" ]]; do
    # Wait for 30 seconds before checking again
    sleep 30
    CURRENT_TIME=$(date +"%H:%M")
done

# Once the target time is reached, do something
echo "The time is now $TARGET_TIME. Executing the command..."
# Example command to execute
# ./your-command.sh
