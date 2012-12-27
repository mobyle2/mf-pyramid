
import pprint
import logging
import datetime
from datetime import datetime,date,time
from ming import Field,schema

#import renderer
from renderer import FormRenderer,TextRenderer, BooleanRenderer, CompositeRenderer, ArrayRenderer, IntegerRenderer, FloatRenderer, HiddenRenderer, DateTimeRenderer

import logging

#logging.basicConfig(level=logging.DEBUG)


class Annotation:
  '''
   Defines annotations and pyramid routes for an administration
   dashboard gneeration
  '''

  # Add static list of klass
  __klasses = []

  # static mongodb connection
  db_conn = None

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
def field_renderer(klass,name,attr_type):
     """
     Gets a renderer for Field type attributes

     :returns: AbstractRenderer -- Renderer for the attribute
     """
     if attr_type == str or attr_type is None:
         logging.debug(name+" is Field string ")
         return TextRenderer(klass,name)
     elif attr_type == schema.ObjectId:
         logging.debug(name+" is Field ObjectId")
         return HiddenRenderer(klass,name)
     elif attr_type == bool:
         logging.debug(name+" is Field bool")
         return BooleanRenderer(klass,name)
     elif attr_type == int:
         logging.debug(name+" is Field integer")
         return IntegerRenderer(klass,name)
     elif attr_type == datetime or attr_type == date or attr_type == time:
         logging.debug(name+" is Field datetime")
         renderer =  DateTimeRenderer(klass,name)
         renderer.type = attr_type.__name__
         return renderer
     elif isinstance(attr_type,dict):
         logging.debug(name+" is Field dict")
         return CompositeRenderer(klass,name,attr_type)
     elif isinstance(attr_type,list):
         logging.debug(name+" is Field array")
         return ArrayRenderer(klass,name)
     else:
         raise Exception(str(attr_type)+" is not a managed type")

@staticmethod
def renderer(klass,name,attr):
     """
     Gets a renderer for an attribute

     param: name of the attribute
     type: str
     param: attribute of the object
     type: object
     rparam: renderer for the attribute
     rtype: AbstractRenderer
     """
     if isinstance(attr,str) or attr == None or isinstance(attr,basestring):
         logging.debug(name+" is string")
         return TextRenderer(klass,name)
     elif isinstance(attr,bool):
         logging.debug(name+" is bool")
         return BooleanRenderer(klass,name)
     elif isinstance(attr,float):
         logging.debug(name+" is float")
         return FloatRenderer(klass,name)
     elif isinstance(attr,int):
         logging.debug(name+" is integer")
         return IntegerRenderer(klass,name)
     elif isinstance(attr,datetime) or type(attr) == date or type(attr)==time:
         logging.debug(name+" is "+attr.__class__.__name__)
         renderer =  DateTimeRenderer(klass,name)
         if type(attr) == date: 
           renderer.type = 'date'
         if type(attr) == time:
           renderer.type = 'time'
         return renderer
     elif isinstance(attr,list):
         logging.debug(name+" is array")
         renderer = ArrayRenderer(klass,name)
         renderer._renderer = renderer.rootklass.renderer(renderer.rootklass,renderer.name,attr[0])
         return renderer
     elif isinstance(attr,dict):
         logging.debug(name+" is dict")
         return CompositeRenderer(klass,name,attr)
     elif isinstance(attr,Field):
         field = klass.field_renderer(klass,name,attr.type)
         return field
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
      fields = sorted(self.__class__.__render_fields)
    form = FormRenderer(self.__class__,None)
    return form.render(self,fields)


def get_renderer(self,name):
    """
    Gets the renderer for an object attribute
    """
    return self.__class__.__render_fields[name]

def bind_form(self,request):
    """
    Binds a request dictionnary to the object

    :param request: request.params.items() in the form [ (key1,value1), (key1,value2), (key2,value1), ...]
    :type request: array
    """
    self.__field_errors = []
    for name in self.__class__.__render_fields:
        renderer = self.__class__.__render_fields[name]

        if isinstance(renderer,CompositeRenderer) or isinstance(renderer,ArrayRenderer):
            err = renderer.bind(request,self,name)
            if err is not None:
              self.__field_errors.extend(err)           
        else:
          #if self.__class__.__name__+"["+name+"]" in request:
          logging.debug("Search "+self.__class__.__name__+"["+name+"] in "+str(request))
          if renderer.get_param(request,self.__class__.__name__+"["+name+"]"):
            err = renderer.bind(request,self,name)
            if err is not None:
              self.__field_errors.extend(err)       
    return self.__field_errors


def mf_decorator(klass):
    '''
    Decorator used with annotations on an object class.
    It is used with the @mf_decorator declaration.
    '''
    klass.__field_errors = []
    klass.__render_fields = dict()
    original_methods = klass.__dict__.copy()
    setattr(klass, "bind_form", bind_form)
    setattr(klass, "render", render)
    setattr(klass, "renderer", renderer)
    setattr(klass, "get_renderer", get_renderer)
    setattr(klass, "field_renderer", field_renderer)
    attributes = dir(klass)
    for name in attributes:
        attr = getattr(klass,name)
        if not callable(attr) and not name.startswith('__'):
            klass.__render_fields[name] = klass.renderer(klass,name,attr)

    return klass

