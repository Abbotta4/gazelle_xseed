#!/usr/bin/python

import sys
import requests
import json
import time

if len(sys.argv) != 3:
	print "usage: test.py [gazelle username] [gazelle password]"
	sys.exit()

baseurl = 'https://apollo.rip/'

GAZELLE_USER = sys.argv[1]
GAZELLE_PASS = sys.argv[2]

data = {
	'action' : 'login',
	'username' : GAZELLE_USER,
	'password' : GAZELLE_PASS
}

# should search string be argv[3] ?
searchstring = "take care"

with requests.Session() as s:

	s.post(baseurl + 'login.php', data = data)
	r = s.get(baseurl + 'ajax.php?action=browse&searchstr=' + searchstring)
	j = r.json()

	if j['status'] == 'success':
		results = j['response']['results']
		print(str(len(results)) + ' torrent groups:')
		for x in results:
			print (x['artist'] + ' - ' + x['groupName'])
		print('going to try ' + results[0]['artist'] + ' - ' + results[0]['groupName'] + ' first')
		print('Sleeping for 5s as per https://goo.gl/RL8mCk')
		time.sleep(5)
		r2 = s.get(baseurl + 'ajax.php?action=torrentgroup&id=' + str(results[0]['groupId']))
		j2 = r2.json()
		print('sizes of releases:')
		for x in range(0, len(j2['response']['torrents'])):
			print(j2['response']['torrents'][x]['media'] + ' ' + j2['response']['torrents'][x]['format'] + j2['response']['torrents'][x]['encoding'] + ': ' + str(j2['response']['torrents'][x]['size']))

	else:
		print("apl requests failed")
