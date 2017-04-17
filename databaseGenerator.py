#!/usr/bin/python2.7
"""
Creates a sample database with basic entries.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from facebookIdSolver import getIdFromUsername
from app import db
from models import *

from re import findall


def generateSampleDatabase():
    """
    Note: only the username field is necessary.
    The other fields are provided with defaults.
    """
    db.create_all()
    persons = [
            Person(
                username='zuck',
                fullname='Mark Zuckerberg',
                gender=True,
                city='Palo Alto',
                school='Harvard',
                rating=1200.0,
                maxRating=1200.0,
                volatility=385.0,
                games=0,
                wins=0,
                hidden=False
            ),
            Person(
                username='klausiohannis',
                gender=True,
                city='Sibiu'
            ),
            Person(
                username='simonahalep',
                gender=False
            ),
            Person(
                username='JKRowling',
                gender=False
            )
    ]

    themes = [
            Theme(
                name='Standard',
                source='//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css',
                background='subtle_white_feathers.png'
            )
            ]

    for x in persons:
        if db.session.query(Person).filter(Person.username == x.username).first() is None:
            db.session.add(x)

    for x in themes:
        if db.session.query(Theme).filter(Theme.name == x.name).first() is None:
            db.session.add(x)

    db.session.commit()
    db.session.close()


def generateDatabase():
    db.create_all()

    newAdded = 0
    for grade in range(7, 13):
        for letter in 'abcdefghi':
            try:
                f = open('static/cns/%s' % str(grade)+letter, 'r')
            except:
                print "Could not open file static/cns/%s (probably doesn't exist)." % (str(grade)+letter)
                continue


            print "FILE: %s" % str(grade)+letter
            for x in f:
                if 'id=' in x.split()[-1]:
                    username = findall(r'id=(\d+)', x.split()[-1])
                else:
                    username = findall(r'facebook\.com\/([a-zA-Z0-9\.]+)', x.split()[-1])

                if username:
                    #print "processing '%s'" % username[0]
                    already = db.session.query(Person).filter(Person.username == username[0]).first()

                    fullname = findall('B?F?\s?(.+)\s?http.+', x)[0]
                    fullname = fullname.replace('\xc5\x9e', 'S')
                    fullname = fullname.replace('\xc8\x98', 'S')
                    fullname = fullname.replace('\xc5\xa2', 'T')
                    fullname = fullname.replace('\xc8\x9a', 'T')
                    fullname = fullname.replace('\xc3\x81', 'A')
                    fullname = fullname.replace('\xc4\x82', 'A')
                    fullname = fullname.replace('\xc3\x82', 'A')
                    fullname = fullname.replace('\xc3\x89', 'E')
                    fullname = fullname.replace('\xc3\x8e', 'I')
                    fullname = fullname.replace('\xc3\x93', 'O')
                    fullname = fullname.replace('\xc3\x96', 'O')
                    fullname = fullname.replace('\xc5\x90', 'O')
                    if fullname[-1] == ' ':
                        fullname = fullname[:-1]

                    school = 'cns/%s' % str(grade)+letter
                    gender = None
                    if x.split()[0] in 'BF':
                        gender = (x.split()[0] == 'B')

                    if already is None:
                        db.session.add(Person(username=username[0], fullname=fullname, gender=gender, school=school))
                        newAdded += 1
                        print "----> added with: gender=%r, school=%s" % (gender, school)
                    else:
                        if gender is not None:
                            already.gender = gender
                        already.school = school
                        #print "----> already exists. updated gender and school."
            f.close()

    themes = [
            Theme(
                name='Standard',
                source='//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css',
                background='subtle_white_feathers.png'
                )
            ]

    extraThemes = zip(
            list('Cyborg Sandstone Simplex Paper'.split()),
            list('wild_oliva.png skelatal_weave.png subtle_white_feathers.png linedpaper.png'.split())
            )
    for x in extraThemes:
        themes.append(
                Theme(
                    name=x[0],
                    source='//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/%s/bootstrap.min.css' % x[0].lower(),
                    background=x[1]
                    )
                )
    for x in themes:
        if db.session.query(Theme).filter(Theme.name == x.name).first() is None:
            db.session.add(x)

    print "added %i new people." % newAdded
    db.session.commit()

def setAllIds():
    for x in db.session.query(Person).all():
        if x.facebookId is not None:
            continue

        oldId = x.facebookId

        if not False in ['0' <= c and c <= '9' for c in x.username]: # username is already equal to id
            x.facebookId = x.username
        else:
            facebookId = getIdFromUsername(x.username)

            print "got id = %r" % facebookId
            if facebookId is not None:
                x.facebookId = facebookId

        if oldId != x.facebookId:
            print "Changed %s's id from %s to %s" % (x.username, oldId, x.facebookId)
            db.session.commit()

if __name__ == '__main__':
    print "Adding entries..."
    generateDatabase()
    print "Setting IDs to entries..."
    setAllIds()
