
import annotation
from annotation import Annotation
from renderer import FormRenderer

class Dashboard:
  ''' Manage administration dashboard for pyramid
  '''

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
      #if config is not None:
      #  config.add_route(klass.__name__+"s",prefix+"/"+klass.__name__+"s")
      #  config.add_view('mf.views.view_'+klass.__name__+"s",name='view_'+klass.__name__+"s",route_name=klass.__name__+"s",renderer="dashboard_list.mako")
      #  config.add_route(klass.__name__,prefix+"/"+klass.__name__+"s/{id}")
      #  config.add_view('mf.views.view_'+klass.__name__,name='view_'+klass.__name__,route_name=klass.__name__+"s",renderer="dashboard_edit.mako")
    if config is not None:
      config.add_route('mf_list',prefix+'/'+{objname}+'s/')
      config.add_route('mf_add',prefix+'/'+{objname}+'s/')
      config.add_route('mf_show',prefix+'/'+{objname}+'s/'+{id})
      config.add_route('mf_delete',prefix+'/'+{objname}+'s/'+{id})
      config.add_route('mf_edit',prefix+'/'+{objname}+'s/'+{id})
      config.add_route('mf_admin',prefix/'/admin')
      config.scan('mf.views')

