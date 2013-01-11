# Introduction

This library provides annotations on a MongoKit object (@mf_decorator) to analyse objects and create actions and forms on objects automatically.

Goal is to generate an admin dashboard for each object (show/edit/delete per object and list of objects).

Renderer is in charge of generating HTML per attribute type.

More customization will also be available to force type of the attribute (Checkbox etc...) in later releases.

Pyramid routes and templates will be set automatically to access objects via REST (though optional). Dashboard is accessible via /admin route.
Dashboard is not automatically installed, it is only for help and can (should?) be customized.
Copy the pyramid directory content in your pyramid application according to your setup.

# TODO

  see bugs/features in github

LIMITATIONS: ArrayRenderer does not support arrays of complex objects, only arrays of basic types or dicts (but not arrays of arrays)

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

Warning: this should be added after your routes declaration because it inserts generic routes to match objets:

/users/ (GET/PUT)
/users/id (POST,DELETE)
/groups/
/groups/id
...

Minimal expected interface is:(as in mongokit)
save()
delete()
find() via connection
find_one() via connection

If user must have only limited access to a query, i.e list only a subset of an object (/users), it is necessary to add to the object a function defined as:

    def my(self, control):
      '''
      Return a mongodb filter on object
      control is a mf.views.MF_LIST or MF_MANAGE according to expected access on object
      if method returns None, then no access is allowed
      if method returns {}, then access is allowed
      if method returns a mongo filter, it will be applied on request to access object(s)
      ....
      return filter

If this function is not defined, then all elements are available via GET method.
Filter is a mongo filter


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


Acknowledgements:

parseDateTime from http://aralbalkan.com/1512
