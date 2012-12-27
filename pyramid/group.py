import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config


@mf_decorator
class Group:

  _id = ''
  name = ''
  creation_date = datetime.utcnow()

