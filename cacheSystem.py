from app import db
from models import *
from settings import SETTINGS
from redirectSolver import solveRedirect
import os.path
import urllib


def computePictureFilename(person):
    return 'static/pics/%s.jpg' % person.facebookId

def saveProfilePicture(person):
    graphURL = SETTINGS['basePic'] % (person.facebookId, 500, 500)
    picURL = solveRedirect(graphURL)

    try:
        urllib.URLopener().retrieve(picURL, computePictureFilename(person))
    except:
        print "Could not download profile picture for user %s :(" % person.username


def getProfilePictureLocation(person):
    # if the requested picture has been cached, return its location
    # otherwise, get it and save it

    filename = computePictureFilename(person)

    if not os.path.isfile(filename):
        print "Need profile picture for user %s, but it doesn't exist. Will try to cache it now." % person.username
        saveProfilePicture(person)

    return filename


def buildEntireCache():
    for i, x in enumerate(db.session.query(Person).all()):
        if i % 100 == 0:
            print "%i/%i" % (i, db.session.query(Person).count())

        saveProfilePicture(x)

    print "Profile picture cache was built."
