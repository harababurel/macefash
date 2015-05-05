from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import macefash.routes

app = Flask(__name__)
app.secret_key = 'fascist'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
from models import *

import generateData
