#!/usr/bin/env python

# WORK IN PROGRESS.
from flask import request, Response

from functools import wraps

class Authentication(object):
    """docstring for Authentication"""
    def __init__(self, arg):
        super(Authentication, self).__init__()
        self.arg = arg
    
    # This is terrible  FIX THIS 
    def check_authentication(self, username, password):
        """ THIS IS A TEMP SHITTY METHOD TO BE FIXED LATER"""
        # TODO: FIX ME Sould query db, and do proper auth
        return username == 'user' and password == 'password'

    def authentication(self):
        return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            print auth
            if auth == None:
                try:
                    return self.authentication()
                except:
                     import ipdb; ipdb.set_trace()
            if self.check_authentication(auth.username, auth.password):
                return f(*args, **kwargs)
            else:
                return self.authentication()
        return decorated
