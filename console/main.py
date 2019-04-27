import argparse
import sys
from PIL import Image
from pytesseract import image_to_string
from spypgen.playlistgenerator import PlaylistGenerator
import json
import os 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--generate", help="Generate a new playlist")
    parser.add_argument("-c","--credentials", default="credentials.json", help="File containing credentials information (user, client ID/secret, etc.) for Spotify ")
    parser.add_argument("-s", "--source_artists", help="Artists used as a source for the generated playlist as a comma-delimited list")
    parser.add_argument("-p", "--playlist_preferences", help="File containing preferences regarding playlist composition")
    args = parser.parse_args()
    
    if not os.path.isfile(args.credentials):
        print("Specified credentials file",args.credentials,"was not found, so authentication with Spotify cannot proceed.")
        sys.exit(1)

    with open(args.credentials) as file:
        credentials = json.loads(file.read())

    user = credentials.get("user")
    client_id = credentials.get("clientId")
    client_secret = credentials.get("clientSecret")
    redirect_port = int(credentials.get("redirectLocalHostPort"))

    if user is None:
        print("'user' not specified in",args.credentials)
        exit(1)
    if client_id is None:
        print("'clientId' not specified in",args.credentials)
        exit(1)
    if client_secret is None:
        print("'clientSecret' not specified in",args.credentials)   
        exit(1)
    if redirect_port is None:
        print("'redirectLocalHostPort' not specified in",args.credentials)
        exit(1)

    pg = PlaylistGenerator()
    pg.authorize(user,client_id,client_secret,redirect_port)

    if args.generate:
        print("Generating playlist '", args.generate, "' for user '", user, "'...", sep="")
        artists = None
        total_songs_per_artist = 8
        num_songs_recent_setlists = 5
        num_songs_popular_spotify = 3
        if args.playlist_preferences:
            if os.path.isfile(args.playlist_preferences):
                with open(args.playlist_preferences) as file:
                    playlist_preferences = json.loads(file.read())
                    artists = playlist_preferences.get("artists")
                    song_preferences = playlist_preferences.get("targetSongCounts")
                    if song_preferences:
                        total_songs_per_artist = song_preferences.get('maxSongsPerArtist', total_songs_per_artist)
                        num_songs_recent_setlists = song_preferences.get('recentSetListSongs', num_songs_recent_setlists)
                        num_songs_popular_spotify = song_preferences.get('topSpotifySongs', num_songs_popular_spotify)
        if artists is None or len(artists) == 0:
            if args.source_artists and len(args.source_artists) > 0:
                artists = args.source_artists.split(',')
            else:
                print("No artists specified in a preferences file using --playlist_preferences or via --source_artists.")
                exit(1)
        pg.set_song_count_preferences(total_songs_per_artist, num_songs_popular_spotify, num_songs_recent_setlists)                    
        pg.create_playlist(args.generate, artists)
    #print(image_to_string(Image.open(sys.argv[1]), config="-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.-()& -psm 6"))