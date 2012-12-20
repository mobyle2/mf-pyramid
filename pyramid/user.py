import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config

def home(request):
    return Response('hello World')


@mf_decorator
class User:

  _id = ''
  name = ''
  email = ''
  age = 0
  admin = False
  options = { 'tags': '' , 'categories': '' }
  creation_date = datetime.utcnow()
  today = date.today()

  def html(self, fields = None):
    return self.render(fields)


if __name__ == "__main__":
  user = User()
  user.name = "osallou"
  user.email = "osallou@irisa.fr"
  user.mongo = "test"
  user.age = 28
  user.admin = True
  user.options["tags"] = 'tag1'
  user.creation_date = datetime.utcnow()

  #print user.metadata.fields
  print user.html()

