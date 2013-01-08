import unittest
import user
from user import User
import mf.dashboard
from mf.dashboard import Dashboard
from mf.annotation import Annotation
import pymongo
from mongokit import Document, Connection

connection = Connection()
connection.register([User])
Dashboard.set_connection(connection)

class TestDashboard(unittest.TestCase):

  def setup(self):
    Dashboard.__klasses = []
    collection = Annotation.get_db("User")
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
    myuser = Annotation.klasses()[0]()
    try:
      html = myuser.html()
    except Exception:
      self.fail("Error while generating html")


  def test_bind_user(self):
    Dashboard.add_dashboard([User])
    request = [("User[name]","sample"), ("User[email]","test@nomail.com")]
    user = User()
    user.bind_form(request)
    assert(user["name"] == "sample")
    assert(user["email"] == "test@nomail.com")

  def test_bind_user_array(self):
    Dashboard.add_dashboard([User])
    request = [("User[array]","test1"), ("User[array]","test2"),  ("User[array]","test3")]
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
    collection = Annotation.get_db("User")
    filter = {}
    filter["_id"] = user["_id"]
    obj= collection.find_one(filter)
    assert(obj["name"] == "sample")
    assert(obj["email"] == "test@nomail.com")

