#-----------------------------------------------------------------------------
# Name:        CollectionEdit.py
# Purpose:     Editor for collection properties
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2003 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Frame:CollectionEditor
print 'importing Views.CollectionEdit'

import os, sys

from wxPython.wx import *

if sys.version[:3] == '2.2' and wxVERSION == (2,3,2):
    from ExternalLib.buttons import wxGenBitmapButton
else:
    from wxPython.lib.buttons import wxGenBitmapButton

import Preferences, Utils
from Preferences import IS, keyDefs
import sourceconst

import InspectableViews

def create(parent):
    return CollectionEditor(parent, None)

[wxID_COLLECTIONEDITOR, wxID_COLLECTIONEDITORTOOLBAR, wxID_COLLECTIONEDITORITEMLIST] = map(lambda _init_ctrls: wxNewId(), range(3))

class CollectionEditor(wxFrame, Utils.FrameRestorerMixin):
    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(200, 250), id = wxID_COLLECTIONEDITOR, title = 'Collection Editor', parent = prnt, name = 'CollectionEditor', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(341, 139))

        self.toolBar = wxToolBar(size = wxDefaultSize, id = wxID_COLLECTIONEDITORTOOLBAR, pos = wxPoint(32, 4), parent = self, name = 'toolBar1', style = wxTB_HORIZONTAL | wxNO_BORDER | Preferences.flatTools)
        self.SetToolBar(self.toolBar)

    def __init__(self, parent, collEditView, additAdders = (), lvStyle = wxLC_REPORT):
        self._init_ctrls(parent)

        self.itemList = wxListCtrl(size = wxPyDefaultSize, id = wxID_COLLECTIONEDITORITEMLIST, parent = self, name = 'itemList', validator = wxDefaultValidator, style = lvStyle | wxLC_SINGLE_SEL | wxSUNKEN_BORDER, pos = wxPyDefaultPosition)
        EVT_LIST_ITEM_SELECTED(self.itemList, wxID_COLLECTIONEDITORITEMLIST, self.OnObjectSelect)
        EVT_LIST_ITEM_DESELECTED(self.itemList, wxID_COLLECTIONEDITORITEMLIST, self.OnObjectDeselect)
        EVT_LEFT_DCLICK(self.itemList, self.OnObjectDClick)

        self.SetIcon(IS.load('Images/Icons/Collection.ico'))

        self.collEditView = collEditView
        self.selected = -1

        self.additAdders = additAdders = 0
        self.additIds = {}

        self.toolLst = []

        acclst = []
        wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
              'Images/Shared/NewItem.png', 'New', self.OnNewClick)
        EVT_MENU(self, wId, self.OnNewClick)
        acclst.append( (keyDefs['Insert'][0], keyDefs['Insert'][1], wId) )
        self.toolLst.append(wId)
        if additAdders:
##            wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
##              'Images/Shared/DropDown.png', 'More...', self.OnMoreNewClick)
##            EVT_MENU(self, wId, self.OnMoreNewClick)
##            self.toolLst.append(wId)
            wId = wxNewId()
            sze = self.toolBar.GetToolSize()
            sze.x = 10
            btn = wxGenBitmapButton(self.toolBar, wId,
                  IS.load('Images/Shared/DropDownThin.png'), size=sze )
            btn.SetToolTipString('More...')
            btn.SetBezelWidth(0)
            btn.SetUseFocusIndicator(0)
            self.toolBar.AddControl(btn)
            EVT_BUTTON(btn, wId, self.OnMoreNewClick)
            self.toolLst.append(wId)
            self.toolBar.AddSeparator()
            self.dropDown = btn

        wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
              'Images/Shared/DeleteItem.png', 'Delete', self.OnDeleteClick)
        EVT_MENU(self, wId, self.OnDeleteClick)
        acclst.append( (keyDefs['Delete'][0], keyDefs['Delete'][1], wId) )
        self.toolLst.append(wId)
        self.toolBar.AddSeparator()
##        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Up.png',
##          'Up (Not implemented)', self.OnUpClick)
##        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Down.png',
##          'Down (Not implemented)', self.OnDownClick)
##        self.toolBar.AddSeparator()
        wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
              'Images/Editor/Refresh.png', 'Refresh', self.OnRefresh)
        EVT_MENU(self, wId, self.OnRefresh)
        acclst.append( (keyDefs['Refresh'][0], keyDefs['Refresh'][1], wId) )
        self.toolLst.append(wId)

        wId = wxNewId()
        EVT_MENU(self, wId, self.OnSwitchToInspector)
        acclst.append( (keyDefs['Inspector'][0], keyDefs['Inspector'][1], wId) )

        wId = wxNewId()
        EVT_MENU(self, wId, self.OnSwitchToDesigner)
        acclst.append( (keyDefs['Designer'][0], keyDefs['Designer'][1], wId) )

        self.SetAcceleratorTable(wxAcceleratorTable(acclst))

        self.toolBar.Realize()

        if lvStyle == wxLC_REPORT:
            self.itemList.InsertColumn(0, 'Name')

        EVT_CLOSE(self, self.OnCloseWindow)

        # Hack to force a refresh, it's not displayed correctly initialy
        self.SetSize((self.GetSize().x +1, self.GetSize().y))

    def destroy(self):
        self.collEditView.frame = None
        del self.collEditView

    def clear(self):
        self.selected = -1
        self.itemList.DeleteAllItems()

    def addItem(self, idx, displayProp):
        self.itemList.InsertStringItem(idx, displayProp)

    def selectObject(self, idx):
        wxxSELECTED = wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED
        self.itemList.SetItemState(idx, wxxSELECTED, wxxSELECTED )

    def GetToolPopupPosition(self, id):
        tb = self.toolBar
        return wxPoint(0, 0)
        margins = tb.GetToolMargins()
        toolSize = tb.GetToolSize()
        xPos = margins.x
        for tId in self.toolLst:
            if tId == id:
                return wxPoint(xPos, margins.y + toolSize.y)

            if tId == -1:
                xPos = xPos + tb.GetToolSeparation()
            else:
                xPos = xPos + toolSize.x

        return wxPoint(0, margins.y + toolSize.y)

    def PopupToolMenu(self, toolId, menu):
        self.PopupMenu(menu, self.GetToolPopupPosition(toolId))

    def OnRefresh(self, event):
        self.collEditView.refreshCtrl(1)

    def OnObjectSelect(self, event):
        self.selected = event.m_itemIndex
        self.collEditView.selectObject(event.m_itemIndex)

    def OnObjectDeselect(self, event):
        self.selected = -1
        self.collEditView.deselectObject()

    def OnNewClick(self, event):
        ni = self.collEditView.companion.appendItem()
        self.collEditView.refreshCtrl()
        self.selectObject(self.itemList.GetItemCount() -1)
        self.Raise()

    def OnDeleteClick(self, event):
        if self.selected >= 0:
            idx = self.selected
            self.collEditView.deleteCtrl()

            if idx == self.itemList.GetItemCount():
                idx = idx - 1
            self.selectObject(idx)

    def OnUpClick(self, event):
        if self.selected > 0:
            idx = self.selected
            name = self.itemList.GetItemText(idx)
            self.itemList.DeleteItem(idx)
            self.itemList.InsertStringItem(idx -1, name)
            self.itemList.SetItemState(idx -1, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)

    def OnDownClick(self, event):
        if (self.selected >= 0) and (self.selected < self.itemList.GetItemCount() -1):
            idx = self.selected
            name = self.itemList.GetItemText(idx)
            self.itemList.DeleteItem(idx)
            self.itemList.InsertStringItem(idx +1, name)
            self.itemList.SetItemState(idx +1, wxLIST_STATE_SELECTED,
              wxLIST_STATE_SELECTED)

    def OnObjectDClick(self, event):
        if self.selected >= 0:
            self.collEditView.companion.defaultAction()
            self.Raise()

    def OnSeledClick(self, event):
        result = []
        for itemIdx in range(self.itemList.GetItemCount()):
            if self.itemList.GetItemState(itemIdx, 0) & wxLIST_STATE_SELECTED:
                result.append(itemIdx)
        wxMessageBox(`result`)

    def OnCloseWindow(self, event):
        if self.selected != -1:
            self.collEditView.deselectObject()
        self.destroy()
        self.Destroy()
        event.Skip()

    def OnMoreNewClick(self, event):
        #self.dropDown.SetBezelWidth(1)
        #self.dropDown.Refresh()
        print self.toolLst[0]
        menu = wxMenu()
        self.additIds = {}
        for item in self.additAdders:
            if item == '-':
                menu.AppendSeparator()
            else:
                wId = wxNewId()
                self.additIds[wId] = item
                EVT_MENU(self, wId, self.OnMoreNewItemClick)
                menu.Append(wId, item)
        self.PopupToolMenu(self.toolLst[0], menu)
        return
        #self.dropDown.SetBezelWidth(0)
        #self.dropDown.Refresh()
        #self.dropDown.SetToggle(self.dropDown.GetToggle())
        #print self.dropDown.hasFocus
        #self.dropDown.ReleaseMouse()
        #self.dropDown.saveUp = self.dropDown.up = 1
        #self.dropDown.Refresh()
        menu.Destroy()

    def OnMoreNewItemClick(self, event):
        print self.additIds[event.GetId()]

    def OnSwitchToInspector(self, event):
        self.collEditView.model.editor.inspector.restore()

    def OnSwitchToDesigner(self, event):
        # XXX Should switch to data view
        if self.collEditView.model.views.has_key('Designer'):
            self.collEditView.model.views['Designer'].restore()

class ImageListCollectionEditor(CollectionEditor):
    def __init__(self, parent, collEditView):
        CollectionEditor.__init__(self, parent, collEditView, wxLC_LIST)
        self.itemList.SetImageList(collEditView.companion.control, wxIMAGE_LIST_SMALL)

    def addItem(self, idx, displayProp):
        self.itemList.InsertImageStringItem(idx, displayProp, idx)

class CollectionEditorView(InspectableViews.InspectableObjectView):
    viewName = 'CollectionEditor'
    collectionMethod = sourceconst.init_coll
    collectionParams = 'self, parent'

    def __init__(self, parent, inspector, model, companion):
        InspectableViews.InspectableObjectView.__init__(self, inspector,
          model, None, (), -1, false)

        self.parent = parent
        self.frame = None
        self.companion = companion
        self.collectionMethod = companion.collectionMethod
        self.srcCollectionMethod = companion.collectionMethod

    def initialise(self):
        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()
        self.initObjectsAndCompanions(objCol.creators, objCol, {}, {})

    def initObjEvts(self, events, name, creator):
        if events.has_key(''):
            self.companion.setEvents(events[''])

    def initObjCreator(self, constrPrs):
        pass

    def renameFrame(self, oldName, newName):
        objColl = self.model.objectCollections[self.collectionMethod]
        objColl.renameFrame(oldName, newName)

    def renameCtrl(self, oldName, newName):
        oldCollMeth = self.collectionMethod
        self.companion.SetName(oldName, newName)
        self.collectionMethod = self.companion.collectionMethod

        objColl = self.model.objectCollections[oldCollMeth]
        del self.model.objectCollections[oldCollMeth]
        self.model.objectCollections[self.collectionMethod] = objColl
        objColl.renameCtrl(oldName, newName)

        if self.frame:
            self.updateFrameTitle()

    def updateFrameTitle(self):
        self.frame.SetTitle('%s.%s - Collection Editor'%(self.companion.name,
          self.companion.propName))

    def saveCtrls(self, module=None):
        def hasCode(lst):
            lsts = Utils.split_seq(lst, '')
            if lsts[1]:
                return reduce(lambda a, b: a or b, lsts[1]) != ''
            else:
                return false

        if not module:
            module = self.model.getModule()

        # XXX Use inherited!
        newBody = []
        objColl = self.model.objectCollections[self.collectionMethod]

        self.companion.writeCollectionInitialiser(newBody)
        self.companion.writeCollectionItems(newBody)
        self.companion.writeEvents(newBody, module=module)
        self.companion.writeCollectionFinaliser(newBody)

        # add method to source
        if hasCode(newBody):
            if Preferences.cgAddInitMethodWarning:
                newBody.insert(0, '%s# %s'%(Utils.getIndentBlock()*2,
                               sourceconst.code_gen_warning))
            module.addMethod(
                self.model.main, self.collectionMethod,
                self.collectionParams, newBody, 0)
        # or remove references to it in other object collections
        else:
            self.model.objectCollections[self.companion.designer.collectionMethod].\
              removeReference(self.companion.name, self.collectionMethod)

            compCollLst = self.companion.parentCompanion.textCollInitList
            i = 0
            while i < len(compCollLst):
                if compCollLst[i].method == self.collectionMethod:
                    del compCollLst[i]
                else:
                    i = i + 1
            i = 0
            propLst = self.companion.parentCompanion.textPropList
            while i < len(propLst):
                if propLst[i].params[0][5:len(self.collectionMethod) +5] == \
                  self.collectionMethod:
                    del propLst[i]
                else:
                    i = i + 1

        self.model.removeWindowIds(self.srcCollectionMethod)
        self.model.writeWindowIds(self.collectionMethod, [self.companion])


    def copyCtrls(self, output):
        def hasCode(lst):
            lsts = Utils.split_seq(lst, '')
#            return lsts[1] and reduce(lambda a, b: a or b, lsts[1]) != '' or false
            if lsts[1]:
                return reduce(lambda a, b: a or b, lsts[1]) != ''
            else:
                return false

        frmName=self.model.main
        self.companion.writeCollectionInitialiser(output, stripFrmId=frmName)
        self.companion.writeCollectionItems(output, stripFrmId=frmName)
        self.companion.writeEvents(output, stripFrmId=frmName)
        self.companion.writeCollectionFinaliser(output, stripFrmId=frmName)

        if hasCode(output):
            output.insert(0, '%sdef %s(%s):'% (sourceconst.methodIndent,
                self.collectionMethod, self.collectionParams))
        else:
            output = []

    def refreshCtrl(self, keepSelected = false):
        self.deselectObject()
        if self.frame:
            if keepSelected: sel = self.frame.selected
            self.frame.clear()

            for idx in range(len(self.companion.textConstrLst)):
                self.companion.setIndex(idx)
                displayProp = self.companion.getDisplayProp()
                self.frame.addItem(idx, displayProp)

            if keepSelected: self.frame.selectObject(sel)

    def selectNone(self):
        if self.frame:
            for itemIdx in range(self.frame.itemList.GetItemCount()):
                a = wxLIST_STATE_SELECTED
                state = self.frame.itemList.GetItemState(itemIdx, a)
                self.frame.itemList.SetItemState(itemIdx, 0, wxLIST_STATE_SELECTED)

    def selectObject(self, idx):
        self.inspector.containment.cleanup()
        # No props goto constructor page
        if self.inspector.pages.GetSelection() == 1:
            self.inspector.pages.SetSelection(0)

        self.companion.setIndex(idx)
        self.inspector.selectObject(self.companion, false, self,
              sessionHandler=self.controllerView)

    def deselectObject(self):
        self.inspector.cleanup()

    def deleteCtrl(self):
        self.deselectObject()
        self.notifyAction(self.companion, 'delete')
        self.companion.designer.notifyAction(self.companion, 'delete')
        self.companion.deleteItem(self.companion.index)
        self.refreshCtrl()

    def close(self):
        self.cleanup()
        InspectableViews.InspectableObjectView.close(self)

    def show(self):
        if not self.frame:
            self.frame = self.companion.CollEditorFrame(self.parent, self)
            self.updateFrameTitle()
            self.refreshCtrl()
        self.frame.restore()

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    class PhonyCompanion: collectionMethod = 'None'
    cev = CollectionEditorView(None, None, None, PhonyCompanion())
    frame = CollectionEditor(None, cev, ('New item', '-', 'Append separator', 'New sub-menu'))
    frame.Show(true)
    app.MainLoop()
