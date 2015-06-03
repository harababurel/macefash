"""
Defines the models upon which
the database tables are based.
"""
from app import db
from settings import SETTINGS


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    fullname = db.Column(db.String, unique=False, nullable=True)
    gender = db.Column(db.Boolean, unique=False, nullable=True)
    city = db.Column(db.String, unique=False, nullable=True)
    school = db.Column(db.String, unique=False, nullable=True)

    rating = db.Column(db.Float, unique=False, nullable=True)
    maxRating = db.Column(db.Float, unique=False, nullable=True)
    volatility = db.Column(db.Float, unique=False, nullable=True)

    games = db.Column(db.Integer, unique=False, nullable=True)
    wins = db.Column(db.Integer, unique=False, nullable=True)

    hidden = db.Column(db.Boolean, unique=False, nullable=True)

    def __init__(
            self,
            username,
            fullname=None,
            gender=None,
            city=None,
            school=None,
            rating=SETTINGS['baseRating'],
            maxRating=SETTINGS['baseRating'],
            volatility=SETTINGS['baseVolatility'],
            games=0,
            wins=0,
            hidden=False
            ):
        self.username = username
        self.fullname = fullname
        self.gender = gender
        self.city = city
        self.school = school
        self.rating = rating
        self.maxRating = maxRating
        self.volatility = volatility
        self.games = games
        self.wins = wins
        self.hidden = hidden

    def __repr__(self):
        return self.username


class Vote(db.Model):
    __tablename__ = 'vote'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, unique=False, nullable=True)
    winner = db.Column(db.String, unique=False, nullable=True)
    loser = db.Column(db.String, unique=False, nullable=True)
    when = db.Column(db.DateTime, unique=False, nullable=True)
    spam = db.Column(db.Boolean, unique=False, nullable=False)

    def __init__(self, ip, winner, loser, when, spam=False):
        self.ip = ip
        self.winner = winner
        self.loser = loser
        self.when = when
        self.spam = spam

    def __repr__(self):
        return "%s voted (%s, %s)" % (self.ip, self.winner, self.loser, self.when)


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=True)
    ip = db.Column(db.String, unique=False, nullable=True)
    message = db.Column(db.String, unique=False, nullable=False)
    when = db.Column(db.DateTime, unique=False, nullable=True)

    def __init__(self, name, ip, message, when):
        self.name = name
        self.ip = ip
        self.message = message
        self.when = when

    def __repr__(self):
        return "%s (ip = %s) wrote: %s" % (self.name, self.ip, self.message)


class Theme(db.Model):
    __tablename__ = 'theme'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    source = db.Column(db.String, unique=True, nullable=False)
    background = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, name, source, background):
        self.name = name
        self.source = source
        self.background = background

    def __repr__(self):
        return "themeName: <%s>" % self.name


class Preference(db.Model):
    __tablename__ = 'preference'

    ip = db.Column(db.String, primary_key=True, nullable=True)
    theme = db.Column(db.String, unique=False, nullable=False)
    gender = db.Column(db.Boolean, unique=False, nullable=True)

    def __init__(self, ip, theme=None, gender=None):
        self.ip = ip
        self.theme = theme if theme is not None else "Simplex"
        self.gender = gender if gender is not None else False

    def __repr__(self):
        return "ip %s wants:\n---> theme: <%s>\n---> gender: %r" % (self.ip, self.theme, self.gender)
