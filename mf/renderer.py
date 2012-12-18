"""
.. module:: mf
   :synopsis: HTML renderers per object type

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>


"""

from datetime import datetime
from ming import Field,schema
import time
import re
import string
import logging

class AbstractRenderer:
  '''
  Base class for all renderers
  '''
  klass = None
  name = None

  err = False

  @staticmethod
  def controls():
    '''Return buttons for the form
    :returns: str - HTML for buttons
    '''
    return _htmlControls()

  def __init__(self,klass,name):
    self.name = name
    self.klass = klass.__name__

  def render(self,value = None, parent = None):
    '''Return HTML for component
    Not implemented
    '''

    raise Exception("Not implemented")

  def unserialize(self,value):
    '''Return a value from input string
    :param value: Value from the form request
    :type value: str
    according to original attribute type
    :returns: object - Value for the attribute
    '''

    raise Exception("Not implemented")

  def validate(self,attr):
    '''Checks that request form value is correct
     Not implemented
    '''
    raise Exception("Not implemented")

  def bind(self,request,instance,name,parent = []):
    '''Bind a request form parameter to the
     object instance attribute
    :param request: Form request list
    :type request: dict
    :param instance: Object instance to bind
    :type instance: object
    :param name: Parameter to bind
    :type name: str
    :param parent: list of parent attributes in case of composite renderer
    :type parent: list
    '''
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

class FormRenderer(AbstractRenderer):
  ''' Render a form with fields
  '''

  prefix = ''

  def render(self,klass,fields):
    '''Render the HTML for the form
    :param klass: instance object to render
    :type klass: object
    :param fields: optional list of fields to display
    :type fields: list
    :return: str HTML form
    '''
    html='<form class="mf-form form-horizontal" action="'+FormRenderer.prefix+'/'+(klass.__class__.__name__).lower()+'s/'+str(getattr(klass,"_id"))+'" type="POST">'
    for name in fields:
        value = getattr(klass,name)
        html += klass.get_renderer(name).render(value)
    html += AbstractRenderer.controls()
    html += '</form>'
    return html


class TextRenderer(AbstractRenderer):
  '''Renderer for Text inputs
  '''


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
  '''Renderer for booleans
  '''


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
  '''Renderer for integer inputs
  '''


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
  '''Renderer for hidden inputs such as ObjectIds
  '''


  def render(self,value = None, parent = None):
    if value is None or isinstance(value,Field):
      value = ''
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    return _htmlHidden(self.klass+parentname+'['+self.name+']',self.name,value)


class DateTimeRenderer(AbstractRenderer):
  '''Renderer for date/time inputs
  '''

  # datetime, date, time
  type = 'datetime'

  def render(self,value = None, parent= None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'

    if value is None or isinstance(value,Field):
      strvalue = ''
    else:
      strvalue = ''
      if type == 'datetime':
        strvalue = value.strftime('%y/%m/%d %H:%M:%s')
      elif type == 'date':
        strvalue = value.strftime("%d/%m/%y")
      elif type == 'time':
        strvalue = value.strftime('%H:%M:%s')
    return _htmlDateTime(self.klass+parentname+'['+self.name+']',self.name,strvalue,self.err, type)

  def unserialize(self,value):
      try:
        if type == 'datetime':
          #return parseDateTime(value)
	  return datetime.strptime(value,'%y/%m/%d %H:%M:%s')
        elif type == 'date':
          return datetime.date.strptime(value,"%Y-%m-%d")
        elif type == 'time':
          return datetime.time.strptime(value,"%H:%M:%S")
      except Exception as e:
        raise Exception('badly formatted date')  
      #raise Exception("not yet implemented")

class ArrayRenderer(AbstractRenderer):
  '''Renderer for lists of renderers
  '''
  _renderers = []

  def __init__(self,klass,name,attr):
    AbstractRenderer.__init__(self,klass,name)
    for obj in attr:
      self._renderers.append(klass.field_renderer(klass,name,attr[obj]))

  def render(self,value=None,parent = None):
    parentname = ''
    if parent:
      parentname = '['+parent+']'
    html = '<div class="mf-array">'
    for index in range(len(value)):
      renderer =  self._renderers[index]
      val = self.value[index]
      html += renderer.render(val,self.name,parent)
    html += '</div>'
    return html

  def bind(self,request,instance,name,parent = []):
    raise Exception("not yet implemented")
    # TODO how to get the nth element of the request name param?
    # request.params.getall returns a list, request.params.getone return a value 

    # elts of  array could be array of composite, need to know the entire request params
    # but should remove treatment elts
    # Add a clone of IMultiDict with remove possibility?

    # Or use request.items => [('pref', 'red'), ('pref', 'blue')] then manage array and search with an appropriate parser
  
    self.err = False
    errs = []    
    for renderer in self._renderers:
      err = renderer.bind(request,instance,renderer.name,parent)
      if err:
        errs.extend(err)
    return errs

  def unserialize(self,value):
    raise Exception("not yet implemented")

class CompositeRenderer(AbstractRenderer):
  '''Renderer for compisite inputs (objects within objects)
  '''


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
  '''Renderer for float inputs
  '''

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

def _htmlDateTime(id,name,value,error = False, type = 'datetime'):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-datetime control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="'+type+'" id="'+id+'" name="'+id+']"   value="'+(str(value or ''))+'"/></div></div>'

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
  return '<div class="mf-field mf-numberfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="number" id="'+id+'" name="'+id+'" value="'+str(value)+'"/></div></div>'


def _htmlControls():
  return '<div class="form-actions mf-actions"><button type="submit" class="btn btn-primary">Save</button></div>'


def parseDateTime(s):
  """Create datetime object representing date/time
     expressed in a string
 
  Takes a string in the format produced by calling str()
  on a python datetime object and returns a datetime
  instance that would produce that string.
 
  Acceptable formats are: "YYYY-MM-DD HH:MM:SS.ssssss+HH:MM",
              "YYYY-MM-DD HH:MM:SS.ssssss",
              "YYYY-MM-DD HH:MM:SS+HH:MM",
              "YYYY-MM-DD HH:MM:SS"
  Where ssssss represents fractional seconds.	 The timezone
  is optional and may be either positive or negative
  hours/minutes east of UTC.
  """
  if s is None:
    return None
  # Split string in the form 2007-06-18 19:39:25.3300-07:00
  # into its constituent date/time, microseconds, and
  # timezone fields where microseconds and timezone are
  # optional.
  m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$',
         str(s))
  datestr, fractional, tzname, tzhour, tzmin = m.groups()
 
  # Create tzinfo object representing the timezone
  # expressed in the input string.  The names we give
  # for the timezones are lame: they are just the offset
  # from UTC (as it appeared in the input string).  We
  # handle UTC specially since it is a very common case
  # and we know its name.
  if tzname is None:
    tz = None
  else:
    tzhour, tzmin = int(tzhour), int(tzmin)
    if tzhour == tzmin == 0:
      tzname = 'UTC'
    tz = FixedOffset(timedelta(hours=tzhour,
                   minutes=tzmin), tzname)
 
  # Convert the date/time field into a python datetime
  # object.
  x = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
 
  # Convert the fractional second portion into a count
  # of microseconds.
  if fractional is None:
    fractional = '0'
  fracpower = 6 - len(fractional)
  fractional = float(fractional) * (10 ** fracpower)
 
  # Return updated datetime object with microseconds and
  # timezone information.
  return x.replace(microsecond=int(fractional), tzinfo=tz)

