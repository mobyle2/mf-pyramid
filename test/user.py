import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config
import mf.views
from mongokit import Document, Connection, CustomType, IS
from group import Group

def home(request):
    return Response('hello World')


class CustomStatus(CustomType):

    mongo_type = int
    python_type = int

    def to_bson(self, value):
        if value is None:
            return 0
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
  'custom' :  CustomStatus(),
  'groupRef' : ObjectId,
  'floattag' : float,
  'alist' : IS(u'one', u'two', u'three'),
  'multi2' : [ { 'group' : ObjectId, 'role' : basestring } ]
  }

  default_values = { 'groups' : [], 'floattag': 0.1 }


  use_autorefs = True


  def html(self, fields = None):
    return self.render(fields)+"\n"+self.render_search(fields)

  def my(self, control, request, authenticated_userid):
    '''
    Checks user access to the object

    :param control: type of access
    :type control: str
    :param request: pyramid request object
    :type request: pyramid.request
    :return: dict - Mongodb filter to apply on object search
    :param authenticated_userid: id of the user logging in
    :type authenticated_userid: str
    '''
    if authenticated_userid == 'anonymous':
        return None
    if control == mf.views.MF_READ:
      return { 'name' : 'Mike' }
    if control == mf.views.MF_EDIT:
        try:
            if self['age'] == 10:
                return None
            param = request.params.getone('User[name]')
            if param == 'Tommy':
                # For testing, prevent updating with name=Tommy
                return None
        except Exception:
            return {}
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

