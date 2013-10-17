import mf.annotation
from mf.annotation import *
from pyramid.response import Response
from pyramid.view import view_config
import mf.views
from mongokit import Document, Connection, CustomType

class GlobalTypes(Document):
  __collection__ = 'types'
  __database__ = 'test'

  structure = { '_type': unicode, 'name': basestring }


@mf_decorator
class Types1(GlobalTypes):

  structure = { 'surname1': basestring }


  def my(self, control, request, authenticated_userid):
    return {}

@mf_decorator
class Types2(GlobalTypes):

  structure = { 'surname2': basestring }

  def my(self, control, request, authenticated_userid):
    return {}

