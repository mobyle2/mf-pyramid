from pyramid.view import view_config
from pyramid.response import Response

view_config(name='mf_list', route_name='mf_list', renderer='dashboard_list.mako')
def mf_list(request):
    return {'status': 'list'}


view_config(name='mf_edit', route_name='mf_edit', renderer='dashboard_edit.mako')
def mf_edit(request):
    return {'status':'edit'}

