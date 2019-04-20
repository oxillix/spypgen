import argparse
import http.server
import itertools
import json
import operator
import os
import pprint 
import requests
import socketserver
import spotipy
import spotipy.util as util
import sys
import webbrowser 
from tracklistscraper import TracklistScraper
from http.server import HTTPServer, BaseHTTPRequestHandler

done = False

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global done
        global request_path
        request_path = self.path        
        done = True
        self.send_response(200, "OK")


class Server(socketserver.TCPServer):
    allow_reuse_address = True


class PlaylistGenerator:
    def __init__(self):
        self.username = ""
        self.access_token = ""
        self.spotipy = None
        self.tracklist_scraper = TracklistScraper()

    def authorize(self, username):
        self.username = username
        scope = 'playlist-modify-public'
        authorize_url = "https://accounts.spotify.com/authorize"
        token_url = "https://accounts.spotify.com/api/token"

        redirect_uri = "http://localhost:8080"
        client_id = os.environ["SPOTIFY_CLIENT_ID"]
        client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

        authorization_url = authorize_url + '?client_id=' + client_id + '&response_type=code&redirect_uri=' + redirect_uri + '&scope=' + scope

        print("Attempting to access ", authorization_url)

        webbrowser.open_new_tab(authorization_url)

        httpd = Server(("localhost", 8080), RequestHandler)
        while not done:
            httpd.handle_request()
        print("Requested path is ", request_path)

        auth_code = request_path.replace('/?code=', "")
        data = {    
            'grant_type':'authorization_code',
            'redirect_uri':redirect_uri,
            'code':auth_code
        }
        access_token_response = requests.post(token_url, data=data,verify=False,allow_redirects=False,auth=(client_id,client_secret))
        tokens = json.loads(access_token_response.text)
        self.access_token = tokens['access_token']
        print('Access token is: ', self.access_token)
        self.spotipy = spotipy.Spotify(auth=self.access_token)
        self.spotipy.trace = False

    def create_playlist(self, playlist_name,playlist_artists,number_songs_per_artist,number_of_tracklist_songs_per_artist,public=True):
        #Cannot specify description without JSON errors resulting in Spotipy
        playlistId = self.spotipy.user_playlist_create(self.username, playlist_name, public)["id"]
        tracks_by_artists = []
        for artist in playlist_artists.split(","):
            (artist_name, artist_id) = self.find_artist(artist)
            print(artist_name, "-", artist_id)
            tracks_by_artists.extend(self.find_tracks(artist_name,artist_id,number_songs_per_artist, number_of_tracklist_songs_per_artist))
        uniq_tracks_by_artists = set(tracks_by_artists)
        playlist = self.spotipy.user_playlist_add_tracks(self.username, playlistId, set([track[2] for track in uniq_tracks_by_artists]))
        pprint.pprint(uniq_tracks_by_artists)

    def find_artist(self,artist_name):
        print("Searching for artist",artist_name,"...")
        foundArtists = self.spotipy.search(artist_name,type='artist')["artists"]["items"]
        for artist in foundArtists:
            if artist["name"] == artist_name:
                return (artist_name, artist["id"])

    def find_tracks(self,artist_name,artist_id,number_songs_per_artist,number_of_tracklist_songs_per_artist):
        print("Finding top tracks for artist",artist_name,"...")
        top_tracks = self.spotipy.artist_top_tracks(artist_id)["tracks"][:number_songs_per_artist]
        recent_tracks = filter(None, [self.find_track(track_name) for track_name in self.tracklist_scraper.get_artists_popular_recent_tracks(artist_name,number_of_tracklist_songs_per_artist)])
        return set([(artist_name,track["name"],track["id"]) for track in itertools.chain(top_tracks,recent_tracks)])

    def find_track(self,track_name):
        print("Searching for",track_name)
        results = self.spotipy.search(track_name.replace("ft.","").replace("&",""),type='track')['tracks']['items']
        if len(results) == 0:
            return None
        return results[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--generate", help="Generate a new playlist")
    parser.add_argument("-u","--user", help="User for playlist operations")
    parser.add_argument("-s", "--source_artists", help="Artists used as a source for the generated playlist as a comma-delimited list")
    parser.add_argument("-n", "--number_of_songs_per_artist", type=int,default=5, help="Number of the artist's popular Spotify songs included in the generated playlist for each artist")
    parser.add_argument("--number_of_tracklist_songs_per_artist", type=int,default=3, help="Number of the artist's popular Spotify songs included in the generated playlist for each artist")
    args = parser.parse_args()
    print("Generating playlist '", args.generate, "' for user '", args.user, "'...", sep="")
    pg = PlaylistGenerator()
    if args.user:
        pg.authorize(args.user)
    else:
        print("No user specified. User specific operations will not be functional.")
    if args.user and args.generate:
        pg.create_playlist(args.generate, args.source_artists, args.number_of_songs_per_artist, args.number_of_tracklist_songs_per_artist)
