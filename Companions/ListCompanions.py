#-----------------------------------------------------------------------------
# Name:        ListCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.ListCompanions'

import string

from wxPython.wx import *

from wxPython.grid import *

from BaseCompanions import WindowDTC, ChoicedDTC, CollectionDTC, CollectionIddDTC

from Constructors import *
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

class ListCtrlDTC(MultiItemCtrlsConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxListCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Columns':         ListColumnsColPropEdit,
                             'ImageListSmall':  ListCtrlImageListClassLinkPropEdit,
                             'ImageListNormal': ListCtrlImageListClassLinkPropEdit})
        self.windowStyles = ['wxLC_LIST', 'wxLC_REPORT', 'wxLC_VIRTUAL', 'wxLC_ICON',
                             'wxLC_SMALL_ICON', 'wxLC_ALIGN_TOP',
                             'wxLC_ALIGN_LEFT', 'wxLC_AUTOARRANGE',
                             'wxLC_USER_TEXT', 'wxLC_EDIT_LABELS',
                             'wxLC_NO_HEADER', 'wxLC_SINGLE_SEL',
                             'wxLC_SORT_ASCENDING', 'wxLC_SORT_DECENDING',
                             'wxLC_HRULES', 'wxLC_VRULES'] + self.windowStyles
        self.subCompanions['Columns'] = ListCtrlColumnsCDTC
        self.listTypeNameMap = {'ImageListSmall'  : wxIMAGE_LIST_SMALL,
                                'ImageListNormal' : wxIMAGE_LIST_NORMAL}
        for name in self.listTypeNameMap.keys():
            self.customPropEvaluators[name] = self.EvalImageList
        self.customPropEvaluators['ImageList'] = self.EvalImageList

    def properties(self):
        props = WindowDTC.properties(self)
        props['Columns'] =  ('NoneRoute', None, None)

        prop = ('NameRoute', self.GetImageList, self.SetImageList)
        for name in self.listTypeNameMap.keys():
            props[name] = prop

        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxLC_ICON',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ListEvent']

#---Image list management-------------------------------------------------------
    def GetImageList(self, name):
        return (self.control.GetImageList(self.listTypeNameMap[name]),
            self.listTypeNameMap[name])

    def SetImageList(self, name, value):
        self.control.SetImageList(value[0], self.listTypeNameMap[name])

    def EvalImageList(self, exprs, objects):
        imgLst, lstTpe = exprs
        return objects[imgLst], eval(lstTpe)

    def notification(self, compn, action):
        WindowDTC.notification(self, compn, action)
        if action == 'delete':
            for propName, typeName in (('ImageListSmall', 'wxIMAGE_LIST_SMALL'),
                                       ('ImageListNormal', 'wxIMAGE_LIST_NORMAL')):
                imgLst, imgLstType = self.GetImageList(propName)
                if imgLst and `imgLst` == `compn.control`:
                    self.SetImageList(propName, (None,))
                    idx = 0
                    while idx < len(self.textPropList):
                        prop = self.textPropList[idx]
                        if prop.prop_setter == 'SetImageList' and \
                              prop.params[1] == typeName:
                            del self.textPropList[idx]
                        else:
                            idx = idx + 1

    def persistProp(self, name, setterName, value):
        if setterName == 'SetImageList':
            imgList, listType = string.split(value, ',')
            imgList, listType = string.strip(imgList), string.strip(listType)
            for prop in self.textPropList:
                if prop.prop_setter == setterName and prop.params[1] == listType:
                    prop.params = [imgList, listType]
                    return
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, [imgList, listType], 'SetImageList'))
        else:
            WindowDTC.persistProp(self, name, setterName, value)


class ListCtrlColumnsCDTC(ListCtrlColumnsConstr, CollectionDTC):
    #wxDocs = HelpCompanions.wxListCtrlDocs
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

    def appendItem(self):
        if not (self.control.GetWindowStyleFlag() & wxLC_REPORT):
            wxMessageBox('wxListCtrl must be created with the wxLC_REPORT flag.',
                  'Error', wxICON_ERROR | wxOK, self.designer)
            return
        CollectionDTC.appendItem(self)

class TreeCtrlDTC(MultiItemCtrlsConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxTreeCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'ImageList': ImageListClassLinkPropEdit,
                             #'StateImageList': ImageListClassLinkPropEdit
                             })
        self.windowStyles = ['wxTR_NO_BUTTONS', 'wxTR_HAS_BUTTONS',
                             'wxTR_EDIT_LABELS', 'wxTR_NO_LINES',
                             'wxTR_LINES_AT_ROOT',
                             #'wxTR_HIDE_ROOT',
                             'wxTR_ROW_LINES',
                             #'wxTR_HAS_VARIABLE_ROW_HEIGHT',
                             'wxTR_SINGLE', 'wxTR_MULTIPLE', 'wxTR_EXTENDED',
                             'wxTR_DEFAULT_STYLE'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxTR_HAS_BUTTONS',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['StateImageList']

    def dependentProps(self):
        return WindowDTC.dependentProps(self) + ['ImageList', 'StateImageList']

    def notification(self, compn, action):
        WindowDTC.notification(self, compn, action)
        if action == 'delete':
            if `self.control.GetImageList()` == `compn.control`:
                self.propRevertToDefault('ImageList', 'SetImageList')
                self.control.SetImageList(None)

##            if `self.control.GetStateImageList()` == `compn.control`:
##                self.propRevertToDefault('StateImageList', 'SetStateImageList')
##                self.control.SetStateImageList(None)

    def events(self):
        return WindowDTC.events(self) + ['TreeEvent']

EventCategories['ListBoxEvent'] = (EVT_LISTBOX, EVT_LISTBOX_DCLICK)
commandCategories.append('ListBoxEvent')
class ListBoxDTC(ListConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxListBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Choices'] = ChoicesConstrPropEdit
        self.windowStyles = ['wxLB_SINGLE', 'wxLB_MULTIPLE', 'wxLB_EXTENDED',
                             'wxLB_HSCROLL', 'wxLB_ALWAYS_SB', 'wxLB_NEEDED_SB',
                             'wxLB_SORT'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'choices': '[]',
                'style': '0',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ListBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ListBoxEvent', 'EVT_LISTBOX')


EventCategories['CheckListBoxEvent'] = (EVT_CHECKLISTBOX,)
class CheckListBoxDTC(ListBoxDTC):
    #wxDocs = HelpCompanions.wxCheckListBoxDocs
    def events(self):
        return ListBoxDTC.events(self) + ['CheckListBoxEvent']

EventCategories['RadioBoxEvent'] = (EVT_RADIOBOX,)
commandCategories.append('RadioBoxEvent')
class RadioBoxDTC(RadioBoxConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxRadioBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MajorDimension'] = MajorDimensionConstrPropEdit
        self.windowStyles = ['wxRA_SPECIFY_ROWS', 'wxRA_SPECIFY_COLS'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'point': position,
                'size': size,
                'choices': `['asd']`,
                'majorDimension': '1',
                'style': 'wxRA_SPECIFY_COLS',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['RadioBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('RadioBoxEvent', 'EVT_RADIOBOX')

class GenericDirCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['DefaultFilter'] = IntConstrPropEdit
        self.windowStyles = ['wxDIRCTRL_DIR_ONLY', 'wxDIRCTRL_SELECT_FIRST',
              'wxDIRCTRL_SHOW_FILTERS', 'wxDIRCTRL_3D_INTERNAL',
              'wxDIRCTRL_EDIT_LABELS'] + self.windowStyles
        self.compositeCtrl = true

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'dir': "'.'",
                'style': 'wxDIRCTRL_3D_INTERNAL | wxSUNKEN_BORDER',
                'filter': "''",
                'defaultFilter': '0',
                'name': `self.name`}

    def constructor(self):
        return {'Name': 'name', 'Position': 'pos', 'Size': 'size',
                'DefaultPath': 'dir', 'Style': 'style', 'Filter': 'filter',
                'DefaultFilter': 'defaultFilter'}


EventCategories['GridEvent'] = (EVT_GRID_CELL_LEFT_CLICK,
      EVT_GRID_CELL_RIGHT_CLICK, EVT_GRID_CELL_LEFT_DCLICK,
      EVT_GRID_CELL_RIGHT_DCLICK, EVT_GRID_LABEL_LEFT_CLICK,
      EVT_GRID_LABEL_RIGHT_CLICK, EVT_GRID_LABEL_LEFT_DCLICK,
      EVT_GRID_LABEL_RIGHT_DCLICK, EVT_GRID_ROW_SIZE, EVT_GRID_COL_SIZE,
      EVT_GRID_RANGE_SELECT, EVT_GRID_CELL_CHANGE, EVT_GRID_SELECT_CELL,
      EVT_GRID_EDITOR_SHOWN, EVT_GRID_EDITOR_HIDDEN, EVT_GRID_EDITOR_CREATED,
)

class GridDTC(WindowConstr, WindowDTC):
#    wxDocs = HelpCompanions.wxGridDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Editable'] = self.editors['GridLinesEnabled'] = BoolPropEdit
        self.editors['SelectionMode'] = EnumPropEdit
        self.compositeCtrl = true

        self.options['SelectionMode'] = [wxGrid.wxGridSelectCells,
                                         wxGrid.wxGridSelectRows,
                                         wxGrid.wxGridSelectColumns]
        self.names['SelectionMode'] = \
              {'wxGrid.wxGridSelectCells': wxGrid.wxGridSelectCells,
               'wxGrid.wxGridSelectRows': wxGrid.wxGridSelectRows,
               'wxGrid.wxGridSelectColumns': wxGrid.wxGridSelectColumns}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': '0',
                'name': `self.name`}

    def properties(self):
        return {'Editable': ('CtrlRoute',
                      wxGridPtr.IsEditable, wxGridPtr.EnableEditing),
                'GridLinesEnabled': ('CtrlRoute',
                      wxGridPtr.GridLinesEnabled, wxGridPtr.EnableGridLines)}

    def designTimeControl(self, position, size, args = None):
        dtc = WindowDTC.designTimeControl(self, position, size, args)
        dtc.CreateGrid(0, 0)
        return dtc

    def events(self):
        return WindowDTC.events(self) + ['GridEvent']

    def writeImports(self):
        return 'from wxPython.grid import *'

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + \
              ['RowLabelAlignment', 'ColLabelAlignment', 'Table',
               'DefaultEditor', 'DefaultRenderer']

#-------------------------------------------------------------------------------
import PaletteStore

PaletteStore.paletteLists['ListControls'] = []
PaletteStore.palette.append(['List Controls', 'Editor/Tabs/Lists',
                            PaletteStore.paletteLists['ListControls']])
PaletteStore.paletteLists['ListControls'].extend([wxRadioBox, wxListBox,
      wxCheckListBox, wxGrid, wxListCtrl, wxTreeCtrl])
try:   PaletteStore.paletteLists['ListControls'].append(wxGenericDirCtrl)
except NameError: pass

PaletteStore.compInfo.update({
    wxListBox: ['wxListBox', ListBoxDTC],
    wxCheckListBox: ['wxCheckListBox', CheckListBoxDTC],
    wxGrid: ['wxGrid', GridDTC],
    wxListCtrl: ['wxListCtrl', ListCtrlDTC],
    wxTreeCtrl: ['wxTreeCtrl', TreeCtrlDTC],
    wxRadioBox: ['wxRadioBox', RadioBoxDTC],
})
try: PaletteStore.compInfo[wxGenericDirCtrl] = ['wxGenericDirCtrl', GenericDirCtrlDTC]
except NameError: pass
