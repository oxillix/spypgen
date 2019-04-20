#import requests
from bs4 import BeautifulSoup
import urllib.request
import pprint 

class Track:
    def __init__(self, full_name, artist, available_on_spotify=False, plays=0):
        self.full_name = full_name
        self.artist = artist
        self.available_on_spotify = available_on_spotify
        self.plays = plays


class TracklistScraper:
    def get_artists_popular_recent_tracks(self,artist_name,max_num_tracks,max_tracklists=5,threshold=0.5):
        plays_by_track = self.get_artist_tracks(artist_name,max_tracklists)
        sorted_tracks = sorted(plays_by_track, key=lambda k: (-plays_by_track[k][0],-plays_by_track[k][1]))
        recent_tracks = []
        for track in sorted_tracks:
            if plays_by_track[track][0]/max_tracklists < threshold:
                break;
            if len(recent_tracks) == max_num_tracks:
                break;
            print(track,'was played in',plays_by_track[track][0],'/',max_tracklists,'of',artist_name,'\'s recent sets')
            recent_tracks.append(track)
        return recent_tracks

    def get_artist_tracks(self,artist_name,max_tracklists=5,spotify_tracks_only=True):
        tracklists = self.get_artist_tracklists(artist_name,max_tracklists)
        plays_by_tracklist = {}
        for tracklist in tracklists:
            tracks = self.get_tracklist_tracks(tracklist[0])
            for track in tracks:
                if not spotify_tracks_only or (spotify_tracks_only and track.available_on_spotify):
                    if track.full_name in plays_by_tracklist:
                        plays_by_tracklist[track.full_name] = (plays_by_tracklist[track.full_name][0] + 1, plays_by_tracklist[track.full_name][1] + track.plays)
                    else:
                        plays_by_tracklist[track.full_name] = (1,track.plays)
        return plays_by_tracklist

    def get_artist_tracklists(self, artist_name,max_tracklists=None):
        artist_name = artist_name.lower().replace(" & ","").replace("&","").replace(" ", "-")
        target_url = "https://www.1001tracklists.com/dj/" + artist_name + "/index.html"
        page = self.get_page(target_url)
        if page is None:
            return []
        soup = BeautifulSoup(page.read(), "html.parser")
        rows = soup.find_all('div', class_="tlLink")
        if max_tracklists is not None:
            rows = rows[:max_tracklists]
        links = [row.find_all('a', href=True)[0] for row in rows]
        return [(link['href'], link.contents[0]) for link in links]

    def get_tracklist_tracks(self, tracklist_link):
        target_url = "https://www.1001tracklists.com" + tracklist_link
        page = self.get_page(target_url)
        if page is None:
            return []
        soup = BeautifulSoup(page.read(), "html.parser")
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('tlp_'))
        tracks = []
        for row in rows:
            metadata_div = row.find('div',class_='tlToogleData')
            if metadata_div:
                track_meta = metadata_div.find('meta',itemprop='name')
                if track_meta is None:
                    continue 
                track_name = track_meta['content']
                artist_meta = metadata_div.find('meta',itemprop='byArtist')
                if artist_meta is None:
                    continue
                artist_name = artist_meta['content']
                plays_and_media_div = row.find('div',class_='addMedia')
                plays = 0
                available_on_spotify = False
                if plays_and_media_div:
                    plays_span = plays_and_media_div.find('span',class_='badge playC')
                    if plays_span:
                        plays = plays_span.contents[1]
                    available_on_spotify = plays_and_media_div.find('i', class_=lambda x: x and 'spotify' in x) != None
                tracks.append(Track(track_name, artist_name, available_on_spotify, int(plays)))
        return tracks
    
    def get_page(self,target_url):
        print('Accessing', target_url,'...')
        try:
            page = urllib.request.urlopen(target_url)
            return page
        except:
            print('Unable to access',target_url)
            return None