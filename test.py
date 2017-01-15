#!/usr/bin/python

import sys
import requests
import json
import time
import bencode
from os import path

if len(sys.argv) != 4:
	print "usage: test.py [gazelle username] [gazelle password] [.torrent file]"
	sys.exit()

baseurl = 'https://passtheheadphones.me/'

GAZELLE_USER = sys.argv[1]
GAZELLE_PASS = sys.argv[2]

data = {
	'action' : 'login',
	'username' : GAZELLE_USER,
	'password' : GAZELLE_PASS
}

with requests.Session() as s:

	torrent_file = open(sys.argv[3])
	dectorrent = bencode.bdecode(torrent_file.read())
	torrentsize = 0
	filelist = dectorrent['info']['files']
	for t in range(0, len(filelist)):
        	torrentsize += files[t]['length']
	searchstring = ' '.join(x['path'][0] for x in dectorrent['info']['files'])

	s.post(baseurl + 'login.php', data = data)
	r = s.get(baseurl + 'ajax.php?action=browse&filelist=' + searchstring)
	j = r.json()

	if j['status'] == 'success':
		results = j['response']['results']
		if results:
			found = false
			iter = 0
			while found == false and iter < len(results):
				if 'size' in results[iter]:
					if results['size'] == torrentsize:
						print('Found a potential match')
						
				else:
					
		else:
			print('No results')

	else:
		print('Requests failed')
