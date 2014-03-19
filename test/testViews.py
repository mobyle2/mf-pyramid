import unittest
import user
from user import User
import group
from group import Group
import mytypes
from mytypes import Types1, Types2
from supergroup import SuperGroup
import mf.dashboard
from mf.dashboard import Dashboard
from mf.db_conn import DbConn
from mf.annotation import Annotation
from mf.views import *
import pymongo
from mongokit import Connection
from datetime import datetime
import logging
import json

from pyramid import testing
from pyramid.httpexceptions import HTTPForbidden

from webob.multidict import MultiDict

connection = Connection()
connection.register([User, Group, SuperGroup, Types1, Types2])
Dashboard.set_connection(connection)


class TestViews(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

        Dashboard.__klasses = []
        collection = connection.User.find()
        for a_user in collection:
            a_user.delete()
        collection = connection.Group.find()
        for a_group in collection:
            a_group.delete()
        collection = connection.Types1.fetch()
        for a_type in collection:
            a_type.delete()
        collection = connection.Types2.fetch()
        for a_type in collection:
            a_type.delete()


        Dashboard.add_dashboard([User, Group, Types1, Types2])

        a_group = connection.Group()
        a_group["name"] = "sampleGroup"
        a_group["creation_date"] = datetime.utcnow()
        a_group.save()

        user1 = connection.User()
        user1['name'] = "Mike"
        user1['email'] = "dummy@nomail.com"
        user1['groups'] = [a_group]
        user1.save()

        user2 = connection.User()
        user2['name'] = "Mike"
        user2['email'] = "other@nomail.com"
        user2['groups'] = [a_group]
        user2.save()

        user3 = connection.User()
        user3['name'] = "John"
        user3['email'] = "different@nomail.com"
        user3['groups'] = [a_group]
        user3.save()

    def tearDown(self):
        testing.tearDown()

    def test_mf_list(self):
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        response = mf_list(request)
        #users = json.loads(response.body)
        users = response
        assert(len(users) == 2)

    def test_mf_list_multiple_types(self):
        type1 = connection.Types1()
        type1["name"] = "sampleType1"
        type1.save()
        type2 = connection.Types2()
        type2["name"] = "sampleType2"
        type2.save()
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'types1'
        response = mf_list(request)
        #types = json.loads(response.body)
        types = response
        assert(len(types) == 1)


    def test_mf_search(self):
        mdict = MultiDict()
        mdict.add('SearchUser[email]', 'other')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        response = mf_search(request)
        #users = json.loads(response.body)
        users = response
        assert(len(users) == 1)
        assert(users[0]['email'] == 'other@nomail.com')

    def test_mf_show(self):
        a_user = connection.User.find_one({'email': 'dummy@nomail.com'})
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = a_user['_id']
        response = mf_show(request)
        #a_user = json.loads(response.body)
        a_user = response
        assert(a_user['user']['email'] == 'dummy@nomail.com')

    def test_mf_add(self):
        #  request = [("User[name]","sample"),
        #  ("User[email]","test@nomail.com")]
        mdict = MultiDict()
        mdict.add('User[email]', 'test@add')
        mdict.add('User[name]', 'testadd')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        response = mf_add(request)
        #res = json.loads(response.body)
        res = response
        assert(res['status'] == 0)
        assert(res['object'] == 'user')
        assert(res['user']['email'] == 'test@add')
        a_user = connection.User.find_one({'email': 'test@add'})
        assert (a_user is not None)

    def test_mf_delete(self):
        a_user = connection.User.find_one({'email': 'dummy@nomail.com'})
        users = connection.User.find().count()
        assert(users == 3)
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = a_user['_id']
        response = mf_delete(request)
        #res = json.loads(response.body)
        res = response
        assert(res['status'] == 0)
        users = connection.User.find().count()
        assert(users == 2)

    def test_mf_edit(self):
        a_user = connection.User.find_one({'email': 'dummy@nomail.com'})
        mdict = MultiDict()
        mdict.add('User[name]', 'Alfred')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = a_user['_id']
        response = mf_edit(request)
        #res = json.loads(response.body)
        res = response
        assert(res['status'] == 0)
        assert(res['object'] == 'user')
        assert(res['user']['name'] == 'Alfred')
        a_user = connection.User.find_one({'email': 'dummy@nomail.com'})
        assert(a_user['name'] == 'Alfred')

    def test_mf_edit_forbidden(self):
        a_user = connection.User.find_one({'email': 'dummy@nomail.com'})
        mdict = MultiDict()
        mdict.add('User[name]', 'Tommy')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = a_user['_id']
        try:
            mf_edit(request)
        except HTTPForbidden:
            pass
            return
        raise HTTPForbidden

    def test_mf_edit_forbidden_age_10(self):
        a_user = connection.User.find_one({'email': 'dummy@nomail.com'})
        a_user['age'] = 20
        a_user.save()
        mdict = MultiDict()
        mdict.add('User[name]', 'Alfred')
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = a_user['_id']
        response = mf_edit(request)
        #res = json.loads(response.body)
        res = response
        assert(res['status'] == 0)
        a_user['age'] = 10
        a_user.save()
        request = testing.DummyRequest(mdict)
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = a_user['_id']
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

    def test_mf_show_by_name(self):
        User.search_by("name")
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = 'John'
        response = mf_show(request)
        #a_user = json.loads(response.body)
        a_user = response
        assert(a_user['user']['email'] == 'different@nomail.com')
        User.search_by("_id")
        request = testing.DummyRequest()
        request.matchdict['objname'] = 'user'
        request.matchdict['id'] = 'John'
        try:
            response = mf_show(request)
            self.fail("user should not be found")
        except HTTPNotFound:
            pass
        self.test_mf_show()
