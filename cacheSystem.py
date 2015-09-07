"""
    Provides a profile picture cache system.
    When new pictures are requested, they are saved locally
    for faster access in the future.
    The buildEntireCache method can be added as a cron job
    in order to keep pictures up to date, periodically.
"""

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
    # otherwise, get it, save it, return its location

    filename = computePictureFilename(person)

    if not os.path.isfile(filename):
        print "Need profile picture for user %s, but it doesn't exist. Will try to cache it now." % person.username
        saveProfilePicture(person)

    return filename


def buildEntireCache():
    # this overwrites all profile pictures with their current state
    for i, x in enumerate(db.session.query(Person).all()):
        if i % 100 == 0:
            print "%i/%i" % (i, db.session.query(Person).count())

        saveProfilePicture(x)

    print "Profile picture cache was built."

def buildMissingCache():
    # this only updates the missing pictures
    for x in db.session.query(Person).all():
        getProfilePictureLocation(x)
