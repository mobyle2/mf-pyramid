from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from mf.annotation import Annotation
from mf.renderer import FormRenderer, CompositeRenderer, FloatRenderer, IntegerRenderer, BooleanRenderer, ReferenceRenderer
import logging

import json
from bson import json_util
from bson.objectid import ObjectId
from bson.dbref import DBRef

from mf.db_conn import DbConn

MF_LIST = 'list'
MF_MANAGE = 'manage'

def pluralize(name):
  '''Pluralize a name
  :param name: Name of the object
  :type name: str
  :return: str - lowercase object name with a final s
  '''
  return name.lower()+"s"

def mf_filter(objname, control):
    '''Return a mongo filter on object. It calls, if exists, the *my* method of the current object and returns the filter obtained from this method.
    '''
    objklass = None
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    if objklass is None:
      return {}
    attr = None
    if hasattr(objklass(),'my'):
      attr = getattr(objklass(),'my')
    filter = {}
    if attr is not None and callable(attr):
        filter = attr(control)
    return filter

def mf_search(request):
    '''Returns a JSON list of objects matching criteria on object

    :type request: IMultiDict
    :return: json - List of objects
    '''
    objklass = None
    objname = request.matchdict['objname']
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    if objklass is None:
      response = json.dumps({ 'status' : 1, 'error' : [], 'message' : 'Object does not exist' }, default=json_util.default)
      return Response(body = response,content_type = "application/json")
    filter = mf_filter(objname, MF_LIST)
    if filter is None:
      raise HTTPForbidden

    for field in objklass.render_fields:
      try:
        param = request.params.getone('Search'+objname.title()+'['+field+']')
      except Exception:
        # This is fine
        param = None
      renderer = objklass().get_renderer(field)
      #if isinstance(renderer,BooleanRenderer) and param is None:
      #  param = False
      if param is not None and param!='':
        if renderer and not isinstance(renderer,CompositeRenderer):

          if isinstance(renderer, ReferenceRenderer):
            filter[field+'.$id'] =  ObjectId(param)
          elif isinstance(renderer, IntegerRenderer):
            filter[field] = int(param)
          elif isinstance(renderer, FloatRenderer):
            filter[field] = float(param)
          elif isinstance(renderer, BooleanRenderer):
            if param in ['True', 'true', '1']:
              filter[field] = True
            else:
              filter[field] = False
          else:
              filter[field] = { "$regex" : param }
    logging.debug("search "+str(filter))
    objlist = []
    collection = DbConn.get_db(objklass.__name__).find(filter)

    for obj in collection:
      objlist.append(obj)
    objlist = json.dumps(objlist, default=json_util.default)
    return Response(body=objlist,content_type = "application/json")

#@view_config(name='mf_list', route_name='mf_list', renderer='json', request_method='GET')
def mf_list(request):
    '''Returns a JSON list of the object defined in the route
    If object has a function "my()", then the function is called to get a
    filter on the request

    :param request: HTTP params
    :type request: IMultiDict
    :return: json - List of objects
    '''
    objname = request.matchdict['objname']
    filter = mf_filter(objname, MF_LIST)
    if filter is None:
      raise HTTPForbidden
    objlist = []
    objklass = None
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    #collection = Annotation.db_conn[pluralize(objname)]
    #for obj in collection.find(filter):
    #  objlist.append(obj)
    objects = DbConn.get_db(objklass.__name__).find(filter)
    for obj in objects:
      objlist.append(obj)
    objlist = json.dumps(objlist, default=json_util.default)
    return Response(body=objlist,content_type = "application/json")


#@view_config(name='mf_show', route_name='mf_show', renderer='json', request_method='GET')
def mf_show(request):
    '''Returns a JSON object defined in the route
    If object has a function "my()", then the function is called to get a
    filter on the request

    :param request: HTTP params
    :type request: IMultiDict
    :return: json - Object from database
    '''
    objname = request.matchdict['objname']
    filter = mf_filter(objname, MF_MANAGE)
    try:
      filter["_id"] = ObjectId(request.matchdict['id'])
    except Exception as e:
      raise HTTPNotFound()
    objlist = []
    objklass = None
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    collection = DbConn.get_db(objklass.__name__)
    obj= collection.find_one(filter)
    if not obj:
      raise HTTPNotFound()
    response = { 'object' :  objname, 'status': 'list', objname : obj, 'filter' : filter }
    response = json.dumps(response, default=json_util.default)
    return Response(body=response,content_type = "application/json")

#@view_config(name='mf_edit', route_name='mf_edit', renderer='json', request_method='POST', context='mf.dashboard.Dashboard', permission='all')
def mf_edit(request):
    '''Update an object in database

    :param request: HTTP params
    :type request: IMultiDict
    :return: json - Status of update and updated object
    '''
    objname = request.matchdict['objname']
    filter = mf_filter(objname, MF_MANAGE)
    filter["_id"] = ObjectId(request.matchdict['id'])
    objlist = []

    objklass = None
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    collection = DbConn.get_db(objklass.__name__)

    status = 0
    obj= collection.find_one(filter)
    if obj:
      err = obj.bind_form(sorted(request.params.items()))
    else:
      status = 1
    if err:
      status = 1
    if status == 0:
      try:
        obj.save()
      except Exception as e:
        logging.error("Error while saving object "+str(e))
        status = 1
    response = json.dumps({ 'status' : status, 'error' : err, 'message' : '', 'object' : obj }, default=json_util.default)
    return Response(body = response,content_type = "application/json")

#@view_config(name='mf_delete', route_name='mf_delete', renderer='json', request_method='DELETE', context='mf.dashboard.Dashboard', permission='all')
def mf_delete(request):
    '''Delete an object 
    If object has a function "my()", then the function is called to get a
    filter on the request

    :param request: HTTP params
    :type request: IMultiDict
    :return: json - Status fo the operation
    '''
    objname = request.matchdict['objname']
    filter = mf_filter(objname, MF_MANAGE)
    filter["_id"] = ObjectId(request.matchdict['id'])
    objlist = []

    objklass = None
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    collection = DbConn.get_db(objklass.__name__)

    #collection = Annotation.db_conn[pluralize(objname)]
    #obj = collection.remove(filter)
    obj = collection.find_one(filter)
    obj.delete()
    response = json.dumps({ 'status' : 0, 'error' : [], 'message' : 'Object deleted' }, default=json_util.default)
    return Response(body = response,content_type = "application/json")

#@view_config(name='mf_add', route_name='mf_add', renderer='json', request_method='PUT', context='mf.dashboard.Dashboard', permission='all')
def mf_add(request):
    objklass = None
    objname = request.matchdict['objname']
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == pluralize(objname):
        objklass = klass
        break
    if objklass is None:
      response = json.dumps({ 'status' : 1, 'error' : [], 'message' : 'Object does not exist' }, default=json_util.default)
      return Response(body = response,content_type = "application/json")
    collection = DbConn.get_db(objklass.__name__)
    obj = collection()
    err = obj.bind_form(sorted(request.params.items()))
    status = 0
    if err:
      status = 1
    else:
      obj.save()
    response = json.dumps({ 'status' : status, 'error' : err, 'message' : '' }, default=json_util.default)
    return Response(body = response, content_type = "application/json")

#@view_config(name='mf_admin', route_name='mf_admin', renderer='dashboard.mako', context='mf.dashboard.Dashboard', permission='all')
def mf_admin(request):
    objects = []
    for klass in Annotation.klasses():
      objects.append(klass.__name__)
    return {'objects':objects, 'klasses': Annotation.klasses(), 'prefix': FormRenderer.prefix }

