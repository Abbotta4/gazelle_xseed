# gazelle_xseed: A cross-seeding helper script

gazelle_xseed will load `.torrent` files in the local directory, search a gazelle-based tracker for the torrents, add, and force-recheck them in your torrent client. Currently only supports deluge

Python modules found in `requirements.txt`. Safest to use a virtual environment:  
```
$ virtualenv env
$ . env/bin/activate
$ pip install -r requirements.txt
```