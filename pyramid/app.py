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

    # Clear database
    db.drop_collection('users')
    db.drop_collection('groups')

    connection = Connection()
    connection.register([User,Group])

    group = connection.Group()
    group["name"] = "sampleGroup"
    group["creation_date"] = datetime.utcnow()
    group.save()
    user1 = connection.User()
    user1["name"] = "Mike"
    user1["age"] = 50
    user1["admin"] = False
    user1["email"] = "nomail"
    user1["creation_date"] = datetime.utcnow()
    user1["today"] = str(date.today())
    user1["array"] = []
    user1["options"]["tags"] = ''
    user1["options"]["categories"] = ''
    user1["group"] = group
    user1.save()
    user2 = connection.User()
    user2["name"] = "Mike"
    user2["age"] = 40
    user2["admin"] = True
    user2["email"] = "othermail@mail.fr"
    user2["creation_date"] = datetime.utcnow()
    user2["today"] = str(date.today())
    user2["array"] = ["four","five"]
    user2["options"]["tags"] = 'cool'
    user2["options"]["categories"] = 'any'
    user2.save()
    user3 = connection.User()
    user3["name"] = "Tommy"
    user3["age"] = 30
    user3["admin"] = False
    user3["email"] = "some mail"
    user3["creation_date"] = datetime.utcnow()
    user3["today"] = str(date.today())
    user3["array"] = ["two"]
    user3["options"]["tags"] = 'anyone'
    user3["options"]["categories"] = ''
    user3["group"] = group
    user3.save()
    #u1 = {"name": "Mike", "admin" : False, "age" : 30, "email" : "nomail", "creation_date" : datetime.utcnow(), "options" : { 'tags': '' , 'categories': '' }, "today": date.today().strftime("%d/%m/%y"), "array" : [] }
    #db.users.insert(u1)
    #u2 = {"name": "Tommy", "admin" : True, "age" : 40, "email" : "nomail", "creation_date" : datetime.utcnow(), "options" : { 'tags': 'cool' , 'categories': '' }, "array" : [ 'three', 'four'] }
    #db.users.insert(u2)
    #u3 = {"name": "Mike", "admin" : True, "age" : 50, "email" : "dummy", "creation_date" : datetime.utcnow(), "options" : { 'tags': 'cool' , 'categories': 'any' }, "array" : [ 'three', 'four'] }
    #db.users.insert(u3)
    #g1 = {"name": "sample", "creation_date" : datetime.utcnow() }
    #db.groups.insert(g1)

    Dashboard.set_connection(connection)

    Dashboard.add_dashboard([User,Group],config)

    renderer = mf.renderer.TextChoiceRenderer(User,'email','')
    renderer.limit([ 'nomail', 'othermail@mail.fr', 'sample@nomail' ])

    groupid_renderer = mf.renderer.SimpleReferenceRenderer(User,'groupid',Group)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6789, app)
    server.serve_forever()
    

