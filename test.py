#!/usr/bin/python

import sys
import requests
import json
import time
import bencode
import subprocess
import glob
import hashlib
from os import path

BASEURL = 'https://passtheheadphones.me/'
GAZELLE_USER = sys.argv[1]
GAZELLE_PASS = sys.argv[2]
AUTHKEY = sys.argv[3]
TORRENTPASS = sys.argv[4]
TORRENTS = glob.glob("*torrent")
DEL_USER = sys.argv[5]
DEL_PASS = sys.argv[6]

if len(sys.argv) != 4:
	print "usage: test.py [gazelle username] [gazelle password] [authkey] [torrentpass] [deluge username] [deluge password]"
	sys.exit()

def download_file(url, name):
    local_filename = name
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

def get_infohash(torrent):
	tf = open(torrent)
	df = bencode.bdecode(tf.read())
	info = df['info']
	return hashlib.sha1(bencode.bencode(info)).hexdigest()

def force_recheck(infohash, username, password):
	connect_args = 'connect localhost ' + username + ' ' + password + '; '

	done = False
	while not done:
	        done = True
	        i = subprocess.check_output(['deluge-console', connect_args + 'info ' + infohash])
	        output = i.split('\n')
	        time.sleep(3)
	        for l in output:
	                if l.startswith('Progress'):
	                        done = False

	i = subprocess.check_output(['deluge-console', connect_args + 'info ' + infohash])
	output_lines = i.split('\n')
	for l in output_lines:
	        if l.startswith("Size"):
	                size_line = l

	done_size = size_line.split(' ')
	out_of = done_size[2].split('/')[1]

	if done_size[1] == out_of:
	        return True
	else:
	        return False
	
login_data = {
	'action' : 'login',
	'username' : GAZELLE_USER,
	'password' : GAZELLE_PASS
}

with requests.Session() as s:

	s.post(baseurl + 'login.php', data = login_data)

	for n in TORRENTS:

		torrent_file = open(n)
		dectorrent = bencode.bdecode(torrent_file.read())

		torrentsize = 0
		filelist = dectorrent['info']['files']
		for t in range(0, len(filelist)):
	        	torrentsize += files[t]['length']

		searchstring = ' '.join(x['path'][0] for x in dectorrent['info']['files'])

		r = s.get(BASEURL + 'ajax.php?action=browse&filelist=' + searchstring)
		j = r.json()

		if j['status'] == 'success':
			results = j['response']['results']
			if results:
				found = False
				iter = 0
				while found == False and iter < len(results):
					possible_find = False
					if 'size' in results[iter]:
						if results[iter]['size'] == torrentsize:
							print('Found a potential match')
							possible_find = True
							torrentid = results[iter]['torrentId']
					else:
						for t in range(0, len(results[iter]['torrents'])):
							if results[iter]['torrents'][t]['size'] == torrentsize:
								print('Found a potential match')
								possible_find = True
								torrentid = results[iter]['torrents'][t]['torrentId']
								break

					if possible_find:
						downloadstring = 'torrents.php?action=download&id=' + str(torrentid) + '&authkey=' + AUTHKEY + '&torrentpass=' + TORRENTPASS
						downloaded_torrent_name = 'torrent' + str(TORRENTS[n].zfill(5)) + 'torrent'
						download_file(BASEURL + downloadstring, downloaded_torrent_name)
						if force_recheck(get_infohash(downloaded_torrent_name, DEL_USER, DEL_PASS)):
	
			else:
				print('No results')
	
		else:
			print('Requests failed')
			sys.exit()
