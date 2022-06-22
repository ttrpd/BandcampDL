import requests
import re
import os
import sys
import json
import mutagen
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TALB, APIC
from bs4 import BeautifulSoup as bs

def sanitize(str):
	return re.sub(r'[/\\:*?"<>|]', '', str)

def getArtistName(albumJSON):
	return sanitize(albumJSON["artist"])

def getAlbumName(albumJSON):
	return sanitize(albumJSON["current"]["title"])

def getTrackName(trackJSON):
	return sanitize(trackJSON["title"])

def getAlbumJSON(html):
	data = bs(html, features='html.parser')
	return json.loads(data.find_all("script", {"data-tralbum": True})[0]["data-tralbum"])
	# print(json.dumps(albumJSON, indent=4, sort_keys=True ))

def getURLFormattedArtistName(link):
	return link[8:link.find('.')]

def getURLFormattedAlbumName(link):
	return link[link.rfind('/')+1:]

def getAlbumArt(link, cd, html):
	album = getURLFormattedAlbumName(link)
	artist = getURLFormattedArtistName(link)
	data = bs(html, features='html.parser')
	imageLink = str(data.findAll("a", {"class" : "popupImage"})[0]['href'])# this gets the largest version of the image, there is a link to a smaller version in the img tag contained within [0]
	artResp = requests.get(imageLink)
	with open(cd+'/'+artist+'-'+album+'AlbumArt.jpg', 'wb') as f:
		f.write(artResp.content)
	
	return cd+'/'+artist+'-'+album+'AlbumArt.jpg'

def getTrack(cd, album, artist, artPath, trackJSON):
	name = getTrackName(trackJSON)
	print('downloading '+name+'...')
	print(trackJSON['file']['mp3-128'])
	trackResp = requests.get(trackJSON['file']['mp3-128'])
	trackPath = cd+'/'+name+'.mp3'
	with open(trackPath, 'wb') as f:
		f.write(trackResp.content)

	try:
		tg = ID3(trackPath)
	except mutagen.id3.ID3NoHeaderError:
		tg = mutagen.File(trackPath)
		tg.add_tags()

	tg['TPE1'] = TPE1(encoding=3, text=artist)
	tg['TALB'] = TALB(encoding=3, text=album)
	tg['TIT2'] = TIT2(encoding=3, text=name)
	tg['TRCK'] = TRCK(encoding=3, text=str(trackJSON["track_num"]))

	with open(artPath, 'rb') as art:
		tg['APIC'] = APIC(
			data=art.read(),
			mime='image/jpeg',
			type=3, desc=u'Cover',
			encoding=3
		)
		tg.save()

def getAlbum(link, downloadDirectory):
	html = requests.get(link).content
	albumJSON = getAlbumJSON(html)
	album = getAlbumName(albumJSON)
	artist = getArtistName(albumJSON)

	print("\n### Downloading "+album+" ###")
	# if the artist's folder doesn't exist in the downloadDirectory
	if(not os.path.exists(downloadDirectory+'/'+artist)):
		# make a folder for the artist
		os.mkdir(downloadDirectory+'/'+artist)
	# make the downloadDirectory this artist's folder
	downloadDirectory = downloadDirectory+'/'+artist
	# if the album's folder doesn't exist in the artist's folder
	if(not os.path.exists(downloadDirectory+'/'+album)):
		# make a folder for the album
		os.mkdir(downloadDirectory+'/'+album)
	# make the downloadDirectory the album's folder in the artist's folder  
	downloadDirectory = downloadDirectory+'/'+album

	# download album art (this is not strictly neccessary)
	art = getAlbumArt(link, downloadDirectory, html)

	# for every track object in the albumJSON["track-info"] (which is a list)
	for trackJSON in albumJSON["trackinfo"]:
		# download the track
		getTrack(downloadDirectory, album, artist, art, trackJSON)

# usage and arg checking
if(len(sys.argv) < 2):
	print("""
	Usage: python bandcamp-dl.py [link] [download destination]

	link                 - the URL to the artist or album page
	download destination - the file path to the folder in which new folders should be created

	as of 8/19/2018 this program only works on albums that can be played for free in full
		""")

	exit()
elif(len(sys.argv) == 2):
	downloadDirectory = '.'
else:
	downloadDirectory = sys.argv[2]

# sets link to the given link
link = sys.argv[1]

# gets the album page response
html = requests.get(link).content
# does the html contain an inline audio player?
if(len(bs(html, features='html.parser').find_all("div", {"class":"inline_player"}))):
	# it does, so it's an album or track link
	getAlbum(link, downloadDirectory)
else:
	# it doesn't, so it's an artist link
	for alb in bs(html, features='html.parser').find("div", {"class":"leftMiddleColumns"}).find("ol").find_all("li"):
		getAlbum(link+alb.find("a")["href"], downloadDirectory)
