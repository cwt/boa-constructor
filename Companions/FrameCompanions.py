#-----------------------------------------------------------------------------
# Name:        FrameCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.FrameCompanions'

from wxPython.wx import *

from BaseCompanions import ContainerDTC

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

from Preferences import wxDefaultFrameSize, wxDefaultFramePos

import sourceconst

class BaseFrameDTC(ContainerDTC):
    defFramePos = wxPyDefaultPosition
    defFrameSize = wxPyDefaultSize
    defFrameStyle = wxDEFAULT_FRAME_STYLE
    
    dialogLayout = false
    
    def __init__(self, name, designer, frameCtrl):
        ContainerDTC.__init__(self, name, designer, None, None)
        self.control = frameCtrl

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

    def properties(self):
        props = ContainerDTC.properties(self)
        del props['Anchors']
        return props

    def hideDesignTime(self):
        hdt = ContainerDTC.hideDesignTime(self) + ['Label', 'Constraints']
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

    def updatePosAndSize(self):
        ContainerDTC.updatePosAndSize(self)
        # Argh, this is needed so that ClientSize is up to date
        if self.textPropList:
            for prop in self.textPropList:
                if prop.prop_name == 'ClientSize':
                    size = self.control.GetClientSize()
                    prop.params = ['wx.Size(%d, %d)' % (size.x, size.y)]

    def writeConstructor(self, output, collectionMethod, stripFrmId=''):
        ContainerDTC.writeConstructor(self, output, collectionMethod, stripFrmId='')
        if self.textConstr:
            # Add call to init utils after frame constructor
            if self.textConstr.comp_name == '' and \
              collectionMethod == sourceconst.init_ctrls:
                if self.designer.dataView.objects:
                    output.append('%sself.%s()'%(sourceconst.bodyIndent, 
                                                 sourceconst.init_utils))

class FramesConstr(Constructors.PropertyKeywordConstructor):
    def constructor(self):
        return {'Title': 'title', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

class FrameDTC(FramesConstr, BaseFrameDTC):
    #wxDocs = HelpCompanions.wxFrameDocs
    def __init__(self, name, designer, frameCtrl):
        BaseFrameDTC.__init__(self, name, designer, frameCtrl)

        self.editors.update({'StatusBar': StatusBarClassLinkPropEdit,
                             'MenuBar': MenuBarClassLinkPropEdit,
                             'ToolBar': ToolBarClassLinkPropEdit })
        self.triggers.update({'ToolBar': self.ChangeToolBar})
        self.windowStyles = ['wx.DEFAULT_FRAME_STYLE', 'wx.ICONIZE',
              'wx.MINIMIZE', 'wx.MAXIMIZE', 'wx.STAY_ON_TOP', 'wx.SYSTEM_MENU',
              'wx.RESIZE_BORDER', 'wx.FRAME_FLOAT_ON_PARENT',
              'wx.FRAME_TOOL_WINDOW'] + self.windowStyles

    def designTimeSource(self):
        return {'title': `self.name`,
                'pos':   `wxDefaultFramePos`,
                'size':  `wxDefaultFrameSize`,
                'name':  `self.name`,
                'style': 'wx.DEFAULT_FRAME_STYLE'}

    def dependentProps(self):
        return BaseFrameDTC.dependentProps(self) + \
          ['ToolBar', 'MenuBar', 'StatusBar']

    def hideDesignTime(self):
        return BaseFrameDTC.hideDesignTime(self) + ['StatusBar']

    def properties(self):
        props = BaseFrameDTC.properties(self)
        props['StatusBar'] = ('CompnRoute', self.GetStatusBar, self.SetStatusBar)
        return props

    def notification(self, compn, action):
        BaseFrameDTC.notification(self, compn, action)
        if action == 'delete':
            # StatusBar
            sb = self.control.GetStatusBar()
            if sb and sb == compn.control:
                self.propRevertToDefault('StatusBar', 'SetStatusBar')
                self.control.SetStatusBar(None)

            # MenuBar
            # XXX MenuBar's have to be handled with care
            # XXX and can only be connected to a frame once
            # XXX Actually not even once!
            mb = self.control.GetMenuBar()
            if mb and `mb` == `compn.control`:
                if wxPlatform == '__WXGTK__':
                    raise 'May not delete a wxMenuBar, it would cause a segfault on wxGTK'
                self.propRevertToDefault('MenuBar', 'SetMenuBar')
                self.control.SetMenuBar(None)
                #if wxPlatform == '__WXGTK__':
                #    wxLogWarning('GTK only allows connecting the wxMenuBar once to the wxFrame')

            # ToolBar
            tb = self.control.GetToolBar()
            if tb and `tb` == `compn.control`:
                self.propRevertToDefault('ToolBar', 'SetToolBar')
                self.control.SetToolBar(None)

    def updatePosAndSize(self):
        # XXX Delete links to frame bars so client size is accurate
        self.control.SetToolBar(None)
        self.control.SetStatusBar(None)
        self.control.SetMenuBar(None)

        BaseFrameDTC.updatePosAndSize(self)

    def ChangeToolBar(self, oldValue, newValue):
        if newValue:
            self.designer.connectToolBar(newValue)
        else:
            self.designer.disconnectToolBar(oldValue)

    def GetStatusBar(self, x):
        return self.control.GetStatusBar()

    def SetStatusBar(self, value):
        self.control.SetStatusBar(value)
        # force a resize event so that statusbar can layout
        if value: 
            self.control.SendSizeEvent()


EventCategories['DialogEvent'] = ('wx.EVT_INIT_DIALOG',)
class DialogDTC(FramesConstr, BaseFrameDTC):
    dialogLayout = true
    
    #wxDocs = HelpCompanions.wxDialogDocs
    def __init__(self, name, designer, frameCtrl):
        BaseFrameDTC.__init__(self, name, designer, frameCtrl)
        self.windowStyles = ['wx.DIALOG_MODAL', 'wx.DIALOG_MODELESS',
              'wx.CAPTION', 'wx.DEFAULT_DIALOG_STYLE', 'wx.RESIZE_BORDER',
              'wx.THICK_FRAME', 'wx.STAY_ON_TOP', 'wx.NO_3D', 'wx.DIALOG_NO_PARENT']\
              + self.windowStyles

    def hideDesignTime(self):
        # Because the Designer is actually a wxFrame pretending to be a
        # wxDialog, introspection will pick up wxFrame specific properties
        # which must be supressed
        return BaseFrameDTC.hideDesignTime(self) + ['ToolBar', 'MenuBar',
              'StatusBar', 'StatusBarPane']

    def designTimeSource(self):
        return {'title': `self.name`,
                'pos':   `wxDefaultFramePos`,
                'size':  `wxDefaultFrameSize`,
                'name':  `self.name`,
                'style': 'wx.DEFAULT_DIALOG_STYLE'}

    def events(self):
        return BaseFrameDTC.events(self) + ['DialogEvent']

class MiniFrameDTC(FramesConstr, FrameDTC):
    #wxDocs = HelpCompanions.wxMiniFrameDocs
    def __init__(self, name, designer, frameCtrl):
        FrameDTC.__init__(self, name, designer, frameCtrl)
        self.windowStyles.extend(['wx.TINY_CAPTION_HORIZ', 'wx.TINY_CAPTION_VERT'])

class MDIParentFrameDTC(FramesConstr, FrameDTC):
    #wxDocs = HelpCompanions.wxMDIParentFrameDocs
    def designTimeSource(self):
        dts = FrameDTC.designTimeSource(self)
        dts.update({'style': 'wx.DEFAULT_FRAME_STYLE | wx.VSCROLL | wx.HSCROLL'})
        return dts

class MDIChildFrameDTC(FramesConstr, FrameDTC):
    #wxDocs = HelpCompanions.wxMDIChildFrameDocs
    pass

class PopupWindowDTC(ContainerDTC):
    defFramePos = wxPyDefaultPosition
    defFrameSize = wxPyDefaultSize
    defFrameStyle = wxDEFAULT_FRAME_STYLE
    
    dialogLayout = false
    suppressWindowId = true

    def __init__(self, name, designer, frameCtrl):
        ContainerDTC.__init__(self, name, designer, None, None)
        self.control = frameCtrl
        self.editors['Flags'] = FlagsConstrPropEdit
        # XXX should rather be enumerated
        self.windowStyles = ['wx.SIMPLE_BORDER', 'wx.DOUBLE_BORDER',
                             'wx.SUNKEN_BORDER', 'wx.RAISED_BORDER',
                             'wx.STATIC_BORDER', 'wx.NO_BORDER']
    def properties(self):
        props = ContainerDTC.properties(self)
        del props['Anchors']
        return props

    def constructor(self):
        return {'Flags': 'flags'}

    def designTimeSource(self):
        return {'flags': 'wx.SIMPLE_BORDER'}

    def hideDesignTime(self):
        return ContainerDTC.hideDesignTime(self) + ['ToolBar', 'MenuBar',
              'StatusBar', 'Icon', 'Anchors', 'Constraints', 'Label']

    def SetName(self, oldValue, newValue):
        self.name = newValue
        self.designer.renameFrame(oldValue, newValue)

EventCategories['PanelEvent'] = ('wx.EVT_SYS_COLOUR_CHANGED',)

class FramePanelDTC(Constructors.WindowConstr, BaseFrameDTC):
    dialogLayout = true
    suppressWindowId = false

    def __init__(self, name, designer, frameCtrl):
        BaseFrameDTC.__init__(self, name, designer, frameCtrl)

        self.editors['DefaultItem'] = ButtonClassLinkPropEdit
        self.windowStyles.insert(0, 'wx.TAB_TRAVERSAL')

    def hideDesignTime(self):
        return BaseFrameDTC.hideDesignTime(self) + ['ToolBar', 'MenuBar',
              'StatusBar', 'StatusBarPane', 'Icon', 'Title', 'Anchors']

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.TAB_TRAVERSAL',
                'name':  `self.name`}

    def events(self):
        # skip frame events
        return ContainerDTC.events(self) + ['PanelEvent']

    def dependentProps(self):
        return BaseFrameDTC.dependentProps(self) + ['DefaultItem']

class wxFramePanel(wxPanel): pass

#-------------------------------------------------------------------------------
import PaletteStore

PaletteStore.compInfo.update({wxApp: ['wx.App', None],
    wxFrame: ['wx.Frame', FrameDTC],
    wxDialog: ['wx.Dialog', DialogDTC],
    wxMiniFrame: ['wx.MiniFrame', MiniFrameDTC],
    wxMDIParentFrame: ['wx.MDIParentFrame', MDIParentFrameDTC],
    wxMDIChildFrame: ['wx.MDIChildFrame', MDIChildFrameDTC],
    wxFramePanel: ['wx.FramePanel', FramePanelDTC],
})

try:
    PaletteStore.compInfo.update({
        wxPopupWindow: ['wx.PopupWindow', PopupWindowDTC],
        wxPopupTransientWindow: ['wx.PopupTransientWindow', PopupWindowDTC]})
except NameError:
    # wxMAC
    pass
