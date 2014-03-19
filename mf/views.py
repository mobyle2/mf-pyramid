from __future__ import absolute_import
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from mf.annotation import Annotation
from mf.renderer import FormRenderer, CompositeRenderer, FloatRenderer
from mf.renderer import IntegerRenderer, BooleanRenderer, ReferenceRenderer
from mf.renderer import SimpleReferenceRenderer
import logging

import json
from bson import json_util
from bson.objectid import ObjectId
#from bson.dbref import DBRef

from mf.db_conn import DbConn

MF_READ = 'read'
MF_EDIT = 'edit'


def pluralize(name):
    '''Pluralize a name
    :param name: Name of the object
    :type name: str
    :return: str - lowercase object name with a final s
    '''
    return name.lower() + "s"


def mf_filter(objname, control, request=None):
    '''Return a mongo filter on object. It calls, if exists,
    the *my* method of the current object and returns the filter
    obtained from this method.
    :param objname: Name of the current object
    :type objname: str
    :param control: Type of operation
    :type control: MF_READ or MF_EDIT
    :param request: Current request
    :type request: pyramid.request
    :return: filter to use (dict)
    '''
    objklass = None
    for klass in Annotation.klasses():
        if pluralize(klass.__name__) == pluralize(objname):
            objklass = klass
            break
    if objklass is None:
        return {}
    attr = None
    id_to_load = None
    #if request.matchdict.has_key('id'):
    if 'id' in request.matchdict:
        id_to_load = request.matchdict['id']
    if id_to_load is not None:
        try:
            collection = DbConn.get_db(objklass.__name__)
            if objklass.__field_search_by is not '_id':
                renderer = klass.render_fields[klass.__field_search_by]
                id_to_load = renderer.unserialize(id_to_load)
                my_object_instance = collection.find_one(
                                    {objklass.__field_search_by: id_to_load})
            else:
                my_object_instance = collection.find_one(
                                    {'_id': ObjectId(id_to_load)})
        except:
            raise HTTPNotFound()
    else:
        my_object_instance = objklass()

    if hasattr(my_object_instance, 'my'):
        attr = getattr(my_object_instance, 'my')
    mffilter = {}
    if attr is not None and callable(attr):
        if request is not None:
            userid = authenticated_userid(request)
        else:
            userid = None
        mffilter = attr(control, request, userid)
    return mffilter

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
        #response = json.dumps({'status': 1, 'error': [], 'message': 'Object does not exist'}, default=json_util.default)
        #return Response(body=response, content_type="application/json")
        return {'status': 1, 'error': [], 'message': 'Object does not exist'}
    mffilter = mf_filter(objname, MF_READ, request)
    if mffilter is None:
        raise HTTPForbidden

    for field in objklass.render_fields:
        try:
            param = request.params.getone('Search' + objklass.__name__ + '[' + field + ']')
        except Exception:
            # This is fine
            param = None
        renderer = objklass().get_renderer(field)
        #if isinstance(renderer,BooleanRenderer) and param is None:
        #  param = False
        if param is not None and param != '':
            if renderer and not isinstance(renderer, CompositeRenderer):

                if isinstance(renderer, ReferenceRenderer) and \
                    not isinstance(renderer, SimpleReferenceRenderer):
                    mffilter[field + '.$id'] = ObjectId(param)
                elif isinstance(renderer, IntegerRenderer):
                    mffilter[field] = int(param)
                elif isinstance(renderer, FloatRenderer):
                    mffilter[field] = float(param)
                elif isinstance(renderer, BooleanRenderer):
                    if param in ['True', 'true', '1']:
                        mffilter[field] = True
                    else:
                        mffilter[field] = False
                else:
                    if renderer.is_object_id:
                        mffilter[field] = ObjectId(param)
                    else:
                        mffilter[field] = {"$regex": param}
    logging.debug("search " + str(mffilter))
    objlist = []
    collection = DbConn.get_db(objklass.__name__).fetch(mffilter)
    if 'order' in request.params:
        collection = collection.sort(request.params.getone('order'), int(request.params.getone('order_type')))
    if 'page' in request.params and 'pagesize' in request.params:
        psize = int(request.params.getone('pagesize'))
        page = int(request.params.getone('page'))
        if page > 0:
            collection = collection.skip(page * psize).limit(psize)
        else:
            collection = collection.limit(psize)
    for obj in collection:
        objlist.append(obj)
    #objlist = json.dumps(objlist, default=json_util.default)
    #return Response(body=objlist, content_type="application/json")
    return objlist


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
    mffilter = mf_filter(objname, MF_READ, request)
    if mffilter is None:
        raise HTTPForbidden
    objlist = []
    objklass = None
    for klass in Annotation.klasses():
        if pluralize(klass.__name__) == pluralize(objname):
            objklass = klass
            break

    # Do we have a search parameter in the request ?
    for field in objklass.render_fields:
        try:
            param = request.params.getone('Search' + objklass.__name__ + '[' + field + ']')
        except Exception:
            # This is fine
            param = None
        if param is not None and param != '':
            # We search for specific objects
            return mf_search(request)

    # No search parameter, get the list

    objects = DbConn.get_db(objklass.__name__).fetch(mffilter)
    if 'order' in request.params:
        objects = objects.sort(request.params.getone('order'), int(request.params.getone('order_type')))
    if 'page' in request.params and 'pagesize' in request.params:
        psize = int(request.params.getone('pagesize'))
        page = int(request.params.getone('page'))
        if page > 0:
            objects = objects.skip(page * psize).limit(psize)
        else:
            objects = objects.limit(psize)
    for obj in objects:
        objlist.append(obj)
    #objlist = json.dumps(objlist, default=json_util.default)
    #return Response(body=objlist, content_type="application/json")
    return objlist


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
    mffilter = mf_filter(objname, MF_READ, request)
    if mffilter is None:
        raise HTTPForbidden

    #objlist = []
    objklass = None
    for klass in Annotation.klasses():
        if pluralize(klass.__name__) == pluralize(objname):
            objklass = klass
            break

    try:
        if objklass.__field_search_by is not '_id':
            renderer = klass.render_fields[klass.__field_search_by]
            id_to_load = renderer.unserialize(request.matchdict['id'])
            mffilter[klass.__field_search_by] = id_to_load
        else:
            mffilter["_id"] = ObjectId(request.matchdict['id'])
    except Exception:
        raise HTTPNotFound()

    collection = DbConn.get_db(objklass.__name__)
    obj = collection.find_one(mffilter)
    if not obj:
        raise HTTPNotFound()
    response = {'object': objname, 'status': 0, objname: obj, 'filter': mffilter}
    #response = json.dumps(response, default=json_util.default)
    #return Response(body=response, content_type="application/json")
    return response


#@view_config(name='mf_edit', route_name='mf_edit', renderer='json', request_method='POST', context='mf.dashboard.Dashboard', permission='all')
def mf_edit(request):
    '''Update an object in database

    :param request: HTTP params
    :type request: IMultiDict
    :return: json - Status of update and updated object
    '''
    objname = request.matchdict['objname']
    mffilter = mf_filter(objname, MF_EDIT, request)
    if mffilter is None:
            raise HTTPForbidden

    #objlist = []

    objklass = None
    for klass in Annotation.klasses():
        if pluralize(klass.__name__) == pluralize(objname):
            objklass = klass
            break
    collection = DbConn.get_db(objklass.__name__)

    try:
        if objklass.__field_search_by is not '_id':
            renderer = klass.render_fields[klass.__field_search_by]
            id_to_load = renderer.unserialize(request.matchdict['id'])
            mffilter[klass.__field_search_by] = id_to_load
        else:
            mffilter["_id"] = ObjectId(request.matchdict['id'])
    except Exception:
        raise HTTPNotFound()

    status = 0
    err = None
    obj = collection.find_one(mffilter)
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
            logging.error("Error while saving object " + str(e))
            status = 1
    #response = json.dumps({'status': status, 'error': err,
    #                        objname: obj, 'object': objname,
    #                        'message': ''},
    #                        default=json_util.default)
    response = {'status': status, 'error': err,
                objname: obj, 'object': objname,
                'message': ''}

    #return Response(body=response, content_type="application/json")
    return response


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
    mffilter = mf_filter(objname, MF_EDIT, request)
    if mffilter is None:
            raise HTTPForbidden

    #objlist = []

    objklass = None
    for klass in Annotation.klasses():
        if pluralize(klass.__name__) == pluralize(objname):
            objklass = klass
            break

    try:
        if objklass.__field_search_by is not '_id':
            renderer = klass.render_fields[klass.__field_search_by]
            id_to_load = renderer.unserialize(request.matchdict['id'])
            mffilter[klass.__field_search_by] = id_to_load
        else:
            mffilter["_id"] = ObjectId(request.matchdict['id'])
    except Exception:
        raise HTTPNotFound()

    collection = DbConn.get_db(objklass.__name__)
    obj = collection.find_one(mffilter)
    if obj is None:
        raise HTTPNotFound()
    obj.delete()
    #response = json.dumps({'status': 0, 'error': [], 'message': 'Object deleted'}, default=json_util.default)
    response = {'status': 0, 'error': [], 'message': 'Object deleted'}
    #return Response(body=response, content_type="application/json")
    return response


#@view_config(name='mf_add', route_name='mf_add', renderer='json', request_method='PUT', context='mf.dashboard.Dashboard', permission='all')
def mf_add(request):
    objklass = None
    objname = request.matchdict['objname']
    for klass in Annotation.klasses():
        if pluralize(klass. __name__) == pluralize(objname):
            objklass = klass
            break
    if objklass is None:
        #response = json.dumps({'status': 1, 'error': [], 'message': 'Object does not exist'}, default=json_util.default)
        #return Response(body=response, content_type="application/json")
        return {'status': 1, 'error': [], 'message': 'Object does not exist'}
    collection = DbConn.get_db(objklass.__name__)
    obj = collection()
    err = obj.bind_form(sorted(request.params.items()))
    status = 0
    if err:
        status = 1
    else:
        obj.save()
    #response = json.dumps({'status': status, 'error': err,
    #                        objname: obj, 'object': objname,
    #                        'message': ''},
    #                        default=json_util.default)
    response = {'status': status, 'error': err,
                objname: obj, 'object': objname,
                'message': ''}

    #return Response(body=response, content_type="application/json")
    return response


#@view_config(name='mf_admin', route_name='mf_admin', renderer='dashboard.mako', context='mf.dashboard.Dashboard', permission='all')
def mf_admin(request):
    objects = []
    for klass in Annotation.klasses():
        objects.append(klass.__name__)
    return {'objects': objects, 'klasses': Annotation.klasses(), 'prefix': FormRenderer.prefix}

