from dotenv import load_dotenv
import os
import requests

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

url = "https://accounts.spotify.com/api/token"

response = requests.post(
    url,
    data={"grant_type": "client_credentials"},
    auth=(CLIENT_ID, CLIENT_SECRET)
)

token = response.json()["access_token"]

print("Connected Successfully")
print(token[:30] + "...")