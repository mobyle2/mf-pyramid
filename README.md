# Introduction

This library provides annotations on a MongoKit object (@mf_decorator) to analyse objects and create actions and forms on objects automatically.

Goal is to generate an admin dashboard for each object (show/edit/delete per object and list of objects).

Renderer is in charge of generating HTML per attribute type.

More customization will also be available to force type of the attribute (Checkbox etc...) in later releases.

Pyramid routes and templates will be set automatically to access objects via REST (though optional). Dashboard is accessible via /admin route.
Dashboard is not automatically installed, it is only for help and can (should?) be customized.
Copy the pyramid directory content in your pyramid application according to your setup:
  - dashboard needs mf.css, mf.js
  - dashboard.mako is a template example and can be copied/adapted to get a base dashboard.

# TODO

  see bugs/features in github

# LIMITATIONS:

MongoKit operators OR, NOT are not supported.
IS operator is supported for strings. In this case, the renderer is
automatically set to a TextChoiceRenderer with options from IS list.

ArrayRenderer does not support arrays of complex objects, only arrays of basic types or dicts (but not arrays of arrays)
Collection name for objects must match object class name with lowercase and a 's'. Example:
class User -> users
class Group -> groups

# LICENSE

LGPL

# USAGE

A sample pyramid application is available in pyramid directory, simply run app.sh

Pyramid acl permissions for dashboard access can be set via config, however, there is no acl on get/post/put/delete REST operations. Control is done via the *my*  method (see below).

Add mf_decorator above your MongoKit classes (see pyramid/user.py for example).

For dashboard, to add User and Group, insert in Pyramid init :

    connection = Connection()
    connection.register([User,Group])
    Dashboard.set_connection(connection)
    Dashboard.add_dashboard([User,Group],config)
    or
    Dashboard.add_dashboard([User,Group],config,'/test') to add an URL prefix

Warning: this should be added after your routes declaration because it inserts generic routes to match objets:

    /users/ (GET/POST)
    /users/id (PUT,DELETE)
    /groups/
    /groups/id
    ...

Minimal expected interface is:(as in mongokit)
save()
delete()
find() via connection
find_one() via connection

If user must have only limited access to a query, i.e list only a subset of an object (/users), it is necessary to add to the object a function defined as:

    def my(self, control, request=None):
      '''
      Return a mongodb filter on object
      control is a mf.views.MF_LIST or MF_MANAGE according to expected access on object
      if method returns None, then no access is allowed
      if method returns {}, then access is allowed
      if method returns a mongo filter, it will be applied on request to access object(s)
      ....
      Request parameter is the pyramid request object, can be used to get
parameters, authenticated user etc...
      return filter

If this function is not defined, then all elements are available via
GET/PUT/POST/DELETE method.

Filter is a pymongo filter

In the case of a MANAGE operation (GET/POST/DELETE/PUT for a specific object
e.g. POST  /notes/12 ), *my* is called on the object instance, and instance
parameters can be used to decide of the operation is allowed. Usually, a
MF_MANAGE will only return None(reject) or {} (accept), according to current
user and current object.
A MF_LIST is not attached to a specific object instance (e.g. GET /notes) , so
the *my* method will be called on a *new* object instance (e.g. notes().my())


Other functions may be implemented in objects to override default behaviour:

    def render(self,fields = None):
      """
      Render in HTML form an object

      param: fields List of fields to show
      type: list
      rparam: HTML form
      rtype: str
      """

    def render_search(self, fields = None):
      """
      Render in HTML a search form an object

      param: fields List of fields to show, limited to first level of document
      type: list
      rparam: HTML form
      rtype: str
      """

    def bind_form(self,request):
      """
      Binds a request dictionnary to the object

      :param request: request.params.items() in the form [ (key1,value1), (key1,value2), (key2,value1), ...]
      :type request: list
      :return: list of fields in error
      """

If any is defined in object, then object method is used, else default implementation is used.

# Custom types

If using custom types in MongoKit (CustomType), library will use default TextRenderer. One can change the renderer afterward (see Custom display).
However, class must define a new method *unserialize* to return an object from a string (to be able to map an HTML form attribute to an object attribute).


    class CustomStatus(CustomType):

        @staticmethod
        def unserialize(value)
            ''' unserizalize from str to expected format

            :param value: input value
            :type value: str
            :return: an integer for this example
            '''
            return int(value)
    
        ...

In this example, we take input string value coming from HTML request parameter and cast it to an int.


# Custom display

Some functions helps you to customize the rendering.

    Group.set_display_fields(['name','creation_date'])

set_display_fields will define the parameters to display, and in which order. This will only work for "first level" parameters (not params of a dict).

    renderer = mf.renderer.TextChoiceRenderer(User,'email','')
    renderer.limit([ 'nomail', 'othermail@mail.fr', 'sample@nomail' ])

Defines for the objects User a new renderer (TextRenderer by default), in this case a TextChoiceRenderer.
Simply create a new renderer with class as first parameter and param name as second parameter to change the default renderer.


    renderer.add_extra_control('<button class="btn btn-info">Fake button</button>')

Adds an extra button for the field (up to you to defined in Javascript what to do with this button).

# Object references

DBref are supported, but if one need to refer to an other object using
ObjectIds, it is possible to specify a parameter as a *SimpleReferenceRenderer*:

        User example: { "mygroups" : [{ "groupid" : basestring }] }, groupid is
        the id of a Group

        groupid_renderer = mf.renderer.SimpleReferenceRenderer(User,'groupid',Group,'mygroups')
        # If the reference is an ObjectID and not a string
        groupid_renderer.is_object_id = True
        # In the dashboard, to display a value, mf search by default the *name*
        # parameter. If it does not exists or is not the expected parameter, one
        # may use the following.
        # NB: set_display_field works only with top level parameters
        groupid_renderer.set_display_field("myfield")

This specifies the User parameter *groupid* is in fact an ObjectId reference to
the Group object.
This initial setup is required to define the link between the objects as the
library cannot guess which object the objectid references.

In MongoKit definition, one can define the parameter link as a basestring or an
ObjectId and must declare the above example (an ObjectId does not give
information on object)a

If parameter is defined as an ObjectId, one *can* simply call the set_reference
function to update the renderer:

    User example: { "mygroups" : [{ "groupid" : ObjectId }] }

    renderer = User.get_renderer('mygroups.groupid')
    renderer.set_reference(Group)




Acknowledgements:

parseDateTime from http://aralbalkan.com/1512
