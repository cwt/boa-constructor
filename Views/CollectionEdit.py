#-----------------------------------------------------------------------------
# Name:        CollectionEdit.py                                              
# Purpose:     Editor for collection properties                               
#                                                                             
# Author:      Riaan Booysen                                                  
#                                                                             
# Created:     2000                                                           
# RCS-ID:      $Id$                                        
# Copyright:   (c) 1999, 2000 Riaan Booysen                                   
# Licence:     GPL                                                            
#-----------------------------------------------------------------------------

from wxPython.wx import *
import Utils, Preferences
from Views import Designer
from PrefsKeys import keyDefs
import os
#from EditorModels import init_coll

#wxNullBitmap = Preferences.IS.load('Images/Inspector/wxNullBitmap.bmp')

def create(parent):
    return CollectionEditor(parent)

[wxID_COLLECTIONEDITOR, wxID_COLLECTIONEDITORTOOLBAR, wxID_COLLECTIONEDITORITEMLIST] = map(lambda _init_ctrls: NewId(), range(3))

class CollectionEditor(wxFrame):
    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(200, 247), id = wxID_COLLECTIONEDITOR, title = 'Collection Editor', parent = prnt, name = 'CollectionEditor', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(341, 139))

        self.toolBar = wxToolBar(size = wxDefaultSize, id = wxID_COLLECTIONEDITORTOOLBAR, pos = wxPoint(32, 4), parent = self, name = 'toolBar1', style = wxTB_HORIZONTAL | wxNO_BORDER | Preferences.flatTools)

        self.SetToolBar(self.toolBar)

    def __init__(self, parent, collEditView, lvStyle = wxLC_REPORT): 
        self._init_ctrls(parent)

        self.itemList = wxListCtrl(size = wxPyDefaultSize, id = wxID_COLLECTIONEDITORITEMLIST, parent = self, name = 'itemList', validator = wxDefaultValidator, style = lvStyle | wxLC_SINGLE_SEL, pos = wxPyDefaultPosition)
        EVT_LIST_ITEM_SELECTED(self.itemList, wxID_COLLECTIONEDITORITEMLIST, self.OnObjectSelect)
        EVT_LIST_ITEM_DESELECTED(self.itemList, wxID_COLLECTIONEDITORITEMLIST, self.OnObjectDeselect)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(wxIcon(Preferences.toPyPath('Images/Icons/Collection.ico'), 
              wxBITMAP_TYPE_ICO))

        self.collEditView = collEditView
        self.selected = -1

        acclst = []
        wId = Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/NewItem.bmp', 
          'New', self.OnNewClick)
        EVT_MENU(self, wId, self.OnNewClick)
        acclst.append( (keyDefs['Insert'][0], keyDefs['Insert'][1], wId) )
        wId = Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/DeleteItem.bmp',  
          'Delete', self.OnDeleteClick)
        EVT_MENU(self, wId, self.OnDeleteClick)
        acclst.append( (keyDefs['Delete'][0], keyDefs['Delete'][1], wId) )
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Up.bmp',
          'Up (Not implemented)', self.OnUpClick)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Down.bmp', 
          'Down (Not implemented)', self.OnDownClick)
        self.toolBar.AddSeparator()
        wId = Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Editor/Refresh.bmp',
          'Refresh', self.OnRefresh)
        EVT_MENU(self, wId, self.OnRefresh)
        acclst.append( (keyDefs['Refresh'][0], keyDefs['Refresh'][1], wId) )

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
        self.itemList.SetItemState(idx,
          wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED,
          wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)

    def OnRefresh(self, event):
        self.collEditView.refreshCtrl(1)
            
    def OnObjectSelect(self, event):
        self.selected = event.m_itemIndex
        self.collEditView.selectObject(event.m_itemIndex)

    def OnObjectDeselect(self, event):
        self.selected = -1
        self.collEditView.deselectObject()

    def OnItemlistListItemSelected(self, event):
        self.selected = event.m_itemIndex

    def OnItemlistListItemDeselected(self, event):
        self.selected = -1

    def OnNewClick(self, event):
        ni = self.collEditView.companion.appendItem()
        self.collEditView.refreshCtrl()
        self.selectObject(self.itemList.GetItemCount() -1)

    def OnDeleteClick(self, event):
        if self.selected >= 0:
            idx = self.selected
            self.collEditView.deselectObject()
            ni = self.collEditView.companion.deleteItem(idx)
            self.selected = -1
            self.collEditView.refreshCtrl()

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

class ImageListCollectionEditor(CollectionEditor):
    def __init__(self, parent, collEditView): 
        CollectionEditor.__init__(self, parent, collEditView, wxLC_LIST)
        self.itemList.SetImageList(collEditView.companion.control, wxIMAGE_LIST_SMALL)

    def addItem(self, idx, displayProp):
        self.itemList.InsertImageStringItem(idx, displayProp, idx)
                
class CollectionEditorView(Designer.InspectableObjectCollectionView):
    viewName = 'CollectionEditor'
    collectionMethod = '_init_coll_'
    collectionParams = 'self, parent'

    def __init__(self, parent, inspector, model, companion): 
        Designer.InspectableObjectCollectionView.__init__(self, inspector, 
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
##        print 'COLLVIEW initObjCreator', constrPrs.asText()
##        ctrlClass = eval(constrPrs.class_name)
##        ctrlCompnClass = PaletteMapping.compInfo[ctrlClass][1]
##        ctrlName = self.loadControl(ctrlClass, ctrlCompnClass, 
##          constrPrs.comp_name, constrPrs.params)            
##        ctrlCompn = self.objects[ctrlName][0]
##        ctrlCompn.setConstr(constrPrs)

    def renameCtrl(self, oldName, newName):
        oldCollMeth = self.collectionMethod
        self.companion.SetName(oldName, newName)
        self.collectionMethod = self.companion.collectionMethod
        
        objColl = self.model.objectCollections[oldCollMeth]
        del self.model.objectCollections[oldCollMeth]
        self.model.objectCollections[self.collectionMethod] = objColl

        if self.frame:
            self.frame.SetTitle('Collection Editor - %s.%s'%(self.companion.name,
              self.companion.propName))

    def saveCtrls(self):
        def hasCode(lst):
            lsts = Utils.split_seq(lst, '')
            if lsts[1]:
                return reduce(lambda a, b: a or b, lsts[1]) != ''
            else:
                return false

        # XXX Use inherited!
        newBody = []
        objColl = self.model.objectCollections[self.collectionMethod]
        
        self.companion.writeCollectionInitialiser(newBody)
        self.companion.writeCollectionItems(newBody)
        self.companion.writeEvents(newBody, addModuleMethod = true)
        self.companion.writeCollectionFinaliser(newBody)

        # add method to source
        if hasCode(newBody):
            module = self.model.getModule()
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

#        objColl = self.model.objectCollections[self.collectionMethod]
        
        self.companion.writeCollectionInitialiser(output)
        self.companion.writeCollectionItems(output)
        self.companion.writeEvents(output, addModuleMethod = false)
        self.companion.writeCollectionFinaliser(output)

        if hasCode(output):
            output.insert(0, '    def %s(%s):'% (self.collectionMethod, self.collectionParams))
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
        # Cause inspector to show Objects tree when Designer ctrl selected
        self.inspector.prevDesigner = 1
        # No props goto constructor page
        if self.inspector.pages.GetSelection() == 1:
            self.inspector.pages.SetSelection(0)
        
        self.companion.setIndex(idx)
        self.inspector.selectObject(self.companion, false)

    def deselectObject(self):
        self.inspector.cleanup()

    def close(self):
        self.cleanup()
        Designer.InspectableObjectCollectionView.close(self)

    def show(self):
        if not self.frame:
            self.frame = self.companion.CollEditorFrame(self.parent, self)
            self.frame.SetTitle('Collection Editor - %s.%s'%(self.companion.name,
              self.companion.propName))
            self.refreshCtrl()
        self.frame.Show(true)
        self.frame.Raise()


