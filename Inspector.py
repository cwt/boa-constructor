#----------------------------------------------------------------------
# Name:        Inspector.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:InspectorFrame

""" Inspects and edits design-time components, manages property editors
    and interacts with the designer and companions
"""

import os
from types import *

from wxPython.wx import *

import PaletteMapping, PaletteStore, sender, Preferences, Help
print 'importing PropertyEditors'
from PropEdit import PropertyEditors
from Companions.EventCollections import *
import Preferences, RTTI, Utils
from Preferences import IS, oiLineHeight, oiNamesWidth, inspPageNames, flatTools
from ZopeLib import PropDlg

scrollBarWidth = 0
IECWidthFudge = 3

[wxID_INSPECTORFRAME, wxID_ENTER, wxID_UNDO, wxID_CRSUP, wxID_CRSDOWN] = map(lambda _init_ctrls: NewId(), range(5))

class InspectorFrame(wxFrame):
    """ Main Inspector frame, mainly does frame initialisation and handles
        events from the toolbar """
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = (-1, -1), id = wxID_INSPECTORFRAME, title = 'Inspector', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE | wxCLIP_CHILDREN, pos = (-1, -1))
        self._init_utils()

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth,
          Preferences.bottomHeight)

        self.propertyRegistry = PropertyEditors.PropertyRegistry()
        PropertyEditors.registerEditors(self.propertyRegistry)

        self.paletteImages = wxImageList(24, 24)
        self.destroying = false

        for cmpInf in PaletteStore.compInfo.values():
            filename ='Images/Palette/Gray/'+ cmpInf[0]+'.bmp'
            if os.path.exists(Preferences.pyPath+'/'+filename):
                cmpInf.append(self.paletteImages.Add(IS.load(filename)))
            else:
                cmpInf.append(self.paletteImages.Add(IS.load('Images/Palette/Gray/Component.bmp')))

        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFont(wxFont(Preferences.inspStatBarFontSize,
          wxDEFAULT, wxNORMAL, wxBOLD, false))

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Inspector.ico'))

        EVT_SIZE(self, self.OnSizing)

        self.vetoSelect = false
        self.selObj = None
        self.selCmp = None
        self.selDesgn = None
        self.prevDesigner = None

        self.toolBar = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|flatTools|wxCLIP_CHILDREN)#|wxTB_FLAT

        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Inspector/Up.bmp',
          'Select parent', self.OnUp)
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Delete.bmp',
          'Delete selection', self.OnDelete)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Cut.bmp',
          'Cut selection', self.OnCut)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Copy.bmp',
          'Copy selection', self.OnCopy)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Paste.bmp',
          'Paste selection', self.OnPaste)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Editor/Refresh.bmp',
          'Recreate selection', self.OnRecreateSelection)
        self.toolBar.AddSeparator()
##        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/RevertItem.bmp',
##          'Revert item', self.OnRevertItem)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/NewItem.bmp',
          'New item', self.OnNewItem)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/DeleteItem.bmp',
          'Delete item', self.OnDelItem)
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Inspector/Post.bmp',
          'Post', self.OnPost)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Inspector/Cancel.bmp',
          'Cancel', self.OnCancel)
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Help.bmp',
          'Show help', self.OnHelp)
        self.toolBar.Realize()

        self.pages = InspectorNotebook(self)

        self.constr = InspectorConstrScrollWin(self.pages, self)
        self.pages.AddPage(self.constr, inspPageNames['Constr'])

        self.props = InspectorPropScrollWin(self.pages, self)
        self.pages.AddPage(self.props, inspPageNames['Props'])

        self.events = EventsWindow(self.pages, self)
        self.pages.AddPage(self.events, inspPageNames['Evts'])

        if wxPlatform == '__WXGTK__':
            prxy, self.containment = Utils.wxProxyPanel(self.pages, ParentTree)
        else:
            prxy = self.containment = ParentTree(self.pages)
#        self.containment = ParentTree(self.pages)
        self.containment.SetImageList(self.paletteImages)
        self.pages.AddPage(prxy, inspPageNames['Objs'])

        self.selection = None

        EVT_CLOSE(self, self.OnCloseWindow)

    def multiSelectObject(self, compn, designer):
        self.selCmp = compn
        self.selDesgn = designer
        self.selObj = None

    def selectObject(self, compn, selectInContainment = true):
        """ Select an object in the inspector by populating the property
            pages. This method is called from the InspectableObjectCollection
            derived classes """
        if self.selCmp == compn or self.vetoSelect:
            return

        # Clear inspector selection
        self.constr.cleanup()
        self.props.cleanup()
        self.events.cleanup()

        if self.prevDesigner and compn.designer and \
          compn.designer != self.prevDesigner:
            if compn.designer.supportsParentView:
                compn.designer.refreshContainment()
            else: pass
        else: pass

        self.prevDesigner = compn.designer

        self.selCmp = compn
        self.selDesgn = compn.designer
        self.selObj = compn.control

        self.statusBar.SetStatusText(compn.name)
        # Update progress inbetween building of property pages
        # Is this convoluted or what :)
        if self.selDesgn:
            sb = self.selDesgn.model.editor.statusBar.progress
        else: sb = None

        if sb: sb.SetValue(10)

        c_p = compn.getPropList()
        if sb: sb.SetValue(30)
        self.constr.readObject(c_p['constructor'])
        if sb: sb.SetValue(50)
        self.props.readObject(c_p['properties'])
        if sb: sb.SetValue(70)
        self.events.readObject()
        if sb: sb.SetValue(90)

        if selectInContainment and self.containment.valid:
            # XXX Ugly must change
            try:
                treeId = self.containment.treeItems[compn.name]
            except:
                treeId = self.containment.treeItems['']

            self.containment.valid = false
            self.containment.SelectItem(treeId)
            self.containment.valid = true
            self.containment.EnsureVisible(treeId)

        if sb: sb.SetValue(0)

    # These methods update property pages.
    # Call when changes in the selected control is detected
    def pageUpdate(self, page, name):
        nv = page.getNameValue(name)
        if nv:
            page.initFromComponent(name)
    def propertyUpdate(self, name):
        self.pageUpdate(self.props, name)
    def constructorUpdate(self, name):
        self.pageUpdate(self.constr, name)
    def eventUpdate(self, name, delete = false):
        if delete:
            self.events.definitions.removeEvent(name)
        else:
            self.pageUpdate(self.events, name)

    # Direct companion source update of position and size when multiselected
    # While multiple components are selected the inspector does not persist
    # selected control value changes
    def directPositionUpdate(self, comp):
        comp.persistProp('Position', 'SetPosition', `comp.control.GetPosition()`)
    def directSizeUpdate(self, comp):
        comp.persistProp('Size', 'SetSize', `comp.control.GetSize()`)

    def selectedCtrlHelpFile(self):
        """ Return the help file/link associated with the selected control """
        if self.selCmp: return self.selCmp.wxDocs
        else: return ''

    def cleanup(self):
        self.selCmp = None
        self.selObj = None
        self.selDesgn = None
        self.constr.cleanup()
        self.props.cleanup()
        self.events.cleanup()
        self.statusBar.SetStatusText('')

    def initSashes(self):
        self.constr.initSash()
        self.props.initSash()
        self.events.definitions.initSash()

    def OnSizing(self, event):
        event.Skip()

    def OnDelete(self, event):
        if self.selDesgn:
            self.selDesgn.OnControlDelete(event)
    def OnUp(self, event):
        if self.selDesgn:
            self.selDesgn.OnSelectParent(event)
    def OnCut(self, event):
        if self.selDesgn:
            self.selDesgn.OnCutSelected(event)
    def OnCopy(self, event):
        if self.selDesgn:
            self.selDesgn.OnCopySelected(event)
    def OnPaste(self, event):
        if self.selDesgn:
            self.selDesgn.OnPasteSelected(event)
    def OnRecreateSelection(self, event):
        if self.selDesgn:
            self.selDesgn.OnRecreateSelected(event)

    def OnPost(self, event):
        if self.selDesgn:
            self.selDesgn.controllerView.saveOnClose = true
            self.selDesgn.controllerView.Close()
##        else:
##            wxLogError('Please use Post in the Editor or from the Designer.')

    def OnCancel(self, event):
        if self.selDesgn:
            self.selDesgn.controllerView.saveOnClose = false
            self.selDesgn.controllerView.Close()
##        else:
##            wxLogError('Please use Cancel in the Editor.')

    def OnHelp(self, event):
        if self.selDesgn:
            url = self.pages.extendHelpUrl(self.selectedCtrlHelpFile())
            Help.showHelp(self, Help.wxWinHelpFrame, url)
        else:
            Help.showHelp(self, Help.BoaHelpFrame, 'Inspector.html')

    def refreshZopeProps(self):
        cmpn = self.selCmp
        cmpn.updateZopeProps()
        self.selCmp = None
        self.selectObject(cmpn)

    def OnRevertItem(self, event):
        if self.selCmp and self.props.prevSel and self.props.prevSel.propEditor:
            propEdit = self.props.prevSel.propEditor
            propEdit.companion.propRevertToDefault(propEdit.name,
                  propEdit.propWrapper.getSetterName())
            self.props.prevSel.showPropNameModified()

    def OnNewItem(self, event):
        if self.selCmp and hasattr(self.selCmp, 'propItems'):
            dlg = PropDlg.create(self)
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.selCmp.addProperty(dlg.tcPropName.GetValue(),
                          dlg.tcValue.GetValue(), dlg.chType.GetStringSelection())
                    self.refreshZopeProps()
            finally:
                dlg.Destroy()

    def OnDelItem(self, event):
        if self.selCmp and self.props.prevSel and hasattr(self.selCmp, 'propItems'):
            self.selCmp.delProperty(self.props.prevSel.propName)
            self.refreshZopeProps()

    def OnCloseWindow(self, event):
        self.Show(false)
        if self.destroying:
            self.cleanup()
            self.pages.destroy()
            self.constr.destroy()
            self.props.destroy()
            self.events.destroy()
            self.Destroy()
            event.Skip()

wxID_PARENTTREE = NewId()
wxID_PARENTTREESELECTED = NewId()
class ParentTree(wxTreeCtrl):
    """ Specialised tree ctrl that displays parent child relationship of
        controls on the frame """
    # XXX Rather associate data with tree item rather than going only on the name
    def __init__(self, parent):
        wxTreeCtrl.__init__(self, parent, wxID_PARENTTREE, style = wxTR_HAS_BUTTONS | wxCLIP_CHILDREN | wxSUNKEN_BORDER)
        self.cleanup()
        EVT_TREE_SEL_CHANGED(self, wxID_PARENTTREE, self.OnSelect)

    def cleanup(self):
        self.designer = None
        self.valid = false
        self.treeItems = {}
        self.DeleteAllItems()

    def addChildren(self, parent, dict, designer):
        """ Recursive method to construct parent/child relationships in a tree """
        for par in dict.keys():
            img = PaletteStore.compInfo[designer.objects[par][1].__class__][2]
            itm = self.AppendItem(parent, par, img)
            self.treeItems[par] = itm
            if len(dict[par]):
                self.addChildren(itm, dict[par], designer)
        self.Expand(parent)


    def refreshCtrl(self, root, relDict, designer):
        self.cleanup()
        self.designer = designer
        self.root = self.AddRoot(root,
     PaletteStore.compInfo[designer.objects[''][1].__class__.__bases__[0]][2])

        self.treeItems[''] = self.root
        self.addChildren(self.root, relDict[''], designer)

        self.valid = true

    def selectName(self, name):
        self.SelectItem(self.treeItems[name])

    def selectedName(self):
        return self.GetItemText(self.GetSelection())

    def selectItemGUIOnly(self, name):
        self.SelectItem(self.treeItems[name])

    def extendHelpUrl(self, url):
        return url

    def OnSelect(self, event):
        """ Event triggered when the selection changes in the tree """
        if self.valid:
            idx = self.GetSelection()
            if self.designer:
##                if idx == self.root:
##                if self.GetRootItem() == idx:
                # Ugly but nothing else works
                try:
                    ctrlInfo = self.designer.objects[self.GetItemText(idx)]
                except KeyError:
                    ctrlInfo = self.designer.objects['']

                if hasattr(self.designer, 'selection') and self.designer.selection:
                    self.designer.selection.selectCtrl(ctrlInfo[1], ctrlInfo[0])


class NameValue:
    """ Base class for all name value pairs that appear in the Inspector """
    def __init__(self, inspector, nameParent, valueParent, companion,
      rootCompanion, name, propWrapper, idx, indent,
      editor = None, options = None, names = None, ownerPropEdit = None):

        self.destr = false
        self.lastSizeN = 0
        self.lastSizeV = 0
        self.indent = indent
        self.inspector = inspector
        self.propName = name
        self.editing = false

        self.nameParent = nameParent
        self.valueParent = valueParent
        self.idx = idx
        self.nameBevelTop = None
        self.nameBevelBottom = None
        self.valueBevelTop = None
        self.valueBevelBottom = None

        if editor:
            self.propEditor = editor(name, valueParent, companion, rootCompanion,
              propWrapper, idx, valueParent.GetSize().x+IECWidthFudge, options,
              names)
        else:
            self.propEditor = self.inspector.inspector.propertyRegistry.factory(name,
              valueParent, companion, rootCompanion, propWrapper, idx,
              valueParent.GetSize().x + IECWidthFudge)

        self.expander = None
        if self.propEditor:
            self.propEditor.ownerPropEdit = ownerPropEdit
            self.updatePropValue()
            displayVal = self.propEditor.getDisplayValue()

            # check if it's expandable
            if PropertyEditors.esExpandable in self.propEditor.getStyle():
                mID = NewId()
                self.expander = wxCheckBox(nameParent, mID, '',
                  wxPoint(8 * self.indent, self.idx * oiLineHeight +2),
                  wxSize(12, 14))
                self.expander.SetValue(true)
                EVT_CHECKBOX(self.expander, mID, self.OnExpand)
        else:
            self.propValue = ''
            displayVal = ''

        self.nameCtrl = wxStaticText(nameParent, -1, name,
          wxPoint(8 * self.indent + 16, idx * oiLineHeight +2),
          wxSize(inspector.panelNames.GetSize().x, oiLineHeight -3),
          style = wxCLIP_CHILDREN | wxST_NO_AUTORESIZE)
        self.nameCtrl.SetToolTipString(companion.getPropertyHelp(name))
        EVT_LEFT_DOWN(self.nameCtrl, self.OnSelect)

        self.showPropNameModified()

        self.value = wxStaticText(valueParent, -1, displayVal,
          wxPoint(2, idx * oiLineHeight +2), wxSize(inspector.getValueWidth(),
          oiLineHeight -3), style = wxCLIP_CHILDREN | wxST_NO_AUTORESIZE)
        self.value.SetForegroundColour(wxColour(0, 0, 100))
        self.value.SetToolTipString(displayVal)
        EVT_LEFT_DOWN(self.value, self.OnSelect)

        self.separatorN = wxPanel(nameParent, -1, wxPoint(0,
          (idx +1) * oiLineHeight), wxSize(inspector.panelNames.GetSize().x, 1),
          style = wxCLIP_CHILDREN)
        self.separatorN.SetBackgroundColour(wxColour(160, 160, 160))

        self.separatorV = wxPanel(valueParent, -1, wxPoint(0,
          (idx +1) * oiLineHeight), wxSize(inspector.getValueWidth(), 1),
          style = wxCLIP_CHILDREN)
        self.separatorV.SetBackgroundColour(wxColour(160, 160, 160))

    def destroy(self, cancel = false):
        self.hideEditor(cancel)
        self.destr = true
        self.nameCtrl.Destroy()
        self.value.Destroy()
        self.separatorN.Destroy()
        self.separatorV.Destroy()
        if self.expander:
            self.expander.Destroy()

    def updatePropValue(self):
        self.propValue = self.propEditor.getValue()

    def showPropNameModified(self):
        if self.propEditor and Preferences.showModifiedProps:
            propEdit = self.propEditor
            propSetter = propEdit.propWrapper.getSetterName()
            mod = not propEdit.companion.propIsDefault(propEdit.name, propSetter)
            fnt = self.nameCtrl.GetFont()
            self.nameCtrl.SetFont(wxFont(fnt.GetPointSize(),
              fnt.GetFamily(), fnt.GetStyle(), mod and wxBOLD or wxNORMAL,
              fnt.GetUnderlined(), fnt.GetFaceName()))

    def updateDisplayValue(self):
        dispVal = self.propEditor.getDisplayValue()
        self.value.SetLabel(dispVal)
        # XXX if not too expensive, only set Tip if caption does not
        # XXX fit in window
        self.value.SetToolTipString(dispVal)
        self.showPropNameModified()

    def setPos(self, idx):
        self.idx = idx
        if self.expander:
            self.expander.SetPosition(wxPoint(8 * self.indent,
            self.idx * oiLineHeight + 2))
        self.nameCtrl.SetPosition(wxPoint(8 * self.indent + 16, idx * oiLineHeight +2))
        self.value.SetPosition(wxPoint(2, idx * oiLineHeight +2))
        self.separatorN.SetPosition(wxPoint(0, (idx +1) * oiLineHeight))
        self.separatorV.SetPosition(wxPoint(0, (idx +1) * oiLineHeight))
        if self.nameBevelTop:
            self.nameBevelTop.SetPosition(wxPoint(0, idx*oiLineHeight -1))
            self.nameBevelBottom.SetPosition(wxPoint(0, (idx + 1)*oiLineHeight -1))
        if self.propEditor:
            self.propEditor.setIdx(idx)
        elif self.valueBevelTop:
            self.valueBevelTop.SetPosition(wxPoint(0, idx*oiLineHeight -1))
            self.valueBevelBottom.SetPosition(wxPoint(0, (idx + 1)*oiLineHeight -1))

    def resize(self, nameWidth, valueWidth):
        if nameWidth <> self.lastSizeN:
            if self.nameBevelTop:
                self.nameBevelTop.SetSize(wxSize(nameWidth, 1))
                self.nameBevelBottom.SetSize(wxSize(nameWidth, 1))

            if nameWidth > 100:
                self.nameCtrl.SetSize(wxSize(nameWidth, self.nameCtrl.GetSize().y))
            else:
                self.nameCtrl.SetSize(wxSize(100, self.nameCtrl.GetSize().y))

            self.separatorN.SetSize(wxSize(nameWidth, 1))

        if valueWidth <> self.lastSizeV:
            if self.valueBevelTop:
                self.valueBevelTop.SetSize(wxSize(valueWidth, 1))
                self.valueBevelBottom.SetSize(wxSize(valueWidth, 1))

            self.value.SetSize(wxSize(valueWidth, self.value.GetSize().y))

            self.separatorV.SetSize(wxSize(valueWidth, 1))

            if self.propEditor:
                self.propEditor.setWidth(valueWidth)

        self.lastSizeN = nameWidth
        self.lastSizeV = valueWidth

    def showEdit(self):
        self.nameBevelTop = wxPanel(self.nameParent, -1,
          wxPoint(0, self.idx*oiLineHeight -1),
          wxSize(self.inspector.panelNames.GetSize().x, 1))
        self.nameBevelTop.SetBackgroundColour(wxBLACK)
        self.nameBevelBottom = wxPanel(self.nameParent, -1,
          wxPoint(0, (self.idx + 1)*oiLineHeight -1),
          wxSize(self.inspector.panelNames.GetSize().x, 1))
        self.nameBevelBottom.SetBackgroundColour(wxWHITE)
        if self.propEditor:
            self.value.SetLabel('')
            self.value.SetToolTipString('')
            self.value.SetSize((0, 0))
            self.propEditor.inspectorEdit()
        else:
            self.valueBevelTop = wxPanel(self.valueParent, -1,
              wxPoint(0, self.idx*oiLineHeight -1),
              wxSize(self.inspector.getValueWidth(), 1))
            self.valueBevelTop.SetBackgroundColour(wxBLACK)
            self.valueBevelBottom = wxPanel(self.valueParent, -1,
              wxPoint(0, (self.idx + 1)*oiLineHeight -1),
              wxSize(self.inspector.getValueWidth(), 1))
            self.valueBevelBottom.SetBackgroundColour(wxWHITE)
        self.editing = true

    def hideEditor(self, cancel = false):
        if self.propEditor:# and (not self.destr):
            if cancel:
                self.propEditor.inspectorCancel()
            else:
                self.propEditor.inspectorPost()
                self.updateDisplayValue()
                self.value.SetSize(wxSize(self.separatorV.GetSize().x,
                  oiLineHeight-3))

        if self.nameBevelTop:
            self.nameBevelTop.Destroy()
            self.nameBevelTop = None
            self.nameBevelBottom.Destroy()
            self.nameBevelBottom = None

        if self.valueBevelTop:
            self.valueBevelTop.Destroy()
            self.valueBevelTop = None
            self.valueBevelBottom.Destroy()
            self.valueBevelBottom = None

        self.editing = false

    def OnSelect(self, event):
        self.inspector.propertySelected(self)

    def OnExpand(self, event):
        if event.Checked(): self.inspector.collapse(self)
        else: self.inspector.expand(self)

class PropNameValue(NameValue):
    """ Name value for properties, usually Get/Set methods, but can also be
        routed to Companion methods """
    def initFromComponent(self):
        """ Update Inspector after possible change to underlying control """
        if self.propEditor:
            self.propEditor.initFromComponent()
            if not self.propEditor.editorCtrl:
                self.updateDisplayValue()
            self.propEditor.persistValue(self.propEditor.valueAsExpr())

class ConstrNameValue(NameValue):
    """ Name value for constructor parameters """
    def initFromComponent(self):
        """ Update Inspector after possible change to underlying control """
        if self.propEditor:
            self.propEditor.initFromComponent()
            if not self.propEditor.editorCtrl:
                self.updateDisplayValue()
            #self.propEditor.persistValue(self.propEditor.valueAsExpr())
    def showPropNameModified(self):
        pass

class EventNameValue(NameValue):
    """ Name value for event definitions """
    def initFromComponent(self):
        if self.propEditor:
            self.propEditor.initFromComponent()
            if not self.propEditor.editorCtrl:
                self.updateDisplayValue()

class ZopePropNameValue(NameValue):
    """ Name value for properties, usually Get/Set methods, but can also be
        routed to Companion methods """
    def initFromComponent(self):
        pass

class EventsWindow(wxSplitterWindow):
    """ Window that hosts event name values and event category selection """
    def __init__(self, parent, inspector):
        wxSplitterWindow.__init__(self, parent, -1,
          style = wxSP_NOBORDER|wxNO_3D|wxSP_LIVE_UPDATE)
        self.inspector = inspector

        self.categories = wxSplitterWindow(self, -1,
          style = wxNO_3D|wxSP_3D|wxSP_LIVE_UPDATE)
        self.definitions = InspectorEventScrollWin(self, inspector)

        self.SetMinimumPaneSize(20)
        self.SplitHorizontally(self.categories, self.definitions)
        self.SetSashPosition(100)

        self.categoryClasses = wxListCtrl(self.categories, 100, style = wxLC_LIST)
        self.selCatClass = -1
        EVT_LIST_ITEM_SELECTED(self.categoryClasses, 100, self.OnCatClassSelect)
        EVT_LIST_ITEM_DESELECTED(self.categoryClasses, 100, self.OnCatClassDeselect)

        self.categoryMacros = wxListCtrl(self.categories, 101, style = wxLC_LIST)
        EVT_LIST_ITEM_SELECTED(self.categoryMacros, 101, self.OnMacClassSelect)
        EVT_LIST_ITEM_DESELECTED(self.categoryMacros, 101, self.OnMacClassDeselect)
        EVT_LEFT_DCLICK(self.categoryMacros, self.OnMacroSelect)

        self.selMacClass = -1

        self.categories.SetMinimumPaneSize(20)
        self.categories.SplitVertically(self.categoryClasses, self.categoryMacros)
        self.categories.SetSashPosition(80)

        tPopupIDAdd = 15
        tPopupIDDelete = 16
        self.menu = wxMenu()
        self.menu.Append(tPopupIDAdd, "Add")
        self.menu.Append(tPopupIDDelete, "Delete")
        EVT_MENU(self, tPopupIDAdd, self.OnAdd)
        EVT_MENU(self, tPopupIDDelete, self.OnDelete)

    def readObject(self):
        #clean up all previous items
        self.cleanup()

        # List available categories
        for catCls in self.inspector.selCmp.events():
            self.categoryClasses.InsertStringItem(0, catCls)

        self.definitions.readObject()

        self.definitions.refreshSplitter()

    def cleanup(self):
        self.definitions.cleanup()
        self.categoryClasses.DeleteAllItems()
        self.categoryMacros.DeleteAllItems()

    def destroy(self):
        self.definitions.destroy()
        self.menu.Destroy()
        del self.inspector

    def findMacro(self, name):
        for macro in EventCategories[self.categoryClasses.GetItemText(self.selCatClass)]:
            if macro.func_name == name: return macro
        raise 'Macro: '+name+' not found.'

    def addEvent(self, name, value, wid = None):
        self.inspector.selCmp.persistEvt(name, value, wid)
        self.inspector.selCmp.evtSetter(name, value)

        self.definitions.addEvent(name)
        self.definitions.refreshSplitter()

    def getEvent(self, name):
        return self.definitions.getNameValue(name)

    def macroNameToEvtName(self, macName):
        flds = string.splitfields(macName, '_')
        del flds[0] #remove 'EVT'
        evtName = 'On'+string.capitalize(self.inspector.selCmp.evtName())
        for fld in flds:
            evtName = evtName + string.capitalize(fld)
        return evtName

    def extendHelpUrl(self, url):
        return url

    def OnCatClassSelect(self, event):
        self.selCatClass = event.m_itemIndex
        catClass = EventCategories[self.categoryClasses.GetItemText(self.selCatClass)]
        for catMac in catClass:
            self.categoryMacros.InsertStringItem(0, catMac.func_name)

    def OnCatClassDeselect(self, event):
        self.selCatClass = -1
        self.selMacClass = -1
        self.categoryMacros.DeleteAllItems()

    def OnMacClassSelect(self, event):
        self.selMacClass = event.m_itemIndex

    def OnMacClassDeselect(self, event):
        self.selMacClass = -1

    def doAddEvent(self, catClassName, macName):
        companion = self.inspector.selCmp
        methName = self.macroNameToEvtName(macName)
        frameName = companion.designer.GetName()
        if catClassName in commandCategories:
            wid = companion.getWinId()
        else:
            wid = None
        nv = self.getEvent(macName[4:])
        if nv:
            self.addEvent(macName[4:], methName, wid)
            nv.initFromComponent()
            nv.OnSelect(None)

        else: self.addEvent(macName[4:], methName, wid)


    def OnMacroSelect(self, event):
        if self.selMacClass > -1:
            catClassName = self.categoryClasses.GetItemText(self.selCatClass)
            macName = self.categoryMacros.GetItemText(self.selMacClass)

            self.doAddEvent(catClassName, macName)

    def OnAdd(self, event):
        self.OnMacroSelect(event)

    def OnDelete(self, event):
        if self.selMacClass > -1:
            macName = self.categoryMacros.GetItemText(self.selMacClass)
            self.addEvent(macName[4:], methName)

# When a namevalue in the inspector is clicked (selected) the following happens
# * Active property editor is hidden, data posted, controls freed
# * New namevalue's propertyeditor creates an editor

class NameValueEditorScrollWin(wxScrolledWindow):
    """ Window that hosts a list of name values. Also provides capability to
        scroll a line at a time, depending on the size of the list """
    def __init__(self, parent):
        wxScrolledWindow.__init__(self, parent, -1, wxPoint(0, 0),
              wxPyDefaultSize, wxSUNKEN_BORDER | wxTAB_TRAVERSAL)
        self.nameValues = []
        self.prevSel = None
        self.splitter = wxSplitterWindow(self, -1, wxPoint(0, 0),
          parent.GetSize(),
          style = wxNO_3D|wxSP_3D|wxSP_NOBORDER|wxSP_LIVE_UPDATE)

        self.panelNames = wxPanel(self.splitter, -1,
          wxDefaultPosition, wxSize(100, 1), style = wxTAB_TRAVERSAL)
        EVT_SIZE(self.panelNames, self.OnNameSize)
        self.panelValues = wxPanel(self.splitter, -1, style = wxTAB_TRAVERSAL)
        EVT_SIZE(self.panelValues, self.OnNameSize)

        self.splitter.SplitVertically(self.panelNames, self.panelValues)
        self.splitter.SetSashPosition(100)
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SetSashSize(4)

        EVT_SIZE(self, self.OnSize)

    def cleanup(self):
        # XXX Does this always have to be inited here?
        self.prevSel = None
        #clean up
        for i in self.nameValues:
            i.destroy(true)
        self.nameValues = []
        self.refreshSplitter()

    def getNameValue(self, name):
        for nv in self.nameValues:
            if nv.propName == name:
                return nv
        return None

    def getWidth(self):
        return self.GetSize().x

    def getHeight(self):
        return len(self.nameValues) *oiLineHeight + 5

    def getValueWidth(self):
        return self.panelValues.GetClientSize().x + IECWidthFudge

    def refreshSplitter(self):
        s = wxSize(self.GetClientSize().x, self.getHeight())
        wOffset, hOffset = self.GetViewStart()
        puw, puh = self.GetScrollPixelsPerUnit()
        if hOffset and len(self.nameValues) < s.y /hOffset:
            hOffset = 0
        self.splitter.SetDimensions(wOffset * puw, hOffset * puh * -1, s.x, s.y)
        self.updateScrollbars(wOffset, hOffset)

    def updateScrollbars(self, wOffset, hOffset):
        height = len(self.nameValues)
        self.SetScrollbars(oiLineHeight, oiLineHeight, 0, height + 1, wOffset, hOffset) #height + 1

    def propertySelected(self, nameValue):
        """ Called when a new name value is selected """
        if self.prevSel:
            if nameValue == self.prevSel: return
            self.prevSel.hideEditor()
        nameValue.showEdit()
        self.prevSel = nameValue

    def resizeNames(self):
        for nv in self.nameValues:
            nv.resize(self.panelNames.GetSize().x, self.getValueWidth())

    def initSash(self):
        self.splitter.SetSashPosition(self.GetSize().x / 2.25)

    def initFromComponent(self, name):
        """ Update a property and it's sub properies from the underlying
            control """

        nv = self.getNameValue(name)
        if nv:
            nv.initFromComponent()
            idx = nv.idx + 1
            idnt = nv.indent + 1
            while 1:
                if idx >= len(self.nameValues): break
                # XXX Why isn't style updating
                nv = self.nameValues[idx]
                if nv.indent < idnt: break
                nv.propEditor.companion.updateObjFromOwner()
                nv.propEditor.propWrapper.connect(nv.propEditor.companion.obj, nv.propEditor.companion)
                nv.initFromComponent()
                idx = idx + 1

    def OnSize(self, event):
        self.refreshSplitter()
        event.Skip()

    def OnNameSize(self, event):
        self.resizeNames()
        event.Skip()

class InspectorScrollWin(NameValueEditorScrollWin):
    """ Derivative of NameValueEditorScrollWin that adds knowledge about the
        Inspector and implements keyboard events """
    def __init__(self, parent, inspector):
        NameValueEditorScrollWin.__init__(self, parent)
        self.inspector = inspector

        self.EnableScrolling(false, true)
        # ?
        self.expanders = sender.SenderMapper()

        self.selObj = inspector.selObj
        self.selCmp = inspector.selCmp

        self.prevSel = None

        EVT_MENU(self, wxID_ENTER, self.OnEnter)
        EVT_MENU(self, wxID_UNDO, self.OnUndo)
        EVT_MENU(self, wxID_CRSUP, self.OnCrsUp)
        EVT_MENU(self, wxID_CRSDOWN, self.OnCrsDown)

        self.SetAcceleratorTable(wxAcceleratorTable([\
          (0, WXK_RETURN, wxID_ENTER),
          (0, WXK_ESCAPE, wxID_UNDO),
          (0, WXK_UP, wxID_CRSUP),
          (0, WXK_DOWN, wxID_CRSDOWN)]))

    def destroy(self):
        del self.inspector

    def readObject(self, propList):
        """ Override this method in derived classes to implement the
            initialisation and construction of the name value list """

    def deleteNameValues(self, idx, count, cancel = false):
        """ Removes a range of name values from the Inspector.
            Used to collapse sub properties
        """
        deleted = 0
        if idx < len(self.nameValues):
            # delete sub properties
            while (idx < len(self.nameValues)) and (deleted < count):
                if self.nameValues[idx] == self.prevSel: self.prevSel = None
                self.nameValues[idx].destroy(cancel)
                del self.nameValues[idx]
                deleted = deleted + 1

            # move properties up
            for idx in range(idx, len(self.nameValues)):
                self.nameValues[idx].setPos(idx)

    def extendHelpUrl(self, url):
        return url

    def collapse(self, nameValue):
        # delete all NameValues until the same indent, count them
        startIndent = nameValue.indent
        idx = nameValue.idx + 1

        # Move deletion into method and use in removeEvent of EventWindow
        i = idx
        if i < len(self.nameValues):
            while (i < len(self.nameValues)) and \
              (self.nameValues[i].indent > startIndent):
                i = i + 1
        count = i - idx

        self.deleteNameValues(idx, count)
        self.refreshSplitter()
        nameValue.propEditor.expanded = false

##    def refreshSplitter(self):
##        NameValueEditorScrollWin.refreshSplitter(self):
##        self.updateScrollbars()

    def OnEnter(self, event):
        for nv in self.nameValues:
            if nv.editing:
                nv.propEditor.inspectorPost(false)

    def OnUndo(self, event):
        # XXX Implement!
        pass

    def OnCrsUp(self, event):
        if len(self.nameValues) > 1:
            for idx in range(1, len(self.nameValues)):
                if self.nameValues[idx].editing:
                    self.propertySelected(self.nameValues[idx-1])
                    #if self.nameValues[idx-1].
                    break
            else:
                self.propertySelected(self.nameValues[0])

            x, y = self.GetViewStart()
            if y >= idx:
                self.Scroll(x, y-1)

    def OnCrsDown(self, event):
        if len(self.nameValues) > 1:
            for idx in range(len(self.nameValues)-1):
                if self.nameValues[idx].editing:
                    self.propertySelected(self.nameValues[idx+1])
                    break
            else:
                self.propertySelected(self.nameValues[-1])

            dx, dy = self.GetScrollPixelsPerUnit()
            cs = self.GetClientSize()
            x, y = self.GetViewStart()
            if y <= idx + 1 - cs.y / dy:
                self.Scroll(x, y+1)

class InspectorPropScrollWin(InspectorScrollWin):
    """ Specialised InspectorScrollWin that understands properties """
    def setNameValues(self, compn, rootCompn, nameValues, insIdx, indent, ownerPropEdit = None):
        top = insIdx
        # Add NameValues to panel
        for nameValue in nameValues:
            # Check if there is an associated companion
            if compn:
                self.nameValues.insert(top, PropNameValue(self, self.panelNames,
                  self.panelValues, compn, rootCompn, nameValue.name,
                  nameValue, top, indent,
                  compn.getPropEditor(nameValue.name),
                  compn.getPropOptions(nameValue.name),
                  compn.getPropNames(nameValue.name),
                  ownerPropEdit))
            top = top + 1

        self.refreshSplitter()

    def extendHelpUrl(self, url):
        if self.prevSel:
            suburl = 'get'+string.lower(self.prevSel.name)
        return url + '#' + suburl

    # read in the root object
    def readObject(self, propList):
        self.setNameValues(self.inspector.selCmp, self.inspector.selCmp,
          propList, 0, 0)

    def expand(self, nameValue):
        nv = self.nameValues[nameValue.idx]
        obj = nv.propValue
        compn = nv.propEditor.getSubCompanion()\
            (nameValue.propName, self.inspector.selCmp.designer,
             self.inspector.selCmp, obj, nv.propEditor.propWrapper)

        compn.updateObjFromOwner()
#                nv.propEditor.propWrapper.connect(nv.propEditor.companion.obj, nv.propEditor.companion)
        propLst = compn.getPropList()['properties']
        sze = len(propLst)

        indt = self.nameValues[nameValue.idx].indent + 1

        # move properties down
        startIdx = nameValue.idx + 1
        for idx in range(startIdx, len(self.nameValues)):
            self.nameValues[idx].setPos(idx +sze)

        # add sub properties in the gap
        self.setNameValues(compn, self.inspector.selCmp, propLst, startIdx, indt, nv.propEditor)
        nv.propEditor.expanded = true
        nv.updateDisplayValue()

class InspectorConstrScrollWin(InspectorScrollWin):
    """ Specialised InspectorScrollWin that understands contructor parameters """
    # read in the root object
    def readObject(self, constrList):
        params = self.inspector.selCmp.constructor()
        paramNames = params.keys()
        paramNames.sort()

        compn = self.inspector.selCmp
        self.addParams(constrList, paramNames, compn, compn)

        self.refreshSplitter()

    def addParams(self, constrList, paramNames, compn, rootCompn, indent = 0, insIdx = -1):
        def findInConstrLst(name, constrList):
            for constr in constrList:
                if constr.name == name:
                    return constr
            return None
        for param in paramNames:
            propWrap = findInConstrLst(param, constrList)
            if propWrap:
                self.addProp(param, compn, rootCompn, propWrap, indent)
            else:
                self.addConstr(param, compn, rootCompn, indent)

    def expand(self, nameValue):
        nv = self.nameValues[nameValue.idx]
        obj = nv.propValue
        compn = nv.propEditor.getSubCompanion()\
            (nameValue.propName, self.inspector.selCmp.designer,
             self.inspector.selCmp, obj, nv.propEditor.propWrapper)

        propLst = compn.getPropList()['properties']
        sze = len(propLst)

        indt = self.nameValues[nameValue.idx].indent + 1

        # move properties down
        startIdx = nameValue.idx + 1
        for idx in range(startIdx, len(self.nameValues)):
            self.nameValues[idx].setPos(idx +sze)

        # add sub properties in the gap
        for propWrap in propLst:
            if propWrap:
                self.addProp(propWrap.name, compn, self.inspector.selCmp,
                      propWrap, indt, startIdx, nv.propEditor)
                startIdx = startIdx + 1
        nv.propEditor.expanded = true
        nv.updateDisplayValue()
        self.refreshSplitter()

    def addConstr(self, name, compn, rootCompn, indent = 0, insIdx = -1):
        props = compn.properties()
        if props.has_key(name):
            rType, getter, setter = props[name]
            propWrap = RTTI.PropertyWrapper(name, rType, getter, setter)
        else:
            propWrap = RTTI.PropertyWrapper(name, 'NoneRoute', None, None)

        if insIdx == -1:
            insIdx = len(self.nameValues)
        self.nameValues.insert(insIdx, ConstrNameValue(self, self.panelNames,
          self.panelValues, compn, rootCompn, name, propWrap,
          insIdx, indent,
          compn.getPropEditor(name), compn.getPropOptions(name),
          compn.getPropNames(name)))

    def addProp(self, name, compn, rootCompn, propWrap, indent = 0, insIdx = -1, ownerPropEdit = None):
        if insIdx == -1:
            insIdx = len(self.nameValues)
        self.nameValues.insert(insIdx,
          PropNameValue(self, self.panelNames, self.panelValues,
          compn, rootCompn, name, propWrap, insIdx, indent,
          compn.getPropEditor(name),
          compn.getPropOptions(name),
          compn.getPropNames(name),
          ownerPropEdit))

class InspectorEventScrollWin(InspectorScrollWin):
    """ Specialised InspectorScrollWin that understands events """
    def readObject(self):
#        self.cleanup()

        for evt in self.inspector.selCmp.getEvents():
            self.addEvent(evt.event_name)

        height = len(self.nameValues)
#        self.SetScrollbars(oiLineHeight, oiLineHeight, 0, height + 1)

        self.refreshSplitter()

    def addEvent(self, name):
        nv = self.getNameValue(name)
        if nv: nv.initFromComponent()
        else:
            self.nameValues.insert(len(self.nameValues),
              EventNameValue(self, self.panelNames,
              self.panelValues, self.inspector.selCmp, self.inspector.selCmp,
              name, RTTI.PropertyWrapper(name, 'EventRoute',
              self.inspector.selCmp.evtGetter, self.inspector.selCmp.evtSetter),
              len(self.nameValues), -2, PropertyEditors.EventPropEdit))

        self.refreshSplitter()
    def removeEvent(self, name):
        # This event will always be selected by a property editor in edit mode
        # therefor nothing will be selected after this

        nv = self.getNameValue(name)
        self.deleteNameValues(nv.idx, 1, true)
        self.prevSel = None

class InspectorNotebook(wxNotebook):
    """ Notebook that hosts Inspector pages """
    def __init__(self, parent):
        wxNotebook.__init__(self, parent, -1, style = Preferences.inspNotebookFlags)
        self.pages = {}
        self.inspector = parent

    def destroy(self):
        del self.pages
        del self.inspector

    def AddPage(self, window, name):
        wxNotebook.AddPage(self, window, name)
        self.pages[name] = window

    def extendHelpUrl(self, name):
        return self.pages[name].extendHelpUrl(url)
