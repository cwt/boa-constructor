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
import os
#from EditorModels import init_coll

wxNullBitmap = Preferences.IS.load('Images\\Inspector\\wxNullBitmap.bmp')

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

        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/NewItem.bmp', 
          'New', self.OnNewClick)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/DeleteItem.bmp',  
          'Delete', self.OnDeleteClick)
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Up.bmp',
          'Up', self.OnUpClick)
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Shared/Down.bmp', 
          'Down', self.OnDownClick)
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolBar, 'Images/Editor/Refresh.bmp',
          'Refresh', self.OnRefresh)

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
##        print 'ONREFRESH'
##        print 'CollEditorView', self.collEditView
##        print 'CollMethod', self.collEditView.collectionMethod
##        print 'Companion', self.collEditView.companion
##        print 'Companion constr', id(self.collEditView.companion.textConstrLst)
##        print 'ObjColl creators', id(self.collEditView.model.objectCollections[self.collEditView.collectionMethod].creators)
##        print 'ObjColl', id(self.collEditView.model.objectCollections[self.collEditView.collectionMethod])
            
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
#        self.collEditView.deselectObject()
        ni = self.collEditView.companion.appendItem()
        self.collEditView.refreshCtrl()
        self.selectObject(self.itemList.GetItemCount() -1)

#        idx = self.itemList.GetItemCount()
#        self.itemList.InsertStringItem(idx, self.collEditView.companion.propName+`idx`)
        
#        self.itemList.GetItem(idx).m_mask  = 3
#        self.list.SetColumnWidth(0, wxLIST_AUTOSIZE)
#        self.itemList.SetItemState(idx, wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED, wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)

    def OnDeleteClick(self, event):
        if self.selected >= 0:
            idx = self.selected
            self.collEditView.deselectObject()
            ni = self.collEditView.companion.deleteItem(idx)
            self.selected = -1
            self.collEditView.refreshCtrl()

##            self.itemList.DeleteItem(idx)
##            if idx < self.itemList.GetItemCount():
##                self.itemList.SetItemState(idx, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
##            elif  idx > 0:
##                self.itemList.SetItemState(idx -1, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)

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

##        self.CollEditorFrame = CollectionEditor
        self.parent = parent
        self.frame = None
        self.companion = companion
        self.collectionMethod = companion.collectionMethod
        self.srcCollectionMethod = companion.collectionMethod
##        self.propEdit = propertyEditor
        
    def initialise(self):
        'COLLVIEW initialise', self.collectionMethod
        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()
        self.initObjectsAndCompanions(objCol.creators, objCol)

    def initObjEvts(self, events, name, creator):
##        print 'COLLVIEW', self.companion, events
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
##        print 'CollEditView renameCtrl', self.companion
        oldCollMeth = self.collectionMethod
        self.companion.SetName(oldName, newName)
##        self.companion.setCollectionMethod()
        self.collectionMethod = self.companion.collectionMethod
##        print 'CollEditView renameCtrl', self.collectionMethod
        
        objColl = self.model.objectCollections[oldCollMeth]
        del self.model.objectCollections[oldCollMeth]
        self.model.objectCollections[self.collectionMethod] = objColl
##        print self.model.objectCollections.keys()
        
##        mod = self.model.module
##        print 'CollEditView renameCtrl', mod.classes[self.model.main].methods.keys()
##        if mod.classes[self.model.main].methods.has_key(oldCollMeth):
##            print 'renaming method in module'
##            mod.renameMethod(self.model.main, oldCollMeth, self.collectionMethod)

    def saveCtrls(self):
        def hasCode(lst):
            lsts = Utils.split_seq(lst, '')
            if lsts[1]:
                return reduce(lambda a, b: a or b, lsts[1]) != ''
            else:
                return false

        # XXX Use inherited!
##        print 'COLLEDIT: Save!'
        newBody = []
        objColl = self.model.objectCollections[self.collectionMethod]
##        objColl.indexOnCtrlName()
        
        newBody.extend(self.companion.initialiser())
        for creator in self.companion.textConstrLst:
            newBody.append('        '+creator.asText())
        self.saveEvts(self.companion, newBody)
##        for evt in self.companion.textEventList:
##            newBody.append('        '+evt.asText())

        newBody.extend(self.companion.finaliser())

        if hasCode(newBody):
            self.model.module.addMethod(self.model.main, 
              self.collectionMethod, self.collectionParams, newBody, 0)
        # remove references to it in other object collections
        else:
##            print 'check for references in', self.companion.designer.collectionMethod, self.collectionMethod
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

##        if self.model.module.classes[self.model.main].methods.has_key(\
##          self.collectionMethod):
##            # Add doc string
##            docs = self.model.module.getClassMethDoc(self.model.main, 
##              self.collectionMethod)
##            if (len(docs) > 0) and docs[0]:
##                newBody.insert(0, '%s""" %s """'%(bodyIndent, docs))
##        
##            if hasCode(newBody):
##                newBody.append('')
##                self.model.module.replaceMethodBody(self.model.main, 
##                  self.collectionMethod, newBody)
##            else:
##                # method is now empty, remove method
##                self.model.module.removeMethod(self.model.main, 
##                  self.collectionMethod)
##
##                print 'check for references in', self.companion.designer.collectionMethod
##                self.model.objectCollections[self.companion.designer.collectionMethod].\
##                  removeReference(self.companion.name, self.collectionMethod)
##                i = 0
##                compCollLst = self.companion.parentCompanion.textCollInitList
##                while i < len(compCollLst):
##                    if compCollLst[i].method == self.collectionMethod:
##                        del compCollLst[i]
##                    else:
##                        i = i + 1
##        # Method does not exist in module
##        else:
##            # Add it
##            if hasCode(newBody):
##                self.model.module.addMethod(self.model.main, 
##                  self.collectionMethod, self.collectionParams, newBody, 0)
##            # remove references to it in other object collections
##            else:
##                print 'check for references in', self.companion.designer.collectionMethod, self.collectionMethod
##                self.model.objectCollections[self.companion.designer.collectionMethod].\
##                  removeReference(self.companion.name, self.collectionMethod)
##
##                compCollLst = self.companion.parentCompanion.textCollInitList
##                i = 0
##                while i < len(compCollLst):
##                    if compCollLst[i].method == self.collectionMethod:
##                        del compCollLst[i]
##                    else:
##                        i = i + 1
##                i = 0
##                propLst = self.companion.parentCompanion.textPropList
##                while i < len(propLst):
##                    if propLst[i].params[0][5:len(self.collectionMethod) +5] == \
##                      self.collectionMethod:
##                        del propLst[i]
##                    else:
##                        i = i + 1
        
        self.model.removeWindowIds(self.srcCollectionMethod)
        self.model.writeWindowIds(self.collectionMethod, [self.companion])
                  
    def refreshCtrl(self, keepSelected = false):
##        print 'COLLEDIT refreshCtrl'
        self.deselectObject()
        if self.frame:
            if keepSelected: sel = self.frame.selected
            self.frame.clear()
##            objColl = self.model.objectCollections[self.collectionMethod]
            
            
            for idx in range(len(self.companion.textConstrLst)):
##                print self.companion.textConstrLst, '::',
                self.companion.setIndex(idx)
                displayProp = self.companion.getDisplayProp()
##                print 'Adding item:', displayProp
                self.frame.addItem(idx, displayProp)

            if keepSelected: self.frame.selectObject(sel)

##        self.frame.clear()
##
##        ctrls, props, events = self.organiseCollection()
##
##        for ctrl in ctrls.creators:
##            if ctrl.comp_name:
##                try:
##                    classObj = eval(ctrl.class_name)
##                    className = classObj.__name__
##                    idx1 = self.il.Add(PaletteMapping.bitmapForComponent(classObj, gray = true))
##                except:
##                    className = aclass
##                    if len(self.model.module.classes[aclass].super):
##                        base = self.model.module.classes[aclass].super[0]
##                        try: base = base.__class__.__name__
##                        except: pass #print 'ERROR', base
##                        idx1 = self.il.Add(PaletteMapping.bitmapForComponent(aclass, base, gray = true))
##                    else:
##                        idx1 = self.il.Add(PaletteMapping.bitmapForComponent(aclass, 'Component'))
##                
##                self.InsertImageStringItem(0, '%s : %s' % (ctrl.comp_name, className), idx1)

##    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
##        """ Create and register given control and companion.
##            See also: newControl """
##        args = self.setupArgs(ctrlName, params, self.handledProps)
##        
##        # Create control and companion
##        companion = ctrlCompanion(ctrlName, self, ctrlClass)
##        self.objects[ctrlName] = [companion, companion.designTimeObject(args), None]
##        self.objectOrder.append(ctrlName)
##        
##        return ctrlName

#    def deleteCtrl(self, name, parentRef = None):
#        self.selectNone()
#        InspectableObjectCollectionView.deleteCtrl(self, name, parentRef)
#        self.refreshCtrl()                

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
        self.inspector.selectObject(None, self.companion, false)

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


