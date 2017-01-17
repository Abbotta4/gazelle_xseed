#!/usr/bin/python

import sys
import requests
import json
import time
import bencode
import subprocess
import glob
import hashlib
import logging

BASEURL = 'https://passtheheadphones.me/'
GAZELLE_USER = sys.argv[1]
GAZELLE_PASS = sys.argv[2]
AUTHKEY = sys.argv[3]
TORRENTPASS = sys.argv[4]
DEL_USER = sys.argv[5]
DEL_PASS = sys.argv[6]

TORRENTS = glob.glob("*torrent")

logging.basicConfig(filename='gazelle_xseed.log',level=logging.DEBUG)

if len(sys.argv) != 7:
	print "usage: test.py [gazelle username] [gazelle password] [authkey] [torrent_pass] [deluge username] [deluge password]"
	sys.exit()

def download_file(url, name):
    local_filename = name
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename

def get_infohash(torrent):
	tf = open(torrent)
	df = bencode.bdecode(tf.read())
	info = df['info']
	tf.close()
	# infohash is the SHA1 hash of the contents of 'info'
	return hashlib.sha1(bencode.bencode(info)).hexdigest()
	

def force_recheck(torrent, username, password):
	connect_args = 'connect localhost ' + username + ' ' + password + '; '
	subprocess.call(['deluge-console', connect_args + 'add ' + torrent])
	subprocess.call(['deluge-console', connect_args + 'recheck ' + get_infohash(torrent)])

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

	s.post(BASEURL + 'login.php', data = login_data)

	test_login = s.post(BASEURL + 'ajax.php')
	if test_login.text == '{"status":"failure","response":[]}':
		logging.info('Authenticated successfully with gazelle')

		for n in TORRENTS:

			torrent_file = open(n)
			dectorrent = bencode.bdecode(torrent_file.read())

			torrentsize = 0
			filelist = dectorrent['info']['files']
			for t in range(0, len(filelist)):
		        	torrentsize += filelist[t]['length']

			searchstring = ' '.join(x['path'][0] for x in dectorrent['info']['files'])

			time.sleep(5) # privisional wait
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
								possible_find = True
								torrentid = results[iter]['torrentId']
						else:
							for t in range(0, len(results[iter]['torrents'])):
								if results[iter]['torrents'][t]['size'] == torrentsize:
									possible_find = True
									torrentid = results[iter]['torrents'][t]['torrentId']
									break

						if possible_find:
							downloadstring = 'torrents.php?action=download&id=' + str(torrentid) + '&authkey=' + AUTHKEY + '&torrent_pass=' + TORRENTPASS
							downloaded_torrent_name = 'torrent' + str(TORRENTS[n].zfill(5)) + '.torrent'
							print ('Found a potential match for ' + dectorrent['info']['name'] + ' at ' + BASEURL + 'torrents.php?torrentid=' + str(torrentid))
							logging.info('Found a potential match for ' + dectorrent['info']['name'] + ' at ' + BASEURL + 'torrents.php?torrentid=' + str(torrentid))
							download_file(BASEURL + downloadstring, downloaded_torrent_name)
							if force_recheck(downloaded_torrent_name, DEL_USER, DEL_PASS):
								print('Successfully found ' + dectorrent['info']['name'])
								logging.info('Successfully found ' + dectorrent['info']['name'])
								found = True

					if not found:
						print('Could not find ' + dectorrent['info']['name'])
						logging.info('Could not find ' + dectorrent['info']['name'])
				else:
					print('No results for ' + dectorrent['info']['name'])
					logging.info('No results for ' + dectorrent['info']['name'])

			else:
				print('Requests failed.')
				logging.critical('Requests failed. Most likely an error with the site.')
				sys.exit()

			torrent_file.close()

	else:
		print ('Could not authenticate. (Wrong gazelle password?)')
		logging.critical('Could not authenticate. (Wrong gazelle password?)')
		sys.exit()
