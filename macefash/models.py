from __init__ import app, db


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    gender = db.Column(db.Boolean, unique=False, nullable=True)
    city = db.Column(db.String, unique=False, nullable=True)
    school = db.Column(db.String, unique=False, nullable=True)

    rating = db.Column(db.Integer, unique=False, nullable=True)
    maxRating = db.Column(db.Integer, unique=False, nullable=True)
    kFactor = db.Column(db.Integer, unique=False, nullable=True)

    games = db.Column(db.Integer, unique=False, nullable=True)
    wins = db.Column(db.Integer, unique=False, nullable=True)

    hidden = db.Column(db.Boolean, unique=False, nullable=True)

    def __init__(self, username, gender=None, city=None, school=None, rating=0, maxRating=0, kFactor=40, games=0, wins=0, hidden=False):
        self.username = username
        self.gender = gender
        self.city = city
        self.school = school
        self.rating = rating
        self.maxRating = maxRating
        self.kFactor = kFactor
        self.games = games
        self.wins = wins
        self.hidden = hidden

    def __repr__(self):
        return self.username


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, unique=False, nullable=True)
    firstOption = db.Column(db.Integer, unique=False, nullable=True)
    secondOption = db.Column(db.Integer, unique=False, nullable=True)
    winner = db.Column(db.Integer, unique=False, nullable=True)
    timestamp = db.Column(db.String, unique=False, nullable=True)

    def __init__(self, ip, firstOption, secondOption, winner, timestamp):
        self.ip = ip
        self.firstOption = firstOption
        self.secondOption = secondOption
        self.winner = winner
        self.timestamp = timestamp

    def __repr__(self):
        return "%s rolled (%i, %i) and voted for %i" (self.ip, self.firstOption, self.secondOption, self.winner)


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=True)
    ip = db.Column(db.String, unique=False, nullable=True)
    message = db.Column(db.String, unique=False, nullable=False)
    timestamp = db.Column(db.String, unique=False, nullable=True)

    def __init__(self, name, ip, message, timestamp):
        self.name = name
        self.ip = ip
        self.message = message
        self.timestamp = timestamp

    def __repr__(self):
        return "%s (ip = %s) wrote: %s" % (self.name, self.ip, self.message)


class Theme(db.Model):
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    source = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, name, source):
        self.name = name
        self.source = source

    def __repr__(self):
        return "themeName: <%s>" % self.name


class UserSettings(db.Model):
    __tablename__ = 'usersettings'

    ip = db.Column(db.String, primary_key=True, nullable=True)
    theme = db.Column(db.String, unique=False, nullable=False)
    gender = db.Column(db.Boolean, unique=False, nullable=True)

    def __init__(self, ip, theme=None, gender=None):
        self.ip = ip
        self.theme = theme if theme is not None else "Standard"
        self.gender = gender if gender is not None else False #aka gurls

    def __repr__(self):
        return "ip %s wants:\n---> theme: <%s>\n---> gender: %r" % (self.ip, self.theme, self.gender)
