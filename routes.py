"""
This module links the URLs to the corresponding templates.
Also contains most of the project's functionality.
"""
from flask import Flask, render_template, redirect, url_for, \
                  request, make_response, session, flash, Response
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from sqlalchemy import and_, or_
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from functools import wraps
from settings import SETTINGS
from random import choice
from redirectSolver import solveRedirect
from voteSystem import processVote
from drawSystem import drawChoices
from ratingSystem import getGradeEquivalent
from cacheSystem import getProfilePictureLocation
from getIP import getIP
from stringSimilarity import getStringSimilarity
from basher import sh

from app import app
from models import *
import datetime

app.debug = SETTINGS['debug']
authomatic = Authomatic(SETTINGS, 'secret_string', report_errors=False)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


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


def getThemes():
    return db.session.query(Theme).order_by(Theme.name).all()


def getCurrentTheme():
    try:
        themeName = db.session.query(Preference).filter(Preference.ip == getIP()).first().theme
        matchedTheme = db.session.query(Theme).filter(Theme.name == themeName).first()
        currentTheme = (themeName, matchedTheme.source, matchedTheme.background)
    except:
        currentTheme = SETTINGS['defaultTheme']
    return currentTheme


def getCurrentGender():
    try:
        currentGender = Preference.query.filter(Preference.ip == getIP()).first().gender
    except:
        currentGender = SETTINGS['defaultGender']
    return currentGender


def getGenderCount():

    return { False: '???', True: '???' }

    """
    nonHiddenPersons = db.session.query(Person).filter(Person.hidden == False)
    return {
            False: nonHiddenPersons.filter(Person.gender == False).count(),
            True: nonHiddenPersons.filter(Person.gender == True).count()
            }
    """


def getTotalVotes():

    return 0 # this is like real fast u kno like O(1) fast

    """
    try:
        totalVotes = db.session.query(Vote).filter(Vote.spam == False).count()
    except:
        totalVotes = 0

    if 1000 <= totalVotes and totalVotes < 1000000:
        return '%.1fk' % (totalVotes/1000.0)
    if 1000000 <= totalVotes:
        return '%.1f mil.' % (totalVotes/1000000.0)
    return '%i' % totalVotes
    """


def getUniqueVoters():

    return 0 # this is like uhm just as fast as the other one

    """
    try:
        uniqueVoters = db.session.query(Vote).distinct(Vote.ip).group_by(Vote.ip).count()
    except:
        uniqueVoters = None
    return uniqueVoters
    """

@app.route('/', methods=['GET', 'POST'])
# @requiresAuth
def home():
    if request.method == 'POST':
        processVote(request.form)
        return redirect(url_for('home'))

    choices = drawChoices(wantedGender=getCurrentGender())

    return render_template(
            'home.html',
            choices=choices,
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentGender=getCurrentGender(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
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
        remaining = db.session.query(Person).filter(and_(Person.gender == None, Person.hidden == False))
        entry = choice(remaining.all())
    except:
        print "no more genders to classify (probably)"
        return redirect(url_for('home'))

    pic = SETTINGS['basePic'] % (entry.facebookId, 400, 400)

    total = db.session.query(Person).count()
    classified = total - remaining.count()

    percentage = float("%.2f" % ((100.0 * classified) / total))

    return render_template(
            'genderclassifier.html',
            x=entry,
            pic=pic,
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentGender=getCurrentGender(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            percentage=percentage
            )


@app.route('/flipHidden', methods=['GET', 'POST'])
def flipHidden():
    if request.method != 'POST':
        return redirect(url_for('home'))

    author = request.form['author']
    target = db.session.query(Person).get(int(request.form['id']))
    action = 'unhide' if target.hidden else 'hide'
    now = datetime.datetime.now()

    target.hidden = not target.hidden
    db.session.add(
            Takedown(
                ip=getIP(),
                author=author,
                target=target.username,
                action=action,
                when=now
                )
            )

    db.session.commit()
    return redirect(url_for('home'))


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


@app.route('/top/<int:gender>')
# @cache.cached(timeout=50)
def showTop(gender=None):
    if gender is None or not gender in range(2):
        return redirect(url_for('home'))

    entries = sorted(db.session.query(Person).filter(and_(Person.gender == gender, Person.hidden == False)).all(), key=lambda x: x.rating, reverse=True)[:20]
    picSizes = [400 for x in entries]
    picSizes[0] = 700
    picSizes[1] = 600
    picSizes[2] = 500

    pics = [getProfilePictureLocation(x) for i, x in enumerate(entries)]
    grades = [getGradeEquivalent(x.rating) for x in entries]

    print "user <%s> accessed the %s top" % (getIP(), ['girls', 'boys'][gender])

    return render_template(
            'top.html',
            entries=entries,
            grades=grades,
            howMany=len(entries),
            pics=pics,
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            userIP=getIP()
            )

@app.route('/all')
@app.route('/all/<int:page>')
@requiresAuth
# @cache.cached(timeout=50)
def showAll(page=None):
    if page is None:
        page = 1
    onPage = SETTINGS['entriesOnPage']

    entriesCount = db.session.query(Person).count()
    pages = entriesCount // onPage + (entriesCount % onPage != 0)
    firstNav, lastNav = max(1, page-3), min(page+3, pages)

    firstEntryID = (page-1)*onPage + 1
    lastEntryID = firstEntryID + onPage - 1

    shownEntries = db.session.query(Person).filter(and_(firstEntryID <= Person.id, Person.id <= lastEntryID)).all()

    # Some entries may not have a cached picture yet
    # So it's a good idea to cache them now.
    # This is slow for a fresh database, but saves
    # user time in the long run and is a one-time thing
    for x in shownEntries:
        getProfilePictureLocation(x)

    return render_template(
            'all.html',
            entries=shownEntries,
            page=page,
            pages=pages,
            firstNav=firstNav,
            lastNav=lastNav,
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            userIP=getIP()
            )


@app.route('/votes')
@app.route('/votes/<int:page>')
@requiresAuth
def showVotes(page=None):
    if page is None:
        page = 1
    onPage = SETTINGS['entriesOnPage']

    voteCount = db.session.query(Vote).count()
    pages = voteCount // onPage + (voteCount % onPage != 0)
    firstNav, lastNav = max(1, page-3), min(page+3, pages)

    lastVoteID = voteCount - (page-1) * onPage
    firstVoteID = lastVoteID - onPage + 1

    shownEntries = db.session.query(Vote).order_by(-Vote.id).filter(and_(firstVoteID <= Vote.id, Vote.id <= lastVoteID)).all()

    return render_template(
            'votes.html',
            entries=shownEntries,
            page=page,
            pages=pages,
            firstNav=firstNav,
            lastNav=lastNav,
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            userIP=getIP()
            )


@app.route('/showTakedowns')
@requiresAuth
def showTakedowns():
    return '<br>'.join([x.__repr__() for x in db.session.query(Takedown).all()[::-1]])


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        response = make_response()
        result = authomatic.login(WerkzeugAdapter(request, response), 'fb')
    except:
        return 'could not log you in :( go <a href="/">home</a>'

    if result:
        if result.user:
            result.user.update()

        realName = result.user.name.upper()
        v = []
        for x in db.session.query(Person).filter(Person.fullname is not None).all():
            facebookName = x.fullname.upper()

            for letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
                if '%s.' % letter in facebookName:
                    facebookName = facebookName.replace('%s.' % letter, '') # get rid of father's initials

            nameSimilarity = getStringSimilarity(realName, facebookName)
            if nameSimilarity > 0.47:
                v.append((nameSimilarity, x))

        v = sorted(v, reverse=True)[:2]

        return render_template(
                'login.html',
                author=realName,
                matches=v,
                totalVotes=getTotalVotes(),
                uniqueVoters=getUniqueVoters(),
                currentTheme=getCurrentTheme(),
                genderCount=getGenderCount(),
                themes=getThemes(),
                userIP=getIP()
                )
    return response


@app.route('/about')
# @cache.cached(timeout=50)
def about():
    deltas = {
            'hour': {
                'hours': 1,
                'votes': None,
                'voters': None
                },
            'day': {
                'hours': 24,
                'votes': None,
                'voters': None
                },
            'week': {
                'hours': 24*7,
                'votes': None,
                'voters': None
                },
            'month': {
                'hours': 24*30,
                'votes': None,
                'voters': None
                },
            'year': {
                'hours': 24*365,
                'votes': None,
                'voters': None
                }
            }

    now = datetime.datetime.now()
    nonSpamVotes = db.session.query(Vote).filter(Vote.spam == False)
    for delta in ['year', 'month', 'week', 'day', 'hour']:
        oneDeltaAgo = now - datetime.timedelta(hours = deltas[delta]['hours'])

        nonSpamVotes = nonSpamVotes.filter(Vote.when > oneDeltaAgo)
        # ^progressively reduce list of votes; O(n) instead of O(n * number of different deltas)

        deltas[delta]['votes'] = nonSpamVotes.count()
        deltas[delta]['voters'] = nonSpamVotes.distinct(Vote.ip).group_by(Vote.ip).count()


    return render_template(
            'about.html',
            deltas=deltas,
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            userIP=getIP()
            )


@app.route('/legal')
def legal():
    return render_template(
            'legal.html',
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            userIP=getIP()
            )


@app.errorhandler(404)
def pageNotFound(e):
    return render_template(
            '404.html',
            totalVotes=getTotalVotes(),
            uniqueVoters=getUniqueVoters(),
            currentTheme=getCurrentTheme(),
            genderCount=getGenderCount(),
            themes=getThemes(),
            userIP=getIP()
            ), 404
