import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config
from mongokit import Document, Connection


@mf_decorator
class Group(Document):

  __collection__ = 'groups'
  __database__ = 'test'

  structure = { 'name' : basestring, 'creation_date' : datetime}

