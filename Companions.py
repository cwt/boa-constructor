#----------------------------------------------------------------------
# Name:        Companions.py
# Purpose:     Classes implementing the design time behaviour of ctrls
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from wxPython.wx import *
from PropertyEditors import *
from Enumerations import *
from EventCollections import *
from BaseCompanions import *
from Constructors import *
from Preferences import wxDefaultFrameSize, wxDefaultFramePos
import HelpCompanions

class BaseFrameDTC(ContainerDTC):
    def __init__(self, name, designer, frameCtrl):
        ContainerDTC.__init__(self, name, designer, None, None)
        self.control = frameCtrl
        
    def generateWindowId(self):
        if self.designer: 
            self.id = Utils.windowIdentifier(self.designer.GetName(), '')
        else: self.id = `NewId()`

    def events(self):
        return ContainerDTC.events(self) + ['FrameEvent']

    def SetName(self, oldValue, newValue):
        print 'setting frame name from', oldValue, 'to', newValue
        self.name = newValue
        self.designer.renameFrame(oldValue, newValue)

    def designTimeSource(self):
        return {'title': `self.name`,
                'pos':  `wxDefaultFramePos`,
                'size': `wxDefaultFrameSize`,
                'name': `self.name`,
                'style': 'wxDEFAULT_FRAME_STYLE'}

class FrameDTC(FramesConstr, BaseFrameDTC):
    wxDocs = 'wx104.htm'


EventCategories['DialogEvent'] = (EVT_INIT_DIALOG,)
class DialogDTC(FramesConstr, BaseFrameDTC):
    wxDocs = HelpCompanions.wxDialogDocs
    def designTimeSource(self):
        dts = BaseFrameDTC.designTimeSource(self)
        dts.update({'style': 'wxDEFAULT_DIALOG_STYLE'})
        return dts

    def events(self):
        return BaseFrameDTC.events(self) + ['DialogEvent']

class MiniFrameDTC(FramesConstr, BaseFrameDTC):
    wxDocs = HelpCompanions.wxMiniFrameDocs

class MDIParentFrameDTC(FramesConstr, BaseFrameDTC):
    wxDocs = HelpCompanions.wxMDIParentFrameDocs
    def designTimeSource(self):
        dts = BaseFrameDTC.designTimeSource(self)
        dts.update({'style': 'wxDEFAULT_FRAME_STYLE | wxVSCROLL | wxHSCROLL'})
        return dts

class MDIChildFrameDTC(FramesConstr, BaseFrameDTC):
    wxDocs = HelpCompanions.wxMDIChildFrameDocs


EventCategories['PanelEvent'] = (EVT_SYS_COLOUR_CHANGED,)
class PanelDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxPanelDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxTAB_TRAVERSAL',
        	'name': `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['PanelEvent']

class ScrolledWindowDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxScrolledWindowDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxTAB_TRAVERSAL',
        	'name': `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['ScrollEvent']

EventCategories['NotebookEvent'] = (EVT_NOTEBOOK_PAGE_CHANGED,
                                    EVT_NOTEBOOK_PAGE_CHANGING)
class NotebookDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxNotebookDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['NotebookEvent']

EventCategories['ButtonEvent'] = (EVT_BUTTON,)
commandCategories.append('ButtonEvent')
class ButtonDTC(LabeledInputConstr, WindowDTC):
    wxDocs = HelpCompanions.wxButtonDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
        	'size': size,
        	'name': `self.name`,
        	'style': '0'}
    
    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

class ListCtrlDTC(MultiItemCtrlsConstr, WindowDTC):
    wxDocs = HelpCompanions.wxListCtrlDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxLC_ICON',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}
            
    def events(self):
        return WindowDTC.events(self) + ['ListEvent']
    
class TreeCtrlDTC(MultiItemCtrlsConstr, WindowDTC):
    wxDocs = HelpCompanions.wxTreeCtrlDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxTR_HAS_BUTTONS',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}
        
    def events(self):
        return WindowDTC.events(self) + ['TreeEvent']

class ScrollBarDTC(MultiItemCtrlsConstr, WindowDTC):
    wxDocs = HelpCompanions.wxScrollBarDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxSB_HORIZONTAL',
        	'name': `self.name`}
            
    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']
    

class ComboBoxDTC(ComboConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxComboBoxDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'value': `self.name`,
                'pos': position,
        	'size': size,
        	'name': `self.name`}
    
class ChoiceDTC(ListConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxChoiceDocs = 'wx41.htm'
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'choices': `[]`,
        	'style': '0',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

class StaticTextDTC(LabeledNonInputConstr, WindowDTC):
    wxDocs = HelpCompanions.wxStaticTextDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
        	'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}

EventCategories['TextCtrlEvent'] = (EVT_TEXT, EVT_TEXT_ENTER)
class TextCtrlDTC(TextCtrlConstr, WindowDTC):
    wxDocs = HelpCompanions.wxTextCtrlDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'value': `self.name`,
        	'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['TextCtrlEvent']

EventCategories['RadioButtonEvent'] = (EVT_RADIOBUTTON,)
class RadioButtonDTC(LabeledInputConstr, WindowDTC):
    wxDocs = HelpCompanions.wxRadioButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
        	'pos': position,
        	'size': size,
        	'style': '0'}
    def events(self):
        return WindowDTC.events(self) + ['RadioButtonEvent']

EventCategories['CheckBoxEvent'] = (EVT_CHECKBOX,)
class CheckBoxDTC(LabeledInputConstr, WindowDTC):
    wxDocs = HelpCompanions.wxCheckBoxDocs = 'wx39.htm'
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
        	'pos': position,
        	'size': size,
        	'style': '0'}
    def events(self):
        return WindowDTC.events(self) + ['CheckBoxEvent']

class SpinButtonDTC(WindowConstr, WindowDTC):
    wxDocs = HelpCompanions.wxSpinButtonDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxSP_HORIZONTAL',
# cfd       	'validator': 'wxDefaultValidator',
        	'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['SpinEvent', 'CmdScrollEvent']
    
# XXX FreqTick handled wrong
class SliderDTC(SliderConstr, WindowDTC):
    wxDocs = HelpCompanions.wxSliderDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MinValue'] = IntConstrPropEdit
        self.editors['MaxValue'] = IntConstrPropEdit
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'value': '0',
        	'minValue': '0',
        	'maxValue': '100',
        	'point': position,
        	'size': size,
        	'style': 'wxSL_HORIZONTAL',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

class GaugeDTC(GaugeConstr, WindowDTC):
    wxDocs = HelpCompanions.wxGaugeDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'range': '100',
        	'pos': position,
        	'size': size,
        	'style': 'wxGA_HORIZONTAL',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

class StaticBoxDTC(LabeledNonInputConstr, WindowDTC):
##    def __init__(self, name, designer, parent, ctrlClass):
##        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
##        self.container = true
    wxDocs = HelpCompanions.wxStaticBox = 'wx220.htm'
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
        	'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}

class StaticLineDTC(WindowConstr, WindowDTC):
##    def __init__(self, name, designer, parent, ctrlClass):
##        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
##        self.container = true
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}
    

class ListBoxDTC(ListConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxListBoxDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'choices': `[]`,
        	'style': '0',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

class CheckListBoxDTC(ListConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxCheckListBoxDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'choices': `[]`,
        	'style': '0',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}


class BitmapButtonDTC(BitmapButtonConstr, WindowDTC):
    wxDocs = HelpCompanions.wxBitmapButtonDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
        	'size': size,
        	'style': 'wxBU_AUTODRAW',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']
    
class StaticBitmapDTC(StaticBitmapConstr, WindowDTC):
    wxDocs = HelpCompanions.wxStaticBitmapDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}


class RadioBoxDTC(RadioBoxConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxRadioBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MajorDimension'] = MajorDimensionConstrPropEdit
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
        	'point': position,
        	'size': size,
        	'choices': `['asd']`,
        	'majorDimension': '1',
        	'style': 'wxRA_SPECIFY_COLS',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

class GridDTC(WindowConstr, WindowDTC):
    wxDocs = HelpCompanions.wxGridDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Editable'] = self.editors['EditInPlace'] = BoolPropEdit
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}


class HtmlWindowDTC(HtmlWindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        del self.editors['Style']

    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
#        	'style': 'wxHW_SCROLLBAR_AUTO',
        	'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']

class FontDTC(HelperDTC):
    def __init__(self, name, designer, ctrl, obj):
        HelperDTC.__init__(self, name, designer, ctrl, obj)
        self.editors = {'Family'    : EnumPropEdit,
        		'Style'     : EnumPropEdit,
        		'Weight'    : EnumPropEdit,
                        'Underlined': BoolPropEdit,
                       }
        self.options = {'Family': fontFamily,
        		'Style' : fontStyle,
        		'Weight': fontWeight,
                       }
        self.names = {'Family': fontFamilyNames,
           	      'Style' : fontStyleNames,
        	      'Weight': fontWeightNames,
                     }
 
class ColourDTC(HelperDTC):
    def __init__(self, name, designer, ctrl, obj):
        HelperDTC.__init__(self, name, designer, ctrl, obj)
        self.editors = {'Red'    : RedColPE,
        		'Green'  : GreenColPE,
        		'Blue'   : BlueColPE,
                       }
    def properties(self):
        return {'Red'  : (wxColour.Get.im_func, wxColour.Set.im_func),
                'Green': (wxColour.Get.im_func, wxColour.Set.im_func),
                'Blue' : (wxColour.Get.im_func, wxColour.Set.im_func)
        }
    
