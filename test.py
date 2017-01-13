#!/usr/bin/python

import sys
import requests
import json

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
searchstring = "run the jewels"

with requests.Session() as s:
    s.post(baseurl + 'login.php', data = data)
    r = s.get(baseurl + 'ajax.php?action=browse&searchstr=' + searchstring)
    j = json.loads(r.text)
    

    if j['status'] == 'success':
	    results = j['response']['results']
	    print(results)
    else:
	    print("apl requests failed")
