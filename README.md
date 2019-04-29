# spypgen - SpotiPy Playlist Generator

## Introduction

_spypgen_ makes it easy to create playlists in Spotify based on a combination of data from Spotify itself and 1001Tracklists. 

## Setup 

### Install dependencies

```shell
python -m pip install requirements.txt
```

### Get Credentials

In order to use spypgen, you need to have valid Spotify credentials. Most of these values are based on configurations obtained by creating and configuring a new client application using the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and login to your Spotify account
1. Create a new client application using '_Create a Client ID_'
1. Configure the client application
    * Edit the settings and add a _redirect URI_ to http://localhost:PORT with a PORT of your choosing
    * Note the Client ID, Client Secret, and the port you chose
1. Use these values to create a JSON file of the following form:

    ```json
    {
      "user": "1255681820",
      "clientId": "d7b9a822782146c2b18cd79e1ccef473",
      "clientSecret": "e244999b618e48e38afbefd6a43d2e11",
      "redirectLocalHostPort": 8080
    }
    ```
    * _user_
        * Obtained by examining your profile in Spotify, and then hitting the ellipses > Share > Copy Spotify URI
    * _clientId_ / _clientSecret_
        * Obtained by visiting the and then creating a Client ID (see above)
    * _redirectLocalHostPort_
        * Needed in order for OAuth2 redirection while authentication with Spotify
        * Should match the port set as your localhost redirect (see above)

## Features

---

### Playlist Generation

Playlist generation using __spypgen__ can use two different workflows depending on the configurability desired.

#### Basic 

```python
$> spypgen generate -c "credentials.json" -n "PlaylistName" -s "Artist 1,Artist2"
```

This generates a playlist with the given name with the default number of songs (5) for each of the artists provided in the comma-separated string based purely off of their popular Spotify songs. 

```python
$> spypgen generate -c "credentials.json" -p "playlist.json"   
```

#### Advanced

This generates a playlist based on detailed configurations specified in a JSON file that appears as follows:

```json
{
    "name": "Anjunabeats LA Day 1",
    "artists": ["Mat Zo","Tinlicker","Grum","ALPHA 9","Jason Ross","Gabriel & Dresden"],
    "targetSongCounts":
    {
        "maxSongsPerArtist": 8,
        "recentSetListSongs": 5,
        "includeTopSpotifySongs": true
    },
    "setlists":
    {
        "numberSearched": 5,
        "inclusionThreshold": 0.5
    },
    "strictSearch": false
}
```

* _name_ - playlist name
* _artists_ - array of artists
* _targetSongCounts_
  * _maxSongsPerArtist_ - Maximum amount of songs included for each artist
  * _recentSetListSongs_ - Maximum amount of songs included for each artist from their recent sets, as listed on 1001Tracklists
  * _includeTopSpotifySongs - Whether to include top Spotify songs when an insufficient number of songs are found from the recent set lists
* _setlists_
  * _numberSearched_ - Number of recent setlists searched for each artist (i.e. n most recent set lists)
  * _inclusionThreshold_ - Barrier for inclusion of a recent set list song (
      * e.g. if set to 0.5, songs are only included if they are played in at least half of the artist's last n sets
* _strictSearch_ - when enabled, found artists are only included if they exactly match the case-insensitive search query 

#### Methodology of Playlist Generation

1. Authenticate with Spotify using OAuth2 and redirecting to a localhost port served by a simple HTTP listener in order to get an access code

    ```text
    Attempting to access https://accounts.spotify.com/authorize?client_id=d7b9a822782146c2b18cd79e1ccef473&response_type=code&redirect_uri=http://localhost:8080&scope=playlist-modify-public
    127.0.0.1 - - [28/Apr/2019 16:40:44] "GET /?code=AQD7NWtH-Y-cSt0QND_XbeSdHeBfKWl8C8MnGJxg4CQNqZh5pbvdG9kab8V5uXbemhspnjFyJbB7OEjSoz9aO5sBZjihhxPyT6K3mw7VU3TFq3zPdnmA2nessVV-D3kx-wV9TT3ezIYCplZuyRbQ5ECD8N2HzFiIdfoIwZPBoeB1mmoKUfYZEWYQwDh8uyRWZLMiT9s02Ke02J5M7rd_2D0CqyLc HTTP/1.1" 200 -
    /usr/local/lib/python3.7/dist-packages/urllib3/connectionpool.py:847: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    InsecureRequestWarning)
    Access token is: BQDQ8EnQ6lN93xnNvvPx_2jLntxMIMtCSTMBZleUlKkcHcugFtF_l3Lca1pEiY5SSX042ZVd_OZ6XvkPdfkeqSBIwtmz09cRa2TlvxeXcKOlb_HLuFV6GrXnIZxsQoepdH0nyhBOmNYWRHDwRLEogb7KU22iZVpqt8AZUANZp2Hh_aBDyY-8
    ```
    * Note- this will open a new tab on your browser
1. Create an empty playlist
1. Find the artists in Spotify
1. If configured, scrape recent sets for each artist on 1001Tracklists to determine commonly played tracks

    ```text
    Searching for artist Grum...
    Found Grum.
    Finding top tracks for artist Grum...
    Accessing https://www.1001tracklists.com/dj/grum/index.html...
    Accessing https://www.1001tracklists.com/tracklist/1r48mch9/grum-egg-london-podcast-160-2019-03-03.html...
    Accessing https://www.1001tracklists.com/tracklist/1yl8l1p9/grum-the-awakening-transmission-prague-o2-arena-prague-czech-republic-2018-10-27.html...
    Accessing https://www.1001tracklists.com/tracklist/v5yqttk/grum-audio-san-francisco-united-states-2018-10-06.html...
    Accessing https://www.1001tracklists.com/tracklist/1ftsp51k/grum-analog-bkny-united-states-2018-10-05.html...
    Accessing https://www.1001tracklists.com/tracklist/u7wrw2t/grum-abgt-300-asiaworld-expo-hong-kong-2018-09-29.html...
    38%|█████████████████████████████████████████████████████████          
    ```
1. Include tracks that meet the inclusion threshold and track limits

    ```text
    Including Grum - Shout since it was played in 4/5 of Grum's recent sets
    Including Grum - Price Of Love since it was played in 4/5 of Grum's recent sets
    Including Grum & Fehrplay - Spirit since it was played in 4/5 of Grum's recent sets
    Including Grum - U since it was played in 3/5 of Grum's recent sets
    Including Rolo Green - Penrith since it was played in 3/5 of Grum's recent sets
    Searching for Grum - Shout...
    44%|█████████████████████████████████████████████████████████████▌     
    ```

1. If configured, add popular tracks from Spotify to fulfill the targeted amount of songs for the artist
1. Output tracklist

    ```text
    ...
    Because You Move Me - Tinlicker,Helsloot
    About You - Tinlicker
    Less Than a Minute - Tinlicker
    Deep Inside - Mat Zo
    Vice - Mat Zo
    Shivers - ALPHA 9 Remix - Armin van Buuren,Susana,ALPHA 9
    As The Rush Comes - Gabriel & Dresden Chillout Mix - Motorcycle,Gabriel & Dresden
    Hey Now - Arty Remix - London Grammar,ARTY
    100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 126/126 [00:51<00:00,  2.84it/s]
    ```
---


### Lineup Scraping

__spypgen__ also supports scraping a list of artists from an image of a lineup, which can then be utilized to create playlist using the _generate_ command. Unfortunately, this comes with the caveat that due to the nature of OCR, this is not 100% accurate, though results can be improved through manipulation of contrast on the image and other pre-processing. 

#### Basic

```shell
spypgen scrape lineup.png 
```

Scrapes a lineup and outputs a list of the found artists to the console with minor processing based on standard delimiters

#### With Validation

```shell
spypgen scrape lineup.png -c credentials.json -v
```

Leveraging existing Spotify credentials, __spypgen__ will query Spotify in order to validate each of the artists found. This allows for the correction of simple mistakes made during OCR.

```text
Found Rezz.
Searching for artist RINZEN...
Found Rinzen.
Searching for artist MATT LANGE...
Found Matt Lange.
Searching for artist RJ VAN XETTEN...
Found Rj Van Xetten.
Searching for artist RL GRIME...
Found RL Grime.
Searching for artist ROB GEE...
Found Rob Gee.
Searching for artist SIAN...
Found Sian Evans.
Searching for artist SLANDER...
Validated artists:  62%|████████████████████████████████████████████████████████████████████████                                             | 154/250 [00:52<00:28,  3.36artist/s]
```

#### Further Customization

Other command line arguments can be used to further customize the lineup processing:

* -o (--output) - specify file for the output artists, which supports the following formats:
  * .csv
  * .json 
  * .txt
* -w (--whitelist_chars) - specified characters that will be recognized by the OCR as a component of an artist's name
  * default - 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&()
* -d (--delimiter_chars) - specified characters that will be recognized by the OCR as delimiters
  * default - \.,\-
  * Note: must be ','-separated
* --include_invalid - includes artists unsuccessfully validated using Spotify in the output so that they can be hand corrected 

