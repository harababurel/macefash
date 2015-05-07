"""
Creates a sample database with basic entries.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from app import db
from models import *


def generateDatabase():
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
