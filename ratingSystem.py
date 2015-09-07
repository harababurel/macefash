"""
Implementation of the TopCoder rating system.
http://apps.topcoder.com/wiki/display/tc/Component+Development+Ratings
"""
from normalCDFinverse import normalCDFinverse
from math import sqrt, erf
from app import db
from models import *


def getWinProbability(comparedTo, currentPlayer):
    return 0.5 * (erf((comparedTo.rating - currentPlayer.rating) / sqrt(2.0 * (comparedTo.volatility**2.0 + currentPlayer.volatility**2.0))) + 1.0)


def getNewTCStyleRatings(currentPlayer, players):
    """
    Note: players should be sorted by rank.
    In the case of 2 players, their order should be [winner, loser].
    IMPORTANT: Something is off. Ratings tend to converge and are
    considerably more sensible to losing than to winning. 
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

    if currentPlayer.games in range(0, 20):
        weight *= 1.0
    elif currentPlayer.games in range(20, 50):
        weight *= 0.8
    elif currentPlayer.games in range(50, 100):
        weight *= 0.6
    else:
        weight *= 0.4

    cap = 150.0 + 1500.0 / (currentPlayer.games + 2.0)

    newRating = (currentPlayer.rating + weight * performedAsRating) / (weight + 1.0)
    if abs(newRating - currentPlayer.rating) > cap:
        if newRating > currentPlayer.rating:
            newRating = currentPlayer.rating + cap
        else:
            newRating = currentPlayer.rating - cap

    newVolatility = sqrt(((newRating - currentPlayer.rating)**2.0) / weight + (currentPlayer.volatility**2.0) / (weight + 1.0))

    print "<%s>: %.0f -> %.0f (%s%.0f)" % (currentPlayer.username, currentPlayer.rating, newRating, '-+'[currentPlayer.rating < newRating], abs(newRating - currentPlayer.rating))
    return {'newRating':newRating, 'newVolatility':newVolatility}


def getNewEloRatings(currentPlayer, players, verbose=True):
    """
    This is a more standard (and simple) approach to implementing the rating system.
    """
    otherPlayer = [x for x in players if x != currentPlayer][0]

    expectedScore = 1.0 / (1.0 + 10.0**((otherPlayer.rating - currentPlayer.rating) / 400.0))
    actualScore = (currentPlayer == players[0])

    newRating = currentPlayer.rating + currentPlayer.volatility * (actualScore - expectedScore)

    if newRating < 2100.0:
        newVolatility = 200.0
    elif 2100.0 <= newRating and newRating <= 2400.0:
        newVolatility = 100.0
    else:
        newVolatility = 50.0

    newVolatility = min(newVolatility, 10000.0 / max(1.0, currentPlayer.games))

    if verbose:
        print "<%s>: %.0f -> %.0f (%s%.0f)" % (currentPlayer.username, currentPlayer.rating, newRating, '-+'[currentPlayer.rating < newRating], abs(newRating - currentPlayer.rating))
    return {'newRating':newRating, 'newVolatility':newVolatility}


def getGradeEquivalent(rating):
    grade = 10.0 * (rating - SETTINGS['gradeZeroRating']) / (SETTINGS['gradeTenRating'] - SETTINGS['gradeZeroRating'])
    return min(10.0, max(0.0, grade))
