import unittest
import user
from user import User
import group
from group import Group
from supergroup import SuperGroup
import mf.dashboard
from mf.dashboard import Dashboard
from mf.db_conn import DbConn
from mf.annotation import Annotation
from mf.views import *
import pymongo
from mongokit import Document, Connection, ObjectId
from datetime import datetime
import logging
import json

from pyramid import testing
from pyramid.httpexceptions import HTTPForbidden

from webob.multidict import MultiDict

connection = Connection()
connection.register([User,Group,SuperGroup])
Dashboard.set_connection(connection)


class TestViews(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

        Dashboard.__klasses = []
        collection = connection.User.find()
        for user in collection:
            user.delete()
        collection = connection.Group.find()
        for group in collection:
            group.delete()

        Dashboard.add_dashboard([User, Group])

        group = connection.Group();
        group["name"] = "sampleGroup"
        group["creation_date"] = datetime.utcnow()
        group.save()


        user1 = connection.User()
        user1['name'] = "Mike"
        user1['email'] = "dummy@nomail.com"
        user1['groups'] = [ group ]
        user1.save()

        user2 = connection.User()
        user2['name'] = "Mike"
        user2['email'] = "other@nomail.com"
        user2['groups'] = [ group ]
        user2.save()

        user3 = connection.User()
        user3['name'] = "John"
        user3['email'] = "different@nomail.com"
        user3['groups'] = [ group ]
        user3.save()

    def tearDown(self):
        testing.tearDown()

    def test_mf_list(self):
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        response = mf_list(request)
        users = json.loads(response.body)
        assert(len(users)==2)

    def test_mf_search(self):
        mdict = MultiDict()
        mdict.add('SearchUser[email]' ,'other')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        response = mf_search(request)
        users = json.loads(response.body)
        assert(len(users)==1)
        assert(users[0]['email'] == 'other@nomail.com')

    def test_mf_show(self):
        user = connection.User.find_one({'email' : 'dummy@nomail.com'})
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = user['_id']
        response = mf_show(request)
        user = json.loads(response.body)
        assert(user['user']['email'] == 'dummy@nomail.com')

    def test_mf_add(self):
        #  request = [("User[name]","sample"),
        #  ("User[email]","test@nomail.com")]
        mdict = MultiDict()
        mdict.add('User[email]' ,'test@add')
        mdict.add('User[name]' ,'testadd')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        response = mf_add(request)
        res = json.loads(response.body)
        assert(res['status']==0)
        user = connection.User.find_one({'email' : 'test@add'})
        assert (user is not None)



    def test_mf_delete(self):
        user = connection.User.find_one({'email' : 'dummy@nomail.com'})
        users = connection.User.find().count()
        assert(users == 3)
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = user['_id']
        response = mf_delete(request)
        res = json.loads(response.body)
        assert(res['status']==0)
        users = connection.User.find().count()
        assert(users == 2)

    def test_mf_edit(self):
        user = connection.User.find_one({'email' : 'dummy@nomail.com'})
        mdict = MultiDict()
        mdict.add('User[name]' ,'Alfred')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = user['_id']
        response = mf_edit(request)
        res = json.loads(response.body)
        assert(res['status']==0)
        user = connection.User.find_one({'email' : 'dummy@nomail.com'})
        assert(user['name'] == 'Alfred')


    def test_mf_edit_forbidden(self):
        user = connection.User.find_one({'email' : 'dummy@nomail.com'})
        mdict = MultiDict()
        mdict.add('User[name]' ,'Tommy')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = user['_id']
        try:
            response = mf_edit(request)
        except HTTPForbidden:
            pass
            return
        raise HTTPForbidden

    def test_mf_edit_forbidden_age_10(self):
        user = connection.User.find_one({'email' : 'dummy@nomail.com'})
        user['age'] = 20
        user.save()
        mdict = MultiDict()
        mdict.add('User[name]' ,'Alfred')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = user['_id']
        response = mf_edit(request)
        res = json.loads(response.body)
        assert(res['status']==0)
        user['age'] = 10
        user.save()
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = user['_id']
        try:
            response = mf_edit(request)
        except HTTPForbidden:
            pass
            return
        raise HTTPForbidden

        

    def test_mf_admin(self):
        request = testing.DummyRequest()
        response = mf_admin(request)
        assert('User' in response['objects'])
