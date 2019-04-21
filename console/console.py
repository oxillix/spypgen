import argparse
from spypgen.playlistgenerator import PlaylistGenerator

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
        artists = []
        if args.source_artists:
            artists = args.source_artists.split(',')
        pg.create_playlist(args.generate, artists, args.number_of_songs_per_artist, args.number_of_tracklist_songs_per_artist)
