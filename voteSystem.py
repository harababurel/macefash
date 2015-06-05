"""
Modules provides functionality for vote processing
and spam detection
"""
from sqlalchemy import and_, or_
from settings import SETTINGS
from app import db
from models import *
from getIP import getIP
from ratingSystem import getNewEloRatings
from basher import sh
import datetime

def detectSpam(players):
    who = getIP()

    try:
        lastVote = db.session.query(Vote).filter(and_(Vote.ip == who, Vote.winner == players[0].username)).order_by(Vote.id.desc()).first()
    except:
        lastVote = None

    isSpam = False
    lastWasSpam = False
    now = datetime.datetime.now()

    if lastVote:
        timeDiff = (now - lastVote.when).total_seconds()
        if timeDiff < SETTINGS['minVoteWait']:
            isSpam = True
        lastWasSpam = lastVote.spam
        #print "waited since last vote: %.2f" % timeDiff

    if not isSpam or (isSpam and not lastWasSpam):
        db.session.add(Vote(ip=who, winner=players[0].username, loser=players[1].username, when=now, spam=isSpam))
    db.session.commit()

    return isSpam


def processVote(form):
    players = [
        db.session.query(Person).get(int(form['winner'])),
        db.session.query(Person).get(int(form['loser']))
        ]

    if detectSpam(players):
        #print "user <%s> is spamming votes for <%s>" % (getIP(), players[0].username)
        return

    print "vote:\n    who:    <%s>\n    winner: <%s>\n    loser:  <%s>" % (getIP(), players[0].username, players[1].username)

    if 'harababurel' in [players[0].username, players[1].username] or 'mihai.rus.777' in [players[0].username, players[1].username]:
        try:
            sh('sh beeper.sh')
        except Exception, e:
            print "tried to execute beeper.sh, but something went wrong (err: %s)" % e

    newStats = {}

    # firstly, get new ratings (without altering anything) for all players
    for currentPlayer in players:
        newStats[currentPlayer] = getNewEloRatings(currentPlayer, players)

    # secondly, update all ratings based on computed values
    for currentPlayer in players:
        currentPlayer.rating = newStats[currentPlayer]['newRating']
        currentPlayer.volatility = newStats[currentPlayer]['newVolatility']
        currentPlayer.games += 1
        if currentPlayer == players[0]:
            currentPlayer.wins += 1
        currentPlayer.maxRating = max(currentPlayer.maxRating, currentPlayer.rating)

    db.session.commit()
