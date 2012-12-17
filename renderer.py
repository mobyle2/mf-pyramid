# TODO manage lists
# TODO manage connections to other objects


from datetime import datetime
from ming import Field,schema

import logging

class AbstractRenderer:

  klass = None
  name = None

  err = False

  @staticmethod
  def controls():
    return _htmlControls()

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
    self.err = False
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
      self.err = True
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
    if value is None or isinstance(value,Field):
      value = ''
    if parent:
      parentname = '['+parent+']'
    return _htmlTextField(self.klass+parentname+'['+self.name+']',self.name,value,self.err)


  def validate(self,value):
    return isinstance(value,str)

  def unserialize(self,value):
    if self.validate(value):
      return value
    else:
      raise Exception("value is not correct type")


class BooleanRenderer(AbstractRenderer):

  def render(self,value = False, parent = None):
     if value is None or isinstance(value,Field):
       value = False
     parentname = ''
     if parent:
       parentname = '['+parent+']'
     html = _htmlCheckBox(self.klass+parentname+'['+self.name+']',self.name,value,self.err)
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

  def render(self,value = None, parent = None):
    if value is None or isinstance(value,Field):
      value = 0
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return _htmlNumber(self.klass+parentname+'['+self.name+']',self.name,value,self.err)

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
    if value is None or isinstance(value,Field):
      value = ''
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return _htmlHidden(self.klass+parentname+'['+self.name+']',self.name,value)


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
    html = '<div class="mf-composite" id="'+self.klass+parentname+'['+self.name+']"><h3>'+self.name+'</h3>'
    for renderer in self._renderers:
      obj = None
      if hasattr(value,renderer.name):
        obj = getattr(value,renderer.name)
      html += renderer.render(obj,self.name)
    html += '</div>'
    return html

  def bind(self,request,instance,name,parent = []):
    self.err = False
    parent.extend([name])
    errs = []
    for renderer in self._renderers:
      obj = getattr(instance,name)
      err = renderer.bind(request,instance,renderer.name,parent)
      if err:
        errs.extend(err)
    return errs

  def unserialize(self,value):
    raise Exception("not yet implemented")

class FloatRenderer(AbstractRenderer):

  def render(self,value = None, parent = None):
    if value is None or isinstance(value,Field):
      value = 0.0
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return _htmlNumber(self.klass+parentname+'['+self.name+']',self.name,value,self.err)

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



def _htmlTextField(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-textfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="text" id="'+id+'" name="'+id+']"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlHidden(id,name,value):
  return '<div class="mf-field mf-textfield control-group"><div class="controls"><input type="hidden" id="'+id+'" name="'+id+']"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlCheckBox(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  checked = ''
  if value:
     checked = 'checked'
  return '<div class="mf-field mf-checkbox control-group '+errorClass+'"><div class="controls"><label class="checkbox"><input type="checkbox" value="'+str(value)+' id="'+id+'" name="'+id+'" '+checked+'>'+name+'</label></div></div>'
 
def _htmlNumber(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-textfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="number" id="'+id+'" name="'+id+'" value="'+str(value)+'"/></div></div>'


def _htmlControls():
  return '<div class="form-actions mf-form"><button type="submit" class="btn btn-primary">Save</button></div>'
