#-----------------------------------------------------------------------------
# Name:        SizerCompanions.py
# Purpose:     Companion classes for Sizer objects
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing Companions.SizerCompanions'

# XXX _in_sizer is not necessary, use GetContainingSizer() instead

import os, copy

from wxPython.wx import *

from wxPython.lib.rcsizer import RowColSizer

import Preferences, Utils

from BaseCompanions import UtilityDTC, CollectionDTC, CollectionIddDTC, wxNullBitmap, NYIDTC
import Companions

from PropEdit.PropertyEditors import IntConstrPropEdit, StrConstrPropEdit, \
      CollectionPropEdit, ObjEnumConstrPropEdit, EnumConstrPropEdit, \
      FlagsConstrPropEdit, WinEnumConstrPropEdit, BoolConstrPropEdit, \
      BoolPropEdit, EnumPropEdit, ReadOnlyConstrPropEdit, \
      SizerEnumConstrPropEdit, SizeConstrPropEdit
from PropEdit import Enumerations
import EventCollections, RTTI, methodparse
import PaletteStore


class SizerItemsColPropEdit(CollectionPropEdit): pass

class BlankSizer(wxBoxSizer):
    """ Used as a placeholder for initial sizer items which has None for
        the window or sizer """
    def __init__(self):
        wxBoxSizer.__init__(self, wxVERTICAL)
        self.AddSpacer((24, 24))

class SizerDTC(UtilityDTC):
    host = 'Sizers'
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors['Items'] = SizerItemsColPropEdit
        self.subCompanions['Items'] = SizerItemsCDTC

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Items': ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return UtilityDTC.dependentProps(self) + ['Items']

    def designTimeSource(self):
        return {}

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Items')
        if nv: nv.propEditor.edit(None)

    def renameCtrl(self, oldName, newName):
        UtilityDTC.renameCtrl(self, oldName, newName)

        self.designer.checkSizerConnectRename(oldName, newName)

    def renameCtrlRefs(self, oldName, newName):
        UtilityDTC.renameCtrlRefs(self, oldName, newName)

        self.designer.checkCollectionRename(oldName, newName, self)

    def recreateSizer(self):
        args = self.designer.setupArgs(self.name, self.textConstr.params,
          self.handledConstrParams, evalDct = self.designer.model.specialAttrs)
        self.control = self.designTimeObject(args)
        self.designer.objects[self.name][1] = self.control

    def recreateSizerItems(self):
        for collComp in self.collections.values():
            collComp.control = self.control
            for crt in collComp.textConstrLst:
                collComp.applyDesignTimeDefaults(crt.params, crt.method)


class SizerFlagsDTC(Companions.FlagsDTC):
    paramName = 'flag'
    propName = 'Flag'

class SizerFlagsConstrPropEdit(FlagsConstrPropEdit):
    def getSubCompanion(self):
        return SizerFlagsDTC

class SizerWinEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getObjects(self):
        designer = self.companion.designer.controllerView
        windows = designer.getObjectsOfClass(wxWindow)
        for n, w in windows.items():
            if hasattr(w, '_in_sizer') or n == 'self':
                del windows[n]
        windowNames = windows.keys()
        windowNames.sort()
        res = ['None'] + windowNames
        if self.value != 'None':
            res.insert(1, self.value)
        return res

    def getCtrlValue(self):
        return self.companion.GetWindow()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetWindow(value)

# XXX Remove 'Insert' special casing, no longer used

class SizerItemsCDTC(CollectionDTC):
    propName = 'Items'
    displayProp = 0
    indexProp = '(None)'
    insertionMethod = 'AddWindow'
    deletionMethod = 'Remove'

    additionalMethods = { 'AddSizer': ('Add sizer', 0, '(None)'),
                          'AddSpacer': ('Add spacer', '', '(None)')
                        }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Window': SizerWinEnumConstrPropEdit,
                        'Sizer': SizerEnumConstrPropEdit,
                        'Proportion': IntConstrPropEdit,
                        'Flag': SizerFlagsConstrPropEdit,
                        'Border': IntConstrPropEdit,
                        'Size': SizeConstrPropEdit,
                       }
        self.windowStyles = ['wx.LEFT', 'wx.RIGHT', 'wx.TOP', 'wx.BOTTOM', 'wx.ALL',
                             'wx.SHRINK', 'wx.GROW', 'wx.EXPAND', 'wx.SHAPED',
                             'wx.ALIGN_LEFT', 'wx.ALIGN_CENTER_HORIZONTAL',
                             'wx.ALIGN_RIGHT', 'wx.ALIGN_BOTTOM',
                             'wx.ALIGN_CENTER_VERTICAL', 'wx.ALIGN_TOP',
                             'wx.ALIGN_CENTER', 'wx.ADJUST_MINSIZE']

    def constructor(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method == 'AddWindow':
            return {'Window': 0, 'Proportion': 1, 'Flag': 'flag',
                    'Border': 'border'}
        elif tcl.method == 'AddSizer':
            return {'Sizer': 0, 'Proportion': 1, 'Flag': 'flag',
                    'Border': 'border'}
        elif tcl.method == 'AddSpacer':
            return {'Size': 0, 'Flag': 'flag',
                    'Border': 'border'}

    def designTimeSource(self, wId, method=None):
        if method is None:
            method = self.insertionMethod

        if method == 'AddWindow':
            return {0: 'None', 1: '0', 'flag': '0', 'border': '0'}
        elif method == 'AddSizer':
            return {0: 'None', 1: '0', 'flag': '0', 'border': '0'}
        elif method == 'AddSpacer':
            return {0:  'wx.Size(8, 8)', 'flag': '0', 'border': '0'}

    def notification(self, compn, action):
        if action == 'delete':
            if not isinstance(compn, CollectionDTC):
                compnSrcRef = Utils.srcRefFromCtrlName(compn.name)
                for constr in self.textConstrLst:
                    if compnSrcRef == constr.params[0]:
                        constr.params[0] = 'None'
                        self.recreateSizers()
                        return

    def appendItem(self, method=None):
        CollectionDTC.appendItem(self, method)
        self.updateGUI()

    def deleteItem(self, idx):
        CollectionDTC.deleteItem(self, idx)
        del self.textConstrLst[idx]
        self.updateGUI()

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            self.recreateSizers()
        return newIdx

    def defaultAction(self):
        constr = self.textConstrLst[self.index]
        if constr.method == 'AddWindow':
            if constr.params[0] != 'None':
                name = Utils.ctrlNameFromSrcRef(constr.params[0])
                designer = self.designer.controllerView
                compn, ctrl = designer.objects[name][:2]
                designer.inspector.selectObject(compn, true)
                designer.Raise()
                designer.selection.selectCtrl(ctrl, compn)

                wxCallAfter(designer.SetFocus)
                return true

        elif constr.method == 'AddSizer':
            if constr.params[0] != 'None':
                name = Utils.ctrlNameFromSrcRef(constr.params[0])
                compn = self.designer.objects[name][0]
                self.designer.inspector.selectObject(compn, true)
                self.designer.selectCtrls([name])

                wxCallAfter(self.designer.SetFocus)
                return true

    def designTimeDefaults(self, vals, method=None):
        if method is None:
            method = self.insertionMethod

        if method in ('AddWindow', 'AddSizer', 'Insert'):
            if method in ('AddWindow', 'AddSizer'): ctrlIdx = 0
            elif method == 'Insert':                ctrlIdx = 1

            if vals[ctrlIdx] != 'None':
                srcRef = vals[ctrlIdx]
                try:
                    # XXX improve
                    int(srcRef)
                except:
                    params = copy.copy(vals)
                    del params[ctrlIdx]
                    dtd = CollectionDTC.designTimeDefaults(self, params, method)
                    dtd[ctrlIdx] = self.designer.controllerView.getAllObjects()[srcRef]
                    if method == 'AddSizer':
                        dtd[ctrlIdx]._sub_sizer = self.control
                    elif method == 'AddWindow':
                        dtd[ctrlIdx]._in_sizer = self.control
                    return dtd

        return CollectionDTC.designTimeDefaults(self, vals, method)

    def applyDesignTimeDefaults(self, params, method=None):
        if method is None:
            method = self.insertionMethod

        if (method in ('AddWindow', 'AddSizer') and params[0] == 'None') or \
           (method == 'Insert' and params[1] == 'None'):
            defaults = self.designTimeDefaults(params, method)
            if method == 'Insert':
                proportion = defaults[2]
                import warnings; warnings.warn('Insert called with BlankSizer')
            else:
                proportion = defaults[1]
            self.control.AddSizer(BlankSizer(), proportion, defaults['flag'],
                                  defaults['border'])
        else:
            CollectionDTC.applyDesignTimeDefaults(self, params, method)

    def setParamAndUpdate(self, key, value):
        constr = self.textConstrLst[self.index]
        constr.params[key] = value
        self.recreateSizers()

    def GetWindow(self):
        return self.textConstrLst[self.index].params[0]
    def SetWindow(self, value):
        self.setParamAndUpdate(0, value)
        colEdKey = (self.parentCompanion.name, 'Items')
        if self.designer.collEditors.has_key(colEdKey):
            collEditView = self.designer.collEditors[colEdKey]
            wxCallAfter(self.setWindowRefresh, collEditView)

    def setWindowRefresh(self, collEditView):
        collEditView.refreshCtrl(1)
        collEditView.selectObject(self.index)
        if collEditView.frame:
            collEditView.frame.selectObject(self.index)


    GetSizer = GetWindow
    SetSizer = SetWindow

    def persistProp(self, name, setterName, value):
        CollectionDTC.persistProp(self, name, setterName, value)
        if name in ('Size'):
            self.recreateSizers()
        elif name in ('Flag', 'Border', 'Proportion'):
            if name == 'Proportion':
                name = 'Option'
            si = self.control.GetChildren()[self.index]
            getattr(si, 'Set'+name)(self.eval(value))
            self.updateGUI()

    def writeCollectionItems(self, output, stripFrmId=''):
        CollectionDTC.writeCollectionItems(self, output, stripFrmId)
        warn = 0
        for constr in self.textConstrLst:
            if constr.params[0] == 'None':
                wxLogWarning('No control/sizer for sizer item of %s'%(
                      self.parentCompanion.name))
                warn = 1
        if warn:
            wxLogWarning('None values are only valid in the Designer.\n'
                         'The generated source will be invalid outside the '
                         'Designer and should be fixed before executing.')

    def recreateSizers(self):
        self.designer.recreateSizers()
        self.updateGUI()

    def updateGUI(self):
        self.control.Layout()
        wxCallAfter(self.designer.controllerView.Refresh)

class BoxSizerDTC(SizerDTC):
    def __init__(self, name, designer, objClass):
        SizerDTC.__init__(self, name, designer, objClass)
        self.editors['Orientation'] = EnumPropEdit
        self.names['Orientation'] = {'wx.VERTICAL': wxVERTICAL,
                                     'wx.HORIZONTAL': wxHORIZONTAL}
        self.options['Orientation'] = [wxVERTICAL, wxHORIZONTAL]

    def constructor(self):
        return {'Name': 'name', 'Orientation': 'orient'}

    def designTimeSource(self):
        return {'orient': 'wx.VERTICAL'}

class GridSizerDTC(SizerDTC):
    def constructor(self):
        return {'Name': 'name', 'Rows': 'rows', 'Cols': 'cols',
                'VGap': 'vgap', 'HGap': 'hgap'}

    def designTimeSource(self):
        return {'rows': '1', 'cols': '0', 'vgap': '0', 'hgap': '0'}


class GrowablesColPropEdit(CollectionPropEdit):
    def edit(self, event):
        ce = self.companion.designer.showCollectionEditor(self.companion.name,
              self.name, false)

        growableRows, growableCols = ce.companion.getGrowables()

        fgsCompn = ce.companion.parentCompanion
        numRows = self.companion.eval(fgsCompn.textConstr.params['rows'])
        numCols = self.companion.eval(fgsCompn.textConstr.params['cols'])

        if not numRows and not numCols:
            wxLogError('Rows and Cols may not both be 0')
            return

        if not numRows or not numCols:
            numItems = len(self.companion.designer.showCollectionEditor(
                self.companion.name, 'Items', false).companion.textConstrLst)
        else:
            numItems = -1

        rows, cols = [], []
        if not numRows:
            numRows = numItems/float(numCols)
            numRows = int(numRows)+(numRows > int(numRows))
        for row in range(numRows):
            rows.append(row in growableRows)

        if not numCols:
            numCols = numItems/float(numRows)
            numCols = int(numCols)+(numCols > int(numCols))
        for col in range(numCols):
            cols.append(col in growableCols)

        from FlexGridGrowableDlg import FlexGridGrowablesDlg
        dlg = FlexGridGrowablesDlg(self.parent, rows, cols)
        try:
            res = dlg.ShowModal()
            if res == wxID_CANCEL:
                return
            if res == wxID_YES:
                ce.show()
                return

            rows = dlg.rows
            cols = dlg.cols
        finally:
            dlg.Destroy()

        ce.companion.setGrowables(rows, cols)
        ce.companion.recreateSizers()


class GrowablesCDTC(CollectionDTC):
    propName = 'Growables'
    displayProp = 0
    indexProp = '(None)'
    insertionMethod = '(None)'
    deletionMethod = '(None)'

    additionalMethods = { 'AddGrowableRow': ('Add growable row', 0, '(None)'),
                          'AddGrowableCol': ('Add growable column', 0, '(None)')
                        }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors['Index'] = IntConstrPropEdit

    def constructor(self):
        return {'Index': 0}

    def designTimeSource(self, wId, method=None):
        return {0: '0'}

    def getGrowables(self):
        rows, cols = [], []
        for constr in self.textConstrLst:
            if constr.method == 'AddGrowableRow':
                rows.append(self.eval(constr.params[0]))
            elif constr.method == 'AddGrowableCol':
                cols.append(self.eval(constr.params[0]))
        return rows, cols

    def _appendItem(self, method, idx):
        self.index = self.getCount()
        if method is None:
            method = self.insertionMethod
        collItemInit = methodparse.CollectionItemInitParse(None,
          self.sourceObjName, method, {0: str(idx)})

        self.textConstrLst.append(collItemInit)
        self.setConstr(collItemInit)

    def setGrowables(self, rows, cols):
        self.textConstrLst = []
        for idx, row in zip(range(len(rows)), rows):
            if row:
                self._appendItem('AddGrowableRow', idx)
        for idx, col in zip(range(len(rows)), cols):
            if col:
                self._appendItem('AddGrowableCol', idx)

    def recreateSizers(self):
        self.designer.recreateSizers()
        self.updateGUI()

    def updateGUI(self):
        self.control.Layout()
        wxCallAfter(self.designer.controllerView.Refresh)


class FlexGridSizerDTC(GridSizerDTC):
    def __init__(self, name, designer, objClass):
        GridSizerDTC.__init__(self, name, designer, objClass)
        self.editors['Growables'] = GrowablesColPropEdit
        self.subCompanions['Growables'] = GrowablesCDTC

    def properties(self):
        props = GridSizerDTC.properties(self)
        props.update({'Growables': ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return GridSizerDTC.dependentProps(self) + ['Growables']

#class RowColSizerDTC(FlexGridSizerDTC):
#    def writeImports(self):
#        return '\n'.join( (GridSizerDTC.writeImports(self),
#                           'from wxPython.lib.rcsizer import RowColSizer') )

class ControlLinkedSizerDTC(SizerDTC):
    LinkClass = None
    ctrlParam = ''
    _linkName = ''
    def designTimeObject(self, args = None):
        if args is not None:
            self.control = apply(self.objClass, (), args)
        else:
            linkClassName = self.LinkClass.__name__[:-3]
            dtd = self.designTimeDefaults()
            linkObjs = self.designer.controllerView.getObjectsOfClass(self.LinkClass).items()
            if not linkObjs:
                raise Exception, 'No %s controls available'%linkClassName

            linkObjs.sort()
            names, objs = [], []
            for name, obj in linkObjs:
                names.append(name); objs.append(obj)

            dlg = wxSingleChoiceDialog(self.designer, 'Choose control',
                  'Create sizer', names)
            try:
                if dlg.ShowModal() != wxID_OK:
                    raise Exception, 'Must choose control to link with sizer'
                idx = dlg.GetSelection()
            finally:
                dlg.Destroy()

            self._linkName = names[idx]
            dtd[self.ctrlParam] = objs[idx]

            self.control = apply(self.objClass, (), dtd)

        return self.control

    def setConstr(self, constr):
        if self._linkName:
            constr.params[self.ctrlParam] = self._linkName
        SizerDTC.setConstr(self, constr)

    def persistConstr(self, className, params):
        if self._linkName:
            params[self.ctrlParam] = self._linkName
        SizerDTC.persistConstr(self, className, params)

    def notification(self, compn, action):
        if action == 'delete' and compn != self:
            compnSrcRef = Utils.srcRefFromCtrlName(compn.name)
            if self.textConstr.params.has_key(self.ctrlParam) and \
                  compnSrcRef == self.textConstr.params[self.ctrlParam]:
                self.designer.deleteCtrl(self.name)


class StaticBoxSizerDTC(ControlLinkedSizerDTC):
    LinkClass = wxStaticBox
    ctrlParam = 'box'
    def __init__(self, name, designer, objClass):
        ControlLinkedSizerDTC.__init__(self, name, designer, objClass)
        self.editors['Orientation'] = EnumPropEdit
        self.names['Orientation'] = {'wx.VERTICAL': wxVERTICAL,
                                     'wx.HORIZONTAL': wxHORIZONTAL}
        self.options['Orientation'] = [wxVERTICAL, wxHORIZONTAL]
        self.editors['StaticBox'] = ReadOnlyConstrPropEdit

    def constructor(self):
        return {'Name': 'name', 'StaticBox': 'box', 'Orientation': 'orient'}

    def designTimeSource(self):
        return {'box': 'None', 'orient': 'wx.VERTICAL'}



class NotebookSizerDTC(ControlLinkedSizerDTC):
    LinkClass = wxNotebook
    ctrlParam = 'nb'
    def __init__(self, name, designer, objClass):
        ControlLinkedSizerDTC.__init__(self, name, designer, objClass)
        self.editors['Notebook'] = ReadOnlyConstrPropEdit

    def constructor(self):
        return {'Name': 'name', 'Notebook': 'nb'}

    def designTimeSource(self):
        return {'nb': 'None'}

    def properties(self):
        props = ControlLinkedSizerDTC.properties(self)
        del props['Items']
        return props

    def defaultAction(self):
        pass


PaletteStore.paletteLists['ContainersLayout'].extend([
  wxBoxSizer, wxGridSizer, wxFlexGridSizer, wxStaticBoxSizer, wxNotebookSizer, # RowColSizer,
])

PaletteStore.compInfo.update({
  wxBoxSizer: ['wx.BoxSizer', BoxSizerDTC],
  wxGridSizer: ['wx.GridSizer', GridSizerDTC],
  wxFlexGridSizer: ['wx.FlexGridSizer', FlexGridSizerDTC],
  wxStaticBoxSizer: ['wx.StaticBoxSizer', StaticBoxSizerDTC],
  wxNotebookSizer: ['wx.NotebookSizer', NotebookSizerDTC]
  #RowColSizer: ['RowColSizer', RowColSizerDTC],
})
