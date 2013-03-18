import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config
import mf.views
from mongokit import Document, Connection, CustomType
from group import Group

def home(request):
    return Response('hello World')


class CustomStatus(CustomType):

    mongo_type = int
    python_type = int

    def to_bson(self, value):
        return int(value)

    def to_python(self, value):
        if value is not None:
            return int(value)

    def validate(self, value, path):
        return isinstance(value, int)

    @staticmethod
    def unserialize(value):
        return str(value)


@mf_decorator
class User(Document):
  ''' Example class for tests
  '''
  __collection__ = 'users'
  __database__ = 'test'

  structure = { 'name': basestring, 'email': basestring, 'age': int, 'admin': bool,
  'options' : { 'tags': basestring , 'categories': basestring }, 'creation_date' : datetime, 'today': basestring, 'array' : [basestring] , 'groups' : [ Group ],
  'multi' : [ { 'name' : basestring, 'role' : basestring } ],
  'custom' :  CustomStatus
  }

  use_autorefs = True


  def html(self, fields = None):
    return self.render(fields)

  def my(self,control):
    '''
    Checks user access to the object

    :param control: type of access
    :type control: str
    :return: dict - Mongodb filter to apply on object search
    '''
    if control == mf.views.MF_LIST:
      return { 'name' : 'Mike' }
    return {}


if __name__ == "__main__":
  connection = Connection()
  connection.register([User])
  print str(connection.User.find())
  for user in connection.User.find():
    print user[ 'name']

  #request = [("User[name]","sample"), ("User[email]","test@nomail.com")]
  #request = [("User[array]","test1"), ("User[array]","test2"),  ("User[array]","test3")]
  #user.bind_form(request)
  #print user.metadata.fields
  print user.html()
  #print user.array

