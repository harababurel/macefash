"""
Modules provides functionality for vote processing
and spam detection
"""
from sqlalchemy import and_, or_
from settings import SETTINGS
from app import db
from models import *
from getIP import getIP
from ratingSystem import getNewRatings
import datetime

def detectSpam(players):
    who = getIP()

    votes = db.session.query(Vote).filter(and_(Vote.ip == who, Vote.winner == players[0].username)).all()
    lastVote = None
    isSpam = False
    now = datetime.datetime.now()

    if votes:
        lastVote = votes[-1]

    if lastVote:
        timeDiff = (now - lastVote.when).total_seconds()
        if timeDiff < SETTINGS['minVoteWait']:
            isSpam = True

        print "waited since last vote: %.2f" % timeDiff

    db.session.add(Vote(ip=who, winner=players[0].username, loser=players[1].username, when=now, spam=isSpam))
    db.session.commit()

    return isSpam


def processVote(form):
    players = [
        db.session.query(Person).get(int(form['winner'])),
        db.session.query(Person).get(int(form['loser']))
        ]

    if detectSpam(players):
        print "user <%s> is spamming votes for <%s>" % (getIP(), players[0].username)
        return

    print "user <%s> voted:\n    winner: <%s>\n    loser: <%s>" % (getIP(), players[0].username, players[1].username)

    newStats = {}

    # firstly, get new ratings (without altering anything) for all players
    for currentPlayer in players:
        newStats[currentPlayer] = getNewRatings(currentPlayer, players)

    # secondly, update all ratings based on computed values
    for currentPlayer in players:
        currentPlayer.rating = newStats[currentPlayer]['newRating']
        currentPlayer.volatility = newStats[currentPlayer]['newVolatility']
        currentPlayer.games += 1
        if currentPlayer == players[0]:
            currentPlayer.wins += 1
        currentPlayer.maxRating = max(currentPlayer.maxRating, currentPlayer.rating)

    db.session.commit()
