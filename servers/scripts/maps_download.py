import os
import re
import requests
import urllib


URL = 'https://maps.ddnet.org/'
DIR = 'C:/Users/Jannis/AppData/Roaming/Teeworlds/downloadedmaps/'


def main():
    resp = requests.get(URL)
    content = resp.text.split('\n')

    for line in content:
        match = re.search(r'<a href="(?P<map>.*\.map)">', line)
        if not match:
            continue

        map_ = match.groups('map')[0]
        path = DIR + map_
        if os.path.isfile(path):
            # map exists already
            continue

        try:
            resp = requests.get(URL + urllib.parse.unquote(map_))
            print(URL + urllib.parse.unquote(map_))
            with open(path, 'wb') as f:
                f.write(resp.content)
        except Exception as exc:
            print(exc)
        else:
            print(map_)


if __name__ == '__main__':
    main()
