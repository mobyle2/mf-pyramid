import logging
from mongokit.database import Database

class DbConn:
  '''
   Defines bd connection
  '''


  # db connection
  db_conn = None

  @staticmethod
  def get_db(key):
      ''' Get db connection for object name

      :param key: Object class name
      :type key: str
      :return: Object - MongoKit connection for object
      '''
      if key in DbConn.db_conn._registered_documents:
          document = DbConn.db_conn._registered_documents[key]
          try:
              return getattr(DbConn.db_conn[document.__database__][document.__collection__], key)
          except AttributeError:
              raise AttributeError("%s: __collection__ attribute not found. "
                  "You cannot specify the `__database__` attribute without "
                  "the `__collection__` attribute" % key)
      else:
          if key not in DbConn.db_conn._databases:
              DbConn.db_conn._databases[key] = Database(DbConn.db_conn, key)
          return DbConn.db_conn._databases[key]
