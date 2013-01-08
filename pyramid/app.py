# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server
import pyramid.config
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from mf.dashboard import Dashboard
from user import *
from user import User
from group import Group

#Use pymongo
from pymongo import MongoClient
from mongokit import Document, Connection


if __name__ == '__main__':
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config = Configurator(session_factory = my_session_factory)
    config.include('pyramid_debugtoolbar')
    config.add_settings({'mako.directories':'templates/'})
    config.add_static_view(name='static', path='static')
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_view(home, route_name='home')
    mgconnection = MongoClient()
    db = mgconnection.test
    #Dashboard.set_connection(db)

    # Clear database
    db.drop_collection('users')
    db.drop_collection('groups')
    u1 = {"name": "Mike", "admin" : False, "age" : 30, "email" : "nomail", "creation_date" : datetime.utcnow(), "options" : { 'tags': '' , 'categories': '' }, "today": date.today().strftime("%d/%m/%y"), "array" : [] }
    db.users.insert(u1)
    u2 = {"name": "Tommy", "admin" : True, "age" : 40, "email" : "nomail", "creation_date" : datetime.utcnow(), "options" : { 'tags': 'cool' , 'categories': '' }, "array" : [ 'three', 'four'] }
    db.users.insert(u2)
    u3 = {"name": "Mike", "admin" : True, "age" : 50, "email" : "dummy", "creation_date" : datetime.utcnow(), "options" : { 'tags': 'cool' , 'categories': 'any' }, "array" : [ 'three', 'four'] }
    db.users.insert(u3)
    g1 = {"name": "sample", "creation_date" : datetime.utcnow() }
    db.groups.insert(g1)


    connection = Connection()
    connection.register([User,Group])
    Dashboard.set_connection(connection)

    Dashboard.add_dashboard([User,Group],config)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6789, app)
    server.serve_forever()
    

