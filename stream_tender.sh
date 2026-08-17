#!/bin/bash

FLAG_FILE="streaming_flag.txt"
cd "$(dirname -- "${BASH_SOURCE[0]}")" || exit
source .venv/bin/activate
while true; do
    # 1. Check if the flag file exists. If not, exit the script.
    if [ ! -f "$FLAG_FILE" ]; then
        echo "Flag file '$FLAG_FILE' not found. Exiting."
        deactivate
        exit 0
    fi

    # 2. Check if user 'bill' is running an ffmpeg process
    if ps -u bill | grep -q "[f]fmpeg"; then
        
        # 3. ffmpeg is running locally, but we need to check YouTube's ingestion status
        if python3 stream_health.py | grep -q "WARNING"; then
            echo "YouTube reports no data (WARNING). Restarting ffmpeg connection..."
            
            # Gracefully kill the stalled ffmpeg process
            killall --user "$USER" --ignore-case --signal INT ffmpeg
            
            # Wait 5 seconds for the process to fully terminate and free up network ports
            sleep 5
            
            # Restart the encoder
            ./start_encoder.sh
        fi

        # 4. Sleep for 30 seconds before letting the loop repeat
        sleep 30
    else
        # 5. ffmpeg is not running at all: start the encoder
        echo "ffmpeg not found. Starting encoder..."
        ./start_encoder.sh
        
        # It is highly recommended to sleep here as well. This prevents the loop 
        # from spamming start_encoder.sh dozens of times a second if the encoder 
        # takes a moment to start up or crashes immediately.
        sleep 30
    fi
done
