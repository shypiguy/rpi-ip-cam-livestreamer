#!/bin/bash

CONFIG_FILE="stream_config.ini"

# 1. Verify the config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file $CONFIG_FILE not found."
    exit 1
fi

# 2. Extract the URLs and audio file safely using grep and sed
# The sed command carefully removes everything up to the *first* equals sign so it doesn't break the camera URL parameters
INPUT_STREAM=$(grep -E '^input_stream[[:space:]]*=' "$CONFIG_FILE" | sed -E 's/^[^=]*=[[:space:]]*//')
STREAM_DESTINATION=$(grep -E '^stream_destination[[:space:]]*=' "$CONFIG_FILE" | sed -E 's/^[^=]*=[[:space:]]*//')
AUDIO_FILE=$(grep -E '^audio_file[[:space:]]*=' "$CONFIG_FILE" | sed -E 's/^[^=]*=[[:space:]]*//')

# 3. Verify we actually retrieved the data
if [ -z "$INPUT_STREAM" ] || [ -z "$STREAM_DESTINATION" ]; then
    echo "Error: Could not read input_stream or stream_destination from $CONFIG_FILE"
    exit 1
fi

# 4. Run ffmpeg in background, connect camera to youtube
if [ -n "$AUDIO_FILE" ] && [ -f "$AUDIO_FILE" ]; then
    echo "Audio file '$AUDIO_FILE' found. Using local audio loop."
    nohup ffmpeg -loglevel error -rtsp_transport tcp -i "$INPUT_STREAM" \
    -stream_loop -1 -i "$AUDIO_FILE" \
    -vcodec copy \
    -acodec aac -b:a 128k -ar 44100 -ac 2 \
    -map 0:v:0 -map 1:a:0 \
    -shortest \
    -f flv "$STREAM_DESTINATION" > /dev/null 2> ffmpeg_error.log &
else
    echo "No valid audio file found in config. Defaulting to camera audio."
    nohup ffmpeg -loglevel error -rtsp_transport tcp -i "$INPUT_STREAM" \
    -vcodec copy \
    -acodec aac -b:a 128k -ar 44100 -ac 2 \
    -f flv "$STREAM_DESTINATION" > /dev/null 2> ffmpeg_error.log &
fi

echo "Encoder started pointing to $STREAM_DESTINATION"