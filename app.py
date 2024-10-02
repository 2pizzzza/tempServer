import requests
import json
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

CLIENT_ID = "76143371ed214edd943d91fdfb795c08"
CLIENT_SECRET = "2f2126fecc714498a0ddd85ef8c5cddd"


def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_token(token):
    return {"Authorization": "Bearer " + token}


def search_song(token, song_name=None, artist_name=None):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_token(token)

    query = ""
    if song_name:
        query += f"track:{song_name}"
    if artist_name:
        if query:
            query += f"%20artist:{artist_name}"
        else:
            query += f"artist:{artist_name}"

    query_url = f"{url}?q={query}&type=track&limit=1"

    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)

    if "tracks" in json_result and json_result["tracks"]["items"]:
        track = json_result["tracks"]["items"][0]
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        album_name = track['album']['name']
        release_date = track['album']['release_date']
        spotify_url = track['external_urls']['spotify']

        return {
            "Song": track_name,
            "Artist": artist_name,
            "Album": album_name,
            "Release Date": release_date,
            "Spotify URL": spotify_url
        }
    else:
        return None


@app.route('/search', methods=['GET'])
def search_endpoint():
    song_name = request.args.get('song')
    artist_name = request.args.get('artist')

    token = get_token()
    track_info = search_song(token, song_name=song_name, artist_name=artist_name)

    if track_info:
        return jsonify(track_info), 200
    else:
        return jsonify({"error": "No tracks found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
