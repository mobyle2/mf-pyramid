"""
.. module:: mf
   :synopsis: Mingflow annotations

.. moduleauthor:: Olivier Sallou <olivier.sallou@irisa.fr>


"""
import annotation
from annotation import Annotation

class Dashboard
  ''' Manage administration dashboard for pyramid
  '''

  @staticmethod
  def add_dashboard(klasses):
    ''' Adds a list of class to the dashboard
    :param klasses: list of object class to add to the dashboard
    :type klasses: list
    '''
    if klasses is None:
      return
    for klass in klasses:
      Annotation.addKlass(klass)

