import unittest
import user
from user import User
import mf.dashboard
from mf.dashboard import Dashboard
from mf.annotation import Annotation
import pymongo

class TestDashboard(unittest.TestCase):

  def setup(self):
    Dashboard.__klasses = []
    c = pymongo.Connection()
    self.db = c.mftest
    self.db.users.remove({})

  def test_add_to_dashboard(self):
    Dashboard.add_dashboard([User])
    #Annotation.dump()
    assert(User in Annotation.klasses())

  def test_instantiate_from_klasses(self):
    Dashboard.add_dashboard([User])
    myuser = Annotation.klasses()[0]()
    assert(isinstance(myuser,User))

  def test_render_new_user(self):
    Dashboard.add_dashboard([User])
    myuser = Annotation.klasses()[0]()
    html = myuser.html()   

  def test_bind_user(self):
    Dashboard.add_dashboard([User])
    request = dict()
    request["User[name]"] = "sample"
    request["User[email]"] = "test@nomail.com"
    user = User()
    user.bind_form(request)
    assert(user.name == "sample")
    assert(user.email == "test@nomail.com")

  def test_update_user(self):
    Dashboard.add_dashboard([User])
    user = User()
    user.name = "Walter"
    user.email = "Bishop"
    user.m.save()
    request = dict()
    request["User[name]"] = "sample"
    request["User[email]"] = "test@nomail.com"
    user.bind_form(request)
    user.m.save()
    assert(user.name == "sample")
    assert(user.email == "test@nomail.com")


