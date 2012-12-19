from pyramid.view import view_config
from pyramid.response import Response

view_config(name='mf_list', route_name='mf_list', renderer='json', request_method='GET')
def mf_list(request):
     # TODO get klass from route  objname
     #attr = getattr(klass,'my')
     #   if attr is not None and callable(attr):
     #     filter = klass().attr()
    return {'status': 'list'}


view_config(name='mf_show', route_name='mf_show', renderer='json', request_method='GET')
def mf_show(request):
    return {'status':'show'}

view_config(name='mf_edit', route_name='mf_edit', renderer='json', request_method='POST', context='mf.dashboard.Dashboard', permission='all')
def mf_edit(request):
    return {'status':'edit'}

view_config(name='mf_delete', route_name='mf_delete', renderer='json', request_method='DELETE', context='mf.dashboard.Dashboard', permission='all')
def mf_delete(request):
    return {'status':'delete'}

view_config(name='mf_add', route_name='mf_add', renderer='json', request_method='PUT', context='mf.dashboard.Dashboard', permission='all')
def mf_add(request):
    return {'status':'add'}

view_config(name='mf_admin', route_name='mf_admin', renderer='dashboard.mako', context='mf.dashboard.Dashboard', permission='all')
def mf_admin(request):
    return {'status':'admin'}

