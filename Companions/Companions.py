#----------------------------------------------------------------------
# Name:        Companions.py
# Purpose:     Classes defining and implementing the design time
#              behaviour of controls
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

""" Classes defining and implementing the design time behaviour of controls """

import copy

from wxPython.wx import *

print 'importing extra wxPython libraries'
from wxPython.grid import wxGrid
from wxPython.html import wxHtmlWindow
from wxPython.lib.buttons import wxGenButton, wxGenBitmapButton, wxGenBitmapTextButton
from wxPython.lib.buttons import wxGenToggleButton, wxGenBitmapToggleButton, wxGenBitmapTextToggleButton
from wxPython.stc import wxStyledTextCtrl
from wxPython.lib.anchors import LayoutAnchors
from wxPython.calendar import *
from wxPython.utils import *
from wxPython.ogl import *
from wxPython.gizmos  import *
from wxPython.help import *

# XXX Fix less of these to import * !
from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *
from EventCollections import *
from BaseCompanions import *
from Constructors import *
from Preferences import wxDefaultFrameSize, wxDefaultFramePos
import PaletteStore

#wxCalendarCtrl

PaletteStore.paletteLists.update({'ContainersLayout': [],
    'BasicControls': [],
    'Buttons': [],
    'ListControls': []})

PaletteStore.palette.extend([
  ['Containers/Layout', 'Editor/Tabs/Containers', PaletteStore.paletteLists['ContainersLayout']],
  ['Basic Controls', 'Editor/Tabs/Basic', PaletteStore.paletteLists['BasicControls']],
  ['Buttons', 'Editor/Tabs/Basic', PaletteStore.paletteLists['Buttons']],
  ['List Controls', 'Editor/Tabs/Lists', PaletteStore.paletteLists['ListControls']],
])

class BaseFrameDTC(ContainerDTC):
    def __init__(self, name, designer, frameCtrl):
        ContainerDTC.__init__(self, name, designer, None, None)
        self.control = frameCtrl
        self.editors.update({'StatusBar': StatusBarClassLinkPropEdit,
                             'MenuBar': MenuBarClassLinkPropEdit,
                             'ToolBar': ToolBarClassLinkPropEdit })
        self.triggers.update({'ToolBar': self.ChangeToolBar,
                              'StatusBar': self.ChangeStatusBar})
        self.windowStyles = ['wxDEFAULT_FRAME_STYLE', 'wxICONIZE',
              'wxMINIMIZE', 'wxMAXIMIZE', 'wxSTAY_ON_TOP', 'wxSYSTEM_MENU',
              'wxRESIZE_BORDER', 'wxTHICK_FRAME', 'wxFRAME_FLOAT_ON_PARENT',
              'wxFRAME_TOOL_WINDOW'] + self.windowStyles

    def extraConstrProps(self):
        return {}

    def dontPersistProps(self):
        # Note this is a workaround for a problem on wxGTK where the size
        # passed to the frame constructor is actually means ClientSize on wxGTK.
        # By having this property always set, this overrides the frame size
        # and uses the same size on Win and Lin
        props = ContainerDTC.dontPersistProps(self)
        props.remove('ClientSize')
        return props

    def hideDesignTime(self):
        hdt = ContainerDTC.hideDesignTime(self) + ['Label', 'Constraints', 'Anchors']
        hdt.remove('Title')
        return hdt

    def generateWindowId(self):
        if self.designer:
            self.id = Utils.windowIdentifier(self.designer.GetName(), '')
        else: self.id = `wxNewId()`

    def events(self):
        return ContainerDTC.events(self) + ['FrameEvent']

    def SetName(self, oldValue, newValue):
        self.name = newValue
        self.designer.renameFrame(oldValue, newValue)

    def ChangeToolBar(self, oldValue, newValue):
        if newValue:
            self.designer.connectToolBar(newValue)
        else:
            self.designer.disconnectToolBar(oldValue)

    def ChangeStatusBar(self, oldValue, newValue):
        pass
        # XXX Cannot refresh designer because statusbar not yet connected

    def designTimeSource(self):
        return {'title': `self.name`,
                'pos':   `wxDefaultFramePos`,
                'size':  `wxDefaultFrameSize`,
                'name':  `self.name`,
                'style': 'wxDEFAULT_FRAME_STYLE'}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + \
          ['ToolBar', 'MenuBar', 'StatusBar']

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            # StatusBar
            sb = self.control.GetStatusBar()
##            if sb and sb.GetId() == compn.control.GetId():
            if sb and `sb` == `compn.control`:
                self.propRevertToDefault('StatusBar', 'SetStatusBar')
                self.control.SetStatusBar(None)

            # MenuBar
            # XXX MenuBar's have to be handled with care
            # XXX and can only be connected to a frame once
            mb = self.control.GetMenuBar()
            if mb and `mb` == `compn.control`:
                self.propRevertToDefault('MenuBar', 'SetMenuBar')
                self.control.SetMenuBar(None)
                if wxPlatform == '__WXGTK__':
                    wxLogWarning('GTK only allows connecting the wxMenuBar once to the wxFrame')

            # ToolBar
            tb = self.control.GetToolBar()
            if tb and `tb` == `compn.control`:
                self.propRevertToDefault('ToolBar', 'SetToolBar')
                self.control.SetToolBar(None)

    def updatePosAndSize(self):
        ContainerDTC.updatePosAndSize(self)
        # Argh, this is needed so that ClientSize is up to date
        # XXX Delete links to frame bars so client size is accurate
        self.control.SetToolBar(None)
        self.control.SetStatusBar(None)
        self.control.SetMenuBar(None)
        if self.textPropList:
            for prop in self.textPropList:
                if prop.prop_name == 'ClientSize':
                    size = self.control.GetClientSize()
                    prop.params = ['wxSize(%d, %d)' % (size.x, size.y)]


class FramesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Title': 'title', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

class FrameDTC(FramesConstr, BaseFrameDTC):
    #wxDocs = HelpCompanions.wxFrameDocs
    pass

EventCategories['DialogEvent'] = (EVT_INIT_DIALOG,)
class DialogDTC(FramesConstr, BaseFrameDTC):
    #wxDocs = HelpCompanions.wxDialogDocs
    def __init__(self, name, designer, frameCtrl):
        BaseFrameDTC.__init__(self, name, designer, frameCtrl)
        self.windowStyles = ['wxDIALOG_MODAL', 'wxDIALOG_MODELESS',
              'wxDEFAULT_DIALOG_STYLE'] + self.windowStyles

    def designTimeSource(self):
        dts = BaseFrameDTC.designTimeSource(self)
        dts.update({'style': 'wxDEFAULT_DIALOG_STYLE'})
        return dts

    def events(self):
        return BaseFrameDTC.events(self) + ['DialogEvent']

class MiniFrameDTC(FramesConstr, BaseFrameDTC):
    #wxDocs = HelpCompanions.wxMiniFrameDocs
    pass

class MDIParentFrameDTC(FramesConstr, BaseFrameDTC):
    #wxDocs = HelpCompanions.wxMDIParentFrameDocs
    def designTimeSource(self):
        dts = BaseFrameDTC.designTimeSource(self)
        dts.update({'style': 'wxDEFAULT_FRAME_STYLE | wxVSCROLL | wxHSCROLL'})
        return dts

class MDIChildFrameDTC(FramesConstr, BaseFrameDTC):
    #wxDocs = HelpCompanions.wxMDIChildFrameDocs
    pass

class PopupWindowDTC(ContainerDTC):
    suppressWindowId = true
    def __init__(self, name, designer, frameCtrl):
        ContainerDTC.__init__(self, name, designer, None, None)
        self.control = frameCtrl
        self.editors['Flags'] = FlagsConstrPropEdit
        # XXX should rather be enumerated
        self.windowStyles = ['wxSIMPLE_BORDER', 'wxDOUBLE_BORDER',
                             'wxSUNKEN_BORDER', 'wxRAISED_BORDER',
                             'wxSTATIC_BORDER', 'wxNO_BORDER']
    def properties(self):
        props = ContainerDTC.properties(self)
        del props['Anchors']
        return props

    def constructor(self):
        return {'Flags': 'flags'}

    def designTimeSource(self):
        return {'flags': 'wxSIMPLE_BORDER'}

    def hideDesignTime(self):
        return ContainerDTC.hideDesignTime(self) + ['ToolBar', 'MenuBar',
              'StatusBar', 'Icon', 'Anchors', 'Constraints', 'Label']

    def SetName(self, oldValue, newValue):
        self.name = newValue
        self.designer.renameFrame(oldValue, newValue)

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
            wxLayoutAlgorithm().LayoutWindow(self.control)

class ScrolledWindowDTC(WindowConstr, ContainerDTC):
    #wxDocs = HelpCompanions.wxScrolledWindowDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['TargetWindow'] = WindowClassLinkPropEdit

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wxTAB_TRAVERSAL',
                'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['TargetWindow']

    def events(self):
        return ContainerDTC.events(self) + ['ScrollEvent']

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            if `self.control.GetTargetWindow()` == `compn.control`:
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
            if `self.control.GetImageList()` == `compn.control`:
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

    def writeCollectionItems(self, output):
        CollectionDTC.writeCollectionItems(self, output)
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
        self.designer.senderMapper.addObject(self)
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

            win1, win2, sashPos = self.GetWindow1(None), self.GetWindow2(None), `self.control.GetSashPosition()`

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

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
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
            ctrl.SplitVertically(window1, window2, sp)
        elif sm == wxSPLIT_HORIZONTAL:
            ctrl.SplitHorizontally(window1, window2, sp)

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

EventCategories['ButtonEvent'] = (EVT_BUTTON,)
commandCategories.append('ButtonEvent')

class ButtonDTC(LabeledInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxBU_LEFT', 'wxBU_TOP', 'wxBU_RIGHT',
                             'wxBU_BOTTOM'] + self.windowStyles
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0',}
                #'validator': 'wxDefaultValidator'}

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')

EventCategories['ToggleButtonEvent'] = (EVT_TOGGLEBUTTON,)
commandCategories.append('ToggleButtonEvent')

class ToggleButtonDTC(ButtonDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit

    def events(self):
        return ButtonDTC.events(self) + ['ToggleButtonEvent']


class BitmapButtonDTC(BitmapButtonConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxBitmapButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap':          BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocused'  : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})
        self.windowStyles = ['wxBU_AUTODRAW', 'wxBU_LEFT', 'wxBU_TOP',
                             'wxBU_RIGHT', 'wxBU_BOTTOM'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
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

    def defaultAction(self):
        insp = self.designer.inspector
        # Show events property page
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')

class GenButtonConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Label': 'label', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

class GenButtonDTC(GenButtonConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxDefaultDocs
    handledConstrParams = ('parent', 'ID')
    windowIdName = 'ID'
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['UseFocusIndicator'] = BoolPropEdit
        self.ctrlDisabled = true

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def writeImports(self):
        return 'from wxPython.lib.buttons import *'

class GenBitmapButtonConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

class GenBitmapButtonDTC(GenBitmapButtonConstr, GenButtonDTC):
    #wxDocs = HelpCompanions.wxDefaultDocs
    windowIdName = 'ID'
    def __init__(self, name, designer, parent, ctrlClass):
        GenButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap'         : BitmapConstrPropEdit,
                             'BitmapLabel'    : BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocus'    : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

    def defaultAction(self):
        insp = self.designer.inspector
        # Show events property page
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')

class GenBitmapTextButtonConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Label': 'label', 'Style': 'style', 'Validator': 'validator',
                'Name': 'name'}

class GenBitmapTextButtonDTC(GenBitmapTextButtonConstr, GenBitmapButtonDTC):
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

class GenToggleButtonMix:
    def __init__(self):
        self.editors['Toggle'] = BoolPropEdit

class GenToggleButtonDTC(GenButtonDTC, GenToggleButtonMix):
    def __init__(self, name, designer, parent, ctrlClass):
        GenButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        GenToggleButtonMix.__init__(self)
class GenBitmapToggleButtonDTC(GenBitmapButtonDTC, GenToggleButtonMix):
    def __init__(self, name, designer, parent, ctrlClass):
        GenBitmapButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        GenToggleButtonMix.__init__(self)
class GenBitmapTextToggleButtonDTC(GenBitmapTextButtonDTC, GenToggleButtonMix):
    def __init__(self, name, designer, parent, ctrlClass):
        GenBitmapTextButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        GenToggleButtonMix.__init__(self)


class ContextHelpButtonConstr:
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style'}

class ContextHelpButtonDTC(ContextHelpButtonConstr, WindowDTC):
    suppressWindowId = true
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxBU_AUTODRAW', 'wxBU_LEFT', 'wxBU_TOP',
                             'wxBU_RIGHT', 'wxBU_BOTTOM'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size':  size,
                'style': 'wxBU_AUTODRAW',}

    def writeImports(self):
        return 'from wxPython.help import *'


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

class ScrollBarDTC(MultiItemCtrlsConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxScrollBarDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxSB_HORIZONTAL', 'wxSB_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxSB_HORIZONTAL',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']

class ComboConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}

EventCategories['ComboEvent'] = (EVT_COMBOBOX, EVT_TEXT)
commandCategories.append('ComboEvent')
class ComboBoxDTC(ComboConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxComboBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxCB_SIMPLE', 'wxCB_DROPDOWN', 'wxCB_READONLY',
                             'wxCB_SORT'] + self.windowStyles
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'choices': '[]',
                'style': '0',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

##    def vetoedMethods(self):
##        return ['GetColumns', 'SetColumns', 'GetSelection', 'SetSelection',
##                'GetStringSelection', 'SetStringSelection']
##
##    def hideDesignTime(self):
##        return ['Label']

    def events(self):
        return ChoicedDTC.events(self) + ['ComboEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ComboEvent', 'EVT_COMBOBOX')

EventCategories['ChoiceEvent'] = (EVT_CHOICE,)
commandCategories.append('ChoiceEvent')
class ChoiceDTC(ListConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxChoiceDocs = 'wx41.htm'
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'choices': `[]`,
                'style': '0',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ChoiceEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ChoiceEvent', 'EVT_CHOICE')

class StaticTextDTC(LabeledNonInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticTextDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxALIGN_LEFT', 'wxALIGN_RIGHT', 'wxALIGN_CENTRE',
                             'wxST_NO_AUTORESIZE'] + self.windowStyles
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

EventCategories['TextCtrlEvent'] = (EVT_TEXT, EVT_TEXT_ENTER, EVT_TEXT_URL, EVT_TEXT_MAXLEN)
commandCategories.append('TextCtrlEvent')
class TextCtrlDTC(TextCtrlConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxTextCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxTE_PROCESS_ENTER', 'wxTE_PROCESS_TAB',
                             'wxTE_MULTILINE', 'wxTE_PASSWORD',
                             'wxTE_READONLY', 'wxTE_RICH', 'wxTE_AUTO_URL',
                             'wxTE_NOHIDESEL',
                             ] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + \
              ['Selection', 'Title', 'Label', 'DefaultStyle']

    def events(self):
        return WindowDTC.events(self) + ['TextCtrlEvent']

EventCategories['RadioButtonEvent'] = (EVT_RADIOBUTTON,)
commandCategories.append('RadioButtonEvent')
class RadioButtonDTC(LabeledInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxRadioButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
        self.windowStyles = ['wxRB_GROUP'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['RadioButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('RadioButtonEvent', 'EVT_RADIOBUTTON')

EventCategories['CheckBoxEvent'] = (EVT_CHECKBOX,)
commandCategories.append('CheckBoxEvent')
class CheckBoxDTC(LabeledInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxCheckBoxDocs = 'wx39.htm'
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['CheckBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('CheckBoxEvent', 'EVT_CHECKBOX')

class SpinButtonDTC(WindowConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxSpinButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxSP_HORIZONTAL', 'wxSP_VERTICAL',
                             'wxSP_ARROW_KEYS', 'wxSP_WRAP'] + self.windowStyles
        self.customPropEvaluators['Range'] = self.EvalRange

    def properties(self):
        props = WindowDTC.properties(self)
        props['Range'] = ('CompnRoute', self.GetRange, self.SetRange)
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxSP_HORIZONTAL',
## cfd           'validator': 'wxDefaultValidator',
                'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['SpinEvent', 'CmdScrollEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('SpinEvent', 'EVT_SPIN')

    def GetRange(self, dummy):
        return (self.control.GetMin(), self.control.GetMax())

    def SetRange(self, value):
        self.control.SetRange(value[0], value[1])

    def EvalRange(self, exprs, objects):
        res = []
        for expr in exprs:
            res.append(self.eval(expr))
        return tuple(res)

    def persistProp(self, name, setterName, value):
        if setterName == 'SetRange':
            rMin, rMax = self.eval(value)
            newParams = [`rMin`, `rMax`]
            # edit if exists
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    prop.params = newParams
                    return
            # add if not defined
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, newParams, 'SetRange'))
        else:
            WindowDTC.persistProp(self, name, setterName, value)

class SliderConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'MinValue': 'minValue', 'MaxValue': 'maxValue',
                'Position': 'point', 'Size': 'size', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}

# XXX FreqTick handled wrong
EventCategories['SliderEvent'] = (EVT_SLIDER,)
commandCategories.append('SliderEvent')
class SliderDTC(SliderConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxSliderDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MinValue'] = IntConstrPropEdit
        self.editors['MaxValue'] = IntConstrPropEdit
        self.windowStyles = ['wxSL_HORIZONTAL', 'wxSL_VERTICAL',
                             'wxSL_AUTOTICKS', 'wxSL_LABELS', 'wxSL_LEFT',
                             'wxSL_RIGHT', 'wxSL_TOP',
                             'wxSL_SELRANGE'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'value': '0',
                'minValue': '0',
                'maxValue': '100',
                'point': position,
                'size': size,
                'style': 'wxSL_HORIZONTAL',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent', 'SliderEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('SliderEvent', 'EVT_SLIDER')

class GaugeConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Range': 'range', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

class GaugeDTC(GaugeConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxGaugeDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxGA_HORIZONTAL', 'wxGA_VERTICAL',
                        'wxGA_PROGRESSBAR', 'wxGA_SMOOTH'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'range': '100',
                'pos': position,
                'size': size,
                'style': 'wxGA_HORIZONTAL',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

class StaticBoxDTC(LabeledNonInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticBoxDocs
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': 'wxSize(150, 150)',
                'style': '0',
                'name': `self.name`}

class StaticLineDTC(WindowConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticLineDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxLI_HORIZONTAL', 'wxLI_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

EventCategories['ListBoxEvent'] = (EVT_LISTBOX, EVT_LISTBOX_DCLICK)
commandCategories.append('ListBoxEvent')
class ListBoxDTC(ListConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxListBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
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


class CheckListBoxDTC(ListBoxDTC):
    #wxDocs = HelpCompanions.wxCheckListBoxDocs
    pass


class StaticBitmapDTC(StaticBitmapConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticBitmapDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Bitmap'] = BitmapPropEdit

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

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


class GridDTC(WindowConstr, WindowDTC):
#    wxDocs = HelpCompanions.wxGridDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Editable'] = self.editors['EditInPlace'] = BoolPropEdit

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def designTimeControl(self, position, size, args = None):
        dtc = WindowDTC.designTimeControl(self, position, size, args)
        dtc.Enable(false)
        return dtc

    def writeImports(self):
        return 'from wxPython.grid import *'

    def vetoedMethods(self):
        # XXX This vetoes all methods introduced by the grid !!!
        # XXX Somehow calling the getters of the grid object causes it to
        # XXX crash later on
        # XXX It will take some time to probe which Getter are guilty
        return dir(self.control.__class__.__bases__[0])

# Getters
##    'GetBatchCount',
##    'GetCellAlignment', 'GetCellBackgroundColour', 'GetCellEditor',
##    'GetCellFont', 'GetCellHighlightColour', 'GetCellRenderer',
##    'GetCellTextColour', 'GetCellValue', 'GetColLabelAlignment',
##    'GetColLabelSize', 'GetColLabelValue', 'GetColSize',
##    'GetDefaultCellAlignment', 'GetDefaultCellBackgroundColour',
##    'GetDefaultCellFont', 'GetDefaultCellTextColour',
##    'GetDefaultColLabelSize', 'GetDefaultColSize', 'GetDefaultEditor',
##    'GetDefaultEditorForCell', 'GetDefaultEditorForType',
##    'GetDefaultRenderer', 'GetDefaultRendererForCell',
##    'GetDefaultRendererForType', 'GetDefaultRowLabelSize',
##    'GetDefaultRowSize', 'GetGridCursorCol', 'GetGridCursorRow',
##    'GetGridLineColour', 'GetLabelBackgroundColour', 'GetLabelFont',
##    'GetLabelTextColour', 'GetNumberCols', 'GetNumberRows',
##    'GetRowLabelAlignment', 'GetRowLabelSize', 'GetRowLabelValue',
##    'GetRowSize', 'GetSelectionBackground', 'GetSelectionForeground',
##    'GetTable', 'GetTextBoxSize',
# Setters
##    'SetCellAlignment',
##    'SetCellBackgroundColour', 'SetCellEditor', 'SetCellFont',
##    'SetCellHighlightColour', 'SetCellRenderer', 'SetCellTextColour',
##    'SetCellValue', 'SetColAttr', 'SetColFormatBool',
##    'SetColFormatCustom', 'SetColFormatFloat', 'SetColFormatNumber',
##    'SetColLabelAlignment', 'SetColLabelSize', 'SetColLabelValue',
##    'SetColMinimalWidth', 'SetColSize', 'SetDefaultCellAlignment',
##    'SetDefaultCellBackgroundColour', 'SetDefaultCellFont',
##    'SetDefaultCellTextColour', 'SetDefaultColSize',
##    'SetDefaultEditor', 'SetDefaultRenderer', 'SetDefaultRowSize',
##    'SetGridCursor', 'SetGridLineColour', 'SetLabelBackgroundColour',
##    'SetLabelFont', 'SetLabelTextColour', 'SetMargins',
##    'SetReadOnly', 'SetRowAttr', 'SetRowLabelAlignment',
##    'SetRowLabelSize', 'SetRowLabelValue',
##    'SetRowMinimalHeight', 'SetRowSize', 'SetSelectionBackground',
##    'SetSelectionForeground', 'SetSelectionMode',
##    'SetTable',


class HtmlWindowDTC(HtmlWindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        del self.editors['Style']

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
##                'style': 'wxHW_SCROLLBAR_AUTO',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']

    def writeImports(self):
        return 'from wxPython.html import *'


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
        return ['', '        parent.Realize()']

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
        self.windowStyles = ['wxSB_SIZEGRIP'] + self.windowStyles

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
        return `self.control.GetStatusText(self.index)`

    def SetText(self, value):
        self.control.SetStatusText(value)

#---Helpers---------------------------------------------------------------------

class FontDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'FaceName'  : EnumPropEdit,
                        'Family'    : EnumPropEdit,
                        'Style'     : EnumPropEdit,
                        'Weight'    : EnumPropEdit,
                        'Underlined': BoolPropEdit,}

        fontEnum = wxFontEnumerator()
        fontEnum.EnumerateFacenames()
        fontNameList = fontEnum.GetFacenames()
        fontFaceName = []
        fontFaceNameNames = {}
        for fnt in fontNameList:
            fontFaceName.append(fnt)
            fontFaceNameNames[fnt] = fnt

        self.options = {'FaceName' : fontFaceName,
                        'Family'   : fontFamily,
                        'Style'    : fontStyle,
                        'Weight'   : fontWeight,}
        self.names = {'FaceName' : fontFaceNameNames,
                      'Family'   : fontFamilyNames,
                      'Style'    : fontStyleNames,
                      'Weight'   : fontWeightNames,}

class ColourDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'Red'    : IntPropEdit,
                        'Green'  : IntPropEdit,
                        'Blue'   : IntPropEdit,}
    def properties(self):
        return {'Red'  : ('CompnRoute', self.GetRed, self.SetRed),
                'Green': ('CompnRoute', self.GetGreen, self.SetGreen),
                'Blue' : ('CompnRoute', self.GetBlue, self.SetBlue),}

    def GetRed(self, cmpn):
        return self.obj.Red()
    def SetRed(self, value):
        self.obj.Set(max(min(value, 255), 0), self.obj.Green(), self.obj.Blue())

    def GetGreen(self, cmpn):
        return self.obj.Green()
    def SetGreen(self, value):
        self.obj.Set(self.obj.Red(), max(min(value, 255), 0), self.obj.Blue())

    def GetBlue(self, cmpn):
        return self.obj.Blue()
    def SetBlue(self, value):
        self.obj.Set(self.obj.Red(), self.obj.Green(), max(min(value, 255), 0))

class PosDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'X' : IntPropEdit,
                        'Y' : IntPropEdit}

    def properties(self):
        return {'X': ('CompnRoute', self.GetX, self.SetX),
                'Y': ('CompnRoute', self.GetY, self.SetY)}

    def GetX(self, comp):
        return self.obj.x
    def SetX(self, value):
        self.obj.Set(value, self.obj.y)

    def GetY(self, comp):
        return self.obj.y
    def SetY(self, value):
        self.obj.Set(self.obj.x, value)

class SizeDTC(HelperDTC): pass

class AnchorsDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'Left'   : BoolPropEdit,
                        'Top'    : BoolPropEdit,
                        'Right'  : BoolPropEdit,
                        'Bottom' : BoolPropEdit}
        self.anchCtrl = cmpn.control
        self.assureAnchors()
        self.GetLeftAnchor('')
        self.GetTopAnchor('')
        self.GetRightAnchor('')
        self.GetBottomAnchor('')

    def properties(self):
        return {'Left'    : ('CompnRoute', self.GetLeftAnchor, self.SetLeftAnchor),
                'Top'     : ('CompnRoute', self.GetTopAnchor, self.SetTopAnchor),
                'Right'   : ('CompnRoute', self.GetRightAnchor, self.SetRightAnchor),
                'Bottom'  : ('CompnRoute', self.GetBottomAnchor, self.SetBottomAnchor),}

##    def getPropList(self):
##        props = self.properties()
##        keys = props.keys()
##        keys.sort();keys.reverse()
##        pl = []
##        for key in keys:
##            rType, getter, setter = props[key]
##            pl.append(RTTI.PropertyWrapper(key, rType, getter, setter))
##        return {'properties': pl}

    def assureAnchors(self):
        if not self.ownerCompn.anchorSettings:
            self.ownerCompn.defaultAnchors()

    def updateAnchors(self):
        from wxPython.lib.anchors import LayoutAnchors
        self.ownerCompn.anchorSettings = [self.left, self.top, self.right, self.bottom]
        self.obj = LayoutAnchors(self.anchCtrl, self.left, self.top, self.right, self.bottom)

    def GetLeftAnchor(self, name):
        self.assureAnchors()
        self.left = self.ownerCompn.anchorSettings[0]
        return self.left
    def SetLeftAnchor(self, value):
        self.assureAnchors()
        self.left = value
        self.updateAnchors()

    def GetTopAnchor(self, name):
        self.assureAnchors()
        self.top = self.ownerCompn.anchorSettings[1]
        return self.top
    def SetTopAnchor(self, value):
        self.assureAnchors()
        self.top = value
        self.updateAnchors()

    def GetRightAnchor(self, name):
        self.assureAnchors()
        self.right = self.ownerCompn.anchorSettings[2]
        return self.right
    def SetRightAnchor(self, value):
        self.assureAnchors()
        self.right = value
        self.updateAnchors()

    def GetBottomAnchor(self, name):
        self.assureAnchors()
        self.bottom = self.ownerCompn.anchorSettings[3]
        return self.bottom
    def SetBottomAnchor(self, value):
        self.assureAnchors()
        self.bottom = value
        self.updateAnchors()


class BaseFlagsDTC(HelperDTC):
    paramName = 'param'
    propName = 'Prop'
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {}
        for flag in self.ownerCompn.windowStyles:
            self.editors[flag] = BoolPropEdit

    # XXX One of these 2 methods is redundant !

    def properties(self):
        props = {}
        prop = ('NameRoute', self.GetStyle, self.SetStyle)
        for flag in self.ownerCompn.windowStyles:
            props[flag] = prop
        return props

    def getPropList(self):
        propLst = []
        for prop in self.ownerCompn.windowStyles:
            propLst.append(RTTI.PropertyWrapper(prop, 'NameRoute',
                  self.GetStyle, self.SetStyle))
        return {'constructor':[], 'properties': propLst}

    def GetStyle(self, name):
        return name in string.split(self.ownerCompn.textConstr.params[self.paramName], ' | ')

    def SetStyle(self, name, value):
        flags = string.split(self.ownerCompn.textConstr.params[self.paramName], ' | ')
        if value:
            if name not in flags:
                if '0' in flags:
                    flags.remove('0')
                flags.insert(0, name)
        else:
            if name in flags:
                flags.remove(name)
                if not flags:
                    flags.append('0')
        flagsSrc = string.join(flags, ' | ')
        self.ownerCompn.textConstr.params[self.paramName] = flagsSrc
        self.designer.inspector.constructorUpdate(self.propName)
        flagsVal = self.eval(flagsSrc)
        ctrl = self.ownerCompn.control
        if hasattr(ctrl, 'SetWindowStyleFlag'):
            ctrl.SetWindowStyleFlag(flagsVal)

class WindowStyleDTC(BaseFlagsDTC):
    paramName = 'style'
    propName = 'Style'

class FlagsDTC(BaseFlagsDTC):
    paramName = 'flags'
    propName = 'Flags'

PaletteStore.paletteLists['ContainersLayout'].extend([wxPanel, wxScrolledWindow,
      wxNotebook, wxSplitterWindow, wxSashWindow, wxSashLayoutWindow,
      wxToolBar, wxStatusBar, wxWindow])
PaletteStore.paletteLists['BasicControls'].extend([wxStaticText, wxTextCtrl,
      wxComboBox, wxChoice, wxCheckBox, wxRadioButton, wxSlider, wxGauge,
      wxScrollBar, wxStaticBitmap, wxStaticLine, wxStaticBox, wxHtmlWindow])
PaletteStore.paletteLists['Buttons'].extend([wxButton, wxBitmapButton,
      wxSpinButton, wxToggleButton,
      wxGenButton, wxGenBitmapButton, wxGenBitmapTextButton,
      wxGenToggleButton, wxGenBitmapToggleButton, wxGenBitmapTextToggleButton,
      wxContextHelpButton])
PaletteStore.paletteLists['ListControls'].extend([wxRadioBox, wxListBox,
      wxCheckListBox, wxGrid, wxListCtrl, wxTreeCtrl])

PaletteStore.compInfo.update({wxApp: ['wxApp', None],
    wxFrame: ['wxFrame', FrameDTC],
    wxDialog: ['wxDialog', DialogDTC],
    wxMiniFrame: ['wxMiniFrame', MiniFrameDTC],
    wxMDIParentFrame: ['wxMDIParentFrame', MDIParentFrameDTC],
    wxMDIChildFrame: ['wxMDIChildFrame', MDIChildFrameDTC],
    wxPopupWindow: ['wxPopupWindow', PopupWindowDTC],
    wxPopupTransientWindow: ['wxPopupTransientWindow', PopupWindowDTC],
    wxToolBar: ['wxToolBar', ToolBarDTC],
    wxStatusBar: ['wxStatusBar', StatusBarDTC],
    wxPanel: ['wxPanel', PanelDTC],
    wxScrolledWindow: ['wxScrolledWindow', ScrolledWindowDTC],
    wxNotebook: ['wxNotebook', NotebookDTC],
    wxSplitterWindow: ['wxSplitterWindow', SplitterWindowDTC],
    wxStaticText: ['wxStaticText', StaticTextDTC],
    wxTextCtrl: ['wxTextCtrl', TextCtrlDTC],
    wxChoice: ['wxChoice', ChoiceDTC],
    wxComboBox: ['wxComboBox', ComboBoxDTC],
    wxCheckBox: ['wxCheckBox', CheckBoxDTC],
    wxButton: ['wxButton', ButtonDTC],
    wxBitmapButton: ['wxBitmapButton', BitmapButtonDTC],
    wxRadioButton: ['wxRadioButton', RadioButtonDTC],
    wxSpinButton: ['wxSpinButton', SpinButtonDTC],
    wxSlider: ['wxSlider', SliderDTC],
    wxGauge: ['wxGauge', GaugeDTC],
    wxStaticBitmap: ['wxStaticBitmap', StaticBitmapDTC],
    wxListBox: ['wxListBox', ListBoxDTC],
    wxCheckListBox: ['wxCheckListBox', CheckListBoxDTC],
    wxGrid: ['wxGrid', GridDTC],
    wxListCtrl: ['wxListCtrl', ListCtrlDTC],
    wxTreeCtrl: ['wxTreeCtrl', TreeCtrlDTC],
    wxScrollBar: ['wxScrollBar', ScrollBarDTC],
    wxStaticBox: ['wxStaticBox', StaticBoxDTC],
    wxStaticLine: ['wxStaticLine', StaticLineDTC],
    wxRadioBox: ['wxRadioBox', RadioBoxDTC],
    wxHtmlWindow: ['wxHtmlWindow', HtmlWindowDTC],
    wxSashWindow: ['wxSashWindow', SashWindowDTC],
    wxSashLayoutWindow: ['wxSashLayoutWindow', SashLayoutWindowDTC],
#    wxBoxSizer: ['wxBoxSizer', BoxSizerDTC],
    wxStyledTextCtrl: ['wxStyledTextCtrl', NYIDTC],
    wxSpinCtrl: ['wxSpinCtrl', NYIDTC],
    wxGenButton: ['wxGenButton', GenButtonDTC],
    wxGenBitmapButton: ['wxGenBitmapButton', GenBitmapButtonDTC],
    wxGenToggleButton: ['wxGenToggleButton', GenToggleButtonDTC],
    wxGenBitmapToggleButton: ['wxGenBitmapToggleButton', GenBitmapToggleButtonDTC],
    wxGenBitmapTextButton: ['wxGenBitmapTextButton', GenBitmapTextButtonDTC],
    wxGenBitmapTextToggleButton: ['wxGenBitmapTextToggleButton', GenBitmapTextToggleButtonDTC],
    wxWindow: ['wxWindow', ContainerDTC],
    wxToggleButton: ['wxToggleButton', ToggleButtonDTC],
    wxContextHelpButton: ['wxContextHelpButton', ContextHelpButtonDTC],
})

PaletteStore.helperClasses.update({'wxFontPtr': FontDTC,
    'wxColourPtr': ColourDTC,
    'Anchors': AnchorsDTC
})
