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
from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *
from EventCollections import *
from BaseCompanions import *
from Constructors import *
from Preferences import wxDefaultFrameSize, wxDefaultFramePos
import HelpCompanions
import copy

class BaseFrameDTC(ContainerDTC):
    def __init__(self, name, designer, frameCtrl):
        ContainerDTC.__init__(self, name, designer, None, None)
        self.control = frameCtrl
        self.editors.update({'StatusBar': StatusBarClassLinkPropEdit, 
        		     'MenuBar': MenuBarClassLinkPropEdit,
        		     'ToolBar': ToolBarClassLinkPropEdit })
        self.triggers.update({'ToolBar': self.ChangeToolBar})
        
    def generateWindowId(self):
        if self.designer: 
            self.id = Utils.windowIdentifier(self.designer.GetName(), '')
        else: self.id = `wxNewId()`

    def events(self):
        return ContainerDTC.events(self) + ['FrameEvent']

    def SetName(self, oldValue, newValue):
##        print 'setting frame name from', oldValue, 'to', newValue
        self.name = newValue
        self.designer.renameFrame(oldValue, newValue)
    
    def ChangeToolBar(self, oldValue, newValue):
        if newValue:
            self.designer.connectToolBar(newValue)
        else:
            self.designer.disconnectToolBar(oldValue)

    def designTimeSource(self):
        return {'title': `self.name`,
                'pos':  `wxDefaultFramePos`,
                'size': `wxDefaultFrameSize`,
                'name': `self.name`,
                'style': 'wxDEFAULT_FRAME_STYLE'}
    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + \
          ['ToolBar', 'MenuBar', 'StatusBar']

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
        return {'pos':   position,
        	'size':  size,
        	'style': 'wxTAB_TRAVERSAL',
        	'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['PanelEvent']

EventCategories['SashEvent'] = (EVT_SASH_DRAGGED, )
commandCategories.append('SashEvent')
class SashWindowDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxSashWindowDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos':   position,
        	'size':  size,
        	'style': 'wxCLIP_CHILDREN | wxSW_3D',
        	'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['SashEvent']

class SashLayoutWindowDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxSashLayoutWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Alignment'   : EnumPropEdit,
        		     'Orientation' : EnumPropEdit,
#        		     'DefaultSize' : SizePropEdit
                            })
        self.options.update({'Alignment'   : sashLayoutAlignment,
        		     'Orientation' : sashLayoutOrientation
                            })
        self.names.update({'Alignment'   : sashLayoutAlignmentNames,
                           'Orientation' : sashLayoutOrientationNames
                          })
#        self.defaultSize = wxSize(self.control.GetSize())
    
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos':   position,
        	'size':  size,
        	'style': 'wxCLIP_CHILDREN | wxSW_3D',
        	'name':  `self.name`}

    def properties(self):
        props = ContainerDTC.properties(self) 
        props.update({'DefaultSize': ('CompnRoute', self.GetDefaultSize, 
          self.SetDefaultSize)})
        return props
        
    def events(self):
        return ContainerDTC.events(self) + ['SashEvent']
    
    def GetDefaultSize(self, something):
        if self.control:
            return self.control.GetSize()
        else:
            return wxSize(15, 15)
            

    def SetDefaultSize(self, size):
        if self.control:
            self.control.SetSize(size)
            wxLayoutAlgorithm().LayoutWindow(self.control)

class ScrolledWindowDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxScrolledWindowDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos':   position,
        	'size':  size,
        	'style': 'wxTAB_TRAVERSAL',
        	'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['ScrollEvent']

EventCategories['NotebookEvent'] = (EVT_NOTEBOOK_PAGE_CHANGED,
                                    EVT_NOTEBOOK_PAGE_CHANGING)
class NotebookDTC(WindowConstr, ContainerDTC):
    wxDocs = HelpCompanions.wxNotebookDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Pages':     CollectionPropEdit,
                             'ImageList': ImageListClassLinkPropEdit})
        self.subCompanions['Pages'] = NotebookPagesCDTC

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Pages': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos':   position,
        	'size':  size,
        	'style': '0',
        	'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + \
          ['ImageList', 'Pages']

    def events(self):
        return ContainerDTC.events(self) + ['NotebookEvent']

class NotebookPagesCDTC(NotebookPageConstr, CollectionDTC):        
    wxDocs = HelpCompanions.wxNotebookDocs
    propName = 'Pages'
    displayProp = 'strText'
    indexProp = '(None)'
    insertionMethod = 'AddPage'
    deletionMethod = 'RemovePage'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Page': ClassLinkConstrPropEdit,
                        'Text': StrConstrPropEdit,
                        'Selected' : BoolConstrPropEdit,
                        'ImageId': IntConstrPropEdit}

#        self.tempPlaceHolders = []
    
    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Page': ('NoneRoute', None, None),
                      'Text': ('NoneRoute', None, None),
                      'Selected' : ('NoneRoute', None, None),
                      'ImageId': ('NoneRoute', None, None)})
        return props

##    def appendItem(self):
##        tph = wxWindow(self.control, -1)
##        self.tempPlaceHolders.append(tph)
##        CollectionDTC.appendItem(self)

    def designTimeSource(self, wId):
        return {'pPage': 'None',
        	'strText': `'%s%d'%(self.propName, wId)`,
        	'bSelect': 'false',
        	'imageId': `-1`}

    def initDesignTimeEvents(self, ctrl):
        EVT_MOTION(ctrl, self.designer.OnMouseOver)
        EVT_LEFT_DOWN(ctrl, self.designer.OnControlSelect)
        EVT_LEFT_UP(ctrl, self.designer.OnControlRelease)
        EVT_LEFT_DCLICK(ctrl, self.designer.OnControlDClick)
        EVT_SIZE(ctrl, self.designer.OnControlResize)

    def applyDesignTimeDefaults(self, params):
        prms = copy.copy(params)
        f = RTTI.getFunction(self.control, self.insertionMethod)
        if params['pPage'] == 'None':
            page = BlankWindowPage(self.control, self.designer, params, 'pPage')
        else:
            page = self.designer.objects[prms['pPage'][5:]][1]

        del prms['pPage']
        params = self.designTimeDefaults(prms)
        params['pPage'] = page
        
        apply(f, [self.control], params)# , idx, page, text
    
##    def finaliser(self):
##        return CollectionDTC.finaliser(self) + ['        parent.test("blah")']

class BlankWindowPage(wxWindow):
    """ Window representing uninitialised space, it grabs the first control
        dropped onto it and replaces None with new ctrl in code.
        
        Used by wxNotebook and wxSplitterWindow
    """
    
    def __init__(self, parent, designer, params, nameKey):
        wxWindow.__init__(self, parent, -1)
        self.params = params
        self.designer = designer

        EVT_MOTION(self, self.designer.OnMouseOver)
        EVT_LEFT_DOWN(self, self.OnControlSelect)
        EVT_LEFT_UP(self, self.designer.OnControlRelease)
        EVT_LEFT_DCLICK(self, self.designer.OnControlDClick)
        EVT_SIZE(self, self.OnControlResize)
 
        self.SetName(parent.GetName())
        self.designer.senderMapper.addObject(self)
        self.ctrl = None
        self.nameKey = nameKey
        
    def OnControlSelect(self, event):
        new = self.designer.compPal.selection
        self.designer.OnControlSelect(event)
        if new:
            self.ctrl = self.designer.objects[self.designer.objectOrder[-1:][0]][1]
            # XXX Special case for frame
            self.params[self.nameKey] = 'self.'+self.ctrl.GetName()
            self.OnControlResize(None)

    def OnControlResize(self, event):
        if self.ctrl:
            s = self.GetSize()
            self.ctrl.SetDimensions(0, 0, s.x, s.y)
        else:
            self.designer.OnControlResize(event)
                    
class SplitterWindowDTC(SplitterWindowConstr, ContainerDTC):        
    wxDocs = HelpCompanions.wxSplitterWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'SplitMode':     EnumPropEdit})
        self.options['SplitMode'] = splitterWindowSplitMode
        self.names['SplitMode'] = splitterWindowSplitModeNames
        self.triggers.update({'SplitMode': self.SetSplitMode})
        
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'point':   position,
        	'size':  size,
        	'style': 'wxSP_3D',
        	'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + \
          ['SplitVertically', 'SplitHorizontally']

    def SetSplitMode(self, oldValue, newValue):
        print 'SetSplitMode!', oldValue, newValue

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

class BitmapButtonDTC(BitmapButtonConstr, WindowDTC):
    wxDocs = HelpCompanions.wxBitmapButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap':          BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocused'  : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})
        
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
        	'size': size,
        	'style': 'wxBU_AUTODRAW',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Bitmap': ('CtrlRoute', wxBitmapButton.GetBitmapLabel, 
          wxBitmapButton.SetBitmapLabel)})
        return props

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

class GenButtonDTC(GenButtonConstr, WindowDTC):
    wxDocs = HelpCompanions.wxDefaultDocs
    windowIdName = 'ID'
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
        	'size': size,
        	'name': `self.name`,
        	'style': '0'}
    
    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

class GenBitmapButtonDTC(GenBitmapButtonConstr, WindowDTC):
    wxDocs = HelpCompanions.wxDefaultDocs
    windowIdName = 'ID'
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'BitmapLabel'    : BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocus'    : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'bitmap': wxNullBitmap,
                'pos': position,
        	'size': size,
        	'name': `self.name`,
        	'style': '0'}
    
    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

class ListCtrlDTC(MultiItemCtrlsConstr, WindowDTC):
    wxDocs = HelpCompanions.wxListCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Columns':         ListColumnsColPropEdit,
                             'SmallImageList':  ImageListClassLinkPropEdit,
                             'NormalImageList': ImageListClassLinkPropEdit})

        self.subCompanions['Columns'] = ListCtrlColumnsCDTC

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Columns': ('NoneRoute', None, None),
                      'SmallImageList': ('NoneRoute', None, None),
                      'NormalImageList': ('NoneRoute', None, None)})
        return props
    
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxLC_ICON',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}
            
    def events(self):
        return WindowDTC.events(self) + ['ListEvent']

class ListCtrlColumnsCDTC(ListCtrlColumnsConstr, CollectionDTC):        
    wxDocs = HelpCompanions.wxListCtrlDocs
    propName = 'Columns'
    displayProp = 'heading'
    indexProp = 'col'
    insertionMethod = 'InsertColumn'
    deletionMethod = 'DeleteColumn'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Width': IntConstrPropEdit,
                        'Heading': StrConstrPropEdit,
                        'Format': EnumConstrPropEdit}#StyleConstrPropEdit}
#        self.options = {'Format': formatStyle}
        self.names = {'Format': formatStyle}
    
    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Column':  ('NoneRoute', None, None),
                      'Heading': ('NoneRoute', None, None),
##                      'Format':  ('IndexRoute', None, None),
                      'Width':   ('IndexRoute', wxListCtrl.GetColumnWidth, 
                                                wxListCtrl.SetColumnWidth)})
        return props

    def designTimeSource(self, wId):
        return {'col': `wId`,
        	'heading': `'%s%d'%(self.propName, wId)`,
        	'format': 'wxLIST_FORMAT_LEFT',
        	'width': `-1`}
    
##    def finaliser(self):
##        return CollectionDTC.finaliser(self) + ['        parent.test("blah")']

    
    
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
    
EventCategories['ComboEvent'] = (EVT_COMBOBOX, EVT_TEXT)
commandCategories.append('ComboEvent')
class ComboBoxDTC(ComboConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxComboBoxDocs
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'value': `self.name`,
                'pos': position,
        	'size': size,
        	'choices': `[]`,
        	'style': '0',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ComboEvent']

EventCategories['ChoiceEvent'] = (EVT_CHOICE,)
commandCategories.append('ChoiceEvent')
class ChoiceDTC(ListConstr, ChoicedDTC):
    wxDocs = HelpCompanions.wxChoiceDocs = 'wx41.htm'
    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'choices': `[]`,
        	'style': '0',
        	'validator': 'wxDefaultValidator',
        	'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ChoiceEvent']

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
    def hideDesignTime(self):
        return ['Selection']
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
## cfd       	'validator': 'wxDefaultValidator',
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

class StaticBoxDTC(LabeledNonInputConstr, ContainerDTC):
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
   
class StaticBitmapDTC(StaticBitmapConstr, WindowDTC):
    wxDocs = HelpCompanions.wxStaticBitmapDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Bitmap'] = BitmapPropEdit

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
#    wxDocs = HelpCompanions.wxGridDocs
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
##        	'style': 'wxHW_SCROLLBAR_AUTO',
        	'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']


EventCategories['ToolEvent'] = (EVT_TOOL,)
commandCategories.append('ToolEvent')

class ToolBarDTC(WindowConstr, WindowDTC):
    wxDocs = HelpCompanions.wxToolBarDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Tools': CollectionPropEdit})
        self.subCompanions['Tools'] = ToolBarToolsCDTC

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Tools': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': 'wxTB_HORIZONTAL | wxNO_BORDER',
        	'name': `self.name`}

class ToolBarToolsCDTC(ToolBarToolsConstr, CollectionIddDTC):        
    wxDocs = HelpCompanions.wxToolBarDocs
    propName = 'Tools'
    displayProp = 'shortHelpString'
    indexProp = '(None)'
    insertionMethod = 'AddTool'
    deletionMethod = 'DeleteTool'
    idProp = 'id'    
    idPropNameFrom = 'tools'
    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Bitmap': BitmapConstrPropEdit,
                        'BitmapOn': BitmapConstrPropEdit,
                        'IsToggle': BoolConstrPropEdit,
                        'ShortHelpString': StrConstrPropEdit,
                        'LongHelpString': StrConstrPropEdit}
    
    def designTimeSource(self, wId):
        newItemName = '%s%d'%(self.propName, wId)
        return {'id': self.newWinId(newItemName), 
                'bitmap': 'wxNullBitmap',
                'pushedBitmap': 'wxNullBitmap',
                'toggle': 'false',
                'shortHelpString': `newItemName`,
                'longHelpString': `newItemName`}

    def finaliser(self):
        return ['', '        parent.Realize()']

    def appendItem(self):
        CollectionIddDTC.appendItem(self)
        self.control.Realize()

    def applyDesignTimeDefaults(self, params):
        CollectionIddDTC.applyDesignTimeDefaults(self, params)
        self.control.Realize()

    def events(self):
        return ['ToolEvent']
                
class StatusBarDTC(WindowConstr, WindowDTC):
    wxDocs = HelpCompanions.wxStatusBarDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Fields'] = CollectionPropEdit
        self.subCompanions['Fields'] = StatusBarFieldsCDTC

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Fields': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position, size = 'wxDefaultSize'):
        return {'pos': position,
        	'size': size,
        	'style': '0',
        	'name': `self.name`}

class StatusBarFieldsCDTC(StatusBarFieldsConstr, CollectionDTC):        
    wxDocs = HelpCompanions.wxStatusBarDocs
    propName = 'Fields'
    displayProp = 'text'
    indexProp = 'i'
    insertionMethod = 'SetStatusText'
    deletionMethod = '(None)'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Index' : IntConstrPropEdit,
                        'Text': StrConstrPropEdit,
                        'Width': SBFWidthConstrPropEdit}
        self.widths = []
    
    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Index':  ('NoneRoute', None, None),
                      'Text':  ('CompnRoute', self.GetText, self.SetText),
                      'Width': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, wId):
        return {'i': `wId`,
        	'text': `'%s%d'%(self.propName, wId)`}
    
    def initialiser(self):
        return ['        parent.SetFieldsCount(%d)'%self.getCount()]+CollectionDTC.initialiser(self)

    def finaliser(self):
        return ['', '        parent.SetStatusWidths(%s)'%`self.widths`]

    def appendItem(self):
        self.widths.append(-1)
        self.control.SetFieldsCount(len(self.widths))
        CollectionDTC.appendItem(self)
        
    def deleteItem(self, index):
        CollectionDTC.deleteItem(self, index)
        for idx in range(index, len(self.widths)):
            self.control.SetStatusText(self.control.GetStatusText(idx+1), idx)
        del self.widths[index]
        self.control.SetStatusWidths(self.widths)
        self.control.SetFieldsCount(len(self.widths))

    def setConstrs(self, constrLst, inits, fins):
##        print 'setConstrs', inits, fins
        CollectionDTC.setConstrs(self, constrLst, inits, fins)
        if len(fins):
            self.widths = eval(fins[0]\
              [string.find(fins[0], '(')+1 : string.rfind(fins[0], ')')])
            self.control.SetFieldsCount(len(self.widths))

    def GetWidth(self):
        return `self.widths[self.index]`

    def SetWidth(self, value):
        self.widths[self.index] = int(value)
        self.control.SetStatusWidths(self.widths)

    def GetText(self):
##        print 'StatusBarFieldsCDTC GetText'
        return `self.control.GetStatusText(self.index)`

    def SetText(self, value):
##        print 'StatusBarFieldsCDTC SetText'
        self.control.SetStatusText(value)

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
        return {'Red'  : ('CtrlRoute', wxColour.Get.im_func, wxColour.Set.im_func),
                'Green': ('CtrlRoute', wxColour.Get.im_func, wxColour.Set.im_func),
                'Blue' : ('CtrlRoute', wxColour.Get.im_func, wxColour.Set.im_func)
        }
        
        
        
        
        
        