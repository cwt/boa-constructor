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
##Boa:Frame:CollectionEditor
print 'importing Views.CollectionEdit'

import os, sys

from wxPython.wx import *

import Preferences, Utils
from Preferences import IS, keyDefs
import sourceconst

import InspectableViews

# XXX 'Select Parent' from the Inspector should select the parent companion 
# XXX of the collection property

_lastDefPos = None
def getNextDefaultPos():
    startPosX = Preferences.inspWidth + Preferences.windowManagerSide*2
    startPosY = Preferences.underPalette

    global _lastDefPos
    if _lastDefPos is not None:
        pos = _lastDefPos
        if pos[0]+400 < Preferences.screenWidth:
            pos = pos[0]+200, pos[1]
        elif pos[1]+500 < Preferences.screenHeight:
            pos = startPosX, pos[1]+250
        else:
            _lastDefPos = None

    if _lastDefPos is None:
        pos = (startPosX, startPosY)

    _lastDefPos = pos

    return pos

[wxID_COLLECTIONEDITOR, wxID_COLLECTIONEDITORTOOLBAR, 
 wxID_COLLECTIONEDITORITEMLIST] = map(lambda _init_ctrls: wxNewId(), range(3))

class CollectionEditor(wxFrame, Utils.FrameRestorerMixin):
    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(200, 250), 
              id = wxID_COLLECTIONEDITOR, title = 'Collection Editor', 
              parent = prnt, name = 'CollectionEditor', 
              style = wxDEFAULT_FRAME_STYLE, pos = self.collEditPos)

        self.toolBar = wxToolBar(size = wxDefaultSize, 
              id = wxID_COLLECTIONEDITORTOOLBAR, pos = wxPoint(32, 4), 
              parent = self, name = 'toolBar1', 
              style = wxTB_HORIZONTAL | wxNO_BORDER | Preferences.flatTools)
        self.SetToolBar(self.toolBar)

    def __init__(self, parent, collEditView, additAdders = (), 
          lvStyle = wxLC_REPORT):
        self.collEditPos = (-1, -1)
        self.collEditPos = getNextDefaultPos()
        
        self._init_ctrls(parent)

        self.itemList = wxListCtrl(size = wxPyDefaultSize, 
              id = wxID_COLLECTIONEDITORITEMLIST, parent = self, 
              name = 'itemList', validator = wxDefaultValidator, 
              style = lvStyle | wxLC_SINGLE_SEL | wxSUNKEN_BORDER, 
              pos = wxPyDefaultPosition)
        EVT_LIST_ITEM_SELECTED(self.itemList, wxID_COLLECTIONEDITORITEMLIST, 
              self.OnObjectSelect)
        EVT_LIST_ITEM_DESELECTED(self.itemList, wxID_COLLECTIONEDITORITEMLIST, 
              self.OnObjectDeselect)
        EVT_LEFT_DCLICK(self.itemList, self.OnObjectDClick)

        self.SetIcon(IS.load('Images/Icons/Collection.ico'))

        self.collEditView = collEditView
        self.selected = -1

        self.additAdders = additAdders #= 0
        self.additIds = {}

        self.toolLst = []

        acclst = []
        wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
              'Images/Shared/NewItem.png', 'New', self.OnNewClick)
        EVT_MENU(self, wId, self.OnNewClick)
        acclst.append( (keyDefs['Insert'][0], keyDefs['Insert'][1], wId) )
        self.toolLst.append(wId)
        if additAdders:
            wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
                  'Images/Shared/NewItems.png', 'More new ...', self.OnMoreNewClick)
            EVT_MENU(self, wId, self.OnMoreNewClick)
            self.toolLst.append(wId)
    
            self.toolBar.AddSeparator()

        wId = Utils.AddToolButtonBmpIS(self, self.toolBar,
              'Images/Shared/DeleteItem.png', 'Delete', self.OnDeleteClick)
        EVT_MENU(self, wId, self.OnDeleteClick)
        acclst.append( (keyDefs['Delete'][0], keyDefs['Delete'][1], wId) )
        self.toolLst.append(wId)
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/up.png',
          'Up', self.OnUpClick)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/down.png',
          'Down', self.OnDownClick)
        self.toolBar.AddSeparator()
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
            self.itemList.InsertColumn(0, 'Name', width=180)

        EVT_CLOSE(self, self.OnCloseWindow)

        self.winConfOption = 'collectioneditor'
        self.loadDims()

        # Hack to force a refresh, it's not displayed correctly initialy
        self.SetSize((self.GetSize().x +1, self.GetSize().y))

    def getDimensions(self):
        size = self.GetSize().asTuple()
        return (None,) + size

    def destroy(self):
        self.collEditView.frame = None
        del self.collEditView

    def setDefaultDimensions(self):
        self.SetSize(wxSize(200, 250))        

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

    _block_selected = false
    def OnObjectSelect(self, event):
        if not self._block_selected:
            self.selected = event.m_itemIndex
            self.collEditView.selectObject(event.m_itemIndex)

    def OnObjectDeselect(self, event):
        if not self._block_selected:
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
        if self.selected > 0 and not self._block_selected:
            newIdx = self.collEditView.companion.moveItem(self.selected, -1)
            self.collEditView.refreshCtrl(1)
            self.selectObject(newIdx)
            
    def OnDownClick(self, event):
        if (self.selected >= 0) and not self._block_selected \
              and (self.selected < self.itemList.GetItemCount() -1):
            newIdx = self.collEditView.companion.moveItem(self.selected, 1)
            self.collEditView.refreshCtrl(1)
            self.selectObject(newIdx)

    def OnObjectDClick(self, event):
        if self.selected >= 0:
            if self.collEditView.companion.defaultAction():
                # block events so that switching actions aren't tripped up
                # by relselection of collection items
                self._block_selected = true
                event.Skip()
                wxCallAfter(self._unblock)
            self.Raise()
    
    def _unblock(self):
        self._block_selected = false

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
        menu = wxMenu()
        self.additIds = {}
        for item, meth in self.additAdders:
            if item == '-':
                menu.AppendSeparator()
            else:
                wId = wxNewId()
                self.additIds[wId] = meth
                EVT_MENU(self, wId, self.OnMoreNewItemClick)
                menu.Append(wId, item)
        
        ts = self.toolBar.GetToolSize()
        # hardcoded to 2nd tool btn position
        self.PopupMenu(menu, wxPoint(ts.x, ts.y))
        menu.Destroy()

    def OnMoreNewItemClick(self, event):
        ni = self.collEditView.companion.appendItem(self.additIds[event.GetId()])
        self.collEditView.refreshCtrl()
        self.selectObject(self.itemList.GetItemCount() -1)
        self.Raise()

    def OnSwitchToInspector(self, event):
        self.collEditView.model.editor.inspector.restore()

    def OnSwitchToDesigner(self, event):
        # XXX Should switch to data view
        if self.collEditView.model.views.has_key('Designer'):
            self.collEditView.model.views['Designer'].restore()

class ImageListCollectionEditor(CollectionEditor):
    def __init__(self, parent, collEditView, additMeths=()):
        CollectionEditor.__init__(self, parent, collEditView, additMeths, wxLC_REPORT)
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
        
        self.additMeths = companion.additionalMethods

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

        imps = self.companion.writeResourceImports()
        if imps:
            imps = imps.split('\n')
            for imp in imps:
                imp = imp.strip()
                if imp:
                    module.addImportStatement(imp, resourceImport=true)

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
            if self.additMeths:
                am = tuple([(methInfo[0], meth) 
                            for meth, methInfo in self.additMeths.items()])
            else:
                am = ()
            
            self.frame = self.companion.CollEditorFrame(self.parent, self, am)
            self.updateFrameTitle()
            self.refreshCtrl()
        self.frame.restore()

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    class PhonyCompanion: collectionMethod = 'None'
    class PhonyEditor: Disconnect = None
    cev = CollectionEditorView(None, None, None, PhonyCompanion())
    frame = CollectionEditor(None, cev, ('New item', '-', 'Append separator', 'New sub-menu'))
    frame.Show(true)
    app.MainLoop()
