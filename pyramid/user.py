import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config
import mf.views

def home(request):
    return Response('hello World')


@mf_decorator
class User:
  ''' Example class for tests
  '''

  _id = ''
  name = ''
  email = ''
  age = 0
  admin = False
  options = { 'tags': '' , 'categories': '' }
  creation_date = datetime.utcnow()
  today = date.today()
  array = [ 'one', 'two']

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
  user = User()
  user.name = "osallou"
  user.email = "osallou@irisa.fr"
  user.mongo = "test"
  user.age = 28
  user.admin = True
  user.options["tags"] = 'tag1'
  user.creation_date = datetime.utcnow()

  #request = [("User[name]","sample"), ("User[email]","test@nomail.com")]
  request = [("User[array]","test1"), ("User[array]","test2"),  ("User[array]","test3")]
  user.bind_form(request)
  #print user.metadata.fields
  #print user.html()
  print user.array

