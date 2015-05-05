"""
Creates a sample database with basic entries.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

"""
Create sample database
"""
db.create_all()
persons = [
        Person(
            username = 'zuck',
            gender = True,
            city = 'Palo Alto',
            school = 'Harvard',
            rating = 1500,
            maxRating = 1500,
            kFactor = 40,
            games = 0,
            wins = 0,
            hidden = False
        ),
        Person(
            username = 'klausiohannis', #only the username field is necessary
            gender = True,
            city = 'Sibiu'
        ),
        Person(
            username = 'simonahalep',
            gender = False
        ),
        Person(
            username = 'JKRowling',
            gender = False
        )
]

themes = [
        Theme(
            name = 'Standard',
            source = '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css'
        ),
        Theme(
            name = 'United',
            source = '//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/united/bootstrap.min.css'
        )
]

for x in persons:
    db.session.add(x)

for x in themes:
    db.session.add(x)

db.session.commit() #save changes
db.session.close()
