# TODO manage lists, dict
# rendercomposite, how to get value for sub object?

from datetime import datetime
import logging

class AbstractRenderer:

  klass = None
  name = None

  def __init__(self,klass,name):
    self.name = name
    self.klass = klass.__name__

  def render(self,value = None, parent = None):
    raise Exception("Not implemented")

  def unserialize(self,value):
    raise Exception("Not implemented")

  def validate(self,attr):
    print "validate "+str(self)

  def bind(self,request,instance,name,parent = []):
    parentname = ''
    if parent is not None:
      for p in parent:
        parentname += "["+p+"]"
    if not request.has_key(instance.__class__.__name__+parentname+"["+name+"]"):
       return []
    value = None
    try:
      value = self.unserialize(request[instance.__class__.__name__+parentname+"["+name+"]"])
    except Exception as e:
      return [name]
    if value is not None:
      if parent:
        obj = instance
        for p in parent:
          obj = getattr(obj,p)
        setattr(obj,name,value)
        
      else:
        setattr(instance,name,value)

class TextRenderer(AbstractRenderer):

  def render(self,value = None, parent = None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return '<label>'+self.name.title()+'</label><input id="'+self.klass+parentname+'['+self.name+']" name="'+self.klass+parentname+'['+self.name+']"   value="'+(str(value or ''))+'"/>'


  def validate(self,value):
    return isinstance(value,str)

  def unserialize(self,value):
    if self.validate(value):
      return value
    else:
      raise Exception("value is not correct type")


class BooleanRenderer(AbstractRenderer):

  def render(self,value = False, parent = None):
     parentname = ''
     if parent:
       parentname = '['+parent+']'
     html= '<input type="checkbox" id="'+self.klass+parentname+'['+self.name+']" name="'+self.klass+parentname+'['+self.name+']" value="'+str(value)+'"'
     if value == True:
       html += ' checked'
     html += '/> '+self.name.title()+'<br>'
     return html

  def validate(self,value):
    if isinstance(value,bool):
      return True
    if isinstance(value,int):
      if value ==1 or value == 0:
        return True
      else:
        return False
    elif str(value).lower() == 'true' or str(value).lower() == 'false':
      return True
    else:
      return False

  def unserialize(self,value):
    if self.validate(value):
      if isinstance(value,bool):
        return value
      if isinstance(value,int):
        if value == 0:
          return False
        elif value == 1:
          return True
      else:
        if str(value).lower == 'false':
          return False
        elif str(value).lower == 'true':
          return True
    else:
      raise Exception("value is not correct type")

class IntegerRenderer(AbstractRenderer):

  def render(self,value = 0, parent = None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return '<label>'+self.name.title()+'</label><input id="'+self.klass+parentname+'['+self.name+']" "'+self.klass+parentname+'['+self.name+']" value="'+str(value)+'"/>'

  def validate(self,value):
    intvalue = 0
    try:
      intvalue = int(value)
    except Exception as e:
      return False
    return True

  def unserialize(self,value):
    if self.validate(value):
      return int(value)
    else:
      raise Exception("value is not correct type")

class HiddenRenderer(TextRenderer):

  def render(self,value = None, parent = None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return '<input type="hidden" id="'+self.klass+parentname+'['+self.name+']" "'+self.klass+parentname+'['+self.name+']" value="'+str(value or '')+'"/>'


class DateTimeRenderer(AbstractRenderer):

  def render(self,value = datetime.now(), parent= None):
    raise Exception("not yet implemented")

class ArrayRenderer(AbstractRenderer):

  def render(self,value = None, parent = None):
    raise Exception("not yet implemented")

class CompositeRenderer(AbstractRenderer):

  _renderers = []

  def __init__(self,klass,name,attr):
    AbstractRenderer.__init__(self,klass,name)
    for obj  in attr:
      self._renderers.append(klass.field_renderer(klass,obj,attr[obj]))
  

  def render(self,value = None, parent = None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    html = '<div class="composite" id="'+self.klass+parentname+'['+self.name+']">'
    for renderer in self._renderers:
      obj = None
      if hasattr(value,renderer.name):
        obj = getattr(value,renderer.name)
      html += renderer.render(obj,self.name)
    html += '</div>'
    return html

  def bind(self,request,instance,name,parent = []):
    parent.extend([name])
    errs = []
    for renderer in self._renderers:
      value = None
      obj = getattr(instance,name)
      print "##DEBUG "+name+": "+str(obj)
      err = renderer.bind(request,instance,renderer.name,parent)
      if err:
        errs.extend(err)
    return errs

  def unserialize(self,value):
    raise Exception("not yet implemented")

class FloatRenderer(AbstractRenderer):

  def render(self,value = 0, parent = None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return '<label>'+self.name.title()+'</label><input id="'+self.klass+parentname+'['+self.name+']" "'+self.klass+parentname+'['+self.name+']" value="'+str(value)+'"/>'

  def validate(self,value):
    intvalue = 0
    try:
      intvalue = float(value)
    except Exception as e:
      return False
    return True

  def unserialize(self,value):
    if self.validate(value):
      return float(value)
    else:
      raise Exception("value is not correct type")


