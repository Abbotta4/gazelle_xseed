#!/usr/bin/python

import sys
import requests

if len( sys.argv ) != 3:
    print "usage: test.py [gazelle username] [gazelle password]"
    sys.exit()

GAZELLE_USER = sys.argv[1]
GAZELLE_PASS = sys.argv[2]
searchstring = "run the jewels"

with requests.Session() as s:
    s.post('https://apollo.rip/login.php', data={'action': 'login', 'username': GAZELLE_USER, 'password': GAZELLE_PASS})
    r = s.get('https://apollo.rip/ajax.php?action=browse&searchstr=' + searchstring)
    print r.text
