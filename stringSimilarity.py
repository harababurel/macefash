"""
Module provides a function for computing the similarity between two strings,
according to the Damerau-Levenshtein distance function.
Purpose: when some user logs in with facebook and wants their picture taken down,
this method helps find the database entry which best matches said user's facebook name.
"""
from random import shuffle

"""
lmax = 100
computed = [[False for j in range(0, lmax)] for i in range(0, lmax)]
solution = [[0 for j in range(0, lmax)] for i in range(0, lmax)]

def DamerauLevenshtein(a, b, i, j):
    if computed[i][j]:
        return solution[i][j]

    if min(i, j) == -1:
        solution[i][j] = max(i, j)

    elif i > 0 and j > 0 and a[i] == b[j-1] and a[i-1] == b[j]:
        solution[i][j] = min(
                DamerauLevenshtein(a, b, i-1, j) + 1,
                DamerauLevenshtein(a, b, i, j-1) + 1,
                DamerauLevenshtein(a, b, i-1, j-1) + (a[i] != b[j]),
                DamerauLevenshtein(a, b, i-2, j-2) + 1
                )
    else:
        solution[i][j] = min(
                DamerauLevenshtein(a, b, i-1, j) + 1,
                DamerauLevenshtein(a, b, i, j-1) + 1,
                DamerauLevenshtein(a, b, i-1, j-1) + (a[i] != b[j])
                )

    computed[i][j] = True
    return solution[i][j]
"""
# ^own implementation is bad :(


def DamerauLevenshtein(a, b):
    """
    source: http://www.guyrutenberg.com/2008/12/15/damerau-levenshtein-distance-in-python/
    """
    d = {}
    for i in xrange(-1, len(a)+1):
        d[(i, -1)] = i+1
    for j in xrange(-1, len(b)+1):
        d[(-1, j)] = j+1

    for i in xrange(len(a)):
        for j in xrange(len(b)):
            d[(i, j)] = min(
                    d[(i-1, j)] + 1,                 # deletion
                    d[(i, j-1)] + 1,                 # insertion
                    d[(i-1, j-1)] + (a[i] != b[j])   # substitution
                    )

            if i and j and a[i] == b[j-1] and a[i-1] == b[j]:
                d[(i, j)] = min(
                        d[(i, j)],
                        d[i-2, j-2] + (a[i] != b[j]) # transposition
                        )

    return d[len(a)-1, len(b)-1]


def getStringSimilarity(a, b):
    bestDistance = 10**9
    maxLength = max(len(a), len(b))

    for _ in range(0, 10):
        distance = DamerauLevenshtein(a, b)
        bestDistance = min(bestDistance, distance)

        a = ' '.join(shuffle(a.split())) # tries a few random permutations of each name
        b = ' '.join(shuffle(b.split())) # increasing the probability that they will match

    return float(maxLength - bestDistance) / maxLength
