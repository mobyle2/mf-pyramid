import unittest
import user
from user import User
import mf.dashboard
from mf.dashboard import Dashboard
from mf.annotation import Annotation

class TestDashboard(unittest.TestCase):

  def test_add_to_dashboard(self):
    Dashboard.add_dashboard([User])
    #Annotation.dump()
    assert(User in Annotation.klasses())
