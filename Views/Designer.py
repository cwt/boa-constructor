#----------------------------------------------------------------------
# Name:        Designer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import string, copy, os, pprint

from wxPython.wx import *

import Preferences, PrefsKeys, Utils, Help
from Preferences import IS
import CtrlAlign, CtrlSize
import sourceconst, sender

from InspectableViews import InspectableObjectView
import SelectionTags

[wxID_CTRLPARENT, wxID_EDITCUT, wxID_EDITCOPY, wxID_EDITPASTE, wxID_EDITDELETE,
 wxID_SHOWINSP, wxID_SHOWEDTR, wxID_CTRLHELP, wxID_EDITALIGN, wxID_EDITSIZE,
 wxID_EDITRECREATE, wxID_EDITSNAPGRID,
] = map(lambda _init_ctrls: wxNewId(), range(12))

[wxID_EDITMOVELEFT, wxID_EDITMOVERIGHT, wxID_EDITMOVEUP, wxID_EDITMOVEDOWN,
 wxID_EDITWIDTHINC, wxID_EDITWIDTHDEC, wxID_EDITHEIGHTINC, wxID_EDITHEIGHTDEC,
] = map(lambda _keys_move_size: wxNewId(), range(8))



class DesignerView(wxFrame, InspectableObjectView):
    """ Frame Designer for design-time creation/manipulation of visual controls
        on frames. """
    viewName = 'Designer'
    docked = false
    collectionMethod = sourceconst.init_ctrls
    handledProps = ['parent', 'id']
    supportsParentView = true

    def setupArgs(self, ctrlName, params, dontEval, parent = None, compClass = None):
        """ Create a dictionary of parameters for the constructor of the
            control from a dictionary of string/source parameters.
        """

        args = InspectableObjectView.setupArgs(self, ctrlName, params, dontEval)

        if compClass:
            prnt = compClass.windowParentName
            wId = compClass.windowIdName
        else:
            prnt = 'parent'
            wId = 'id'

        # Determine parent
        if parent:
            args[prnt] = parent
        else:
            srcPrnt = args[prnt]
            if srcPrnt == 'None':
                args[prnt] = None
            elif srcPrnt == 'self':
                try:
                    args[prnt] = self
                except AttributeError, name:
                    # XXX This isn't right
                    if self.objects.has_key(name):
                        pass
                    elif self.model.objectCollections.has_key(name):
                        pass
                    else:
                        raise
            else:
                dot = string.find(srcPrnt, '.')
                if dot != -1:
                    srcPrnt = srcPrnt[dot + 1:]
                else: raise 'Component name illegal '+ srcPrnt
                args[prnt] = self.objects[srcPrnt][1]


        args[wId] = NewId()
        args['name'] = ctrlName

        return args

    def __init__(self, parent, inspector, model, compPal, companionClass, dataView):
        args = self.setupArgs(model.main, model.mainConstr.params,
          ['parent', 'id'], parent, companionClass)
        wxFrame.__init__(self, parent, -1, args['title'], args['pos'], args['size'])#, args['style'], args['name'])
        InspectableObjectView.__init__(self, inspector, model, compPal)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Designer.ico'))

        EVT_MOVE(self, self.OnFramePos)

        self.pageIdx = -1
        self.dataView = dataView
        self.dataView.controllerView = self
        self.controllerView = self
        self.saveOnClose = true

        self.ctrlEvtHandler = DesignerControlsEvtHandler(self)

        self.companion = companionClass(self.model.main, self, self)
        self.companion.id = Utils.windowIdentifier(self.model.main, '')

        self.companion.control = self
        self.mainMultiDrag = None

        self.lastSize = (-1, -1)

        # the objects dict has the following structure:
        #    key = componentname
        #    value = list of companion, control, deltaConstr, deltaProps, deltaEvents
        # Note that the frame itself is defined as the blank string name
        self.objects[''] = [self.companion, self, None]
        self.objectOrder.append('')
        self.SetName(self.model.main)

        self.companion.initDesignTimeControl()

        self.active = true
        self.destroying = false
        self.selection = None
        self.multiSelection = []
        self.vetoResize = false

        self.menu.Append(wxID_CTRLPARENT, 'Up')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_EDITCUT, 'Cut')
        self.menu.Append(wxID_EDITCOPY, 'Copy')
        self.menu.Append(wxID_EDITPASTE, 'Paste')
        self.menu.Append(wxID_EDITDELETE, 'Delete')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_EDITRECREATE, 'Recreate')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_EDITSNAPGRID, 'Snap to grid')
        self.menu.Append(wxID_EDITALIGN, 'Align...')
        self.menu.Append(wxID_EDITSIZE, 'Size...')

        EVT_CLOSE(self, self.OnCloseWindow)
        EVT_MENU(self, wxID_EDITDELETE, self.OnControlDelete)
        EVT_MENU(self, wxID_SHOWINSP, self.OnInspector)
        EVT_MENU(self, wxID_SHOWEDTR, self.OnEditor)
        EVT_MENU(self, wxID_CTRLHELP, self.OnCtrlHelp)
        EVT_MENU(self, wxID_EDITALIGN, self.OnAlignSelected)
        EVT_MENU(self, wxID_EDITSIZE, self.OnSizeSelected)
        EVT_MENU(self, wxID_CTRLPARENT, self.OnSelectParent)
        EVT_MENU(self, wxID_EDITCUT, self.OnCutSelected)
        EVT_MENU(self, wxID_EDITCOPY, self.OnCopySelected)
        EVT_MENU(self, wxID_EDITPASTE, self.OnPasteSelected)
        EVT_MENU(self, wxID_EDITRECREATE, self.OnRecreateSelected)
        EVT_MENU(self, wxID_EDITSNAPGRID, self.OnSnapToGrid)

        EVT_MENU(self, wxID_EDITMOVELEFT, self.OnMoveLeft)
        EVT_MENU(self, wxID_EDITMOVERIGHT, self.OnMoveRight)
        EVT_MENU(self, wxID_EDITMOVEUP, self.OnMoveUp)
        EVT_MENU(self, wxID_EDITMOVEDOWN, self.OnMoveDown)
        EVT_MENU(self, wxID_EDITWIDTHINC, self.OnWidthInc)
        EVT_MENU(self, wxID_EDITWIDTHDEC, self.OnWidthDec)
        EVT_MENU(self, wxID_EDITHEIGHTINC, self.OnHeightInc)
        EVT_MENU(self, wxID_EDITHEIGHTDEC, self.OnHeightDec)

        # Key bindings
        accLst = []
        for name, wId in (('Delete', wxID_EDITDELETE),
                          ('Inspector', wxID_SHOWINSP),
                          ('Editor', wxID_SHOWEDTR),
                          ('ContextHelp', wxID_CTRLHELP),
                          ('Escape', wxID_CTRLPARENT),
                          ('Copy', wxID_EDITCOPY),
                          ('Paste', wxID_EDITPASTE),
                          ('MoveLeft', wxID_EDITMOVELEFT),
                          ('MoveRight', wxID_EDITMOVERIGHT),
                          ('MoveUp', wxID_EDITMOVEUP),
                          ('MoveDown', wxID_EDITMOVEDOWN),
                          ('WidthInc', wxID_EDITWIDTHINC),
                          ('WidthDec', wxID_EDITWIDTHDEC),
                          ('HeightInc', wxID_EDITHEIGHTINC),
                          ('HeightDec', wxID_EDITHEIGHTDEC),
                        ):
            tpe, key, code = PrefsKeys.keyDefs[name]
            accLst.append((tpe, key, wId))

        self.SetAcceleratorTable(wxAcceleratorTable(accLst))

    def saveCtrls(self, definedCtrls):
        """ Generate source code for Designer """
        # Remove all collection methods
        for oc in self.model.identifyCollectionMethods():
            if len(oc) > len('_init_coll_') and oc[:11] == '_init_coll_':
                module = self.model.getModule()
                module.removeMethod(self.model.main, oc)

        # Update all size and pos parameters possibly updated externally
        for compn, ctrl, prnt in self.objects.values():
            compn.updatePosAndSize()

        # Generate code
        InspectableObjectView.saveCtrls(self, definedCtrls)

        # Regenerate window ids
        companions = map(lambda i: i[0], self.objects.values())
        self.model.writeWindowIds(self.collectionMethod, companions)

    def renameCtrl(self, oldName, newName):
        """ Rename control, references to control and update
            parent tree """

        prel, pref = self.buildParentRelationship()
        # rename other ctrl references like parent
#        for ctrl in pref[oldName].keys():
        # XXX Not adequate to only notify the children

        children = pref[oldName].keys()
        for ctrl in self.objectOrder:
##            print 'notifying', ctrl
            # Notify
            self.objects[ctrl][0].renameCtrlRefs(oldName, newName)
            # Rename childrens' parents
            if ctrl in children:
                self.objects[ctrl][2] = newName
        # also do collections
        for coll in self.collEditors.values():
            coll.companion.renameCtrlRefs(oldName, newName)

        InspectableObjectView.renameCtrl(self, oldName, newName)
        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = newName

        self.refreshContainment(selName)

    def refreshCtrl(self):
        """ Model View method that is called when the Designer should
            create itself from source
        """
        if self.destroying: return

        # Delete previous
        comps = {}

        # Create selection if none is defined
        if not self.selection:
            self.selection = \
                  SelectionTags.SingleSelectionGroup(self, self.senderMapper,
                  self.inspector, self)

        self.model.editor.statusBar.setHint('Creating frame')

        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()

        self.model.editor.statusBar.progress.SetValue(20)

        stepsDone = 20.0

        # Initialise the design time controls and
        # companion with default values
        # initObjectsAndCompanions(creators, props, events)

        self.inspector.vetoSelect = true
        try:
            # init main construtor
            self.companion.setConstr(self.model.mainConstr)
            ctrlCompn = self.companion
            deps = {}
            depLnks = {}

            self.initObjProps(objCol.propertiesByName, '', objCol.creators[0], deps, depLnks)
            self.initObjEvts(objCol.eventsByName, '', objCol.creators[0])

            if len(objCol.creators) > 1:
                self.initObjectsAndCompanions(objCol.creators[1:], objCol, deps, depLnks)

                # Track progress
                step = (90 - stepsDone) / len(objCol.creators)
                stepsDone = stepsDone + step
                self.model.editor.statusBar.progress.SetValue(int(stepsDone))

            self.finaliseDepLinks(depLnks)

        finally:
            self.inspector.vetoSelect = false

        self.model.editor.statusBar.progress.SetValue(80)
        self.refreshContainment()
        self.model.editor.statusBar.progress.SetValue(0)
        self.model.editor.statusBar.setHint(' ')

    def initSelection(self):
        """ Create a selection group """
        self.selection = SelectionTags.SingleSelectionGroup(self,
              self.senderMapper, self.inspector, self)

    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl
        """

        dontEval = [ctrlCompanion.windowParentName, ctrlCompanion.windowIdName]

        args = self.setupArgs(ctrlName, params, dontEval, compClass = ctrlCompanion)

        parent = Utils.ctrlNameFromSrcRef(params[ctrlCompanion.windowParentName])
##        if params[ctrlCompanion.windowParentName] == 'self':
##            parent = ''
##        else:
##            parent = string.split(params[ctrlCompanion.windowParentName], '.')[1]

        # Create control and companion
        companion = ctrlCompanion(ctrlName, self, None, ctrlClass)

        self.addObject(ctrlName, companion,
          companion.designTimeControl(None, None, args), parent)

        return ctrlName

    def newControl(self, parent, ctrlClass, ctrlCompanion, position = None, size = None):
        """ At design time, when adding a new ctrl from the palette, create and
            register given control and companion.
            See also: loadControl
        """
        ctrlName = self.newObjName(ctrlClass.__name__)

        self.checkHost(ctrlCompanion)

        companion = ctrlCompanion(ctrlName, self, parent, ctrlClass)

        params = companion.designTimeSource('wxPoint(%d, %d)' % (position.x, position.y))

        if parent.GetName() != self.GetName():
            parentName = parent.GetName()
            params[companion.windowParentName] = 'self.'+parentName
        else:
            parentName = ''
            params[companion.windowParentName] = 'self'

        self.addObject(ctrlName, companion,
          companion.designTimeControl(position, size), parentName)

        params[companion.windowIdName] = companion.id
        companion.persistConstr(ctrlClass.__name__, params)

        self.refreshContainment()

        return ctrlName

    def removeEvent(self, name):
        # XXX Remove event!
        self.inspector.eventUpdate(name, true)

    def getObjectsOfClass(self, theClass):
        """ Overridden to also add objects from the DataView """
        results = InspectableObjectView.getObjectsOfClass(self, theClass)
        dataResults = {}
        for objName in self.dataView.objects.keys():
            if self.dataView.objects[objName][1].__class__ is theClass:
                dataResults['self.'+objName] = self.dataView.objects[objName][1]
        results.update(dataResults)
        return results

    def getAllObjects(self):
        """ Overridden to also add objects from the DataView """
        results = InspectableObjectView.getAllObjects(self)
        for objName in self.dataView.objects.keys():
            results[Utils.srcRefFromCtrlName(objName)] = \
                  self.dataView.objects[objName][1]
        return results

    def selectParent(self, ctrl):
        """ Change the selection to the parent of the currently selected control. """
        if self.selection or self.multiSelection:
            if self.multiSelection:
                self.clearMultiSelection()
                self.assureSingleSelection()

            if ctrl != self:
                parent = ctrl.GetParent()
                parentName = parent.GetName()
                if parentName == self.GetName():
                    parentName = ''
                self.inspector.containment.selectName(parentName)

    def renameFrame(self, oldName, newName):
        """ Hook that also updates the Model and window ids of the
            Frame when it's name changes """
        self.SetName(newName)

        # update windowids & ctrls
        for comp, ctrl, dummy in self.objects.values():
            comp.updateWindowIds()

        # propagate rename to model
        self.model.renameMain(oldName, newName)

        # propagate rename to inspector
        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = ''

        self.refreshContainment(selName)

    def deleteCtrl(self, name, parentRef = None):
        """ Delete a control, update selection and parent tree """
        ctrlInfo = self.objects[name]
        if ctrlInfo[1] == self:
            wxMessageBox("Can't delete frame")
            return
        parRel = None
        # build relationship, this will only happen for the first call
        if not parentRef:
            # select parent so long, pretty soon won't be able to ask who
            # the parent is
            parentName = ctrlInfo[1].GetParent().GetName()
            if parentName == self.GetName(): parentName = ''

            self.selectParent(ctrlInfo[1])
            parRel, parRef = self.buildParentRelationship()
        else:
            parRef = parentRef

        # notify other components of deletion
        self.notifyAction(ctrlInfo[0], 'delete')

        # delete all children
        children = parRef[name]
        for child in children.keys():
            self.deleteCtrl(child, parRef)

        InspectableObjectView.deleteCtrl(self, name)

        ctrlInfo[1].Destroy()

        if parRel is not None:
            self.refreshContainment(parentName)

    def selectNone(self):
        if self.selection:
            self.selection.selectNone()
        elif self.multiSelection:
            for sel in self.multiSelection:
                sel.selectNone()
                sel.destroy()
            self.multiSelection = []
            self.assureSingleSelection()

    def close(self):
        self.Close()

    ignoreWindows = [wxToolBar, wxStatusBar]

    def connectToolBar(self, toolBar):
        parRel, parRef = self.buildParentRelationship()
        children = parRef['']
        for childName in children.keys():
            childCompn, childCtrl = self.objects[childName][:2]
            if not childCtrl.__class__ in self.ignoreWindows:
                pos = childCtrl.GetPosition()
                childCtrl.SetPosition( (pos.x, pos.y + toolBar.GetSize().y) )

    def disconnectToolBar(self, toolBar):
        parRel, parRef = self.buildParentRelationship()
        children = parRef['']
        for childName in children.keys():
            childCompn, childCtrl = self.objects[childName][:2]
            if not childCtrl.__class__ in self.ignoreWindows:
                pos = childCtrl.GetPosition()
                childCtrl.SetPosition( (pos.x, pos.y - toolBar.GetSize().y) )

    def checkChildCtrlClick(self, ctrlName, ctrl, companion, clickPos):
        """ Check whether the click on the control actually falls
            within a region occupied by one of it's children.
            The click is then transfered to the child. """
        selCtrl, selCompn, selPos = ctrl, companion, clickPos


        if companion.container:
            parent = ctrl
        else:
            parent = ctrl.GetParent()

        # Hack: Shortcut intersection tests if click was directly in a proxy
        #       container
        if wxPlatform == '__WXGTK__' and hasattr(ctrl, 'proxyContainer'):
            return selCtrl, selCompn, selPos

        # Workaround toolbar offset bug
        offset = [0, 0]
        if parent == self:
            tb = self.GetToolBar()
            if tb:
                offset[1] = tb.GetSize().y #* -1

        # XXX Is this going to become to slow for frames with many ctrls?
        parRel, parRef = self.buildParentRelationship()
        if ctrl == self:
            officialParent = ''
            children = parRef['']
        else:
            officialParent = ctrlName
            children = parRef[ctrlName]

        for childName in children.keys():
            childCompn, childCtrl = self.objects[childName][:2]
            try:
                pos = childCtrl.GetPosition()
                sze = childCtrl.GetSize()

##                realParent = childCtrl.GetParent()
##                if realParent.this[:8] != \
##                      self.objects[officialParent][1].this[:8]:
##                    print 'adjusting pos', pos, realParent.GetPosition()
##                    pos = realParent.GetPosition()
            except:
                print 'could not get child ctrl size', childCtrl
            else:
                realParent = childCtrl.GetParent()
                # Compensate for BlankWindowPages's offset
                if realParent.this[:8] != \
                      self.objects[officialParent][1].this[:8]:
                    offset[0] = offset[0] + realParent.GetPosition().x
                    offset[1] = offset[1] + realParent.GetPosition().y

                # Check for intersection
                if childCtrl.IsShown() and realParent.IsShown() and \
                      wxIntersectRect((clickPos.x - offset[0],
                                       clickPos.y - offset[1], 1, 1),
                                      (pos.x, pos.y, sze.x, sze.y)) is not None:

                    selCtrl = childCtrl
                    selCompn = childCompn
                    selPos = wxPoint(clickPos.x - offset[0] - pos.x,
                          clickPos.y - offset[1] - pos.y)
                    break

        return selCtrl, selCompn, selPos

    def clearMultiSelection(self):
        """ Destroys multi selection groups """
        for sel in self.multiSelection:
            sel.destroy()
        self.multiSelection = []

    def assureSingleSelection(self):
        """ Assure that a valid single selection exists """
        if not self.selection:
            self.selection = SelectionTags.SingleSelectionGroup(self,
                  self.senderMapper, self.inspector, self)

    def flattenParentRelationship(self, rel, lst):
        """ Add all items in a nested dictionary into a single list """
        for itm in rel.keys():
            lst.append(itm)
            self.flattenParentRelationship(rel[itm], lst)

    def expandNamesToContainers(self, ctrlNames):
        """ Expand set of names to include the names of all their children """
        exp = ctrlNames[:]
        rel, ref = self.buildParentRelationship()
        for ctrl in ctrlNames:
            children = []
            self.flattenParentRelationship(ref[ctrl], children)
            exp.extend(children)

        return exp

    def collapseNamesToContainers(self, ctrlNames):
        """ Collapse set of names to exclude the names of all their children """

        def hasParentInList(item, list):
            return intem in list
        exp = ctrlNames[:]

        colLst = filter(\
            lambda name, names=ctrlNames, objs=self.objects: \
                objs[name][2] not in names, ctrlNames)

        return colLst

    def selectControlByPos(self, ctrl, pos, multiSelect):
        """ Handle selection of a control from a users click of creation
            of a new one if a component was selected on the palette.

            Some ctrls do not register clicks, the click is then
            picked up from the parent which checks if a click
            intersects any child regions. For efficiency this
            is only applied for 2 levels.

            Also handles single and multiple selection logic.

            #Returns true if the ctrl also wants the click event
        """
        self.vetoResize = true
        try:
            if ctrl == self:
                companion = self.companion
            else:
                companion = self.objects[ctrl.GetName()][0]

            ctrlName = companion.name

            selCtrl, selCompn, selPos = \
                  self.checkChildCtrlClick(ctrlName, ctrl, companion, pos)

            # Component on palette selected, create it
            if self.compPal.selection:
                if selCompn.container:
                    parent = selCtrl
                    pos = selPos
                else:
                    parent = selCtrl.GetParent()
                    screenPos = selCtrl.ClientToScreen(selPos)
                    pos = parent.ScreenToClient(screenPos)

                # Workaround toolbar offset bug
                if parent == self:
                    tb = self.GetToolBar()
                    if tb:
                        pos.y = pos.y - tb.GetSize().y

                # Granularise position
                pos = wxPoint(SelectionTags.granularise(pos.x),
                              SelectionTags.granularise(pos.y))

                ctrlName = self.newControl(parent, self.compPal.selection[1],
                    self.compPal.selection[2], pos)
                self.compPal.selectNone()

                if self.selection:
                    ctrl = self.objects[ctrlName][1]
                    self.selection.selectCtrl(ctrl, self.objects[ctrlName][0])
            # Select ctrl
            else:
                if self.selection or self.multiSelection:
                    #evtPos = event.GetPosition()
    ##                ctrlName = companion.name
    ##
    ##                selCtrl, selCompn, selPos = \
    ##                      self.checkChildCtrlClick(ctrlName, ctrl, companion, pos)

                    # Multi selection
                    if multiSelect:
                        # Verify that it's a legal multi selection
                        # They must have the same parent
                        if self.selection:
                            if selCtrl.GetParent().this != self.selection.selection.GetParent().this:
                                return
                        elif self.multiSelection:
                            if selCtrl.GetParent().this != self.multiSelection[0].selection.GetParent().this:
                                return

                        if not self.multiSelection:
                            # don't select if multiselecting single selection
                            if selCtrl == self.selection.selection:
                                return

                            newSelection = SelectionTags.MultiSelectionGroup(self,
                                  self.senderMapper, self.inspector, self)
                            newSelection.assign(self.selection)
                            self.selection.destroy()
                            self.selection = None
                            self.multiSelection = [newSelection]

                        # Check that this is not a de-selection
                        # don't deselect if there's only one
                        if len(self.multiSelection) > 1:
                            for selIdx in range(len(self.multiSelection)):
                                if self.multiSelection[selIdx].selection == ctrl:
                                    self.multiSelection[selIdx].destroy()
                                    del self.multiSelection[selIdx]
                                    # Change to single selection if 2nd last one
                                    # deselected
                                    if len(self.multiSelection) == 1:
                                        self.selection = SelectionTags.SingleSelectionGroup(self,
                                            self.senderMapper, self.inspector, self)

                                        self.selection.assign(self.multiSelection[0])
                                        self.selection.selectCtrl(self.multiSelection[0].selection,
                                              self.multiSelection[0].selCompn)
                                        self.clearMultiSelection()
                                    return

                        newSelection = SelectionTags.MultiSelectionGroup(self,
                              self.senderMapper, self.inspector, self)
                        newSelection.selectCtrl(selCtrl, selCompn)
                        self.multiSelection.append(newSelection)
                    # Single selection
                    else:
                        # Deselect multiple selection or start multiple drag
                        if self.multiSelection:
                            for sel in self.multiSelection:
                                if selCtrl == sel.selection:
                                    sel.moveCapture(selCtrl, selCompn, selPos)
                                    self.mainMultiDrag = selCtrl
                                    others = self.multiSelection[:]
                                    others.remove(sel)
                                    for capSel in others:
                                        capSel.moveCapture(capSel.selection, capSel.selCompn, selPos)
                                    return

                            self.clearMultiSelection()

                        self.assureSingleSelection()

                        self.selection.selectCtrl(selCtrl, selCompn)
                        self.selection.moveCapture(selCtrl, selCompn, selPos)

                        return 0#selCompn.letClickThru
        finally:
            self.vetoResize = false

    def OnFramePos(self, event):
        """ Called when frame is repositioned """
#        self.assureSingleSelection()
#        self.selection.selectCtrl(self, self.companion)
        if self.selection and self.selection.selection == self:
            self.inspector.constructorUpdate('Position')
        event.Skip()

    def OnCloseWindow(self, event):
        """ When the Designer closes, the code generation process is started.
            General Inspector and Designer clean-up"""
        self.destroying = true
        if self.selection:
            self.selection.destroy()
            self.selection = None
        elif self.multiSelection:
            for sel in self.multiSelection:
                sel.destroy()
            self.multiSelection = None

        self.inspector.cleanup()
        self.inspector.containment.cleanup()

        # Make source r/w
        self.model.views['Source'].disableSource(false)

        if self.saveOnClose:
            self.saveCtrls(self.dataView.objectOrder[:])
            self.model.modified = true
            self.model.editor.updateModulePage(self.model)

            self.dataView.saveCtrls([])

            self.refreshModel()


        self.dataView.deleteFromNotebook('Source', 'Data')

        self.cleanup()
        self.Show(false)
        self.Destroy()

        del self.model.views['Designer']
        del self.companion

        self.destroy()
        event.Skip()

    def OnRightDown(self, event):
        """ Store popup position of the menu relative to the control that
            triggered the event """
        ctrl = self.senderMapper.getObject(event)
        screenPos = ctrl.ClientToScreen(wxPoint(event.GetX(), event.GetY()))
        parentPos = self.ScreenToClient(screenPos)
        self.popx = parentPos.x
        self.popy = parentPos.y

    def OnEditor(self, event):
        """ Bring Editor to the front """
        self.model.editor.Show(true)
        self.model.editor.Raise()

    def OnInspector(self, event):
        """ Bring Inspector to the front """
        self.inspector.Show(true)
        self.inspector.Raise()

    def OnControlDelete(self, event):
        """ Delete the currently selected controls """
        ctrls = []
        if self.selection:
            if self.selection.isProxySelection():
                wxLogError('Nothing to delete')
                return
            ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        #map(self.deleteCtrl, ctrls)
        for ctrlName in ctrls:
            self.deleteCtrl(ctrlName)

    def OnCtrlHelp(self, event):
        """ Show help for the selected control """
        if self.inspector.selCmp:
            Help.showHelp(self, Help.wxWinHelpFrame,
              self.inspector.selCmp.wxDocs, None)

    def OnAlignSelected(self, event):
        """ Show alignment dialog for multi selections"""
        if self.multiSelection:
            dlg = CtrlAlign.ControlAlignmentFrame(self, self.multiSelection)
            try: dlg.ShowModal()
            finally: dlg.Destroy()

    def OnSizeSelected(self, event):
        """ Show size dialog for multi selections"""
        if self.multiSelection:
            dlg = CtrlSize.ControlSizeFrame(self, self.multiSelection)
            try: dlg.ShowModal()
            finally: dlg.Destroy()

    def OnSelectParent(self, event):
        """ Select parent of the selected control """
        if self.selection:
            self.selectParent(self.selection.selection)
        elif self.multiSelection:
            self.selectParent(self.multiSelection[0].selection)

#---Clipboard operations--------------------------------------------------------
    def OnCutSelected(self, event):
        """ Cut current selection to the clipboard """
        if self.selection:
            if self.selection.isProxySelection():
                wxLogError('Nothing to cut')
                return
            else:
                ctrls = [self.selection.name]
            #self.selectParent(self.selection.selection)
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        output = []
        self.cutCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(string.join(output, os.linesep))

        self.refreshContainment()

    def OnCopySelected(self, event):
        """ Copy current selection to the clipboard """
        if self.selection:
            if self.selection.isProxySelection():
                wxLogError('Nothing to copy')
                return
            else:
                ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        output = []
        self.copyCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(string.join(output, os.linesep))

    def OnPasteSelected(self, event):
        """ Paste current clipboard contents into the current selection """
        if self.selection:
            # If the selection is not a container, select it's parent (a container)
            if not self.selection.selCompn.container:
                self.selectParent(self.selection.selection)

            pasted = self.pasteCtrls(self.selection.name,
                  string.split(Utils.readTextFromClipboard(), os.linesep))

            if len(pasted):
                self.refreshContainment()
                pasted = self.collapseNamesToContainers(pasted)
                # Single control pasted, select it
                if len(pasted) == 1:
                    if self.selection.isProxySelection():
                        self.selection.selection.linkToNewestControl()
                        self.objects[pasted[0]][1].Reparent(self.selection.selection)

                    self.selection.selectCtrl(self.objects[pasted[0]][1],
                          self.objects[pasted[0]][0])
                # Multiple controls pasted, select them
                else:
                    if self.selection.isProxySelection():
                        # Undo the pasting
                        for ctrlName in pasted:
                            self.deleteCtrl(ctrlName)
                        self.selection.selectNone()
                        self.inspector.cleanup()
                        wxLogError('Only 1 control can be pasted into this container')
                    else:
                        self.selection.destroy()
                        self.selection = None
                        self.multiSelection = []
                        for ctrlName in pasted:
                            selCompn, selCtrl, prnt = self.objects[ctrlName]
                            newSelection = SelectionTags.MultiSelectionGroup(self,
                                  self.senderMapper, self.inspector, self)
                            newSelection.selectCtrl(selCtrl, selCompn)
                            self.multiSelection.append(newSelection)

    def OnRecreateSelected(self, event):
        """ Recreate the current selection by cutting and pasting it.
            The clipboard is not disturbed.
            This is useful for applying changes to constructor parameters """
        if self.selection and self.selection.selection != self:
            output = []
            ctrlName = self.selection.name
            # XXX Boa should be able to tell me this
            parent = self.selection.selection.GetParent()
            if parent.GetId() == self.GetId():
                parentName = ''
            else:
                parentName = parent.GetName()

            self.cutCtrls([ctrlName], [], output)
            self.pasteCtrls(parentName, output)

#---Moving/Sizing selections with the keyboard----------------------------------
    def getSelAsList(self):
        if self.selection:
            return [self.selection]
        elif self.multiSelection:
            return self.multiSelection
        else:
            return []

    def moveUpdate(self, sel):
        sel.setSelection(true)
        sel.resizeCtrl()

    def OnMoveLeft(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.x = sel.position.x - 1
                sel.startPos.x = sel.startPos.x - 1
                self.moveUpdate(sel)
    def OnMoveRight(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.x = sel.position.x + 1
                sel.startPos.x = sel.startPos.x + 1
                self.moveUpdate(sel)
    def OnMoveUp(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.y = sel.position.y - 1
                sel.startPos.y = sel.startPos.y - 1
                self.moveUpdate(sel)
    def OnMoveDown(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.y = sel.position.y + 1
                sel.startPos.y = sel.startPos.y + 1
                self.moveUpdate(sel)

    def sizeUpdate(self, sel):
        sel.resizeCtrl()
        sel.setSelection(true)

    def OnWidthInc(self, event):
        sel = self.selection
        if sel and sel.selection != self:
            sel.size.x = sel.size.x + 1
            self.sizeUpdate(sel)
    def OnWidthDec(self, event):
        sel = self.selection
        if sel and sel.selection != self and sel.size.x > 0:
            sel.size.x = sel.size.x - 1
            self.sizeUpdate(sel)
    def OnHeightInc(self, event):
        sel = self.selection
        if sel and sel.selection != self:
            sel.size.y = sel.size.y + 1
            self.sizeUpdate(sel)
    def OnHeightDec(self, event):
        sel = self.selection
        if sel and sel.selection != self and sel.size.y > 0:
            sel.size.y = sel.size.y - 1
            self.sizeUpdate(sel)

    def OnSnapToGrid(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.x = SelectionTags.granularise(sel.position.x)
                sel.position.y = SelectionTags.granularise(sel.position.y)
                sel.startPos.x = sel.position.x
                sel.startPos.y = sel.position.y
                self.moveUpdate(sel)


class DesignerControlsEvtHandler(wxEvtHandler):
    def __init__(self, designer):
        wxEvtHandler.__init__(self)
        self.designer = designer

        self.drawGridMethods = {'lines' : self.drawGrid_intersectingLines,
                                'dots'  : self.drawGrid_dots,
                                'bitmap': self.drawGrid_bitmap,
                                'grid'  : self.drawGrid_grid}

    def connectEvts(self, ctrl):
        EVT_MOTION(ctrl, self.OnMouseOver)
        EVT_LEFT_DOWN(ctrl, self.OnControlSelect)
        EVT_LEFT_UP(ctrl, self.OnControlRelease)
        EVT_LEFT_DCLICK(ctrl, self.OnControlDClick)
        EVT_SIZE(ctrl, self.OnControlResize)
        EVT_MOVE(ctrl, self.OnControlMove)

        # XXX Hack testing grid paint, should be flag esPaintGrid for companions
        if Preferences.drawDesignerGrid:
            if Preferences.drawDesignerGridForSubWindows and \
                  ctrl.__class__  in (wxPanel, wxScrolledWindow) or \
                  ctrl.__class__ == DesignerView:
                EVT_PAINT(ctrl, self.OnPaint)


    def OnMouseOver(self, event):
        if event.Dragging():
            dsgn = self.designer
            pos = event.GetPosition()
            ctrl = dsgn.senderMapper.getObject(event)

            if dsgn.selection:
                dsgn.selection.moving(ctrl, pos)
            elif dsgn.multiSelection:
                for sel in dsgn.multiSelection:
                    sel.moving(ctrl, pos, dsgn.mainMultiDrag)

        event.Skip()

    def OnControlSelect(self, event):
        print 'OnControlSelect'
        """ Control is clicked. Either select it or add control from palette """
        dsgn = self.designer
        # XXX wxPython bug workaround only here for when testing
        if event.GetEventObject():
            ctrl = dsgn.senderMapper.getObject(event)
        else:
            ctrl = dsgn
        if dsgn.selectControlByPos(ctrl, event.GetPosition(), event.ShiftDown()):
            event.Skip()

    def OnControlRelease(self, event):
        """ A select or drag operation is ended """
        dsgn = self.designer
        if dsgn.selection:
            dsgn.selection.moveRelease()
        elif dsgn.multiSelection:
            for sel in dsgn.multiSelection:
                sel.moveRelease()
            dsgn.mainMultiDrag = None
        event.Skip()

    def OnControlResize(self, event):
        """ Control is resized, emulate native wxWindows layout behaviour """
        dsgn = self.designer
        try:
            if dsgn.vetoResize:
                return
            if event.GetId() == dsgn.GetId():
                if event.GetSize().asTuple() == dsgn.lastSize:
                    return
                dsgn.lastSize = event.GetSize().asTuple()

                if dsgn.selection:
                    dsgn.selection.selectCtrl(dsgn, dsgn.companion)
                elif dsgn.multiSelection:
                    dsgn.clearMultiSelection()
                    dsgn.assureSingleSelection()
                    dsgn.selection.selectCtrl(dsgn, dsgn.companion)
                    return

                # Compensate for autolayout=false and 1 ctrl on frame behaviour
                # Needed because incl selection tags there are actually 5 ctrls

                if not dsgn.GetAutoLayout():
                    # Count children
                    c = 0
                    ctrl = None
                    for ctrlLst in dsgn.objects.values():
                        if len(ctrlLst) > 2 and ctrlLst[2] == '' and \
                          (ctrlLst[1].__class__ not in dsgn.ignoreWindows):
                            c = c + 1
                            ctrl = ctrlLst[1]

                    if c == 1:
                        s = dsgn.GetClientSize()
                        ctrl.SetDimensions(0, 0, s.x, s.y)

            if dsgn.selection:
                dsgn.selection.sizeFromCtrl()
                dsgn.selection.setSelection()
        finally:
            event.Skip()

    def OnControlDClick(self, event):
        dsgn = self.designer

        if dsgn.selection:
            ctrl = dsgn.senderMapper.getObject(event)

            dsgn.selectControlByPos(ctrl, event.GetPosition(), event.ShiftDown())
            if ctrl == dsgn:
                companion = dsgn.companion
                ctrlName = ''
            else:
                ctrlName = ctrl.GetName()
                companion = dsgn.objects[ctrlName][0]

            selCtrl, selCompn, selPos = \
                  dsgn.checkChildCtrlClick(ctrlName, ctrl, companion,
                  event.GetPosition())

            selCompn.defaultAction()

            dsgn.selection.moveRelease()

    def OnControlMove(self, event):
        ctrl = self.designer.senderMapper.getObject(event)
        parent = ctrl.GetParent()
        if parent:
            wxPostEvent(parent, wxSizeEvent( parent.GetSize() ))
        event.Skip()

#---Grid drawing----------------------------------------------------------------

    def _drawLines(self, dc, col, loglFunc, sze, sg):
        """ Draw horizontal and vertical lines
        """
        pen1 = wxPen(col)
        dc.SetPen(pen1)
        dc.SetLogicalFunction(loglFunc)
        for y in range(sze.y / sg + 1):
            dc.DrawLine(0, y * sg, sze.x, y * sg)

        for x in range(sze.x / sg + 1):
            dc.DrawLine(x * sg, 0, x * sg, sze.y)

    def drawGrid_intersectingLines(self, dc, sze, sg):
        """ Cute hack to draw dots by intersecting lines
        """
        bgCol = dc.GetBackground().GetColour()
        xorBgCol = wxColour(255^bgCol.Red(), 255^bgCol.Green(), 255^bgCol.Blue())

        self._drawLines(dc, xorBgCol, wxCOPY, sze, sg)
        self._drawLines(dc, wxNamedColour('WHITE'), wxXOR, sze, sg)

    darken = 15
    def drawGrid_grid(self, dc, sze, sg):
        """ The default method, drawing horizontal and vertical grid lines.
        """
        bgCol = dc.GetBackground().GetColour()
        darkerBgCol = wxColour(max(bgCol.Red()   -self.darken, 0),
                               max(bgCol.Green() -self.darken, 0),
                               max(bgCol.Blue()  -self.darken, 0))

        self._drawLines(dc, darkerBgCol, wxCOPY, sze, sg)

    def drawGrid_dots(self, dc, sze, sg):
        """ The slowest method, drawing each dot of the grid individually
        """
        pen1 = wxPen(wxNamedColour('BLACK'))
        dc.SetPen(pen1)
        for y in range(sze.y / sg + 1):
            for x in range(sze.x / sg + 1):
                dc.DrawPoint(x * sg, y * sg)

    def drawGrid_bitmap(self, dc, sze, sg):
        """ This should be the most efficient method, when the granularity is
            changed, a new (possibly +-32x32) bitmap should be created with
            transparent background and black grid points. This can then be
            blitted over background
        """
        pass

    def OnPaint(self, event):
        # XXX Paint event fired after destruction, should remove EVT ?
        if hasattr(self.designer, 'senderMapper'):
            ctrl = self.designer.senderMapper.getObject(event)

            dc = wxPaintDC(ctrl)
            sze = ctrl.GetClientSize()
            sg = SelectionTags.screenGran

            drawGrid = self.drawGridMethods[Preferences.drawGridMethod]

            dc.BeginDrawing()
            try:
                drawGrid(dc, sze, sg)
            finally:
                dc.EndDrawing()

        event.Skip()
