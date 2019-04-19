import argparse
import http.server
import json
import os
import pprint 
import requests
import socketserver
import spotipy
import spotipy.util as util
import sys
import webbrowser 
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
    username = ""
    access_token = ""

    def Authorize(self, username):
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

    def CreatePlaylist(self, playlist_name,public=True):
        sp = spotipy.Spotify(auth=self.access_token)
        sp.trace = False
        #Cannot specify description without JSON errors resulting in Spotipy
        playlists = sp.user_playlist_create(self.username, playlist_name, public)
        pprint.pprint(playlists)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--generate", help="Generate a new playlist")
    parser.add_argument("-u","--user", help="User for playlist operations")
    args = parser.parse_args()
    print("Generating playlist '", args.generate, "' for user '", args.user, "'...", sep="")
    pg = PlaylistGenerator()
    if args.user:
        pg.Authorize(args.user)
    else:
        print("No user specified. User specific operations will not be functional.")
    if args.user and args.generate:
        pg.CreatePlaylist(args.generate)
