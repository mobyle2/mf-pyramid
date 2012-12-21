
import annotation
from annotation import Annotation
from renderer import FormRenderer
from views import *

class Dashboard:
  ''' Manage administration dashboard for pyramid
  '''


  @staticmethod
  def set_connection(conn):
    '''Sets the db connection to mongo
    :param conn: MongoDB connection objects
    :type conn: Connection
    '''
    Annotation.db_conn = conn

  @staticmethod
  def add_dashboard(klasses, config = None, prefix = ''):
    ''' Adds a list of class to the dashboard

    :param klasses: list of object class to add to the dashboard
    :type klasses: list
    :param config: Pyramid Configurator
    :type config: pyramid.config.Configurator
    :param prefix: optional prefix to add in front of the routes
    :type prefix: str
    '''
    if klasses is None:
      return
    if prefix is not None:
      FormRenderer.prefix = prefix
    for klass in klasses:
      Annotation.addKlass(klass)
    if config is not None:
      config.add_route('mf_objects',prefix+'/{objname}s/')
      #config.add_route('mf_add',prefix+'/{objname}s/')
      config.add_route('mf_object',prefix+'/{objname}s/{id}')
      #config.add_route('mf_delete',prefix+'/{objname}s/{id}')
      #config.add_route('mf_edit',prefix+'/{objname}s/{id}')
      config.add_route('mf_admin',prefix+'/admin')
      config.add_view(mf_list, route_name='mf_objects', renderer='json', request_method='GET')
      config.add_view(mf_show, route_name='mf_object', renderer='json', request_method='GET')
      config.add_view(mf_edit, route_name='mf_object', renderer='json', request_method='POST')
      config.add_view(mf_delete, route_name='mf_object', renderer='json', request_method='DELETE')
      #config.add_view(mf_add, route_name='mf_add', renderer='json', request_method='(POST,PUT)')
      config.add_view(mf_add, route_name='mf_objects', renderer='json', request_method='PUT')
      config.add_view(mf_admin, route_name='mf_admin', renderer='dashboard.mako')
      #config.scan()

