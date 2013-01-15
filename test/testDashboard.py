import unittest
import user
from user import User
import group
from group import Group
import mf.dashboard
from mf.dashboard import Dashboard
from mf.db_conn import DbConn
from mf.annotation import Annotation
import pymongo
from mongokit import Document, Connection
from datetime import datetime
import logging

connection = Connection()
connection.register([User,Group])
Dashboard.set_connection(connection)

class TestDashboard(unittest.TestCase):

  def setup(self):
    Dashboard.__klasses = []
    collection = DbConn.get_db("User")
    for user in collection:
      user.delete()

  def test_add_to_dashboard(self):
    Dashboard.add_dashboard([User])
    assert(User in Annotation.klasses())

  def test_instantiate_from_klasses(self):
    Dashboard.add_dashboard([User])
    myuser = Annotation.klasses()[0]()
    assert(isinstance(myuser,User))

  def test_render_new_user(self):
    Dashboard.add_dashboard([User])
    myuser = User()
    try:
      html = myuser.html()
    except Exception as e:
      self.fail("Error while generating html: "+str(e))


  def test_bind_user(self):
    Dashboard.add_dashboard([User])
    request = [("User[name]","sample"), ("User[email]","test@nomail.com")]
    user = User()
    user.bind_form(request)
    assert(user["name"] == "sample")
    assert(user["email"] == "test@nomail.com")

  def test_bind_user_array(self):
    Dashboard.add_dashboard([User])
    request = [("User[array][0]","test1"), ("User[array][1]","test2"),  ("User[array][3]","test3")]
    user = User()
    user.bind_form(request)
    assert(len(user["array"]) == 3)
    assert(user["array"][0]=="test1")

  def test_bind_user_dict(self):
    Dashboard.add_dashboard([User])
    request = [("User[options][tags]","sample")]
    user = User()
    user.bind_form(request)
    print str(user)
    assert(user["options"]["tags"] == "sample")

  def test_user_bind_save_get(self):
    Dashboard.add_dashboard([User])
    request = [("User[name]","sample"), ("User[email]","test@nomail.com")]
    user = connection.User()
    user.bind_form(request)
    user.save()
    collection = DbConn.get_db("User")
    filter = {}
    filter["_id"] = user["_id"]
    obj= collection.find_one(filter)
    assert(obj["name"] == "sample")
    assert(obj["email"] == "test@nomail.com")

  def test_dbref(self):
    Dashboard.add_dashboard([User,Group])
    group = connection.Group()
    group["name"] = "sampleGroup"
    group["creation_date"] = datetime.utcnow()
    group.save()
    user = connection.User()
    user["name"] = "sampleUser"
    user["email"] = "test@nomail.com"
    user["groups"] = [ group ]
    user.save()
    assert(group["_id"] == user["groups"][0]["_id"])

  def test_bind_with_dbref(self):
    Dashboard.add_dashboard([User])
    group = connection.Group()
    group["name"] = "sampleGroup"
    group["creation_date"] = datetime.utcnow()
    group.save()
    request = [("User[groups][0]",str(group["_id"]))]
    user = connection.User()
    user["name"] = "sampleUser"
    user["email"] = "test@nomail.com"
    user.save()
    user.bind_form(request)
    user.save()
    assert(group["_id"] == user["groups"][0]["_id"])


  def test_bind_multi_array(self):
    Dashboard.add_dashboard([User])
    request = [("User[multi][name][1]","name2"),("User[multi][role][0]","role1"),("User[multi][name][0]","name1"),("User[multi][role][1]","role2")]
    user = User()
    user.bind_form(sorted(request))
    print str(user)
    assert(len(user["multi"]) == 2)      
    assert(user["multi"][0]["role"] == "role1")

    
