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

def drawChoices(wantedGender):
    pool = sorted(db.session.query(Person).filter(and_(Person.gender == wantedGender, Person.hidden == False)).all(), key=lambda x: x.games)
    L, R = sample(pool[:10], 2) # at first, choices are selected from the least voted persons
    if randint(1, 2) == 1:      # in order to guarantee variety, each choice has a 50% chance
        L = choice(pool)        # of being re-chosen from the entire person pool
    if randint(1, 2) == 1:
        R = choice(pool)

    while L == R:
        R = choice(pool)

    picL = solveRedirect(SETTINGS['basePic'] % (L.username, 500, 500))
    picR = solveRedirect(SETTINGS['basePic'] % (R.username, 500, 500))

    return {
            'L': L,
            'R': R,
            'picL': picL,
            'picR': picR
            }
