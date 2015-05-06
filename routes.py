"""
This module links the URLs to the corresponding templates.
Also contains most of the project's functionality.
"""
from flask import Flask, render_template, redirect, url_for, \
                  request, session, flash, Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from functools import wraps
from settings import SETTINGS
from subprocess import Popen, PIPE
from random import randint, choice, sample, shuffle
from redirectSolver import solveRedirect

from app import app
from models import *
import os

basePic = 'https://graph.facebook.com/%s/picture?width=%s&height=%s'


def checkAuth(username, password):
    return (username, password) in SETTINGS['auth']


def requiresAuth(f):
    """
    Function only allows access on certain pages (marked with the decorator)
    for users who have the user:pass specified in the settings.py module
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not checkAuth(auth.username, auth.password):
            return Response(
                    'sorry, can\'t let you in :-(\n',
                    401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'}
                    )
        return f(*args, **kwargs)
    return decorated


def sh(script):
    """
    Can run a bash script.
    Not used, for the moment.
    """
    (out, err) = Popen(list(script.split()), stdout=PIPE).communicate()
    return str(out)


def getIP():
    """
    'unknown' serves as a universal IP :D
    """
    ip = request.headers.get('X-Real-IP')
    if ip is None:
        ip = 'unknown'
    return ip


def getThemes():
    return sorted(db.session.query(Theme).all(), key=lambda x: x.name)


def getCurrentTheme():
    try:
        themeName = Preference.query.filter(Preference.ip == getIP()).first()
        themeURL = Theme.query.filter(Theme.name == themeName).first().source
    except:
        themeName = 'United'
        themeURL = 'http://bootswatch.com/united/bootstrap.min.css'

    return (themeName, themeURL)


def getCurrentGender():
    try:
        currentGender = Preference.query.filter(Preference.ip == getIP()).first().gender
    except:
        currentGender = False
    return currentGender


def getGenderCount(gender):
    return len(Person.query.filter(Person.gender == gender).all())


def updateRatings(A, B):
    """
    Elo rating system.
    kFactor values similar to the ones used by FIDE.
    """
    A = db.session.query(Person).get(A)
    B = db.session.query(Person).get(B)

    expectedA = 1.0 / (1.0 + 10.0 ** ((B.rating - A.rating)/400.0))
    expectedB = 1.0 / (1.0 + 10.0 ** ((A.rating - B.rating)/400.0))

    newA = int(A.rating + A.kFactor * (1.0 - expectedA))
    newB = int(B.rating + B.kFactor * (0.0 - expectedB))

    deltaA = newA - A.rating
    deltaB = newB - B.rating

    print "new rating for <%s>: %i (delta: %i)\nnew rating for <%s>: %i (delta: %i)" % (A.username, newA, deltaA, B.username, newB, deltaB)

    # update all relevant stats
    A.rating, B.rating = newA, newB
    A.maxRating, B.maxRating = max(A.maxRating, A.rating), max(B.maxRating, B.rating)
    A.games, B.games = A.games + 1, B.games + 1
    A.wins = A.wins + 1

    for X in [A, B]:
        if X.kFactor == 40 and (X.maxRating >= 2300 or X.games > 30):
            X.kFactor = 20
        if X.kFactor == 20 and X.maxRating > 2400:
            X.kFactor = 10

    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@requiresAuth
def home():
    global basePic

    if request.method == 'POST':
        A, B = int(request.form['winner']), int(request.form['loser'])
        print "user <%s> voted for <%i> instead of <%i>" % (getIP(), A, B)

        updateRatings(A, B)
        return redirect(url_for('home'))

    L, R = sample(list(db.session.query(Person).filter(and_(Person.gender == getCurrentGender(), Person.hidden == False)).all()), 2)

    picL = solveRedirect(basePic % (L.username, 500, 500))
    picR = solveRedirect(basePic % (R.username, 500, 500))

    return render_template(
            'home.html',
            L=L,
            R=R,
            picL=picL,
            picR=picR,
            ip=getIP(),
            currentGender=getCurrentGender(),
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=getGenderCount(False),
            boys=getGenderCount(True),
            ungendered=getGenderCount(None),
            userIP=getIP()
            )


@app.route('/setTheme/<string:theme>')
def setTheme(theme):
    currentUser = Preference.query.filter(Preference.ip == getIP()).first()
    if currentUser is None:
        db.session.add(Preference(ip=getIP(), theme=theme))
        print "user %s selected theme <%s> for the first time" % (getIP(), theme)
    else:
        currentUser.theme = theme
        print "user %s changed theme to <%s>" % (getIP(), theme)

    db.session.commit()
    return redirect(url_for('home'))


@app.route('/setGender/<int:gender>')
def setGender(gender):
    gender = (gender == 1)
    currentUser = Preference.query.filter(Preference.ip == getIP()).first()
    if currentUser is None:
        db.session.add(Preference(ip=getIP(), gender=gender))
        print "user %s selected gender <%r> for the first time" % (getIP(), gender)
    else:
        currentUser.gender = gender
        print "user %s changed gender to <%r>" % (getIP(), gender)

    db.session.commit()
    return redirect(url_for('home'))


@app.route('/genderHelp')
@requiresAuth
def genderHelp():
    """
    note to self: and_(Person.gender is None, not Person.hidden) doesn't work
    """
    try:
        remaining = list(db.session.query(Person).filter(and_(Person.gender == None, Person.hidden == False)).all())
        entry = choice(remaining)
        # entry = db.session.query(Person).filter(and_(Person.gender==None, Person.hidden==False)).first() #by id
    except:
        print "no more genders to classify (probably)"
        return redirect(url_for('home'))

    pic = solveRedirect(basePic % (entry.username, 400, 400))
    girls = getGenderCount(False)
    boys = getGenderCount(True)
    ungendered = getGenderCount(None)

    total = len([x for x in db.session.query(Person).all()])
    classified = total - len(remaining)

    percentage = float("%.2f" % ((100.0 * classified) / total))

    return render_template(
            'genderclassifier.html',
            x=entry,
            pic=pic,
            currentGender=getCurrentGender(),
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=girls,
            boys=boys,
            ungendered=ungendered,
            percentage=percentage
            )


@app.route('/classifyGender/<string:username>')
@app.route('/classifyGender/<string:username>/<int:newGender>')
@requiresAuth
def classifyGender(username=None, newGender=None):
    if username is None:
        print "username is None. dunno wot 2 do :-??"
        return redirect(url_for('genderHelp'))

    if newGender is not None:
        if newGender == 3:
            db.session.query(Person).filter(Person.username == username).first().hidden = True
        else:
            db.session.query(Person).filter(Person.username == username).first().gender = [False, True, None][newGender]

    db.session.commit()
    return redirect(url_for('genderHelp'))


@app.route('/all')
@app.route('/all/<int:page>')
@requiresAuth
def showAll(page=None):
    if page is None:
        page = 1
    onPage = 40

    entries = db.session.query(Person).all()
    entries = sorted(entries, key=lambda x: x.rating, reverse=True)
    # shuffle(entries)
    pages = len(entries) // onPage + (len(entries) % onPage != 0)
    firstNav, lastNav = max(1, page-3), min(page+3, pages)
    shownEntries = entries[(page-1)*onPage: min(len(entries), page*onPage)]

    return render_template(
            'all.html',
            entries=shownEntries,
            page=page,
            pages=pages,
            firstNav=firstNav,
            lastNav=lastNav,
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=getGenderCount(False),
            boys=getGenderCount(True),
            ungendered=getGenderCount(None)
            )


@app.errorhandler(404)
def pageNotFound(e):
    return render_template(
            '404.html',
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=getGenderCount(False),
            boys=getGenderCount(True),
            ungendered=getGenderCount(None)
            ), 404
