from pyramid.view import view_config
from pyramid.response import Response
from mf.annotation import Annotation
#from mf.dashboard import Dashboard

import json
from bson import json_util
from bson.objectid import ObjectId

def pluralize(name):
  '''Pluralize a name
  :param name: Name of the object
  :type name: str
  :return: str - lowercase object name with a final s
  '''
  return name.lower()+"s"

def mf_filter(objname):
    '''Return a mongo filter on object
    '''
    objklass = None
    for klass in Annotation.klasses():
      if pluralize(klass.__name__) == objname:
        objklass = klass
        break
    if objklass is None:
      return {}
    attr = None
    if hasattr(objklass(),'my'):
      attr = getattr(objklass(),'my')
    filter = {}
    if attr is not None and callable(attr):
        filter = klass().attr()
    return filter

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
    filter = mf_filter(objname)
    objlist = []
    collection = Annotation.db_conn[pluralize(objname)]
    for obj in collection.find(filter):
      objlist.append(obj)
    response = { 'object' :  objname, 'status': 'list', objname : objlist }
    objlist = json.dumps(objlist, default=json_util.default)
    return Response(body=objlist,content_type = "application/json")


#@view_config(name='mf_show', route_name='mf_show', renderer='json', request_method='GET')
def mf_show(request):
    objname = request.matchdict['objname']
    filter = mf_filter(objname)
    filter["_id"] = ObjectId(request.matchdict['id'])
    objlist = []
    collection = Annotation.db_conn[pluralize(objname)]
    obj= collection.find_one(filter)
    response = { 'object' :  objname, 'status': 'list', objname : obj, 'filter' : filter }
    response = json.dumps(response, default=json_util.default)
    return Response(body=response,content_type = "application/json")

#@view_config(name='mf_edit', route_name='mf_edit', renderer='json', request_method='POST', context='mf.dashboard.Dashboard', permission='all')
def mf_edit(request):
    return {'status':'edit'}

#@view_config(name='mf_delete', route_name='mf_delete', renderer='json', request_method='DELETE', context='mf.dashboard.Dashboard', permission='all')
def mf_delete(request):
    return {'status':'delete'}

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
    
    err = objklass().bind_form(request.params.items())
    status = 0
    if err:
      status = 1
    response = json.dumps({ 'status' : status, 'error' : err, 'message' : '' }, default=json_util.default)
    return Response(body = response, content_type = "application/json")

#@view_config(name='mf_admin', route_name='mf_admin', renderer='dashboard.mako', context='mf.dashboard.Dashboard', permission='all')
def mf_admin(request):
    objects = []
    for klass in Annotation.klasses():
      objects.append(klass.__name__)
    return {'objects':objects, 'klasses': Annotation.klasses()}

