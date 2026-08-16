import os
import datetime
import configparser
import argparse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CONFIG_FILE = 'stream_config.ini'

def load_settings():
    # 1. Define hardcoded fallbacks
    defaults = {
        'permanent_stream_id': '',
        'playlist_id': '',
        'stream_title': 'Live Stream - {date}',
        'stream_description': 'Automated daily stream.',
        'categoryid': '15',
        'tags': 'live',
        'privacystatus': 'public',
        'selfdeclaredmadeforkids': 'False',
        'containssyntheticmedia': 'False'
    }

    # 2. Parse configuration file if it exists
    config = configparser.ConfigParser(defaults=defaults)
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    
    # 3. Handle command line argument overrides
    parser = argparse.ArgumentParser(description="Priming tool for daily YouTube Livestreaming context.")
    parser.add_argument('--stream_id', default=config.get('StreamSettings', 'PERMANENT_STREAM_ID'))
    parser.add_argument('--playlist_id', default=config.get('StreamSettings', 'PLAYLIST_ID'))
    parser.add_argument('--title', default=config.get('StreamSettings', 'stream_title'))
    parser.add_argument('--description', default=config.get('StreamSettings', 'stream_description'))
    parser.add_argument('--category', default=config.get('StreamSettings', 'categoryId'))
    parser.add_argument('--tags', default=config.get('StreamSettings', 'tags'))
    parser.add_argument('--privacy', default=config.get('StreamSettings', 'privacyStatus'))
    parser.add_argument('--kids', default=config.get('StreamSettings', 'selfDeclaredMadeForKids'))
    parser.add_argument('--ai', default=config.get('StreamSettings', 'containsSyntheticMedia'))
    
    args = parser.parse_args()

    # Convert comma-separated tag string into a standard list structure
    tag_list = [tag.strip() for tag in args.tags.split(',') if tag.strip()]

    # Helper function to properly cast boolean configuration strings
    def to_bool(val):
        return str(val).lower() in ['true', '1', 'yes', 'on']

    now = datetime.datetime.utcnow()
    formatted_title = args.title.replace('{date}', now.strftime('%Y-%m-%d'))

    return {
        'PERMANENT_STREAM_ID': args.stream_id,
        'PLAYLIST_ID': args.playlist_id,
        'stream_title': formatted_title,
        'stream_description': args.description,
        'categoryId': args.category,
        'tags': tag_list,
        'privacyStatus': args.privacy,
        'selfDeclaredMadeForKids': to_bool(args.kids),
        'containsSyntheticMedia': to_bool(args.ai)
    }

def get_authenticated_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(
                host='localhost',
                port=8080,
                open_browser=False
            )
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def run_daily_sync():
    settings = load_settings()
    youtube = get_authenticated_service()
    now = datetime.datetime.utcnow()
    
    # 1. Create the Broadcast container (Scheduling only)
    broadcast = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {
                "title": settings['stream_title'],
                "description": settings['stream_description'],
                "scheduledStartTime": now.isoformat() + "Z"
            },
            "status": {
                "privacyStatus": settings['privacyStatus'],
                "selfDeclaredMadeForKids": settings['selfDeclaredMadeForKids']
            },
            "contentDetails": {
                "enableAutoStart": True,
                "enableAutoEnd": True
            }
        }
    ).execute()
    
    broadcast_id = broadcast["id"]
    
    # 2. Update the underlying Video resource with full metadata
    youtube.videos().update(
        part="snippet,status",
        body={
            "id": broadcast_id,
            "snippet": {
                "title": settings['stream_title'],         
                "description": settings['stream_description'], 
                "categoryId": settings['categoryId'],            
                "tags": settings['tags']
            },
            "status": {
                "privacyStatus": settings['privacyStatus'],
                "selfDeclaredMadeForKids": settings['selfDeclaredMadeForKids'],
                "containsSyntheticMedia": settings['containsSyntheticMedia']  
            }
        }
    ).execute()
    
    # 3. Bind it using your stream ID
    youtube.liveBroadcasts().bind(
        id=broadcast_id,
        part="id,contentDetails",
        streamId=settings['PERMANENT_STREAM_ID']
    ).execute()
    
    # 4. Add the new broadcast to the Playlist
    if settings['PLAYLIST_ID']:
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": settings['PLAYLIST_ID'],
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": broadcast_id
                        }
                    }
                }
            ).execute()
            print("Successfully added today's stream to the playlist.")
        except Exception as e:
            print(f"Failed to add to playlist: {e}")
    
    print("YouTube is primed. Fire up the Pi's encoder stream whenever you're ready!")

if __name__ == "__main__":
    run_daily_sync()