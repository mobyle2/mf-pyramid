
import annotation
from db_conn import DbConn
from renderer import FormRenderer
from views import *

class Dashboard:
  ''' Manage administration dashboard for pyramid
  '''

  dconfig = { 'permission' : None, 'templates' : '' }


  @staticmethod
  def set_config(config):
    '''Global config for dashboard.
     - permission: Pyramid permission for /admin views, no permission by default
     - templates: path to Mako dashboard template, default is Dashboard.mako

    :param config: configuration dictionary
    :type config: dict
    '''
    Dashboard.dconfig = config


  @staticmethod
  def get_config():
    return Dashboard.dconfig

  @staticmethod
  def set_connection(conn):
    '''Sets the db connection to mongo

    :param conn: MongoDB connection objects
    :type conn: Connection
    '''
    DbConn.db_conn = conn

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
      config.add_route('mf_admin',prefix+'/admin')
      config.add_route('mf_objects',prefix+'/{objname}s/')
      config.add_route('mf_object',prefix+'/{objname}s/{id}')
      config.add_view(mf_search, route_name='mf_objects', renderer='json', request_method='POST')      
      config.add_view(mf_list, route_name='mf_objects', renderer='json', request_method='GET')
      config.add_view(mf_show, route_name='mf_object', renderer='json', request_method='GET')
      config.add_view(mf_edit, route_name='mf_object', renderer='json', request_method='POST')
      config.add_view(mf_delete, route_name='mf_object', renderer='json', request_method='DELETE')
      config.add_view(mf_add, route_name='mf_objects', renderer='json', request_method='PUT')
      templates = Dashboard.dconfig['templates']
      if not templates:
        templates = 'dashboard.mako'
      if Dashboard.dconfig['permission'] is not None:
        config.add_view(mf_admin, route_name='mf_admin', renderer=templates, permission = Dashboard.dconfig['permission'])
      else:
        config.add_view(mf_admin, route_name='mf_admin', renderer=templates)

