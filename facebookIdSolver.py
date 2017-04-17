from app import db
from models import *
import requests

def getIdFromUsername(username):
    try:
        """
        r = requests.post(
                "http://findmyfbid.com",
                data={'url': "https://www.facebook.com/%s" % username}
                )
        """

        r = requests.post("https://www.graphsearcher.com/facebook-id",
                data = {
                    '_token': 'oAKiCzYOre7TZnsYoHva4TwOWNLEJRgH3n5KRZI9',
                    'url': 'https://www.facebook.com/%s' % username,
                    },
                headers = {
                    'content-type': 'application/x-www-form-urlencoded',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'cookie': 'XSRF-TOKEN=eyJpdiI6IkU1RzBRclZJejdrU05EMEY3U1NWZ2c9PSIsInZhbHVlIjoiUFlyZzg2eVBkb3ljT1d5Y3JjREpMZndPVmFncmlUUE5cL2FiM2lIYU9mT3F1ZmdlRjM0SUNpUUcxdDZ3bWJydVwvTlRFcXloQ1ZXZ3ZLXC9oOVRcL1hOUUl3PT0iLCJtYWMiOiJkMDRmNThlMGJiZmU3NTA5YTY5MWJjMjVmZDM2YmFlYzY1Yjc5MTYxNTE1NjE1ZWU3YTc1YTE4ZTg3YTdiOWM0In0%3D; laravel_session=e4ddfdbbc0a0c36d67f925be13b8d5f4bea82a17; _ga=GA1.2.1924267867.1492461333; _'
                    }
                )

        if r.status_code == 200:
            ret = ''.join([x for x in r.url if '0' <= x and x <= '9'])
            if ret == '':
                ret = None
            return ret
    except:
        return None
