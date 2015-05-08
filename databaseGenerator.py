"""
Creates a sample database with basic entries.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
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
                source='//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css'
            ),
            Theme(
                name='United',
                source='//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/united/bootstrap.min.css'
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

    for grade in range(9, 13):
        for letter in 'abcdefghi':
            with open('static/cns/%s' % str(grade)+letter, 'r') as f:

                print "FILE: %s" % str(grade)+letter
                for x in f:
                    if 'id=' in x.split()[-1]:
                        username = findall(r'id=(\d+)', x.split()[-1])
                    else:
                        username = findall(r'facebook\.com\/([a-zA-Z0-9\.]+)', x.split()[-1])

                    if username:
                        print "processing '%s'" % username[0]
                        already = db.session.query(Person).filter(Person.username == username[0]).first()

                        school = 'cns/%s' % str(grade)+letter
                        gender = None
                        if x.split()[0] in 'BF':
                            gender = (x.split()[0] == 'B')

                        if already is None:
                            db.session.add(Person(username=username[0], gender=gender, school=school))
                            print "----> added with: gender=%r, school=%s" % (gender, school)
                        else:
                            already.gender = gender
                            already.school = school
                            print "----> already exists. updated gender and school."

    themes = [
            Theme(
                name='Standard',
                source='//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css'
                ),
            Theme(
                name='United',
                source='//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/united/bootstrap.min.css'
                )
            ]
    for x in themes:
        if db.session.query(Theme).filter(Theme.name == x.name).first() is None:
            db.session.add(x)

    db.session.commit()

if __name__ == '__main__':
    generateDatabase()
