'''
Created on Mar 29, 2016
File to handle session management
@author: Arentios
'''
from beaker.middleware import SessionMiddleware

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
}