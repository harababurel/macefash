"""
aka *secret sauce* --
-- a single entry-point that resolves the import dependencies.
"""
from app import app, db
from models import *
from databaseGenerator import generateDatabase
import routes

if __name__ == '__main__':
    # generateDatabase()
    app.run(host='0.0.0.0', port=8080, debug=True)
