import unittest
import unittest.mock
import sys
import urllib.request
from unittest.mock import patch, MagicMock
from spypgen.tracklistscraper import TracklistScraper
from spypgen.tracklistscraper import Track
from bs4 import BeautifulSoup

class TestBasicFunction(unittest.TestCase):

    def setUp(self):
        with open('test/matzo_index.html', 'r') as file:
            self.example_idx = file.read()
        with open('test/matzo_example_tracklist.html', 'r') as file:
            self.example_tracklist = file.read()
        self.scraper = TracklistScraper()

    @patch('urllib.request.urlopen')
    def test_get_artist_tracklists_calls_lowercased_artistname_url(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = ''
        mock_urlopen.return_value = cm

        self.scraper.get_artist_tracklists("Tinlicker")
        mock_urlopen.assert_called_with('https://www.1001tracklists.com/dj/tinlicker/index.html')  

    @patch('urllib.request.urlopen')
    def test_get_artist_tracklists_replaces_spaces_with_hyphens_in_called_url(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = ''
        mock_urlopen.return_value = cm

        self.scraper.get_artist_tracklists("Mat Zo")
        mock_urlopen.assert_called_with('https://www.1001tracklists.com/dj/mat-zo/index.html')     

    @patch('urllib.request.urlopen')
    def test_get_artist_tracklists_removes_amperstands_in_called_url(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = ''
        mock_urlopen.return_value = cm

        self.scraper.get_artist_tracklists('Above & Beyond')
        mock_urlopen.assert_called_with('https://www.1001tracklists.com/dj/abovebeyond/index.html')     

    @patch('urllib.request.urlopen')
    def test_get_artist_tracklists_fetches_tracklists_names_and_links(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = self.example_idx
        mock_urlopen.return_value = cm

        tracklists = self.scraper.get_artist_tracklists("Mat Zo")
        self.assertEqual(len(tracklists), 4)
        self.assertEqual(tracklists[0], 
            ('/tracklist/2wdkk149/mat-zo-dombresky-night-owl-radio-194-2019-05-03.html', 
                'Mat Zo & Dombresky - Night Owl Radio 194'))
        self.assertEqual(tracklists[1], 
            ('/tracklist/25364lvt/swedish-egil-mat-zo-groove-radio-international-1360-2018-12-19.html', 
                'Swedish Egil & Mat Zo - Groove Radio International #1360'))
        self.assertEqual(tracklists[2], 
            ('/tracklist/2bpt9n51/richard-vission-chris-liebing-mat-zo-vanilla-ace-powertools-mixshow-2018-11-24.html', 
                'Richard Vission & Chris Liebing & Mat Zo & Vanilla Ace - Powertools Mixshow'))
        self.assertEqual(tracklists[3], 
            ('/tracklist/2wcy10d9/above-and-beyond-mat-zo-group-therapy-radio-304-2018-10-26.html', 
                'Above & Beyond & Mat Zo - Group Therapy Radio 304'))

    @patch('urllib.request.urlopen')
    def test_get_tracklist_tracks_fetches_correct_url(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = ''
        mock_urlopen.return_value = cm

        self.scraper.get_tracklist_tracks('/tracklist/1cwxhltk/mat-zo-anjunabeats-classics-set-the-observatory-santa-ana-united-states-2017-07-15.html')
        mock_urlopen.assert_called_with('https://www.1001tracklists.com/tracklist/1cwxhltk/mat-zo-anjunabeats-classics-set-the-observatory-santa-ana-united-states-2017-07-15.html')     

    @patch('urllib.request.urlopen')
    def test_get_tracklist_tracks_returns_list_track_objs(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = self.example_tracklist
        mock_urlopen.return_value = cm

        tracks = self.scraper.get_tracklist_tracks('/tracklist/1cwxhltk/mat-zo-anjunabeats-classics-set-the-observatory-santa-ana-united-states-2017-07-15.html')
        self.assertEqual(tracks[0],Track('Reeves - Call Of Loneliness (Mat Zo Remix)','Reeves',False,5))
        self.assertEqual(tracks[1],Track('Mat Zo - Yoyo Ma','Mat Zo',True,21))
        self.assertEqual(tracks[2],Track('deadmau5 - Not Exactly','deadmau5',False,77))
        self.assertEqual(tracks[3],Track("Above & Beyond ft. Ashley Tomberlin - Can't Sleep",'Above & Beyond',False,58))
        self.assertEqual(tracks[4],Track('Above & Beyond & Andy Moor - Air For Life','Above & Beyond & Andy Moor',True,80))
        self.assertEqual(tracks[5],Track('OceanLab & Above & Beyond vs. Mat Zo & Arty ft. Justine Suissa - Satellite vs. Synapse Dynamics (Mat Zo Mashup)','OceanLab & Above & Beyond vs. Mat Zo & Arty',False,29))
        self.assertEqual(tracks[6],Track('Mat Zo - Synapse Dynamics (Arty Remix)','Mat Zo',True,0))
        self.assertEqual(tracks[7],Track('Porter Robinson & Mat Zo - Easy','Porter Robinson & Mat Zo',True,587))
        self.assertEqual(tracks[8],Track('Ravenkis vs. Mat Zo ft. Rachel K Collier - Stellar vs. Only For You (Mat Zo Mash Up)','Ravenkis vs. Mat Zo',False,0))
        self.assertEqual(tracks[9],Track('RavenKis - Stellar','RavenKis',True,0))
        self.assertEqual(tracks[10],Track('Mat Zo ft. Rachel K Collier - Only For You','Mat Zo',False,0))
        self.assertEqual(tracks[11],Track("Arty & Mat Zo vs. The Temptations - Mozart vs. Ain't Too Proud To Beg (Mat Zo Mashup)",'Arty & Mat Zo vs. The Temptations',False,0))
        self.assertEqual(tracks[12],Track('Signalrunners - Meet Me In Montauk','Signalrunners',False,29))
        self.assertEqual(tracks[13],Track('Mat Zo - Superman','Mat Zo',False,122))
        self.assertEqual(tracks[14],Track('Signalrunners ft. Julie Thompson - These Shoulders','Signalrunners',False,34))
        self.assertEqual(tracks[15],Track('Super8 & Tab - Needs To Feel (Wippenberg Remix)','Super8 & Tab',False,33))
        self.assertEqual(tracks[16],Track('Cressida - 6AM (Kyau & Albert Remix)','Cressida',False,86))
        self.assertEqual(tracks[17],Track('Chris Malinchak - So Good To Me (Westfunk & Steve Smart Remix)','Chris Malinchak',False,36))
        self.assertEqual(tracks[18],Track('Arty & Mat Zo - Rebound','ARTY & Mat Zo',False,257))
        self.assertEqual(tracks[19],Track('Kyau & Albert & Mat Zo vs. Daft Punk - Be There 4 U One More Time (Above & Beyond Bootleg)','Kyau & Albert & Mat Zo vs. Daft Punk',False,10))
        self.assertEqual(tracks[20],Track('Daft Punk - One More Time','Daft Punk',True,0))
        self.assertEqual(tracks[21],Track('Kyau & Albert - Be There 4 U (Mat Zo Remix)','Kyau & Albert',False,0))
        self.assertEqual(tracks[22],Track("Mat Zo - Don't Say The T Word",'Mat Zo',False,8))

if __name__ == '__main__':
    unittest.main()