#-----------------------------------------------------------------------------
# Name:        ContainerCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.ContainerCompanions'

import copy, string

from wxPython.wx import *

from BaseCompanions import ContainerDTC, CollectionDTC, CollectionIddDTC
import PaletteStore

from Constructors import *
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

import methodparse, sourceconst

EventCategories['PanelEvent'] = (EVT_SYS_COLOUR_CHANGED,)

class PanelDTC(WindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxPanelDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['DefaultItem'] = ButtonClassLinkPropEdit
        self.windowStyles.insert(0, 'wxTAB_TRAVERSAL')

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wxTAB_TRAVERSAL',
                'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['PanelEvent']

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['DefaultItem']

EventCategories['SashEvent'] = (EVT_SASH_DRAGGED, )
commandCategories.append('SashEvent')
class SashWindowDTC(WindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxSashWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'SashVisibleLeft' : SashVisiblePropEdit,
                             'SashVisibleTop' : SashVisiblePropEdit,
                             'SashVisibleRight' : SashVisiblePropEdit,
                             'SashVisibleBottom' : SashVisiblePropEdit})
        self.windowStyles = ['wxSW_3D', 'wxSW_3DSASH', 'wxSW_3DBORDER',
                             'wxSW_BORDER'] + self.windowStyles
        self.edgeNameMap = {'SashVisibleLeft'  : wxSASH_LEFT,
                            'SashVisibleTop'   : wxSASH_TOP,
                            'SashVisibleRight' : wxSASH_RIGHT,
                            'SashVisibleBottom': wxSASH_BOTTOM}
        for name in self.edgeNameMap.keys() + ['SashVisible']:
            self.customPropEvaluators[name] = self.EvalSashVisible
        #self.customPropEvaluators['SashVisible'] = self.EvalSashVisible

    def properties(self):
        props = ContainerDTC.properties(self)
        prop = ('NameRoute', self.GetSashVisible, self.SetSashVisible)
        for name in self.edgeNameMap.keys():
            props[name] = prop
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wxCLIP_CHILDREN | wxSW_3D',
                'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['SashEvent']

    def GetSashVisible(self, name):
        return self.edgeNameMap[name], self.control.GetSashVisible(self.edgeNameMap[name])

    def SetSashVisible(self, name, value):
        self.control.SetSashVisible(self.edgeNameMap[name], value[1])

    def EvalSashVisible(self, exprs, objects):
        res = []
        for expr in exprs:
            res.append(self.eval(expr))
        return tuple(res)

    def persistProp(self, name, setterName, value):
        if setterName == 'SetSashVisible':
            edge, visbl = string.split(value, ',')
            for prop in self.textPropList:
                if prop.prop_setter == setterName and prop.params[0] == edge:
                    prop.params = [string.strip(edge), string.strip(visbl)]
                    return
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, [string.strip(edge), string.strip(visbl)], 'SetSashVisible'))
        else:
            ContainerDTC.persistProp(self, name, setterName, value)

class SashLayoutWindowDTC(SashWindowDTC):
    #wxDocs = HelpCompanions.wxSashLayoutWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        SashWindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Alignment'   : EnumPropEdit,
                             'Orientation' : EnumPropEdit,
                            })
        self.options.update({'Alignment'   : sashLayoutAlignment,
                             'Orientation' : sashLayoutOrientation
                            })
        self.names.update({'Alignment'   : sashLayoutAlignmentNames,
                           'Orientation' : sashLayoutOrientationNames
                          })

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wxCLIP_CHILDREN | wxSW_3D',
                'name':  `self.name`}

    def properties(self):
        props = SashWindowDTC.properties(self)
        props.update({'DefaultSize': ('CompnRoute', self.GetDefaultSize,
          self.SetDefaultSize)})
        return props

    def getSizeDependentProps(self):
        return SashWindowDTC.getSizeDependentProps(self)+[('prop', 'DefaultSize')]

##    def events(self):
##        return ContainerDTC.events(self) + ['SashEvent']

    def GetDefaultSize(self, something):
        if self.control:
            return self.control.GetSize()
        else:
            return wxSize(15, 15)

    def SetDefaultSize(self, size):
        if self.control:
            self.control.SetSize(size)

    def defaultAction(self):
        # should be called from 'Relayout' command
        self.control.SetDefaultSize(self.control.GetSize())
        wxLayoutAlgorithm().LayoutWindow(self.control.GetParent())

class ScrolledWindowDTC(WindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxScrolledWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['TargetWindow'] = WindowClassLinkPropEdit

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wxHSCROLL | wxVSCROLL',
                'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['TargetWindow']

    def events(self):
        return ContainerDTC.events(self) + ['ScrollWinEvent']

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            if self.control.GetTargetWindow() == compn.control:
                self.propRevertToDefault('TargetWindow', 'SetTargetWindow')
                self.control.SetTargetWindow(self.control)

EventCategories['NotebookEvent'] = (EVT_NOTEBOOK_PAGE_CHANGED,
                                    EVT_NOTEBOOK_PAGE_CHANGING)
commandCategories.append('NotebookEvent')
class NotebookDTC(WindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxNotebookDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Pages':     CollectionPropEdit,
                             'ImageList': ImageListClassLinkPropEdit})
        self.subCompanions['Pages'] = NotebookPagesCDTC
        self.windowStyles = ['wxNB_FIXEDWIDTH', 'wxNB_LEFT', 'wxNB_RIGHT',
                             'wxNB_BOTTOM'] + self.windowStyles
        self.letClickThru = true

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Pages': ('NoneRoute', None, None)})
        return props

    def designTimeControl(self, position, size, args = None):
        ctrl = ContainerDTC.designTimeControl(self, position, size, args)
        EVT_NOTEBOOK_PAGE_CHANGED(ctrl, ctrl.GetId(), self.OnPageChanged)
        return ctrl

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size':  size,
                'style': '0',
                'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['ImageList', 'Pages']

    def dontPersistProps(self):
        return ContainerDTC.dontPersistProps(self) + ['Selection']

    def events(self):
        return ContainerDTC.events(self) + ['NotebookEvent']

    def defaultAction(self):
        self.designer.inspector.props.getNameValue('Pages').propEditor.edit(None)

    def OnPageChanged(self, event):
        try:
            if self.collections.has_key('Pages'):
                self.collections['Pages'].updateSelection(event.GetSelection())
                wxPostEvent(self.control, wxSizeEvent( self.control.GetSize() ))
        except Exception, err:
            print 'OnPageChanged exception', str(err)
        event.Skip()

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            if self.control.GetImageList() == compn.control:
                self.propRevertToDefault('ImageList', 'SetImageList')
                self.control.SetImageList(None)

class NotebookPagesCDTC(NotebookPageConstr, CollectionDTC):
    #wxDocs = HelpCompanions.wxNotebookDocs
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

        self.tempPlaceHolders = []

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Page': ('NoneRoute', None, None),
                      'Text': ('IndexRoute', wxNotebook.GetPageText.im_func, wxNotebook.SetPageText.im_func),
                      'Selected' : ('CompnRoute', self.GetPageSelected, self.SetPageSelected),
                      'ImageId': ('IndexRoute', wxNotebook.GetPageImage.im_func, wxNotebook.SetPageImage.im_func)})
        return props

##    def appendItem(self):
##        tph = wxWindow(self.control, -1)
##        self.tempPlaceHolders.append(tph)
##        CollectionDTC.appendItem(self)

    def designTimeSource(self, wId):
        return {'pPage': 'None',
                'strText': `'%s%d'%(self.propName, wId)`,
                'bSelect': 'true',
                'imageId': `-1`}

    def initDesignTimeEvents(self, ctrl):
        ctrlEvtHandler = self.designer.ctrlEvtHandler
        EVT_MOTION(ctrl, ctrlEvtHandler.OnMouseOver)
        EVT_LEFT_DOWN(ctrl, ctrlEvtHandler.OnControlSelect)
        EVT_LEFT_UP(ctrl, ctrlEvtHandler.OnControlRelease)
        EVT_LEFT_DCLICK(ctrl, ctrlEvtHandler.OnControlDClick)
        EVT_SIZE(ctrl, ctrlEvtHandler.OnControlResize)

    def applyDesignTimeDefaults(self, params):
        prms = copy.copy(params)

        page = BlankWindowPage(self.control, self.designer, params, 'pPage')
        self.tempPlaceHolders.append(page)
        if params['pPage'] != 'None':
            ctrl = self.designer.objects[prms['pPage'][5:]][1]
            ctrl.Reparent(page)
            page.ctrl = ctrl

        del prms['pPage']
        params = self.designTimeDefaults(prms)
        params['pPage'] = page

        apply(getattr(self.control, self.insertionMethod), (), params)

    def deleteItem(self, idx):
        activePageDeleted = self.control.GetSelection() == idx

        CollectionDTC.deleteItem(self, idx)

        # Delete BlankWindow
        self.tempPlaceHolders[idx].Destroy()
        del self.tempPlaceHolders[idx]

        # Set new active page if necesary
        if activePageDeleted:
            newIdx = idx
            if idx == len(self.textConstrLst):
                newIdx = newIdx - 1
            elif len(self.textConstrLst) == 0:
                newIdx = None

            if newIdx is not None:
                self.updateSelection(newIdx)
                self.control.SetSelection(newIdx)
                self.control.Refresh()


    def updateSelection(self, newSelection):
        idx = 0
        for constr in self.textConstrLst:
            constr.params['bSelect'] = newSelection == idx and 'true' or 'false'
            idx = idx + 1

    def defaultAction(self):
        self.SetPageSelected(true)

    def GetPageSelected(self, compn):
        pass

    def SetPageSelected(self, value):
        if value:
            self.control.SetSelection(self.index)

    def notification(self, compn, action):
        if action == 'delete':
            if compn == self:
                # Notebook page being deleted
                # XXX Consider overwriting deleteItem for this
                constr = self.textConstrLst[compn.index]
                if constr.params['pPage'] != 'None':
                    self.designer.deleteCtrl(Utils.ctrlNameFromSrcRef(constr.params['pPage']))
            else:
                for constr in self.textConstrLst:
                    if Utils.srcRefFromCtrlName(compn.name) == constr.params['pPage']:
                        constr.params['pPage'] == 'None'

                for tph in self.tempPlaceHolders:
                    if tph.ctrl == compn.control:
                        tph.clearCtrl()

    def writeCollectionItems(self, output, stripFrmId=''):
        CollectionDTC.writeCollectionItems(self, output, stripFrmId)
        warn = 0
        for constr in self.textConstrLst:
            if constr.params['pPage'] == 'None':
                wxLogWarning('No control for %s, page %s'%(
                      self.parentCompanion.name, constr.params['strText']))
                warn = 1
        if warn:
            wxLogWarning('The red-dashed area of a wxNotebook page must contain\n'\
            'a control or the generated source will be invalid outside the Designer')


[wxID_CTRLPARENT, wxID_EDITPASTE, wxID_EDITDELETE] = Utils.wxNewIds(3)

class BlankWindowPage(wxWindow):
    """ Window representing uninitialised space, it grabs the first control
        dropped onto it and replaces None with new ctrl in code.

        Used by wxNotebook for a default page
    """

    # XXX A delete of this object should remove the page from the notebook

    # XXX Copy/Cutting a blank page does not make sense ???

    def __init__(self, parent, designer, params, nameKey):
        wxWindow.__init__(self, parent, -1)
        self.params = params
        self.designer = designer

        # XXX how/when can I delete this menu, it will leak !!
        self.menu = wxMenu()
        self.menu.Append(wxID_CTRLPARENT, 'Up')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_EDITPASTE, 'Paste')
        self.menu.Append(wxID_EDITDELETE, 'Delete')
        EVT_MENU(self, wxID_CTRLPARENT, self.OnCtrlParent)
        EVT_MENU(self, wxID_EDITPASTE, self.OnCtrlPaste)
        EVT_MENU(self, wxID_EDITDELETE, self.OnCtrlDelete)

        ctrlEvtHandler = self.designer.ctrlEvtHandler
        EVT_MOTION(self, ctrlEvtHandler.OnMouseOver)
        EVT_LEFT_DOWN(self, self.OnControlSelect)
        EVT_LEFT_UP(self, ctrlEvtHandler.OnControlRelease)
        EVT_LEFT_DCLICK(self, ctrlEvtHandler.OnControlDClick)
        EVT_SIZE(self, self.OnControlResize)
        EVT_MOVE(self, self.OnControlMove)
        EVT_PAINT(self, self.OnPaint)
        EVT_RIGHT_UP(self, self.OnPopupMenu)

        self.SetName(parent.GetName())
        self.ctrl = None
        self.nameKey = nameKey

        self.proxyContainer = true

    def clearCtrl(self):
        self.ctrl = None
        self.params[self.nameKey] = 'None'

    def OnControlSelect(self, event):
        """ Select parent of proxy container or create new control, update
            page reference to it and resize new ctrl to fill proxy container
        """
        dsgn = self.designer
        new = dsgn.compPal.selection
        if self.ctrl:
            dsgn.selectControlByPos(self.ctrl, event.GetPosition(), event.ShiftDown())
        else:
            dsgn.ctrlEvtHandler.OnControlSelect(event)

        if new:
            self.linkToNewestControl()

    def OnControlResize(self, event):
        """ Child ctrl of the proxy container should be sized to fill the control
        """
        if self.ctrl:
            p = self.GetPosition()
            s = self.GetSize()
            self.ctrl.SetDimensions(0, 0, s.x, s.y)
        else:
            self.designer.ctrlEvtHandler.OnControlResize(event)

    dashSize = 8
    def OnPaint(self, event):
        """ Draw red dash pattern, hopefully implying danger are that must be
            filled
        """
        try:
            if self.ctrl is None:
                dc = wxPaintDC(self)
                sze = self.GetClientSize()

                dc.SetPen(wxRED_PEN)
                dc.BeginDrawing()
                try:
                    for i in range((sze.x + sze.y) / self.dashSize):
                        dc.DrawLine(0, i*self.dashSize, i*self.dashSize, 0)
                finally:
                    dc.EndDrawing()
        finally:
            event.Skip()

    def OnControlMove(self, event):
        """ When moved or sized, ignore and fill the proxy container
        """
        parent = self.GetParent()
        wxPostEvent(parent, wxSizeEvent( parent.GetSize() ))

    def OnCtrlParent(self, event):
        self.designer.OnSelectParent(event)

    def OnCtrlPaste(self, event):
        self.designer.OnPasteSelected(event)

    def OnCtrlDelete(self, event):
        self.designer.OnControlDelete(event)

    def OnPopupMenu(self, event):
        self.PopupMenu(self.menu, event.GetPosition())

    def linkToNewestControl(self):
        self.ctrl = self.designer.objects[self.designer.objectOrder[-1:][0]][1]
        self.params[self.nameKey] = Utils.srcRefFromCtrlName(self.ctrl.GetName())
        self.OnControlResize(None)


EventCategories['SplitterWindowEvent'] = (EVT_SPLITTER_SASH_POS_CHANGING,
                                          EVT_SPLITTER_SASH_POS_CHANGED,
                                          EVT_SPLITTER_UNSPLIT,
                                          EVT_SPLITTER_DOUBLECLICKED)
commandCategories.append('SplitterWindowEvent')

class SplitterWindowConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'point', 'Size': 'size', 'Style': 'style',
                'Name': 'name'}

class SplitterWindowDTC(SplitterWindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxSplitterWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'SplitMode': EnumPropEdit,
                             'Window1'  : WindowClassLinkWithParentPropEdit,
                             'Window2'  : WindowClassLinkWithParentPropEdit})
        self.options['SplitMode'] = splitterWindowSplitMode
        self.names['SplitMode'] = splitterWindowSplitModeNames
        self.windowStyles = ['wxSP_3D', 'wxSP_3DSASH', 'wxSP_3DBORDER',
                             'wxSP_FULLSASH', 'wxSP_BORDER', 'wxSP_NOBORDER',
                             'wxSP_PERMIT_UNSPLIT', 'wxSP_LIVE_UPDATE',
                             ] + self.windowStyles #'wxSP_3DSASH', 'wxSP_3DBORDER', 'wxSP_FULLSASH',
        self.win1 = None
        self.win2 = None

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Window1'  : ('CompnRoute', self.GetWindow1, self.SetWindow1),
                      'Window2'  : ('CompnRoute', self.GetWindow2, self.SetWindow2),
                      'SplitMode': ('CompnRoute', self.GetSplitMode, self.SetSplitMode),})
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'point': position,
                'size': self.getDefCtrlSize(),
                'style': 'wxSP_3D',
                'name':  `self.name`}

    def hideDesignTime(self):
        return ContainerDTC.hideDesignTime(self) + ['SplitMode']

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + \
          ['SplitVertically', 'SplitHorizontally']

    def events(self):
        return ContainerDTC.events(self) + ['SplitterWindowEvent']

    modeMethMap = {wxSPLIT_VERTICAL:   'SplitVertically',
                   wxSPLIT_HORIZONTAL: 'SplitHorizontally'}

    def renameCtrlRefs(self, oldName, newName):
        ContainerDTC.renameCtrlRefs(self, oldName, newName)
        # Check if subwindow references have changed
        # XXX should maybe be done with notification, action = 'rename'
        oldSrc = Utils.srcRefFromCtrlName(oldName)
        for prop in self.textPropList:
            if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                if oldSrc in prop.params:
                    prop.params[prop.params.index(oldSrc)] = \
                          Utils.srcRefFromCtrlName(newName)

    def persistProp(self, name, setterName, value):
        """ When attempting to persist the Window properties and the
            SplitMode property, add, or update a previously
            defined  SplitVertically or SplitHorizontally method."""

        if setterName in ('SetWindow1', 'SetWindow2'):
            propSN = setterName
            setterName = self.modeMethMap[self.control.GetSplitMode()]

            win1, win2 = self.GetWindow1(None), self.GetWindow2(None)
            sashPos = `self.control.GetSashPosition()`

            if win1: win1 = 'self.'+win1.GetName()
            else: win1 = 'None'
            if win2: win2 = 'self.'+win2.GetName()
            else: win2 = 'None'

            for prop in self.textPropList:
                if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                    prop.prop_setter = setterName
                    prop.params = [win1, win2, sashPos]
                    return
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, [win1, win2, sashPos], setterName))
        elif setterName == 'SetSplitMode':
            sm = self.control.GetSplitMode()
            setterName = self.modeMethMap[sm]
            for prop in self.textPropList:
                if prop.prop_setter == 'SplitVertically' and sm == wxSPLIT_HORIZONTAL or \
                   prop.prop_setter == 'SplitHorizontally' and sm == wxSPLIT_VERTICAL:
                    prop.prop_setter = setterName
                    return

        elif setterName == 'SetSashPosition':
            for prop in self.textPropList:
                if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                    prop.params[2] = value
                    return
        else:
            ContainerDTC.persistProp(self, name, setterName, value)

    def persistedPropVal(self, name, setterName):
        # Unlike usual properties, SashPosition is persisted as a Split* method
        # Therefore it needs to check the Split* method for the source value
        if setterName == 'SetSashPosition':
            for prop in self.textPropList:
                if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                    return prop.params[2]
        return ContainerDTC.persistedPropVal(self, name, setterName)

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            # If the splitter itself is deleted it should unsplit so that
            # deletion notifications from it's children won't cause
            # access to deleted controls
            if compn.control == self.control:
                self.win1 = self.win2 = None
                self.splitWindow(None, None)
                return
            # Win 1
            # If Window1 is None, splitter can only be unsplit
            if compn.control == self.GetWindow1(None):
                self.control.Unsplit()
                if self.win2: self.win2.Show(true)
                self.win1 = self.win2 = None

                setterName = self.modeMethMap[self.control.GetSplitMode()]
                self.propRevertToDefault('Window1', setterName)
                self.designer.inspector.propertyUpdate('Window1')
                self.designer.inspector.propertyUpdate('Window2')
                return
            if compn.control == self.GetWindow2(None):
                self.SetWindow2(None)
                setterName = self.modeMethMap[self.control.GetSplitMode()]
                self.persistProp('Window2', setterName, None)
                self.designer.inspector.propertyUpdate('Window2')
                return

#---Split mode------------------------------------------------------------------
    def GetSplitMode(self, compn):
        return self.control.GetSplitMode()

    def SetSplitMode(self, value):
        ctrl = self.control
        ctrl.SetSplitMode(value)

        # Resplit to force splitter to update
        w1, w2 = ctrl.GetWindow1(), ctrl.GetWindow2()
        self.splitWindow(w1, w2)

#---Window1&2 methods---------------------------------------------------------
    def splitWindow(self, window1, window2):
        ctrl = self.control
        sm = ctrl.GetSplitMode()
        sp = ctrl.GetSashPosition()

        if ctrl.IsSplit():
            ctrl.Unsplit()

        if sm == wxSPLIT_VERTICAL:
            splitMeth = ctrl.SplitVertically
        elif sm == wxSPLIT_HORIZONTAL:
            splitMeth = ctrl.SplitHorizontally
        else:
            return

        if window1 and window2:
            splitMeth(window1, window2, sp)
        elif window1 or window2:
            if window1:
                ctrl.Initialize(window1)
            else:
                ctrl.Initialize(window2)

        if window1: window1.Show(true)
        if window2: window2.Show(true)

        self.designer.inspector.propertyUpdate('SashPosition')

    def getWindow(self, win, winGetter):
        if not win:
            w = winGetter()
            if w:
                wId = w.GetId()
                for cmpn, ctrl, prnt in self.designer.objects.values():
                    if ctrl.GetId() == wId:
                        return ctrl
            return None
        else:
            return win

    def GetWindow1(self, compn):
        self.win1 = self.getWindow(self.win1, self.control.GetWindow1)
        return self.win1

    def SetWindow1(self, value):
        # XXX check win1!=win2
        self.win1 = value
        w2 = self.GetWindow2(None)
        if value:
            self.splitWindow(value, w2)
        elif w2:
            self.win1 = self.win2 = None
            self.control.Unsplit()
            self.propRevertToDefault('Window1', self.modeMethMap[self.control.GetSplitMode()])
            self.designer.inspector.propertyUpdate('Window2')

    def GetWindow2(self, compn):
        self.win2 = self.getWindow(self.win2, self.control.GetWindow2)
        return self.win2

    def SetWindow2(self, value):
        self.win2 = value
        self.splitWindow(self.control.GetWindow1(), value)

EventCategories['ToolEvent'] = (EVT_TOOL, EVT_TOOL_RCLICKED)
commandCategories.append('ToolEvent')
class ToolBarDTC(WindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxToolBarDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Tools': CollectionPropEdit})
        self.subCompanions['Tools'] = ToolBarToolsCDTC
        self.windowStyles = ['wxTB_FLAT', 'wxTB_DOCKABLE', 'wxTB_HORIZONTAL',
                             'wxTB_VERTICAL', 'wxTB_3DBUTTONS'] + self.windowStyles

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Tools': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxTB_HORIZONTAL | wxNO_BORDER',
                'name': `self.name`}

    def defaultAction(self):
        self.designer.inspector.props.getNameValue('Tools').propEditor.edit(None)

class ToolBarToolsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'ItemId': 'id', 'Bitmap': 'bitmap', 'PushedBitmap': 'pushedBitmap',
                'IsToggle': 'isToggle',
#                'XPos': 'xPos', 'YPos': 'yPos',
                'ShortHelpString': 'shortHelpString',
                'LongHelpString': 'longHelpString'}

class ToolBarToolsCDTC(ToolBarToolsConstr, CollectionIddDTC):
    #wxDocs = HelpCompanions.wxToolBarDocs
    propName = 'Tools'
    displayProp = 'shortHelpString'
    indexProp = '(None)'
    insertionMethod = 'AddTool'
    deletionMethod = 'DeleteToolByPos'
    idProp = 'id'
    idPropNameFrom = 'tools'
    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionIddDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Bitmap': BitmapConstrPropEdit,
                             'BitmapOn': BitmapConstrPropEdit,
                             'IsToggle': BoolConstrPropEdit,
                             'ShortHelpString': StrConstrPropEdit,
                             'LongHelpString': StrConstrPropEdit})

    def designTimeSource(self, wId):
        newItemName, winId = self.newUnusedItemNames(wId)
        return {'id': winId,
                'bitmap': 'wxNullBitmap',
                'pushedBitmap': 'wxNullBitmap',
                'isToggle': 'false',
                'shortHelpString': `newItemName`,
                'longHelpString': `''`}

    def finaliser(self):
        return ['', sourceconst.bodyIndent+'parent.Realize()']

    def appendItem(self):
        CollectionIddDTC.appendItem(self)
        self.control.Realize()

    def applyDesignTimeDefaults(self, params):
        CollectionIddDTC.applyDesignTimeDefaults(self, params)
        self.control.Realize()

    def events(self):
        return ['ToolEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ToolEvent', 'EVT_TOOL')

class StatusBarConstr(PropertyKeywordConstructor):
    def constructor(self): return {'Style': 'style', 'Name': 'name'}

class StatusBarDTC(StatusBarConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxStatusBarDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Fields'] = CollectionPropEdit
        self.subCompanions['Fields'] = StatusBarFieldsCDTC
        self.windowStyles = ['wxST_SIZEGRIP'] + self.windowStyles

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Fields': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'style': '0',
                'name': `self.name`}

class StatusBarFieldsCDTC(StatusBarFieldsConstr, CollectionDTC):
    #wxDocs = HelpCompanions.wxStatusBarDocs
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
        return [sourceconst.bodyIndent+'parent.SetFieldsCount(%d)'%(
                self.getCount())]+CollectionDTC.initialiser(self)

    def finaliser(self):
        return ['', sourceconst.bodyIndent+'parent.SetStatusWidths(%s)'%`self.widths`]

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
        CollectionDTC.setConstrs(self, constrLst, inits, fins)
        if len(fins):
            self.widths = self.eval(fins[0]\
              [string.find(fins[0], '(')+1 : string.rfind(fins[0], ')')])
            self.control.SetFieldsCount(len(self.widths))

    def GetWidth(self):
        return `self.widths[self.index]`

    def SetWidth(self, value):
        self.widths[self.index] = int(value)
        self.control.SetStatusWidths(self.widths)

    def GetText(self):
        return `self.control.GetStatusText(self.index)`

    def SetText(self, value):
        self.control.SetStatusText(value)

#-------------------------------------------------------------------------------

PaletteStore.paletteLists['ContainersLayout'] = []
PaletteStore.palette.append(['Containers/Layout', 'Editor/Tabs/Containers',
                             PaletteStore.paletteLists['ContainersLayout']])
PaletteStore.paletteLists['ContainersLayout'].extend([wxPanel, wxScrolledWindow,
      wxNotebook, wxSplitterWindow, wxSashWindow, wxSashLayoutWindow,
      wxToolBar, wxStatusBar, wxWindow])

PaletteStore.compInfo.update({
    wxToolBar: ['wxToolBar', ToolBarDTC],
    wxStatusBar: ['wxStatusBar', StatusBarDTC],
    wxPanel: ['wxPanel', PanelDTC],
    wxScrolledWindow: ['wxScrolledWindow', ScrolledWindowDTC],
    wxNotebook: ['wxNotebook', NotebookDTC],
    wxSplitterWindow: ['wxSplitterWindow', SplitterWindowDTC],
    wxSashWindow: ['wxSashWindow', SashWindowDTC],
    wxSashLayoutWindow: ['wxSashLayoutWindow', SashLayoutWindowDTC],
    wxWindow: ['wxWindow', ContainerDTC],
})
