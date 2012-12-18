"""
.. module:: mf
   :synopsis: Mingflow annotations

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>


"""
import pprint
import logging
from datetime import datetime

from ming import Field,schema

import renderer
from renderer import *

import logging


class Annotation:
  '''
   Defines annotations and pyramid routes for an administration
   dashboard gneeration
  '''

  # Add static list of klass
  __klasses = []

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
     if attr_type == str:
         logging.debug(name+" is Field string ")
         return TextRenderer(klass,name)
     elif attr_type == int:
         logging.debug(name+" is Field integer")
         return IntegerRenderer(klass,name)
     elif attr_type == schema.ObjectId:
         logging.debug(name+" is Field ObjectId")
         return HiddenRenderer(klass,name)
     elif attr_type == bool:
         logging.debug(name+" is Field bool")
         return BooleanRenderer(klass,name)
     elif attr_type == datetime:
         logging.debug(name+" is Field datetime")
         return DateTimeRenderer(klass,name)
     elif isinstance(attr_type,dict):
         logging.debug(name+" is Field dict")
         return CompositeRenderer(klass,name,attr_type)         
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
     if isinstance(attr,str):
         logging.debug(name+" is string")
         return TextRenderer(klass,name)
     elif isinstance(attr,int):
         logging.debug(name+" is integer")
         return IntegerRenderer(klass,name)
     elif isinstance(attr,bool):
         logging.debug(name+" is bool")
         return BooleanRenderer(klass,name)
     elif isinstance(attr,datetime):
         logging.debug(name+" is datetime")
         return DateTimeRenderer(klass,name)
     elif isinstance(attr,Field):
         field = klass.field_renderer(klass,name,attr.type)
         return field
     else:
         raise Exception(attr.__class__.__name__+" is not a managed type")

def render(self,fields = None):
    """
    Render in HTML form an object
    param: fields List of fields to show
    type: list
    rparam: HTML form
    rtype: str
    """
    html=""
    attributes = dir(self)
    #for name in attributes:
    #    attr = getattr(self,name)
    #    if not callable(attr) and not name.startswith('__'):
    #        self.__render_fields[name] = self.renderer(name,attr)
    if not fields:
      fields = sorted(self.__class__.__render_fields)
    for name in fields:
        value = getattr(self,name)
        #if isinstance(value,Field):
          # not yet set and no default
          #value = None
        html += self.__class__.__render_fields[name].render(value)
    html += AbstractRenderer.controls()
    return html


def get_renderer(self,name):
    """
    Gets the renderer for an object attribute
    """
    return self.__class__.__render_fields[name]

def bind_form(self,request):
    """
    Binds a request dictionnary to the object
    """
    self.__field_errors = []
    for name in self.__class__.__render_fields:
        renderer = self.__class__.__render_fields[name]


        if isinstance(renderer,CompositeRenderer):
            err = renderer.bind(request,self,name)
            if err is not None:
              self.__field_errors.extend(err)            
        else:
          if self.__class__.__name__+"["+name+"]" in request:
            err = renderer.bind(request,self,name)
            if err is not None:
              self.__field_errors.extend(err)       


        #if self.__class__.__name__+"["+name+"]" in request:
          
          #err = renderer.bind(request,self,name)
          #if err is not None:
          #  self.__field_errors.append(err)



def mf_decorator(klass):
    klass.__field_errors = []
    klass.__render_fields = dict()
    original_methods = klass.__dict__.copy()
    #for name, method in original_methods.iteritems():
    #    if method is not None:
    #      print name+":"+str(method)
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

