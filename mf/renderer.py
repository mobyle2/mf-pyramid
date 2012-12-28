
from datetime import datetime
from ming import Field,schema
import time
import re
import string
import logging


#logging.basicConfig(level=logging.DEBUG)

class AbstractRenderer:
  '''
  Base class for all renderers
  '''
  klass = None
  name = None
  rootklass = None
  err = False

  is_object_id = False


  def controls(self):
    '''Return buttons for the form

    :returns: str - HTML for buttons
    '''
    return _htmlControls(self.klass)

  def __init__(self,klass,name):
    self.name = name
    self.rootklass = klass
    self.klass = klass.__name__
    self.err = False

  def render(self,value = None, parent = None):
    '''Return HTML for component

    Not implemented
    '''

    raise Exception("Not implemented")


  def render_search(self,value = None):
    '''Return HTML for search component

    Not implemented
    '''

    raise Exception("Not implemented")

  def unserialize(self,value):
    '''Return a value from input string

    :param value: Value from the form request
    :type value: str
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
    #if not request.has_key(instance.__class__.__name__+parentname+"["+name+"]"):
    #   return []
    paramlist = []
    #paramvalue = self.get_param(request,instance.__class__.__name__+parentname+"["+name+"]",True)
    #if paramvalue is None or paramvalue == '':
    #  return []
    # Search for array items
    while self.get_param(request,instance.__class__.__name__+parentname+"["+name+"]"):
      paramlist.append(self.get_param(request,instance.__class__.__name__+parentname+"["+name+"]",True))

    #if not paramlist:
    #  return []

    value = []
    try:
      for paramvalue in paramlist:
        value.append(self.unserialize(paramvalue))
    except Exception as e:
      self.err = True
      if parent is not None:
       error = ''
       for p in parent:
         error += p+"."
      error+= name
      return [error]
    if value is not None:
      if parent:
        obj = instance
        for p in parent:
          if isinstance(obj,dict):
            if p in obj:
              obj = obj[p]
            else:
              obj[p] = {}
              obj = obj[p]
          else:
            obj = getattr(obj,p)
        if isinstance(obj,dict) and value:
          obj[name]=value
        else:
          if isinstance(obj,(list,tuple)):
            setattr(obj,name,value)
          else:
            if value:
              setattr(obj,name,value[0])
        
      else:
        if isinstance(getattr(instance,name),(list,tuple)):
          print name+"it is a list"
          setattr(instance,name,value)
        elif value:
          print name+"it is not a list"
          setattr(instance,name,value[0])
    return []


  def get_param(self,request,name,delete = False):
    ''' Get the first value from request parameter
    and remove it from array

    :param request: HTML request object
    :type request: array
    :param name: parameter to search
    :type name: str
    :return: str - Value from the form
    '''
    for index in range(len(request)):
      key,value = request[index]
      if key == name:
        if delete:
          request.pop(index)
        return str(value)
    return None

class SearchFormRenderer(AbstractRenderer):
  ''' Render a search form with fields
  '''

  prefix = ''

  def render(self,klass,fields):
    '''Render the HTML for the search form

    :param klass: instance object to render
    :type klass: object
    :param fields: optional list of fields to display
    :type fields: list
    :return: str HTML form
    '''
    html='<h2>Search</h2><form class="mf-form form-horizontal" id="mf-search-form-'+klass.__class__.__name__+'">'
    for name in fields:
        value = getattr(klass,name)
        logging.debug("Render "+name+" for class "+klass.__class__.__name__)
        renderer = klass.get_renderer(name)
        html += renderer.render_search(value)
    html += '<div class="form-actions mf-actions"><button id="mf-search-'+name+'" class="mf-btn btn btn-primary">Search</button></div>'
    html += '</form>'
    return html


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
    html='<form class="mf-form form-horizontal" id="mf-form-'+klass.__class__.__name__+'">'
    for name in fields:
        value = getattr(klass,name)
        logging.debug("Render "+name+" for class "+klass.__class__.__name__)
        html += klass.get_renderer(name).render(value)
    html += self.controls()
    html += '</form>'
    return html


class TextRenderer(AbstractRenderer):
  '''Renderer for Text inputs
  '''

  def render_search(self, value = None):
    return _htmlTextField(self.klass+'['+self.name+']',self.name,'')    

  def render(self,value = None, parent = None):
    parentname = ''
    if value is None or isinstance(value,Field):
      value = ''
    if parent:
      parentname = parent
    return _htmlTextField(self.klass+parentname+'['+self.name+']',self.name,value,self.err)


  def validate(self,value):
    return isinstance(value,basestring)

  def unserialize(self,value):
    if self.validate(value):
      return value
    else:
      raise Exception("value is not correct type")


class BooleanRenderer(AbstractRenderer):
  '''Renderer for booleans
  '''

  def render_search(self, value = None):
    return _htmlCheckBox(self.klass+'['+self.name+']',self.name,False) 

  def render(self,value = False, parent = None):
     if value is None or isinstance(value,Field):
       value = False
     parentname = ''
     if parent:
       parentname = parent
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

  def render_search(self, value = None):
    return _htmlNumber(self.klass+'['+self.name+']',self.name,'') 

  def render(self,value = None, parent = None):
    if value is None or isinstance(value,Field):
      value = 0
    parentname = ''
    if parent:
      parentname = parent
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

  def render_search(self, value = None):
    return '' 

  def render(self,value = None, parent = None):
    if value is None or isinstance(value,Field):
      value = ''
    parentname = ''
    if parent:
      parentname = parent
    return _htmlHidden(self.klass+parentname+'['+self.name+']',self.name,value)


class DateTimeRenderer(AbstractRenderer):
  '''Renderer for date/time inputs
  '''

  # datetime, date, time
  type = 'datetime'

  def render(self,value = None, parent= None):
    parentname = ''
    if parent:
      parentname = parent

    if value is None or isinstance(value,Field):
      strvalue = ''
    else:
      strvalue = ''
      if self.type == 'datetime':
        strvalue = value.strftime('%y/%m/%d %H:%M:%s')
      elif self.type == 'date':
        strvalue = value.strftime("%d/%m/%y")
      elif self.type == 'time':
        strvalue = value.strftime('%H:%M:%s')
    return _htmlDateTime(self.klass+parentname+'['+self.name+']',self.name,strvalue,self.err, self.type)

  def render_search(self, value = None):
    return _htmlDateTime(self.klass+'['+self.name+']',self.name,'','',self.type) 

  def unserialize(self,value):
      try:
        if type == 'datetime':
          #return parseDateTime(value)
	  return datetime.strptime(value,'%y/%m/%d %H:%M:%s')
        elif type == 'date':
          return datetime.date.strptime(value,"%d/%m/%y")
        elif type == 'time':
          return datetime.time.strptime(value,"%H:%M:%S")
      except Exception as e:
        raise Exception('badly formatted date')  
      #raise Exception("not yet implemented")

class ArrayRenderer(AbstractRenderer):
  '''Renderer for lists of renderers
  '''
  # Renderer to use for array elements, must be of the same type
  _renderer = None

  def render_search(self, value = None):
    if len(value)>0:
      renderer = self.rootklass.renderer(self.rootklass,self.name,value[0])
      return renderer.render_search(value[0])
    else:
      return _htmlTextField(self.klass+'['+self.name+']',self.name,'') 

  def render(self,value=None,parent = None):
    parentname = ''
    if parent:
      parentname = parent
    html = '<div class="mf-array"><span class="mf-composite-label">'+self.name.title()+' list</span>'
    for i in range(len(value)):
      logging.debug("set array renderer "+self.name)
      renderer = self.rootklass.renderer(self.rootklass,self.name,value[i])
      logging.debug("renderer = "+str(renderer))
      self._renderer =  renderer
      val = value[i]
      elt = self.klass+parentname+'['+self.name+']'
      elt = elt.replace('[','\\[')
      elt = elt.replace(']','\\]')
      html += '<div class="mf-array-elt control-group">'
      html += renderer.render(val,parentname)
      html += '<button elt="'+elt+'" class="mf-del mf-btn btn btn-primary controls">Remove</button>'
      html += '</div>'
    html += '<button elt="'+elt+'" class="mf-add mf-btn btn btn-primary">Add</button>'
    html += '</div>'
    return html

  def bind(self,request,instance,name,parent = []):

    self.err = False
    errs = []
    err = self._renderer.bind(request,instance,self._renderer.name,parent)
    if err:
        errs.extend(err)
    return errs

  def unserialize(self,value):
    raise Exception("not yet implemented")

class CompositeRenderer(AbstractRenderer):
  '''Renderer for compisite inputs (objects within objects)
  '''


  _renderers = []

  def render_search(self, value = None):
    return ''

  def __init__(self,klass,name,attr):
    AbstractRenderer.__init__(self,klass,name)
    for obj  in attr:
      self._renderers.append(klass.renderer(klass,obj,attr[obj]))
  

  def render(self,value = None, parent = None):
    parentname = ''
    if parent:
      parentname = parent
    html = '<div class="mf-composite" id="'+self.klass+parentname+'['+self.name+']'+'"><span class="mf-composite-label">'+self.name+'</span>'
    for renderer in self._renderers:
      obj = None
      if isinstance(value,dict):
        obj = value[renderer.name]
      elif hasattr(value,renderer.name):
        obj = getattr(value,renderer.name)
      html += renderer.render(obj,parentname+'['+self.name+']')
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
      parentname = parent
    return _htmlNumber(self.klass+parentname+'['+self.name+']',self.name,value,self.err)

  def render_search(self, value = None):
    return _htmlNumber(self.klass+'['+self.name+']',self.name,'') 

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
  return '<div class="mf-field mf-textfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="text" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlDateTime(id,name,value,error = False, type = 'datetime'):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-datetime control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="'+type+'" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlHidden(id,name,value):
  return '<div class="mf-field mf-textfield control-group"><div class="controls"><input type="hidden" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlCheckBox(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  checked = ''
  if value:
     checked = 'checked'
  return '<div class="mf-field mf-checkbox control-group '+errorClass+'"><div class="controls"><label class="checkbox"><input type="checkbox" value="'+str(value)+'" id="'+id+'" name="'+id+'" '+checked+'>'+name+'</label></div></div>'
 
def _htmlNumber(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-numberfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input type="number" id="'+id+'" name="'+id+'" value="'+str(value)+'"/></div></div>'


def _htmlControls(name):
  return '<div class="form-actions mf-actions"><button id="mf-save-'+name+'" class="mf-btn btn btn-primary">Save</button><button id=mf-clear-'+name+'" class="mf-btn btn btn-primary">Clear</button><button id=mf-delete-'+name+'" class="mf-btn btn btn-danger">Delete</button></div>'


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

  Where ssssss represents fractional seconds. The timezone
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

