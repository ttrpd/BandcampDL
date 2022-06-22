import argparse
import glob
import music_tag

def printTags(track):
	print(track)

### TrackName ###
def setTrackName(track, name):
	track['tracktitle'] = name

def printTrackName(track):
	print(track['tracktitle'])

### Artist ###
def setArtistName(track, name):
	track['artist'] = name
	track['albumartist'] = name
	track['composer'] = name

def printArtistName(track):
	print(track['artist'])

### Album ###
def setAlbumName(track, name):
	track['album'] = name

def printAlbumName(track):
	print(track['album'])

### Album Art ###
def setAlbumArt(track, imgPath):
	with open(imgPath, 'rb') as art:
		track['artwork'] = art.read()

### Track ###
def setTrackNumber(track, num):
	track['tracknumber'] = num
	# track.add(TRCK(encoding=3, text=num))
	# track.save()

def printTrackNumber(track):
	print(track['tracknumber'])


### Declaring the command line arguments ###
parser = argparse.ArgumentParser(description='Edits the metadata of media files')
parser.add_argument('path', metavar='FILE PATH', nargs='?', help='The path of the file(s) to be edited')
parser.add_argument('-name', metavar='Name', nargs='?', help='The new name for the track')
parser.add_argument('-artist', metavar='Artist', nargs='?', help='The new artist for the track')
parser.add_argument('-album', metavar='Album', nargs='?', help='The new album for the track')
parser.add_argument('-number', metavar='Number', nargs='?', help='The new number for the track')
parser.add_argument('-numbers', metavar='Numbers', nargs='+', help='A list of numbers to map to the given collection of tracks')
parser.add_argument('-art', metavar='Art', nargs='?', help='The new art for the track')

# parse the command line input
args = vars(parser.parse_args())

if not (args['numbers'] is None): # if numbers list is provided
	args['numbers'].reverse() # reverse it

# a dictionary relating the values to be set
# to the functions that set them
funcs = {
	'name' : setTrackName,
	'artist' : setArtistName,
	'album' : setAlbumName,
	'number' : setTrackNumber,
	'art' : setAlbumArt,
	'numbers' : (lambda track, num: setTrackNumber(track, args['numbers'].pop()) if len(args['numbers']) else False)
}


if not (args['path'] is None): # if a path is given
	for file in glob.glob(args['path']): # for every file it refers to
		f = music_tag.load_file(file) # load tags from file
		for arg, val in list(args.items())[1:]: # for every tag in that file (excluding path itself)
			if not (val is None): # if a value for this tag was given
				funcs[arg](f, val) # set the appropriate tag to the given value
		f.save() # write tags to file