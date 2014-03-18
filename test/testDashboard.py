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
import pymongo
from mongokit import Document, Connection, ObjectId
from datetime import datetime
import logging

connection = Connection()
connection.register([User,Group,SuperGroup])
Dashboard.set_connection(connection)

class TestDashboard(unittest.TestCase):

  def setUp(self):
    Dashboard.__klasses = []
    collection = connection.User.find()
    for user in collection:
      user.delete()
    collection = connection.Group.find()
    for group in collection:
        group.delete()

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
    myuser['keytype']['test1'] = 'test1'
    myuser['keytype']['test2'] = 'test2'
    try:
      html = myuser.html()
    except Exception as e:
      self.fail("Error while generating html: "+str(e))

  def test_render_with_specific_list(self):
    Dashboard.add_dashboard([User])
    User.set_display_fields(['name','email','options'])
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

  def test_bind_user_generic_dict(self):
    Dashboard.add_dashboard([User])
    request = [("User[name]","sample"), ("User[email]","test@nomail.com"),
                ("User[keytype][test1]","test1"),
                ("User[keytype][test2]","test2")]
    user = User()
    user.bind_form(request)
    assert(user["keytype"]["test1"] == "test1")
    assert(user["keytype"]["test2"] == "test2")


  def test_bind_user_IS_operator(self):
    Dashboard.add_dashboard([User])
    request = [("User[name]","sample"), ("User[alist]","one")]
    user = User()
    user.bind_form(request)
    assert(user["name"] == "sample")
    assert(user["alist"] == "one")
    request = [("User[name]","sample"), ("User[alist]","four")]
    user = User()
    res = user.bind_form(request)
    assert('alist' in res)
    assert(user["alist"] is not "four")

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

  def test_inheritance(self):
    Dashboard.add_dashboard([User])
    sgroup = connection.SuperGroup()
    sgroup["name"] = "sampleGroup"
    sgroup["creation_date"] = datetime.utcnow()
    sgroup.save()


  def test_bind_multi_array(self):
    Dashboard.add_dashboard([User])
    request = [("User[multi][name][1]","name2"),("User[multi][role][0]","role1"),("User[multi][name][0]","name1"),("User[multi][role][1]","role2")]
    user = User()
    user.bind_form(sorted(request))
    print str(user)
    assert(len(user["multi"]) == 2)      
    assert(user["multi"][0]["role"] == "role1")


  def test_bind_multi_array2(self):
    Dashboard.add_dashboard([User])
    request = [("User[multi][1][name]","name2"),("User[multi][0][role]","role1"),("User[multi][0][name]","name1"),("User[multi][1][role]","role2")]
    user = User()
    user.bind_form(sorted(request))
    assert(len(user["multi"]) == 2)
    assert(user["multi"][0]["role"] == "role1")

  def test_bind_multi_array3(self):
    Dashboard.add_dashboard([User])
    group = connection.Group()
    group["name"] = "sampleGroup"
    group["creation_date"] = datetime.utcnow()
    group.save()

    request = [("User[multi2][0][group]",str(group['_id'])),("User[multi2][0][role]","role1")]
    renderer = User.get_renderer("multi2.group")
    renderer.set_reference(Group)

    user = User()
    user.bind_form(sorted(request))
    assert(len(user["multi2"]) == 1)
    assert(user["multi2"][0]["role"] == "role1")
    assert(user["multi2"][0]["group"] == group['_id'])


  def test_bind_multi_array4(self):
    Dashboard.add_dashboard([User])
    group = connection.Group()
    group["name"] = "sampleGroup"
    group["creation_date"] = datetime.utcnow()
    group.save()

    request = [("User[multi2][0][group]",str(group['_id'])),("User[multi2][0][role]","role1")]
    renderer = mf.renderer.SimpleReferenceRenderer(User, 'group', Group, 'multi2')
    renderer.is_object_id = True
    #renderer = User.get_renderer("multi2.group")
    #renderer.set_reference(Group)

    user = User()
    user.bind_form(sorted(request))
    print str(User.get_renderer("multi2.group").__class__.__name__)
    assert(len(user["multi2"]) == 1)
    assert(user["multi2"][0]["role"] == "role1")
    assert(user["multi2"][0]["group"] == group['_id'])


  def test_bind_custom(self):
    Dashboard.add_dashboard([User])
    from mf.renderer import TextRenderer
    from user import CustomStatus
    assert(isinstance(User.get_renderer("custom"),TextRenderer) == True)
    request = [("User[custom]","one")]
    user = User()
    user.bind_form(request)
    print "custom= "+str(user)
    assert(user["custom"] == CustomStatus.unserialize("one"))


  def test_objectdbref(self):
      Dashboard.add_dashboard([User])
      group = connection.Group()
      group["name"] = "sampleGroup"
      group["creation_date"] = datetime.utcnow()
      group.save()
      request = [("User[groups][0]",str(group["_id"]))]
      user = connection.User()
      user["name"] = "sampleUser"
      user["email"] = "test@nomail.com"
      user["groupRef"] = group["_id"]
      renderer = User.get_renderer("groupRef")
      assert(renderer.is_object_id == True)
      renderer.set_reference(Group)
      user.save()
      assert(group["_id"] == user['groupRef'])
      assert(isinstance(user['groupRef'],ObjectId))

  def test_parseDateTime(self):
      from mf.renderer import parseDateTime
      dt = parseDateTime("2013-12-25 01:02:03")
      assert(dt is not None)
