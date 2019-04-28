import argparse
import sys
import json
import os 
import re

from PIL import Image
from pytesseract import image_to_string
from playlistgenerator import PlaylistGenerator


class Application:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description = 'Provides various utilities related to generating Spotify playlists',
            usage = '''spypgen <command> [<args>] 

The most commonly used commands are:
    generate    Generate a Spotify playlist based on a list of artists and optional specified configurations
    scrape      Scrapes artists from an image of a lineup that can then be used to generate a playlist
''')
        parser.add_argument('command', help='Subcommand to be run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print(args.command,'is not a recognized command!')
            parser.print_help()
            exit(1)
        self.playlist_generator = PlaylistGenerator()
        getattr(self, args.command)()


    def generate(self):
        parser = argparse.ArgumentParser(
            description = "Generates a playlist in Spotify based on supplied artists and preferences",
            usage = '''spypgen generate [<args>]

The most commonly used variants are:
    -c "credentials.json" -n "PlaylistName" -s "Artist 1,Artist2"     Generates a playlist with the given name using the list of artists and specified Spotify credentials
    -c "credentials.json" -p "playlist.json"    Generates a playlist using specified preferences/content and credentials            
''')
        parser.add_argument("-n", "--name", help="Name for playlist")
        parser.add_argument("-c","--credentials", default="credentials.json", help="File containing credentials information (user, client ID/secret, etc.) for Spotify ")
        parser.add_argument("-s", "--source_artists", help="Artists used as a source for the generated playlist as a comma-delimited list")
        parser.add_argument("-p", "--playlist_preferences", help="File containing preferences regarding playlist composition")
        args = parser.parse_args(sys.argv[2:])
    
        user = self.authorize_generator(args.credentials)
        if user is None:
            print("Unable to authenticate")
            sys.exit(1)

        print("Generating playlist '", args.name, "' for user '", user, "'...", sep="")
        artists = None
        if args.playlist_preferences:
            if os.path.isfile(args.playlist_preferences):
                with open(args.playlist_preferences) as file:
                    playlist_preferences = json.loads(file.read())
                    artists = playlist_preferences.get("artists")
                    playlist_name = playlist_preferences.get("name")
                    song_preferences = playlist_preferences.get("targetSongCounts")
                    if song_preferences:
                        total_songs_per_artist = song_preferences.get('maxSongsPerArtist')
                        num_songs_recent_setlists = song_preferences.get('recentSetListSongs')
                        num_songs_popular_spotify = song_preferences.get('topSpotifySongs')
                        self.playlist_generator.set_song_count_preferences(total_songs_per_artist, num_songs_popular_spotify, num_songs_recent_setlists)                    
                    setlist_preferences = playlist_preferences.get("setlists")
                    if setlist_preferences:
                        num_searched = setlist_preferences.get('numberSearched')
                        inclusion_threshhold = setlist_preferences.get('inclusionThreshold')
                        self.playlist_generator.set_tracklist_search_preferences(num_searched, inclusion_threshhold)

        if artists is None or len(artists) == 0:
            if args.source_artists and len(args.source_artists) > 0:
                artists = args.source_artists.split(',')
            else:
                print("No artists specified in a preferences file using --playlist_preferences or via --source_artists.")
                sys.exit(1)

        if args.name:
            playlist_name = args.Name
        if playlist_name is None:
            print("No playlist name specified in a preferences file using --playlist_preferences or via --name.")
            sys.exit(1)

        self.playlist_generator.create_playlist(playlist_name, artists)

    def scrape(self):
        parser = argparse.ArgumentParser(
            description = 'Scrapes artists from an image of a lineup that can then be used to generate a playlist',
            usage = '''spypgen scrape file.png [<args>]''')
        parser.add_argument('file', help='Image file to be scraped')
        parser.add_argument('-o', '--output', help='Output file for the scraped artists')
        parser.add_argument('-v', '--validate', action='store_true', help='Validates generated list of artists by querying Spotify (which requires credentials)')
        parser.add_argument('--include_invalid', action='store_true', help='Include artists not found in Spotify (useful for hand correcting)')
        parser.add_argument('-c','--credentials', default='credentials.json', help='File containing credentials information (user, client ID/secret, etc.) for Spotify')
        parser.add_argument('-w', '--whitelist_chars', default='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&()')
        parser.add_argument('-d', '--delimiter_chars', default=r'.,\-,\w')
        args = parser.parse_args(sys.argv[2:])

        raw_artists = self.process_image(args.file, args.whitelist_chars, args.delimiter_chars)
        processed_artists = self.process_raw(raw_artists, args.delimiter_chars.split(','))
        if args.validate:
            processed_artists = self.validate_artists(processed_artists, args.include_invalid, args.credentials)
        self.output_artists(processed_artists, args.output)

    def process_image(self, image_file, whitelist_chars, delimiter_chars):
        if image_file is None:
            print("No file was specified for scraping.")
            sys.exit(1)
        if not os.path.isfile(image_file):
            print("Specified file",image_file,"could not be found.")
            sys.exit(1)
        print("Processing image", image_file,"using Tesseract OCR...")
        return image_to_string(Image.open(image_file), config="-c tessedit_char_whitelist=" + whitelist_chars + delimiter_chars + " psm 6")
        
    def process_raw(self, raw_ocr_str, delimiter_chars):
        print("Cleaning OCR output...")
        sample_delim = ' ' + delimiter_chars[0] + ' '
        processed_str = raw_ocr_str.replace('\n', sample_delim)
        #replace B2B and known misparsed variations (323, 828, etc.) with a delimiter character
        processed_str = re.sub('[835BED][2|Z][835BED]', sample_delim, processed_str)
        delimiter_chars.append(',')
        delimiters_chars_without_slashw = '[' + '|'.join([char for char in delimiter_chars if char != r'\w']) + ']'
        split_delim  = '( [' + '|'.join(delimiter_chars) + '] )|( ' + delimiters_chars_without_slashw + ')|(' + delimiters_chars_without_slashw + ' )'
        #Delimiters should be prefaced or suffixed with a ' ', unless the delimiter is \w, in which case it must be both prefixed and suffixed with ' '
        split_artists = re.split(split_delim, processed_str)
        stripped_artists = [sa.strip() for sa in split_artists if sa is not None]
        for i in range(0, len(stripped_artists)):
            artist = stripped_artists[i]
            #remove set qualifier in parentheses (e.g. (LIVE), (OLD SCHOOL SET), etc.)
            artist = re.sub(r'\([a-zA-Z ]*\)', '', artist)
            #remove set qualifier based on presents (e.g. 'Ben Nicky Presents HF XTreme')
            stripped_artists[i] = re.sub(r'(PRESENTS|[P|p]resents|LIVE|[L|l]ive).*', '', artist)
        return [artist for artist in stripped_artists if len(artist) > 1]

    def validate_artists(self, unvalidated_artists, include_invalid, credentials):
        validated_artists = []
        print("Validating parsed artists...")
        if not self.authorize_generator(credentials):
            print("Unable to authenticate with Spotify, which prevents validation of the artists")
        else:
            for artist in unvalidated_artists:
                spotify_artist = self.playlist_generator.find_artist(artist) 
                if not spotify_artist and 'V' in artist:
                    spotify_artist = self.playlist_generator.find_artist(re.sub('V','Y', artist))
                if not spotify_artist:
                    validated_artists.append((artist,"NotFound"))
                else:
                    validated_artists.append((artist,spotify_artist[0]))
        success_rate = len([artist for artist in validated_artists if artist[1] != 'NotFound'])/len(validated_artists)
        print('Validated artists (',success_rate,'%):')
        for artist in validated_artists:
            print(artist)
        if include_invalid:
            processed_artists = [artist[1] if artist[1] != 'NotFound' else artist[0] for artist in validated_artists]
        else:
            processed_artists = [artist[1] for artist in validated_artists if artist[1] != 'NotFound']
        return processed_artists

    def output_artists(self,artists,output_file):
        if output_file is not None:
            with open(output_file, 'w+') as file:
                if output_file.endswith('.json'):
                    file.write('{\n')
                    file.write('\t"artists":[\n')
                    file.write('\t\t"')
                    file.write('",\n\t\t"'.join(artists))
                    file.write('"\n')
                    file.write('\t]\n')
                    file.write('}')
                elif output_file.endswith('.csv'):
                    file.write(','.join(artists))
                else:
                    file.write('\n'.join(artists))
        else:
            for artist in artists:
                print(artist)

    def authorize_generator(self, credentials_file):
        if not os.path.isfile(credentials_file):
            print("Specified credentials file",credentials_file,"was not found, so authentication with Spotify cannot proceed.")
            return None

        with open(credentials_file) as file:
            credentials = json.loads(file.read())

        user = credentials.get("user")
        client_id = credentials.get("clientId")
        client_secret = credentials.get("clientSecret")
        redirect_port = int(credentials.get("redirectLocalHostPort"))

        if user is None:
            print("'user' not specified in",credentials_file)
            return None
        if client_id is None:
            print("'clientId' not specified in",credentials_file)
            return None
        if client_secret is None:
            print("'clientSecret' not specified in",credentials_file)   
            return None
        if redirect_port is None:
            print("'redirectLocalHostPort' not specified in",credentials_file)
            return None

        if self.playlist_generator.authorize(user,client_id,client_secret,redirect_port):
            return user
        else:
            return None


if __name__ == "__main__":
    app = Application()