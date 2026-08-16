# IP Camera Livestreamer

This project provides an automated solution for broadcasting an IP camera directly to YouTube Live using a Raspberry Pi 4. Originally designed for streaming a backyard fish pond—providing a continuous view of the goldfish, minnows, frogs, and turtles—this codebase can be deployed for any dedicated 24/7 observation stream. 

The application utilizes Python and shell scripting to manage the YouTube Data API, handle automated authentication, and manage a continuous video encoder. 

## Prerequisites

*   **Hardware:**
    *   Raspberry Pi 4 (connected to the internet via onboard Wi-Fi).
    *   IP Camera.
    *   Ethernet cable.
*   **Accounts:**
    *   A Google Account with a YouTube channel verified for live streaming.

## Project Structure

This repository contains the following files:

*   `requirements.txt`: Python package dependencies.
*   `stream_config.ini`: Configuration file for storing stream keys, API IDs, and paths.
*   `start.sh` / `stop.sh`: Primary shell scripts to initialize or safely terminate the stream, intended for cron scheduling.
*   `start_encoder.sh`: The script responsible for kicking off the video encoding process.
*   `stream_starter.py` / `stream_ender.py`: Python scripts utilizing the YouTube API to transition the stream state to live or complete.
*   `get_stream_id.py`: Utility script to retrieve your permanent YouTube stream ID.
*   `stream_health.py` / `stream_tender.sh`: Watchdog scripts to monitor the stream status and restart the encoder if it fails.
*   `.gitignore`: Specifies intentionally untracked files to ignore.

## Setup Instructions

### 1. Hardware & Network Configuration
1. Connect your Raspberry Pi 4 to your local internet network via Wi-Fi.
2. Connect your IP Camera directly to the Raspberry Pi using an Ethernet cable.
3. Configure the Raspberry Pi's Ethernet adapter to be on the same subnet/segment as the IP Camera so they can communicate locally.

### 2. YouTube Channel Setup
1. Log into YouTube Studio and click **Create > Go live** to create a new live stream.
2. Note your stream settings and copy your **Stream Key**. You will need to add this to `stream_config.ini`.
3. Locate your chosen **Playlist ID** and **Video Category ID** from YouTube (e.g., 15 for Pets & Animals) to include in your configuration.

### 3. Google Cloud API Configuration
1. Navigate to the Google Cloud Console and create a new project.
2. Enable the **YouTube Data API v3** for your project.
3. Configure the OAuth consent screen and create an OAuth 2.0 Client ID (Desktop App).
4. Download the resulting client secrets JSON file and place it in the project root folder.

### 4. Software Installation & Authentication
1. Clone this repository and install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
2. Run stream_starter.py for the first time directly on the Raspberry Pi. This will prompt you to open a web browser to authenticate your Google Account. Complete the flow to receive your local authentication token.
3. Run get_stream_id.py to fetch your permanent stream_id and save it to your configuration file.
4. (Optional) Download and place an audio file in the project directory if you want to loop a background track over the video feed. Be sure to reference its path in your config.

### 5. Automation
To ensure the stream runs autonomously (even after power outages or reboots), schedule the start and stop scripts using the Raspberry Pi's crontab.

1. Open your cron editor:
    ```Bash
    crontab -e
2. Add your desired schedules. For example, to start the stream at sunrise and stop it at sunset, add:
    ```Plaintext
    0 6 * * * /path/to/ip-cam-livestreamer-main/start.sh
    0 20 * * * /path/to/ip-cam-livestreamer-main/stop.sh

### License
This project is licensed under the MIT License.

MIT License

Copyright (c) 2026 Bill Jones

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.   
