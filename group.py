from admin import Admin
from admin import *
from ming import Field,schema
from ming.datastore import DataStore
from ming import Session, create_datastore

bind = create_datastore("%s%s"%('mongodb://localhost:27017','test'))
session = Session(bind)

@admin_decorator
class Group:

  class __mongometa__:
      session = session
      name = 'groups'

  _id = Field(schema.ObjectId) 
  name = Field(str)

  def html(self, fields = None):
    return self.render(fields)


if __name__ == "__main__":
  group = Group()
  group.name = "mygroup"
  group.save
