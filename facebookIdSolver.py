from app import db
from models import *
import requests

def getIdFromUsername(username):
    try:
        r = requests.post(
                "http://findmyfbid.com",
                data={'url': "https://www.facebook.com/%s" % username}
                )

        if r.status_code == 200 and r.reason == 'OK' and 'success' in r.url:
            return ''.join([x for x in r.url if '0' <= x and x <= '9'])
    except:
        return "Could not get ID from username"
