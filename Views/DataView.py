#----------------------------------------------------------------------
# Name:        DataView.py
# Purpose:     Designer for Utility (non visual) objects
#
# Author:      Riaan Booysen
#
# Created:     2000/02/14
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Views.DataView'

import os

from wxPython.wx import *

import Preferences, Utils

import sourceconst
import PaletteMapping, Help

from InspectableViews import InspectableObjectView

class DataView(wxListCtrl, InspectableObjectView):
    viewName = 'Data'
    collectionMethod = sourceconst.init_utils
    postBmp = 'Images/Inspector/Post.png'
    cancelBmp = 'Images/Inspector/Cancel.png'
    def __init__(self, parent, inspector, model, compPal):
        [self.wxID_DATAVIEW] = map(lambda _init_ctrls: wxNewId(), range(1))
        wxListCtrl.__init__(self, parent, self.wxID_DATAVIEW, style = Preferences.dataViewListStyle | wxSUNKEN_BORDER)#wxLC_LIST)

        InspectableObjectView.__init__(self, inspector, model, compPal,
          (('Default editor', self.OnDefaultEditor, '-', ''),
           ('Post', self.OnPost, self.postBmp, ''),
           ('Cancel', self.OnCancel, self.cancelBmp, ''),
           ('-', None, '-', ''),
           ('Cut', self.OnCutSelected, '-', ''),
           ('Copy', self.OnCopySelected, '-', 'Copy'),
           ('Paste', self.OnPasteSelected, '-', 'Paste'),
           ('Delete', self.OnControlDelete, '-', 'Delete'),
           ('-', None, '-', ''),
           ('Creation/Tab order...', self.OnCreationOrder, '-', ''),
           ('-', None, '-', ''),
           ('Context help', self.OnContextHelp, '-', 'ContextHelp'),
           ), 0)

        self.il = wxImageList(24, 24)
        self.SetImageList(self.il, wxIMAGE_LIST_SMALL)

        EVT_LEFT_DOWN(self, self.OnSelectOrAdd)
        EVT_LIST_ITEM_SELECTED(self, self.wxID_DATAVIEW, self.OnObjectSelect)
        EVT_LIST_ITEM_DESELECTED(self, self.wxID_DATAVIEW, self.OnObjectDeselect)

        self.selection = []
        self.vetoSelect = false

        self.active = true

    def initialize(self):
        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()

        deps, depLinks = {}, {}
        self.initObjectsAndCompanions(objCol.creators, objCol, deps, depLinks)

    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):
        InspectableObjectView.initObjectsAndCompanions(self, creators, objColl, dependents, depLinks)
        self.initIdOnlyObjEvts(objColl.events, creators)

    def refreshCtrl(self):
        #if self.opened: return

        self.DeleteAllItems()

        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()

        creators = {}
        for ctrl in objCol.creators:
            if ctrl.comp_name:
                creators[ctrl.comp_name] = ctrl

        for name in self.objectOrder:
            ctrl = creators[name]
            try:
                classObj = PaletteMapping.evalCtrl(ctrl.class_name)
                className = classObj.__name__
                idx1 = self.il.Add(PaletteMapping.bitmapForComponent(classObj))
            except:
                # XXX Check this !!
                className = ctrl.class_name
                module = self.model.getModule()
                if len(module.classes[className].super):
                    base = module.classes[className].super[0]
                    try: base = base.__class__.__name__
                    except: pass #print 'ERROR', base
                    idx1 = self.il.Add(PaletteMapping.bitmapForComponent(className, base))
                else:
                    idx1 = self.il.Add(PaletteMapping.bitmapForComponent(className, 'Component'))

            self.InsertImageStringItem(self.GetItemCount(), '%s : %s' % (ctrl.comp_name, className), idx1)
        self.opened = true

    def saveCtrls(self, definedCtrls, module=None):
        InspectableObjectView.saveCtrls(self, definedCtrls, module)

        compns = []
        for objInf in self.objects.values():
            compns.append(objInf[0])
        self.model.removeWindowIds(self.collectionMethod)
        self.model.writeWindowIds(self.collectionMethod, compns)

    def loadControl(self, CtrlClass, CtrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl """
        args = self.setupArgs(ctrlName, params,
          CtrlCompanion.handledConstrParams, evalDct = self.model.specialAttrs)

        # Create control and companion
        companion = CtrlCompanion(ctrlName, self, CtrlClass)
        self.objects[ctrlName] = [companion, companion.designTimeObject(args), None]
        self.objectOrder.append(ctrlName)

        return ctrlName

    def restore(self):
        # This is needed for when the inspector switches to it's designer
        self.model.editor.restore()
        # XXX Should probably switch to the DataView page in the notebook.

    def selectNone(self):
        for itemIdx in range(self.GetItemCount()):
            a = wxLIST_STATE_SELECTED
            state = self.GetItemState(itemIdx, a)
            self.SetItemState(itemIdx, 0, a)

    def selectCtrls(self, ctrls):
        for itemIdx in range(self.GetItemCount()):
            name = string.split(self.GetItemText(itemIdx), ' : ')[0]
            a = wxLIST_STATE_SELECTED
            if name in ctrls: f = a
            else: f = 0
            state = self.GetItemState(itemIdx, a)
            self.SetItemState(itemIdx, f, a)

    def deleteCtrl(self, name, parentRef = None):
        self.selectNone()

        # notify other components of deletion
        self.controllerView.notifyAction(self.objects[name][0], 'delete')

        InspectableObjectView.deleteCtrl(self, name, parentRef)
        self.refreshCtrl()

    def renameCtrl(self, oldName, newName):
        InspectableObjectView.renameCtrl(self, oldName, newName)
        self.refreshCtrl()
        self.selectCtrls( (newName,) )

    def destroy(self):
        InspectableObjectView.destroy(self)
        self.il = None

    def close(self):
        self.cleanup()
        InspectableObjectView.close(self)

    def getSelectedName(self):
        return string.split(self.GetItemText(self.selection[0]), ' : ')[0]

    def getSelectedNames(self):
        selected = []
        for itemIdx in range(self.GetItemCount()):
            name = string.split(self.GetItemText(itemIdx), ' : ')[0]
            state = self.GetItemState(itemIdx, wxLIST_STATE_SELECTED)
            if state:
                selected.append( (name, itemIdx) )
        return selected

    def OnSelectOrAdd(self, event):
        """ Control is clicked. Either select it or add control from palette """
        if self.compPal.selection:
            objName = self.newObject(self.compPal.selection[1], self.compPal.selection[2])
            self.compPal.selectNone()
            self.refreshCtrl()
            self.selectCtrls([objName])
        else:
            # Skip so that OnObjectSelect may be fired
            event.Skip()

    def updateSelection(self):
        if len(self.selection) == 1:
            self.inspector.selectObject(self.objects[self.selection[0][0]][0],
                  false, sessionHandler=self.controllerView)
        else:
            self.inspector.cleanup()

    def OnObjectSelect(self, event):
        self.inspector.containment.cleanup()
        self.selection = self.getSelectedNames()
        self.updateSelection()

    def OnObjectDeselect(self, event):
        event.Skip()
        if self.vetoSelect: return
        idx = 0
        while idx < len(self.selection):
            name, ctrlIdx = self.selection[idx]
            if ctrlIdx == event.m_itemIndex:
                del self.selection[idx]
            else:
                idx = idx + 1

#        self.inspector.cleanup()
        self.updateSelection()

    def OnPost(self, event):
        """ Close all designers and save all changes """
        self.controllerView.saveOnClose = true
        self.close()

    def OnCancel(self, event):
        """ Close all designers and discard all changes """
        self.controllerView.saveOnClose = false
        self.controllerView.confirmCancel = true
        self.close()

    def OnCutSelected(self, event):
        """ Cut current selection to the clipboard """
        ctrls = map(lambda ni: ni[0], self.selection)

        output = []
        self.cutCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(string.join(output, os.linesep))

        self.refreshCtrl()

    def OnCopySelected(self, event):
        """ Copy current selection to the clipboard """
        ctrls = map(lambda ni: ni[0], self.selection)

        output = []
        self.copyCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(string.join(output, os.linesep))

    def OnPasteSelected(self, event):
        """ Paste current clipboard contents into the current selection """
        pasted = self.pasteCtrls('', string.split(Utils.readTextFromClipboard(),
                                                  os.linesep))
        if len(pasted):
            self.refreshCtrl()
            self.selectCtrls(pasted)

    def OnControlDelete(self, event):
        self.vetoSelect = true
        try:
            for name, idx in self.selection:
                self.deleteCtrl(name)
        finally:
            self.vetoSelect = false

        self.selection = self.getSelectedNames()
        self.updateSelection()

    def OnDefaultEditor(self, event):
        if len(self.selection) == 1:
            self.objects[self.selection[0][0]][0].defaultAction()

    def OnContextHelp(self, event):
        Help.showCtrlHelp(self.objects[self.selection[0][0]][0].GetClass())

    def OnRecreateSelected(self, event):
        wxLogError('Recreating not supported in the Data view')

    def OnCreationOrder(self, event):
        #names = [name for name, idx in self.getSelectedNames()]
        names = []
        for name, idx in self.getSelectedNames():
            names.append(name)
        self.showCreationOrderDlg(None)
        self.refreshCtrl()
        self.selectCtrls(names)
