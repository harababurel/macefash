"""
Implementation of the TopCoder rating system.
http://apps.topcoder.com/wiki/display/tc/Component+Development+Ratings
"""
from normalCDFinverse import normalCDFinverse
from getIP import getIP
from math import sqrt, erf
from app import db
from models import *


def getWinProbability(comparedTo, currentPlayer):
    return 0.5 * (erf((comparedTo.rating - currentPlayer.rating) / sqrt(2.0 * (comparedTo.volatility**2.0 + currentPlayer.volatility**2.0))) + 1.0)


def getNewRatings(currentPlayer, players):
    """
    Note: players should be sorted by rank.
    In the case of 2 players, their order should be [winner, loser].
    """
    averageRating = float(sum([x.rating for x in players])) / len(players)

    squareVolatilitySum = sum([x.volatility ** 2.0 for x in players])
    squareRatingDiffSum = sum([(x.rating - averageRating) ** 2.0 for x in players])

    competitionFactor = sqrt(squareVolatilitySum / float(len(players)) + squareRatingDiffSum / float(len(players)-1))

    expectedRank = 0.5 + sum([getWinProbability(x, currentPlayer) for x in players])
    actualRank = players.index(currentPlayer) + 1

    expectedPerformance = -normalCDFinverse((expectedRank - 0.5) / float(len(players)))
    actualPerformance = -normalCDFinverse((actualRank - 0.5) / float(len(players)))

    performedAsRating = currentPlayer.rating + competitionFactor * (actualPerformance - expectedPerformance)
    weight = 1.0 / (1.0 - (0.42 / (currentPlayer.games + 1.0) + 0.18)) - 1.0

    if 2000 <= currentPlayer.rating and currentPlayer.rating <= 2500:
        weight *= 0.9
    if 2500 < currentPlayer.rating:
        weight *= 0.8

    cap = 150.0 + 1500.0 / (currentPlayer.games + 2.0)

    newRating = (currentPlayer.rating + weight * performedAsRating) / (weight + 1.0)
    newVolatility = sqrt(((newRating - currentPlayer.rating)**2.0) / weight + (currentPlayer.volatility**2.0) / (weight + 1.0))

    print "newRating: %.2f\nnewVolatility: %.2f" % (newRating, newVolatility)
    return {'newRating':newRating, 'newVolatility':newVolatility}


def processVote(form):
    players = [
        db.session.query(Person).get(int(form['winner'])),
        db.session.query(Person).get(int(form['loser']))
        ]
    print "user <%s> voted:\n    winner: <%s>\n    loser: <%s>" % (getIP(), players[0].username, players[1].username)

    newStats = {}

    # firstly, get new ratings (without altering anything)
    for currentPlayer in players:
        newStats[currentPlayer] = getNewRatings(currentPlayer, players)

    # secondly, update all ratings based on received values
    for currentPlayer in players:
        currentPlayer.rating = newStats[currentPlayer]['newRating']
        currentPlayer.volatility = newStats[currentPlayer]['newVolatility']
        currentPlayer.games += 1
        if currentPlayer == players[0]:
            currentPlayer.wins += 1
        currentPlayer.maxRating = max(currentPlayer.maxRating, currentPlayer.rating)

    db.session.commit()

