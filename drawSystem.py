"""
Module provides a method for drawing a satisfactory
pair of Persons from the database.
"""
from random import randint, choice, sample
from sqlalchemy import and_, or_
from app import db
from models import *
from settings import SETTINGS
from redirectSolver import solveRedirect
from ratingSystem import getGradeEquivalent
from facebookIdSolver import getIdFromUsername
from cacheSystem import getProfilePictureLocation, computePictureFilename


def drawChoices(wantedGender):
    pool = sorted(db.session.query(Person).filter(and_(Person.gender == wantedGender, Person.hidden == False, Person.facebookId != None)).all(), key=lambda x: x.games)
    L, R = sample(pool[:50], 2) # at first, choices are selected from the least voted persons
    if randint(1, 2) == 1:      # in order to guarantee variety, each choice has a 50% chance
        L = choice(pool)        # of being re-chosen from the entire person pool
    if randint(1, 2) == 1:
        R = choice(pool)

    while L == R:
        R = choice(pool)

    # picL = solveRedirect(SETTINGS['basePic'] % (L.username, 500, 500))
    # picR = solveRedirect(SETTINGS['basePic'] % (R.username, 500, 500))
    # ^the solveRedirect method is EXTREMELY slow
    picL = getProfilePictureLocation(L)
    picR = getProfilePictureLocation(R)

    nuevoL = ' (nuev%s)' % ['a', 'o'][L.gender] if '8' in L.school else None
    nuevoR = ' (nuev%s)' % ['a', 'o'][R.gender] if '8' in R.school else None

    return {
            'L': L,
            'R': R,
            'picL': picL,
            'picR': picR,
            'gradeL': getGradeEquivalent(L.rating),
            'gradeR': getGradeEquivalent(R.rating),
            'nuevoL': nuevoL,
            'nuevoR': nuevoR
            }
