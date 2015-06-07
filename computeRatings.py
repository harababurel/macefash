"""
In case of changes made to the rating system, this module provides a method
for computing all ratings from scratch based on stored vote results.
"""
from app import db
from models import *
from ratingSystem import getNewEloRatings
from settings import SETTINGS
# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.interpolate import spline


print "WARNING: this is going to reset all ratings and recompute them from scratch."
try:
    assert(raw_input("if you wish to continue, type 'yes please': ") == 'yes please')
except AssertionError:
    print 'ok, i won\'t do anything then.'
    exit(0)

baseRating = raw_input('enter base rating (default = %.1f): ' % SETTINGS['baseRating'])
try:
    baseRating = float(baseRating)
except:
    if baseRating == '':
        baseRating = SETTINGS['baseRating']
        pass
    else:
        print 'that doesn\'t seem to be a floating point value. aborting.'
        exit(0)

baseVolatility = raw_input('enter base volatility (default = %.1f): ' % SETTINGS['baseVolatility'])
try:
    baseVolatility = float(baseVolatility)
except:
    if baseVolatility == '':
        baseVolatility = SETTINGS['baseVolatility']
        pass
    else:
        print 'that doesn\'t seem to be a floating point value. aborting.'
        exit(0)

print
print 'resetting stats (rating, maxRating, volatility, games, wins) to base values...',
for x in db.session.query(Person).all():
    x.rating = baseRating
    x.maxRating = baseRating
    x.volatility = baseVolatility
    x.games = 0
    x.wins = 0
print 'done!'

print 'fetching real world votes...',
votes = db.session.query(Vote).filter(Vote.spam == False).all()
print 'done!'

print 'simulating the vote process based on real world votes...',
toFollow = {}
for i, x in enumerate(votes):
    if i % 1000 == 0:
        print i
    players = [
            db.session.query(Person).filter(Person.username == x.winner).first(),
            db.session.query(Person).filter(Person.username == x.loser).first()
            ]

    newStats = {}
    for currentPlayer in players:
        newStats[currentPlayer] = getNewEloRatings(currentPlayer, players, verbose=False)

    for currentPlayer in players:
        currentPlayer.rating = newStats[currentPlayer]['newRating']
        currentPlayer.volatility = newStats[currentPlayer]['newVolatility']
        currentPlayer.games += 1
        if currentPlayer == players[0]:
            currentPlayer.wins += 1
        currentPlayer.maxRating = max(currentPlayer.maxRating, currentPlayer.rating)

        if not currentPlayer.username in toFollow:
            toFollow[currentPlayer.username] = [SETTINGS['baseRating']]
        toFollow[currentPlayer.username].append(currentPlayer.rating)

print 'done!'

print 'committing changes...',
db.session.commit()
print 'done!'
print

"""
try:
    assert(raw_input('do you also want to generate rating graphs? \'yes please\' to confirm: ') == 'yes please')
except AssertionError:
    print 'ok, i won\'t do anything then.'
    exit(0)

print 'generating rating graphs...',
for x in toFollow:
    if len(toFollow[x]) < 3:
        continue

    plt.clf()
    xs = np.array(range(len(toFollow[x])))
    ys = np.array(toFollow[x])

    xSmooth = np.linspace(xs.min(), xs.max(), 300)
    ySmooth = spline(xs, ys, xSmooth)

    plt.plot(xSmooth, ySmooth, 'blue', linewidth=2)
    plt.xlabel('vote')
    plt.ylabel('rating')
    plt.title('rating evolution of %s' % str(x))
    plt.savefig('static/graphs/%s.png' % str(x))
print 'done!'
"""
print 'everything was computed. good day to you! :D'
