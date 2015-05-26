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
from random import choice
from redirectSolver import solveRedirect
from ratingSystem import getNewRatings
from voteSystem import processVote
from drawSystem import drawChoices
from getIP import getIP

from app import app
from models import *
import os


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


def getThemes():
    return sorted(db.session.query(Theme).all(), key=lambda x: x.name)


def getCurrentTheme():
    try:
        themeName = db.session.query(Preference).filter(Preference.ip == getIP()).first().theme
        themeURL = db.session.query(Theme).filter(Theme.name == themeName).first().source
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


def getTotalVotes():
    try:
        totalVotes = sum([x.wins for x in db.session.query(Person).filter(Person.hidden == False).all()])
    except:
        totalVotes = None
    return totalVotes


def getGenderCount(gender):
    return len(Person.query.filter(Person.gender == gender).all())


@app.route('/', methods=['GET', 'POST'])
# @requiresAuth
def home():
    if request.method == 'POST':
        processVote(request.form)
        return redirect(url_for('home'))

    choices = drawChoices(wantedGender=getCurrentGender())

    return render_template(
            'home.html',
            L=choices['L'],
            R=choices['R'],
            picL=choices['picL'],
            picR=choices['picR'],
            totalVotes=getTotalVotes(),
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
    except:
        print "no more genders to classify (probably)"
        return redirect(url_for('home'))

    pic = SETTINGS['basePic'] % (entry.username, 400, 400)
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
            totalVotes=getTotalVotes(),
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
            totalVotes=getTotalVotes(),
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=getGenderCount(False),
            boys=getGenderCount(True),
            ungendered=getGenderCount(None)
            )


@app.route('/votes')
@app.route('/votes/<int:page>')
@requiresAuth
def showVotes(page=None):
    if page is None:
        page = 1
    onPage = 40

    entries = db.session.query(Vote).all()[::-1]
    pages = len(entries) // onPage + (len(entries) % onPage != 0)
    firstNav, lastNav = max(1, page-3), min(page+3, pages)
    shownEntries = entries[(page-1)*onPage: min(len(entries), page*onPage)]

    return render_template(
            'votes.html',
            entries=shownEntries,
            page=page,
            pages=pages,
            firstNav=firstNav,
            lastNav=lastNav,
            totalVotes=getTotalVotes(),
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=getGenderCount(False),
            boys=getGenderCount(True),
            ungendered=getGenderCount(None)
            )


@app.route('/about')
def about():
    return render_template(
            'about.html',
            totalVotes=getTotalVotes(),
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
            totalVotes=getTotalVotes(),
            currentTheme=getCurrentTheme(),
            themes=getThemes(),
            girls=getGenderCount(False),
            boys=getGenderCount(True),
            ungendered=getGenderCount(None)
            ), 404
