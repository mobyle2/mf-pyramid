from admin import Admin
from admin import *
from ming import Field,schema
from ming.datastore import DataStore
from ming import Session, create_datastore

bind = create_datastore("%s%s"%('mongodb://localhost:27017','test'))
session = Session(bind)

@admin_decorator
class User:

  class __mongometa__:
      session = session
      name = 'users'

  _id = Field(schema.ObjectId) 
  name = Field(str)
  email = Field(str)
  mongo = Field(str)
  age = Field(int)
  admin = Field(bool, if_missing = False)
  options = Field(dict( tags=str, categories=str))


  def html(self, fields = None):
    return self.render(fields)


if __name__ == "__main__":
  user = User()
  user.name = "osallou"
  user.email = "osallou@irisa.fr"
  user.mongo = "test"
  user.age = 28
  user.admin = True
  user.options.tags = 'tag1'

  #print user.metadata.fields
  print user.html()

  r = user.get_renderer('name')
  assert r.validate('blabla')
  assert not r.validate(1)
  r = user.get_renderer('age')
  assert not r.validate('blabla')
  assert r.validate(1)
  r = user.get_renderer('admin')
  assert r.validate('True')
  assert r.validate(1)
  assert not r.validate('blo')

  request = dict()
  request["User[name]"] = "test"
  request["User[email]"] = "test@nomail.com"
  request["User[age]"] = "39"
  request["User[admin]"] = "nimportequoi"
  request["User[options][categories]"] = "cat2"

  user.bind_form(request)
  print user.html()

  #print user.html(["name","email"])

  print "Errors: "+str(user.__field_errors)

  print str(User.__render_fields)
