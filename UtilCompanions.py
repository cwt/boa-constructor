from wxPython.wx import *

from BaseCompanions import UtilityDTC
from Constructors import ImageListConstr, EmptyConstr, MenuConstr
from PropertyEditors import IntConstrPropEdit, StrConstrPropEdit
import HelpCompanions

class ImageListDTC(ImageListConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxImageListDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors = {'Width': IntConstrPropEdit,
                        'Height': IntConstrPropEdit}
#                        'Enabled': BoolPropEdit}
#                        'EvtHandlerEnabled': BoolPropEdit,
#                        'Style': StyleConstrPropEdit}
    def designTimeSource(self):
        return {'width': '16',
                'height': '16'}
#        	  'mask': 'true',
#        	  'initialCount': '1'}

class TimerDTC(EmptyConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxTimerDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
    def designTimeSource(self):
        return {}

class AcceleratorTableDTC(EmptyConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxAcceleratorTableDocs
    def designTimeSource(self):
        return {}

class MenuDTC(MenuConstr, UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors = {'Title': StrConstrPropEdit}
    def designTimeSource(self):
        return {'title': "''"}
