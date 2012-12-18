import unittest
import user
from user import User
import mf.dashboard
from mf.dashboard import Dashboard
from mf.annotation import Annotation

class TestDashboard(unittest.TestCase):

  def setup(self):
    Dashboard.__klasses = []

  def test_add_to_dashboard(self):
    Dashboard.add_dashboard([User])
    #Annotation.dump()
    assert(User in Annotation.klasses())

  def test_instantiate_from_klasses(self):
    Dashboard.add_dashboard([User])
    myuser = Annotation.klasses()[0]()
    assert(isinstance(myuser,User))
