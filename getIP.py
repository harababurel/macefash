"""
Module provides a function that finds the current user IP.
"""
from flask import request


def getIP():
    """
    'unknown' serves as a universal IP :D
    """
    ip = request.headers.get('X-Real-IP')
    if ip is None:
        try:
            ip = request.headers.getlist("X-Forwarded-For")[0]
        except:
            ip = None
    if ip is None:
        ip = 'unknown'
    return ip
