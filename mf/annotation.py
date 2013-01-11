
import pprint
import logging
import datetime
from datetime import datetime,date,time
import types
import inspect


#import renderer
from renderer import SearchFormRenderer, FormRenderer,TextRenderer, BooleanRenderer, CompositeRenderer, ArrayRenderer, IntegerRenderer, FloatRenderer, HiddenRenderer, DateTimeRenderer, ReferenceRenderer,AbstractRenderer

from mongokit.database import Database

#logging.basicConfig(level=logging.DEBUG)


class Annotation:
  '''
   Defines annotations and pyramid routes for an administration
   dashboard gneeration
  '''

  # Add static list of klass
  __klasses = []


  # use a schema variable like in mongokit ? specify it
  schema_variable = 'structure'

  @staticmethod
  def set_schema_variable(var):
    Annotation.schema_variable = var

  @staticmethod
  def use_schema_variable():
    return Annotation.schema_variable

  @staticmethod
  def addKlass(klass):
    """
    Adds a class to the admin dashboard

    :param klass: Class to manage
    :type klass: class
    """
    if klass not in Annotation.__klasses:
      Annotation.__klasses.append(klass)

  @staticmethod
  def klasses():
    return Annotation.__klasses

  @staticmethod
  def dump():
    """
    Print the classes managed in the dashboard
    """
    for item in Annotation.__klasses:
        print item


@staticmethod
def renderer(klass,name,attr,parent=''):
     """
     Gets a renderer for an attribute

     param: name of the attribute
     type: str
     param: attribute of the object
     type: object
     rparam: renderer for the attribute
     rtype: AbstractRenderer
     """
     if isinstance(attr,str) or attr == None or isinstance(attr,basestring) or attr == basestring:
         logging.debug(name+" is string")
         return TextRenderer(klass,name,parent)
     elif isinstance(attr,bool) or attr == bool:
         logging.debug(name+" is bool")
         return BooleanRenderer(klass,name,parent)
     elif isinstance(attr,float) or attr == float:
         logging.debug(name+" is float")
         return FloatRenderer(klass,name,parent)
     elif isinstance(attr,int) or attr == int:
         logging.debug(name+" is integer")
         return IntegerRenderer(klass,name,parent)
     elif isinstance(attr,datetime) or type(attr) == date or type(attr)==time or attr == datetime:
         logging.debug(name+" is "+attr.__class__.__name__)
         renderer =  DateTimeRenderer(klass,name,parent)
         if type(attr) == date: 
           renderer.type = 'date'
         if type(attr) == time:
           renderer.type = 'time'
         return renderer
     elif isinstance(attr,list):
         logging.debug(name+" is array")
         renderer = ArrayRenderer(klass,name,parent)
         renderer._renderer = renderer.rootklass.renderer(renderer.rootklass,renderer.name,attr[0])
         renderer.rootklass.render_fields[renderer.name] = renderer
         return renderer
     elif isinstance(attr,dict):
         logging.debug(name+" is dict")
         return CompositeRenderer(klass,name,attr,parent)
     elif inspect.isclass(attr):
         logging.debug(name+" is dbref")
         renderer = ReferenceRenderer(klass,name,attr,parent)
         return renderer
     else:
         raise Exception(name+", "+attr.__class__.__name__+" is not a managed type")

def render(self,fields = None):
    """
    Render in HTML form an object

    param: fields List of fields to show
    type: list
    rparam: HTML form
    rtype: str
    """
    if not fields:
      fields = sorted(self.__class__.render_fields)
    logging.debug(self.__class__.render_fields)
    form = FormRenderer(self.__class__,None)
    return form.render(self,fields)

def render_search(self, fields = None):
    """
    Render in HTML a search form an object

    param: fields List of fields to show, limited to first level of document
    type: list
    rparam: HTML form
    rtype: str
    """
    if not fields:
      fields = sorted(self.__class__.render_fields)
    form = SearchFormRenderer(self.__class__,None)
    return form.render(self,fields)

def get_renderer(self,name):
    """
    Gets the renderer for an object attribute
    """
    return self.__class__.render_fields[name]

def set_renderer(self,name,renderer):
    """
    Sets the renderer for an object attribute
    """
    self.__class__.render_fields[name] = renderer


def bind_form(self,request):
    """
    Binds a request dictionnary to the object

    :param request: request.params.items() in the form [ (key1,value1), (key1,value2), (key2,value1), ...]
    :type request: list
    :return: list of fields in error
    """
    self.__field_errors = []
    for name in self.__class__.render_fields:
        # Only first level fields, others are made recursivly
        if name is None or "." in name:
          continue
        renderer = self.__class__.render_fields[name]

        if isinstance(renderer,CompositeRenderer) or isinstance(renderer,ArrayRenderer):
            err = renderer.bind(request,self,name,[])
            if err is not None:
              self.__field_errors.extend(err)           
        else:
          #if self.__class__.__name__+"["+name+"]" in request:
          logging.debug("Search "+self.__class__.__name__+"["+name+"] in "+str(request))
          if renderer.get_param(request,self.__class__.__name__+"["+name+"]") or isinstance(renderer,BooleanRenderer):
            err = renderer.bind(request,self,name,[])
            if err is not None:
              self.__field_errors.extend(err)       
    return self.__field_errors


def mf_decorator(klass):
    '''
    Decorator used with annotations on an object class.
    It is used with the @mf_decorator declaration.
    '''
    klass.__field_errors = []
    klass.render_fields = dict()
    original_methods = klass.__dict__.copy()
    if not hasattr(klass,'bind_form'):
      setattr(klass, "bind_form", bind_form)
    if not hasattr(klass,'render'):
      setattr(klass, "render", render)
    if not hasattr(klass,'render_search'):
      setattr(klass, "render_search", render_search)
    setattr(klass, "renderer", renderer)
    setattr(klass, "get_renderer", get_renderer)
    setattr(klass, "set_renderer", set_renderer)

    attributes = dir(klass)
    if Annotation.use_schema_variable() is not None:
      schema_variable =  getattr(klass,Annotation.use_schema_variable())
      for name in schema_variable:
        attr = schema_variable[name]
        #klass.render_fields[name] = klass.renderer(klass,name,attr)
	r= klass.renderer(klass,name,attr)

    else:
      for name in attributes:
        attr = getattr(klass,name)
        if not callable(attr) and not name.startswith('__'):
          #klass.render_fields[name] = klass.renderer(klass,name,attr)
          klass.renderer(klass,name,attr)

    return klass


