#----------------------------------------------------------------------
# Name:        DataView.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2000/02/14
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from wxPython.wx import *
from Designer import InspectableObjectCollectionView
from Utils import AddToolButtonBmpIS
from EditorModels import init_utils
import PaletteMapping
import os
            
class DataView(wxListCtrl, InspectableObjectCollectionView):
    viewName = 'Data'
    collectionMethod = init_utils
    postBmp = 'Images/Inspector/Post.bmp'
    cancelBmp = 'Images/Inspector/Cancel.bmp'
    def __init__(self, parent, inspector, model, compPal):
        [self.wxID_DATAVIEW] = map(lambda _init_ctrls: wxNewId(), range(1))    
        wxListCtrl.__init__(self, parent, self.wxID_DATAVIEW, style = wxLC_SMALL_ICON)#wxLC_LIST)

        InspectableObjectCollectionView.__init__(self, inspector, model, compPal,
          (('Post', self.OnPost, self.postBmp, ()),
           ('Cancel', self.OnCancel, self.cancelBmp, ())), 0)

        self.il = wxImageList(24, 24)
        self.SetImageList(self.il, wxIMAGE_LIST_SMALL)

        EVT_LEFT_DOWN(self, self.OnSelectOrAdd)
        EVT_LIST_ITEM_SELECTED(self, self.wxID_DATAVIEW, self.OnObjectSelect)
        EVT_LIST_ITEM_DESELECTED(self, self.wxID_DATAVIEW, self.OnObjectDeselect)

        self.selected = -1

        self.active = true

    def initialize(self):
        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()

        deps, depLinks = {}, {}
        self.initObjectsAndCompanions(objCol.creators, objCol, deps, depLinks)

    def refreshCtrl(self):
        self.DeleteAllItems()

        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()

#        ctrls, props, events = self.organiseCollection()

        for ctrl in objCol.creators:
            if ctrl.comp_name:
                try:
                    classObj = eval(ctrl.class_name)
                    className = classObj.__name__
                    idx1 = self.il.Add(PaletteMapping.bitmapForComponent(classObj, gray = true))
                except:
                    className = aclass
                    if len(self.model.module.classes[aclass].super):
                        base = self.model.module.classes[aclass].super[0]
                        try: base = base.__class__.__name__
                        except: pass #print 'ERROR', base
                        idx1 = self.il.Add(PaletteMapping.bitmapForComponent(aclass, base, gray = true))
                    else:
                        idx1 = self.il.Add(PaletteMapping.bitmapForComponent(aclass, 'Component'))
                
                self.InsertImageStringItem(0, '%s : %s' % (ctrl.comp_name, className), idx1)

##        print '$$$$ INIT DV'
##        for i in self.collEditors.values():
##            print id(i.companion.textConstrLst),
##            print id(self.model.objectCollections[i.companion.collectionMethod].creators)

##    def renameCtrl(self, oldName, newName):
##        print self.objects

    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl """
        args = self.setupArgs(ctrlName, params, self.handledProps)
        
        # Create control and companion
        companion = ctrlCompanion(ctrlName, self, ctrlClass)
        self.objects[ctrlName] = [companion, companion.designTimeObject(args), None]
        self.objectOrder.append(ctrlName)
        
        return ctrlName

    def selectNone(self):
        for itemIdx in range(self.GetItemCount()):
            a = wxLIST_STATE_SELECTED
            state = self.GetItemState(itemIdx, a)
            self.SetItemState(itemIdx, 0, wxLIST_STATE_SELECTED)

    def deleteCtrl(self, name, parentRef = None):
        self.selectNone()
        InspectableObjectCollectionView.deleteCtrl(self, name, parentRef)
        self.refreshCtrl()                

    def renameCtrl(self, oldName, newName):
        InspectableObjectCollectionView.renameCtrl(self, oldName, newName)
        self.refreshCtrl()                
        self.SetItemState(self.selected, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)

    def close(self):
##        print 'DATAVIEW CLOSE'
        self.cleanup()
        InspectableObjectCollectionView.close(self)

    def OnSelectOrAdd(self, event):
        """ Control is clicked. Either select it or add control from palette """
        if self.compPal.selection:
            objName = self.newObject(self.compPal.selection[1], self.compPal.selection[2])
            self.compPal.selectNone()
            self.refreshCtrl()
        else:
            # Skip so that OnObjectSelect may be fired
            event.Skip()
    
    def OnObjectSelect(self, event):
        self.inspector.containment.cleanup()
        self.selected = event.m_itemIndex
        name = string.split(self.GetItemText(self.selected), ' : ')[0]
        self.inspector.selectObject(self.objects[name][1], self.objects[name][0], false)

    def OnObjectDeselect(self, event):
        self.inspector.cleanup()

    def OnPost(self, event):
        self.controllerView.saveOnClose = true
        self.close()

    def OnCancel(self, event):
        self.controllerView.saveOnClose = false
        self.close()
        
        
        
        
    