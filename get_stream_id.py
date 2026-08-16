from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Load your working credentials
creds = Credentials.from_authorized_user_file('token.json')
youtube = build('youtube', 'v3', credentials=creds)

# Ask YouTube to list your stream profiles
response = youtube.liveStreams().list(
    part="id,snippet",
    mine=True
).execute()

# Print out the IDs found
for item in response.get('items', []):
    print(f"Stream Name/Title: {item['snippet']['title']}")
    print(f"Your PERMANENT_STREAM_ID is: {item['id']}")
    print("-" * 40)