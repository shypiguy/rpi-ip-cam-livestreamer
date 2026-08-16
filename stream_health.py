import os
import configparser
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Note: Use your actual permanent stream ID here
#PERMANENT_STREAM_ID = "-4O5xj9K-QgPK64F_U3FFg1781622083634026"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CONFIG_FILE = 'stream_config.ini'

def load_settings():
    # 1. Define hardcoded fallbacks
    defaults = {
        'permanent_stream_id': ''
    }

    # 2. Parse configuration file if it exists
    config = configparser.ConfigParser(defaults=defaults)
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    
    # 3. Handle command line argument overrides
    parser = argparse.ArgumentParser(description="Priming tool for daily YouTube Livestreaming context.")
    parser.add_argument('--stream_id', default=config.get('StreamSettings', 'PERMANENT_STREAM_ID'))
    
    args = parser.parse_args()


    return {
        'PERMANENT_STREAM_ID': args.stream_id
    }

def get_authenticated_service():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return build('youtube', 'v3', credentials=creds)
    else:
        print("Error: token.json not found. Run stream_starter.py first.")
        exit(1)

def check_stream_health():
    settings = load_settings()
    youtube = get_authenticated_service()

    try:
        response = youtube.liveStreams().list(
            part="status",
            id=settings['PERMANENT_STREAM_ID']
        ).execute()

        items = response.get("items", [])
        if not items:
            print("Stream ID not found.")
            return

        status_data = items[0]["status"]
        
        # Extract the two vital metrics
        stream_status = status_data.get("streamStatus", "Unknown")
        health_status = status_data.get("healthStatus", {}).get("status", "Unknown")

        print(f"--- YouTube Ingestion Status ---")
        print(f"Stream Status: {stream_status}")
        print(f"Health Status: {health_status}")

        # Basic logic to determine if ffmpeg needs a restart
        if health_status == "noData" or stream_status == "inactive":
            print("\nWARNING: YouTube is NOT receiving data.")
        elif health_status in ["good", "ok"]:
            print("\nSUCCESS: Stream is healthy and receiving data.")
        else:
            print("\nNOTICE: Stream is receiving data, but quality is poor.")

    except HttpError as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    load_settings()  
    check_stream_health()
