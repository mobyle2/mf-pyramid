import mf.annotation
#from admin.admin import Admin
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config
from mongokit import Document, Connection

from group import Group


@mf_decorator
class SuperGroup(Group):

  __collection__ = 'supergroups'
  __database__ = 'test'

  structure = { 'tags' :  basestring }

