# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server
import pyramid.config
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from mf.dashboard import Dashboard
from user import *
from user import User

#Use pymongo
from pymongo import MongoClient

if __name__ == '__main__':
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config = Configurator(session_factory = my_session_factory)
    config.include('pyramid_debugtoolbar')
    config.add_settings({'mako.directories':'templates/'})
    config.add_static_view(name='static', path='static')
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_view(home, route_name='home')
    connection = MongoClient()
    db = connection.test
    Dashboard.set_connection(db)
    # Clear database
    db.drop_collection('users')
    u1 = {"name": "Mike", "age" : 30, "email" : "nomail", "creation_date" : datetime.utcnow(), "options" : { 'tags': '' , 'categories': '' } }
    db.users.insert(u1)
    u2 = {"name": "Tommy", "admin" : True, "age" : 40, "email" : "nomail", "creation_date" : datetime.utcnow(), "options" : { 'tags': 'cool' , 'categories': '' } }
    db.users.insert(u2)
    Dashboard.add_dashboard([User],config)
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6789, app)
    server.serve_forever()
    

