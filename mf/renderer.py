
from datetime import datetime
import time
import re
import string
import logging
from db_conn import DbConn
from bson.objectid import ObjectId
import re

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

  render_fields = dict()
  
  bind_only_one = False
  
  def add_extra_control(self,extra):
    '''Adds an additional button next to the element
    
    :param extra: HTML for the button
    :type extra: str
    '''
    self.extra_controls.append(extra)
  
  def get_extra_controls(self):
    ''' Get the HTML for the extra control elements (buttons)
    '''
    if not self.extra_controls:
      return ''
    html = '<div class="form-actions mf-extra-actions control-group">'
    for extra in self.extra_controls:
      html += extra
    html += '</div>'
    return html

  def controls(self):
    '''Return buttons for the form

    :returns: str - HTML for buttons
    '''
    return _htmlControls(self.klass)

  def __init__(self,klass,name,parent=''):
    self.name = name
    self.rootklass = klass
    self.klass = klass.__name__
    self.err = False
    
    self.bind_only_one = False
    self.count = 0
    self.reset = False
    self.in_array = False
    
    self.extra_controls = []
    
    fieldname = name
    if parent:
      fieldname = parent+"."+name
    if self.name != "_id":
      self.rootklass.render_fields[fieldname] = self


  def render(self,value = None, parents = []):
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

  def getObject(self,obj,parent):
    ''' Get attribute element from object according to its parent
    
    :param obj: Object instance
    :param type: object
    :param parent: list of parent attributes
    :type parent: list
    :return: object attribute
    '''
    for p in parent:
      if isinstance(obj,dict):
        if p in obj:
          obj = obj[p]
        else:
          obj[p] = {}
          obj = obj[p]
      else:
        if hasattr(obj,p):
          obj = getattr(obj,p)
        else:
          obj = obj[p]
    return obj

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

    paramlist = []

    # Search for array items
    logging.debug("## bind "+instance.__class__.__name__+parentname+"["+name+"]"+" with "+str(self.get_param(request,instance.__class__.__name__+parentname+"["+name+"]")))
    while self.get_param(request,instance.__class__.__name__+parentname+"["+name+"]") is not None:
      
      param = self.get_param(request,instance.__class__.__name__+parentname+"["+name+"]",True)
      #paramlist.append(param)
      if not self.in_array:
        paramlist.append(param)
      elif self.in_array and str(param) != '':
        paramlist.append(param)
      if self.bind_only_one and str(param) != '':
        break;
    #if not paramlist:
    #  return []
    value = []
    try:
      for paramvalue in paramlist:
        value.append(self.unserialize(paramvalue))
    except Exception as e:
      logging.error("Unserialize error "+str(e))
      self.err = True
      if parent is not None:
       error = ''
       for p in parent:
         error += p+"."
      error+= name
      return [error]


    # Unckecked boxes are not set, e.g. no value available. Default to False.
    if not value:
      if isinstance(self,BooleanRenderer):
        value = [False]
      else:
        return None
    
    if value:
      if parent:
        obj = self.getObject(instance,parent)
        if isinstance(obj,dict) and value:
          obj[name]=value[0]
        else:
          if isinstance(obj,(list,tuple)):
            if hasattr(obj,name):
              setattr(obj,name,value)
            else:
              # An array that contains Composite objects, fill only one element
              if self.bind_only_one:
                if self.reset :
                  del obj[:]
                  self.reset = False
                if len(obj)>self.count:
                  obj[self.count][name] = value[0]
                else:
                  obj.append({ name : value[0] })
              else:
                obj[name]=value
          else:
            if value:
              if hasattr(obj,name):
                setattr(obj,name,value[0])
              else:
                obj[name]=value[0] 
      else:
        instanceobj = None
        if hasattr(instance,name):
          instanceobj = getattr(instance,name)
        else:
          if name in instance:
            instanceobj = instance[name]
        if instanceobj is not None and isinstance(instanceobj,(list,tuple)):
          if hasattr(instance,name):
              setattr(instance,name,value)
          else:
              instance[name]=value
        elif value:
          if hasattr(instance,name):
              setattr(instance,name,value[0])
          else:
              instance[name]=value[0]
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
      rname = name.replace('[','\[')
      rname = rname.replace(']','\]')
      array_regexp = ''
      if self.in_array:
        array_regexp = '\[\d+\]'
      if re.compile(rname+array_regexp+'$').search(key):
      #if key == name:
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
    html='<form class="mf-form form-horizontal" id="mf-search-form-'+klass.__class__.__name__+'">'
    for name in fields:
        # First level fields only
        if name is None or "." in name:
          continue
        if name != '_id':
          if hasattr(klass,name):
            value = getattr(klass,name)

          else:
           value = klass[name]
          logging.debug("Render "+name+" for class "+klass.__class__.__name__)
          renderer = klass.get_renderer(name)
          html += renderer.render_search(value)
    html += '<div class="form-actions mf-actions"><button id="mf-search-'+klass.__class__.__name__+'" class="mf-btn btn btn-primary">Search</button><button class="mf-btn btn btn-primary" id="mf-search-clear-'+klass.__class__.__name__+'">Clear form</button></div>'
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

    if "_id" not in fields:
      logging.debug("Add default _id")
      html += HiddenRenderer(klass.__class__,"_id").render('')
    for name in fields:
        # First level fields only
        if name is None or "." in name:
          continue
        if not hasattr(klass,name):
          value = klass[name]
        else:
          value = getattr(klass,name)
        logging.debug("Render "+name+" for class "+klass.__class__.__name__)
        html += klass.get_renderer(name).render(value,[])
    html += self.controls()
    html += self.get_extra_controls()
    html += '</form>'
    return html


class TextRenderer(AbstractRenderer):
  '''Renderer for Text inputs
  '''

  def render_search(self, value = None):
    return _htmlTextField('Search'+self.klass+'['+self.name+']',self.name,'')    

  def render(self,value = None, parents = []):
    parentname = ''
    if value is None:
      value = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    return _htmlTextField(self.klass+parentname+'['+self.name+']',self.name,value,self.err) + self.get_extra_controls()


  def validate(self,value):
    return isinstance(value,basestring)

  def unserialize(self,value):
    if self.validate(value):
      return value
    else:
      raise Exception("value is not correct type")

class TextChoiceRenderer(TextRenderer):
  ''' Text renderer with dropdown list of choice
  '''
  choices = None

  def limit(self,choice_list=None):
    '''Set the values for this list
    
    :param choice_list: List of values to display in form
    :type choice_list: list
    '''
    if choice_list:
      self.choices = choice_list

  def validate(self,value):
    return value in self.choices

  def render_search(self, value = None):
    return _htmlChoiceTextField('Search'+self.klass+'['+self.name+']',self.name,'',self.choices)    

  def render(self,value = None, parents = []):
    parentname = ''
    if value is None:
      value = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    return _htmlChoiceTextField(self.klass+parentname+'['+self.name+']',self.name,value,self.choices,self.err) + self.get_extra_controls()  

class BooleanRenderer(AbstractRenderer):
  '''Renderer for booleans
  '''

  def render_search(self, value = None):
    #return _htmlCheckBox('Search'+self.klass+'['+self.name+']',self.name,False)
    return _htmlChoiceTextField('Search'+self.klass+'['+self.name+']',self.name,'', ["","true","false"])

  def render(self,value = False, parents = []):
     if value is None:
       value = False
     parentname = ''
     if parents:
      for parent in parents:
        parentname += '['+parent+']'
     #html = _htmlCheckBox(self.klass+parentname+'['+self.name+']',self.name,value,self.err)
     html = _htmlChoiceTextField(self.klass+parentname+'['+self.name+']',self.name,value, ["true","false"],self.err)
     return html + self.get_extra_controls()

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
        if str(value).lower() == 'false':
          return False
        elif str(value).lower() == 'true':
          return True
    else:
      raise Exception("value is not correct type")

class IntegerRenderer(AbstractRenderer):
  '''Renderer for integer inputs
  '''

  def render_search(self, value = None):
    return _htmlNumber('Search'+self.klass+'['+self.name+']',self.name,'') 

  def render(self,value = None, parents = []):
    if value is None:
      value = 0
    parentname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    return _htmlNumber(self.klass+parentname+'['+self.name+']',self.name,value,self.err) + self.get_extra_controls()

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

  def render(self,value = None, parents = []):
    if value is None:
      value = ''
    parentname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    return _htmlHidden(self.klass+parentname+'['+self.name+']',self.name,value) + self.get_extra_controls()


class DateTimeRenderer(AbstractRenderer):
  '''Renderer for date/time inputs
  '''

  # datetime, date, time
  type = 'datetime'

  def render(self,value = None, parents = []):
    parentname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'

    if value is None:
      strvalue = ''
    else:
      strvalue = ''
      if self.type == 'datetime':
        strvalue = value.strftime('%Y/%m/%d %H:%M:%S')
      elif self.type == 'date':
        strvalue = value.strftime("%d/%m/%Y")
      elif self.type == 'time':
        strvalue = value.strftime('%H:%M:%s')
    return _htmlDateTime(self.klass+parentname+'['+self.name+']',self.name,strvalue,self.err, self.type) + self.get_extra_controls()

  def render_search(self, value = None):
    return _htmlDateTime('Search'+self.klass+'['+self.name+']',self.name,'','',self.type) 

  def unserialize(self,value):
      try:
        if self.type == 'datetime':
	  return datetime.strptime(value,'%Y/%m/%d %H:%M:%S')
        elif self.type == 'date':
          return datetime.date.strptime(value,"%d/%m/%Y")
        elif self.type == 'time':
          return datetime.time.strptime(value,"%H:%M:%S")
      except Exception as e:
        raise Exception('badly formatted date')  
      #raise Exception("not yet implemented")

class ArrayRenderer(AbstractRenderer):
  '''Renderer for lists of renderers
  '''
  # Renderer to use for array elements, must be of the same type
  #_renderer = None


  def render_search(self, value = None):
    if len(value)>0:
      renderer = self.rootklass.renderer(self.rootklass,self.name,value[0])
      return renderer.render_search(value[0])
    else:
      return _htmlTextField('Search'+self.klass+'['+self.name+']',self.name,'') 

  def render(self,value=None, parents = []):
    parentname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    html = '<div class="mf-array"><span class="mf-composite-label">'+self.name.title()+' list</span>'

    elt = self.klass+parentname+'['+self.name+']'
    #elt = elt.replace('[','\\[')
    #elt = elt.replace(']','\\]')
    #if len(value) == 0:
    html += '<div class="mf-template" id="Template'+self.klass+parentname+'['+self.name+']'+'">'
    html += '<div class="mf-array-elt control-group">'
    newparent = parents.append(self.name)
    html += self._renderer.render(None,newparent)
    html += '<button elt="'+self.klass+parentname+'['+self.name+']'+'" class="mf-del mf-btn btn btn-primary controls">Remove</button>'
    html += '</div>'
    html += '</div>'
    html += '<div id="Clone'+self.klass+parentname+'['+self.name+']'+'" class="mf-template-clone">'
    for i in range(len(value)):
      logging.debug("set array renderer "+self.name)
      renderer = self.rootklass.renderer(self.rootklass,self.name,value[i])
      logging.debug("renderer = "+str(renderer))
      if not self._renderer:
        self._renderer =  renderer
      val = value[i]
      html += '<div class="mf-array-elt control-group">'
      html += renderer.render(val,newparent)
      html += '<button elt="'+elt+'" class="mf-del mf-btn btn btn-primary controls">Remove</button>'
      html += '</div>'
    html += '</div>'
    html += '<button elt="'+elt+'" class="mf-add mf-btn btn btn-primary">Add</button>'
    html += '</div>'
    return html + self.get_extra_controls()

  def bind(self,request,instance,name,parent = []):
    self.err = False
    errs = []
    self._renderer.in_array = True
    # Clear array
    if parent:
      curarray = list(parent).extend(name)
    else:
      curarray = [name]
    array = self.getObject(instance,curarray)
    del array[:]
    if isinstance(self._renderer,CompositeRenderer):
      err = self._renderer.bind_all(request,instance,self._renderer.name,parent)
    else:
      err = self._renderer.bind(request,instance,self._renderer.name,parent)
    if err:
        errs.extend(err)
    return errs

  def unserialize(self,value):
    raise Exception("not yet implemented")

class CompositeRenderer(AbstractRenderer):
  '''Renderer for composite inputs (objects within objects, dicts)
  '''

  def render_search(self, value = None):
    return ''

  def __init__(self,klass,name,attr,parent = ''):
    AbstractRenderer.__init__(self,klass,name,parent)
    self._renderers = []
    for obj  in attr:
      parentname = self.name
      if parent:
        parentname = parent+"."+self.name
      srenderer = klass.renderer(klass,obj,attr[obj],parentname)
      #self._renderers.append(srenderer)
      self._renderers.append(obj)
  

  def render(self,value = None, parents = []):
    parentname = ''
    fieldname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
        fieldname += parent+"."
    fieldname += self.name
    html = '<div class="mf-composite" id="'+self.klass+parentname+'['+self.name+']'+'"><span class="mf-composite-label">'+self.name+'</span>'
    #for renderer in self._renderers:
    for field in self._renderers:
      renderer = self.rootklass().get_renderer(fieldname+"."+field)
      obj = None
      if isinstance(value,dict):
        obj = value[renderer.name]
      elif hasattr(value,renderer.name):
        obj = getattr(value,renderer.name)
      if parents:
        newparent = parents.append(self.name)
      else:
        newparent = [self.name]
      html += renderer.render(obj,newparent)
    html += '</div>'
    return html + self.get_extra_controls()

  def bind(self,request,instance,name,parent = []):
    self.err = False
    parent.extend([name])
    errs = []
    fieldname = ''
    if parent:
      for p in parent:
        fieldname += p+"."

    #for renderer in self._renderers:
    for field in self._renderers:
      renderer = self.rootklass().get_renderer(fieldname+field)
      if self.in_array:
        renderer.in_array = True
      if hasattr(instance,name):
        obj = getattr(instance,name)
      else:
        obj = instance[name]
      if self.bind_only_one:
        renderer.bind_only_one = True
      err = renderer.bind(request,instance,renderer.name,parent)
      if err:
        errs.extend(err)
    return errs


  def bind_all(self,request,instance,name,parent = []):
    '''
    In case of array containing Composite, one need to extract each composite one by one
    '''
    self.err = False
    parent.extend([name])
    errs = []
    fieldname = ''
    if parent:
      for p in parent:
        fieldname += p+"."
    
    #for renderer in self._renderers:
    reset = True
    for field in self._renderers:
      renderer = self.rootklass().get_renderer(fieldname+field)
      if self.in_array:
        renderer.in_array = True
      if reset:
        renderer.reset = True
        reset = False
      else:
        renderer.reset = False
        
      if hasattr(instance,name):
        obj = getattr(instance,name)
      else:
        obj = instance[name]
        
      renderer.bind_only_one = True
      
      try:
        err = []
        
        while err is not None:
          err = renderer.bind(request,instance,renderer.name,parent)
          renderer.count += 1
      except Exception:
        logging.debug('no more element to match')
      renderer.count = 0
      renderer.bind_only_one = False
      if err:
        errs.extend(err)
    return errs

  def unserialize(self,value):
    raise Exception("not yet implemented")

class FloatRenderer(AbstractRenderer):
  '''Renderer for float inputs
  '''

  def render(self,value = None, parents = []):
    if value is None:
      value = 0.0
    parentname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    return _htmlNumber(self.klass+parentname+'['+self.name+']',self.name,value,self.err) + self.get_extra_controls()

  def render_search(self, value = None):
    return _htmlNumber('Search'+self.klass+'['+self.name+']',self.name,'') 

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

class ReferenceRenderer(AbstractRenderer):
  '''
  Renderer for an object reference
  '''

  collection = None

  def __init__(self,klass,name,attr,parent=''):
    self._reference = attr.__name__
    self._renderer = TextRenderer(klass,name,parent)
    AbstractRenderer.__init__(self,klass,name,parent)


  def render(self,value = None, parents = []):
    parentname = ''
    if parents:
      for parent in parents:
        parentname += '['+parent+']'
    html = '<div class="mf-reference" id="Ref'+self.klass+parentname+'['+self.name+']'+'">'
    html += _htmlAutoComplete(self.klass+parentname+'['+self.name+']',self.name,value,self._reference)
    html += '</div>'
    return html + self.get_extra_controls()


  def render_search(self,value = None):
    html = '<div class="mf-reference" id="Ref'+self.klass+'['+self.name+']'+'">'
    html += _htmlAutoComplete('Search'+self.klass+'['+self.name+']',self.name,'',self._reference)
    html += '</div>'
    return html

    
  def unserialize(self,value):
    if(str(value)==''):
      return None
    collection = DbConn.get_db(self._reference)
    obj= collection.find_one({ "_id" : ObjectId(str(value)) })
    logging.debug("match obj "+str(obj)+" with id "+str(value))
    if not obj:
      return None
    return obj



  def validate(self,attr):
    return True


  #def bind(self,request,instance,name,parent = []):
  #  print "##### reference"
  #  return self._renderer.bind(request,instance,name,parent)

class SimpleReferenceRenderer(ReferenceRenderer):
  '''
  Renderer for on object reference but using object ids (str) instead
   of DbRef
  '''
  def unserialize(self,value):
    # Check that object exists or empty string
    if(str(value)==''):
      return ''
    collection = DbConn.get_db(self._reference)
    obj= collection.find_one({ "_id" : ObjectId(str(value)) })
    logging.debug("match obj "+str(obj)+" with id "+str(value))
    if not obj:
      return None
    return str(value)

def _htmlChoiceTextField(id,name,value,choice_list,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  html = '<div class="mf-field mf-textfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><select data-default="'+(str(value) or '')+'" data-type="choice" id="'+id+'" name="'+id+'">'
  for choice in choice_list:
    if choice == value:
      selected = 'selected'
    else:
      selected = ''
    html += '<option value="'+choice+'"  '+selected+'>'+(choice or 'Any')+'</option>'
  html += '</select></div></div>'
  return html

def _htmlTextField(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-textfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input data-default="'+(str(value) or '')+'" type="text" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlAutoComplete(id,name,value,klass,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-autocomplete control-group '+errorClass+'"><label class="control-label" for="DbRef'+id+'">'+name.title()+'</label><div class="controls"><input data-default="'+(str(value) or '')+'" data-type="dbref" type="hidden" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"/><input type="text" data-object="'+klass+'" data-dbref="'+id+'" id="DbRef'+id+'" class="mf-dbref"><i data-dbref="'+id+'" id="DbRefClear'+id+'" class="mf-clear-object icon-trash"></i></div></div>'

def _htmlDateTime(id,name,value,error = False, type = 'datetime'):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-datetime control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input data-default="'+(str(value) or '')+'" type="'+type+'" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"/></div></div>'

def _htmlHidden(id,name,value):
  return '<div class="mf-field mf-textfield control-group"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input data-default="'+(str(value) or '')+'" type="text" id="'+id+'" name="'+id+'"   value="'+(str(value or ''))+'"  disabled/></div></div>'

def _htmlCheckBox(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  checked = ''
  if value:
     checked = 'checked'
  return '<div class="mf-field mf-checkbox control-group '+errorClass+'"><div class="controls"><label class="checkbox"><input data-default="'+str(value)+'" type="checkbox" value="'+str(value)+'" id="'+id+'" name="'+id+'" '+checked+'>'+name+'</label></div></div>'
 
def _htmlNumber(id,name,value,error = False):
  errorClass = ''
  if error:
    errorClass = 'error'
  return '<div class="mf-field mf-numberfield control-group '+errorClass+'"><label class="control-label" for="'+id+'">'+name.title()+'</label><div class="controls"><input data-default="'+str(value)+'" type="number" id="'+id+'" name="'+id+'" value="'+str(value)+'"/></div></div>'


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

