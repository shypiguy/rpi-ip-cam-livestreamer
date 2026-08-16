import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

def get_authenticated_service():
    # Uses your existing token.json file generated during setup
    creds = Credentials.from_authorized_user_file('token.json')
    return build('youtube', 'v3', credentials=creds)

def end_active_stream():
    youtube = get_authenticated_service()

    try:
        # 1. Find the currently live broadcast ID
        print("Searching for active live broadcasts...")
        list_response = youtube.liveBroadcasts().list(
            part="id,status",
            broadcastStatus="active",  # Look for what is currently live
            broadcastType="all"       # SWAP mine=True FOR THIS
        ).execute()

        items = list_response.get("items", [])
        
        if not items:
            print("No active live streams found to end.")
            return

        # Target the first active broadcast found
        broadcast_id = items[0]["id"]
        print(f"Found active broadcast ID: {broadcast_id}")

        # 2. Transition the status to 'complete'
        print("Transitioning broadcast status to complete...")
        transition_response = youtube.liveBroadcasts().transition(
            broadcastStatus="complete",
            id=broadcast_id,
            part="id,status"
        ).execute()

        print(f"Success! Stream has been cleanly ended and closed.")
        print(f"Current Status: {transition_response['status']['lifeCycleStatus']}")

    except HttpError as e:
        print(f"An API error occurred: {e.content.decode()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    end_active_stream()
