#----------------------------------------------------------------------
# Name:        Designer.py
# Purpose:     Visual frame designer
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2004 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

print 'importing Views.Designer'

import copy, os, pprint, math

from wxPython.wx import *

import Preferences, Utils, Help
from Preferences import IS
import CtrlAlign, CtrlSize
import sourceconst

from InspectableViews import InspectableObjectView
import SelectionTags

[wxID_CTRLPARENT, wxID_EDITCUT, wxID_EDITCOPY, wxID_EDITPASTE, wxID_EDITDELETE,
 wxID_SHOWINSP, wxID_SHOWEDTR, wxID_CTRLHELP, wxID_EDITALIGN, wxID_EDITSIZE,
 wxID_EDITRECREATE, wxID_EDITSNAPGRID, wxID_EDITRELAYOUT, wxID_EDITRELAYOUTSEL,
 wxID_EDITRELAYOUTDESGN, wxID_EDITCREATEORDER, wxID_EDITFITINSIDESIZER,
 wxID_EDITFITSIZER,
] = Utils.wxNewIds(18)

[wxID_EDITMOVELEFT, wxID_EDITMOVERIGHT, wxID_EDITMOVEUP, wxID_EDITMOVEDOWN,
 wxID_EDITWIDTHINC, wxID_EDITWIDTHDEC, wxID_EDITHEIGHTINC, wxID_EDITHEIGHTDEC,
] = Utils.wxNewIds(8)

[wxID_EDITSELECTLEFT, wxID_EDITSELECTRIGHT, wxID_EDITSELECTUP, wxID_EDITSELECTDOWN,
] = Utils.wxNewIds(4)

# XXX When opening a frame with a connected menubar, the frame is not selected
# XXX in the inspector

class DesignerView(wxFrame, InspectableObjectView, Utils.FrameRestorerMixin):
    """ Frame Designer for design-time creation/manipulation of visual controls
        on frames. """
    viewName = 'Designer'
    docked = false
    collectionMethod = sourceconst.init_ctrls
    supportsParentView = true

    def setupArgs(self, ctrlName, params, dontEval, parent=None, compClass=None, evalDct={}, doId=true):
        """ Create a dictionary of parameters for the constructor of the
            control from a dictionary of string/source parameters.
        """
        args = InspectableObjectView.setupArgs(self, ctrlName, params, dontEval, evalDct=evalDct)

        if compClass:
            prnt = compClass.windowParentName
            wId = compClass.windowIdName
            doId = not compClass.suppressWindowId
        else:
            prnt = 'parent'
            wId = 'id'
            doId = true

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
                dot = srcPrnt.find('.')
                if dot != -1:
                    srcPrnt = srcPrnt[dot + 1:]
                else: raise 'Component name illegal '+ srcPrnt
                args[prnt] = self.objects[srcPrnt][1]


        if doId: args[wId] = wxNewId()

        return args

    defPos = wxPyDefaultPosition

    def __init__(self, parent, inspector, model, compPal, CompanionClass, 
          dataView):
        self.controllerView = self
        self.objectNamespace = DesignerNamespace(self)

        args = self.setupArgs(model.main, model.mainConstr.params,
          CompanionClass.handledConstrParams, parent, CompanionClass, 
          model.specialAttrs)

        style = wxDEFAULT_FRAME_STYLE
        wxFrame.__init__(self, parent, -1, args.get('title', ''),
                                           args.get('pos', CompanionClass.defFramePos),
                                           args.get('size', CompanionClass.defFrameSize),
                                           style=CompanionClass.defFrameStyle)
        InspectableObjectView.__init__(self, inspector, model, compPal)
        self.controllerView = self

        if model.dialogLook:
            self.SetBackgroundColour(
                  wxSystemSettings_GetSystemColour(wxSYS_COLOUR_BTNFACE))

        self.SetIcon(IS.load('Images/Icons/Designer.ico'))

        EVT_MOVE(self, self.OnFramePos)

        self.pageIdx = -1
        self.dataView = dataView
        self.dataView.controllerView = self
        self.sizersView = None
        #self.controllerView = self
        self.saveOnClose = true
        self.confirmCancel = false

        self.ctrlEvtHandler = DesignerControlsEvtHandler(self)

        self.companion = CompanionClass(self.model.main, self, self)
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
        # flags controlling behaviour in resize event
        self.vetoResize = false
        self.forceResize = false
        self.deletingCtrl = false
        #self.objectNamespace = DesignerNamespace(self)
        # XXX Move this definition into actions

        self.menu = wxMenu()

        self.menu.Append(wxID_CTRLPARENT, 'Up')
        self.menu.AppendSeparator()
        self.menu.Append(wxID_EDITCUT, 'Cut')
        self.menu.Append(wxID_EDITCOPY, 'Copy')
        self.menu.Append(wxID_EDITPASTE, 'Paste')
        self.menu.Append(wxID_EDITDELETE, 'Delete')
        self.menu.AppendSeparator()
        self.menu.Append(wxID_EDITRECREATE, 'Recreate')
        self.menu.Append(wxID_EDITRELAYOUTSEL, 'Relayout selection')
        self.menu.Append(wxID_EDITRELAYOUTDESGN, 'Relayout Designer')
        self.menu.AppendSeparator()
        self.menu.Append(wxID_EDITFITSIZER, 'Fit sizer')
        #self.menu.Append(wxID_EDITFITINSIDESIZER, 'Fit sizer')
        self.menu.AppendSeparator()
        self.menu.Append(wxID_EDITSNAPGRID, 'Snap to grid')
        self.menu.Append(wxID_EDITALIGN, 'Align...')
        self.menu.Append(wxID_EDITSIZE, 'Size...')
        self.menu.AppendSeparator()
        self.menu.Append(wxID_EDITCREATEORDER, 'Creation/Tab order...')

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
        EVT_MENU(self, wxID_EDITRELAYOUTSEL, self.OnRelayoutSelection)
        EVT_MENU(self, wxID_EDITRELAYOUTDESGN, self.OnRelayoutDesigner)
        EVT_MENU(self, wxID_EDITSNAPGRID, self.OnSnapToGrid)
        EVT_MENU(self, wxID_EDITCREATEORDER, self.OnCreationOrder)
        EVT_MENU(self, wxID_EDITFITSIZER, self.OnFitSizer)
        #EVT_MENU(self, wxID_EDITFITINSIDESIZER, self.OnFitInsideSizer)
        

        EVT_MENU(self, wxID_EDITMOVELEFT, self.OnMoveLeft)
        EVT_MENU(self, wxID_EDITMOVERIGHT, self.OnMoveRight)
        EVT_MENU(self, wxID_EDITMOVEUP, self.OnMoveUp)
        EVT_MENU(self, wxID_EDITMOVEDOWN, self.OnMoveDown)
        EVT_MENU(self, wxID_EDITWIDTHINC, self.OnWidthInc)
        EVT_MENU(self, wxID_EDITWIDTHDEC, self.OnWidthDec)
        EVT_MENU(self, wxID_EDITHEIGHTINC, self.OnHeightInc)
        EVT_MENU(self, wxID_EDITHEIGHTDEC, self.OnHeightDec)

        EVT_MENU(self, wxID_EDITSELECTLEFT, self.OnSelectLeft)
        EVT_MENU(self, wxID_EDITSELECTRIGHT, self.OnSelectRight)
        EVT_MENU(self, wxID_EDITSELECTUP, self.OnSelectUp)
        EVT_MENU(self, wxID_EDITSELECTDOWN, self.OnSelectDown)

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

                          ('SelectLeft', wxID_EDITSELECTLEFT),
                          ('SelectRight', wxID_EDITSELECTRIGHT),
                          ('SelectUp', wxID_EDITSELECTUP),
                          ('SelectDown', wxID_EDITSELECTDOWN),
                        ):
            tpe, key, code = Preferences.keyDefs[name]
            accLst.append((tpe, key, wId))

        self.SetAcceleratorTable(wxAcceleratorTable(accLst))

    def generateMenu(self):
        return Utils.duplicateMenu(self.menu)

    def saveCtrls(self, definedCtrls, module=None):
        """ Generate source code for Designer """

        if not module:
            module = self.model.getModule()
        # Remove all collection methods
        for oc in self.model.identifyCollectionMethods():
            if len(oc) > len('_init_coll_') and oc[:11] == '_init_coll_':
##                module = self.model.getModule()
                module.removeMethod(self.model.main, oc)

        # Update all size and pos parameters possibly updated externally
        for compn, ctrl, prnt in self.objects.values():
            compn.updatePosAndSize()

        if self.sizersView and self.sizersView.objects:
            collDeps = ['%sself.%s()'%(sourceconst.bodyIndent, 
                                       sourceconst.init_sizers)]
        else:
            collDeps = None

        # Generate code
        InspectableObjectView.saveCtrls(self, definedCtrls, module, collDeps)

        # Regenerate window ids
        companions = map(lambda i: i[0], self.objects.values())
        self.model.writeWindowIds(self.collectionMethod, companions)

    def renameCtrlAndParentRefs(self, oldName, newName, children=()):
        # rename other ctrl references like parent
        for ctrl in self.objectOrder:
            # Notify
            self.objects[ctrl][0].renameCtrlRefs(oldName, newName)
            # Rename childrens' parents
            if ctrl in children:
                self.objects[ctrl][2] = newName
        # also do collections
        for coll in self.collEditors.values():
            coll.companion.renameCtrlRefs(oldName, newName)

    def renameCtrl(self, oldName, newName):
        """ Rename control, references to control and update parent tree """

        prel, pref = self.buildParentRelationship()

        # rename other ctrl references like parent
        children = pref[oldName].keys()
        self.renameCtrlAndParentRefs(oldName, newName, children)

        InspectableObjectView.renameCtrl(self, oldName, newName)
        
        if self.sizersView:
            self.sizersView.designerRenameNotify(oldName, newName)
        selName = self.inspector.containment.selectedName()
        if selName == oldName: 
            selName = newName
        
        self.refreshContainment(selName)

        if self.selection.name == oldName:
            self.selection.name = newName

    def renameFrame(self, oldName, newName):
        """ Hook that also updates the Model and window ids of the
            Frame when it's name changes """
        self.SetName(newName)

        # propagate rename to model
        self.model.renameMain(oldName, newName)

        # update window ids in designer and data
        InspectableObjectView.renameFrame(self, oldName, newName)
        self.dataView.renameFrame(oldName, newName)
        if self.sizersView:
            self.sizersView.renameFrame(oldName, newName)

        # update window ids in collection items
        collEditors = self.collEditors.values() + \
                      self.dataView.collEditors.values()
        if self.sizersView:
            collEditors.extend(self.sizersView.collEditors.values())
                
        for collEditor in collEditors:
            collEditor.renameFrame(oldName, newName)

        # propagate rename to inspector
        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = ''

        self.refreshContainment(selName)

    def refreshCtrl(self):
        """ Model View method that is called when the Designer should
            create itself from source
        """
        if self.destroying or self.opened: return

        # Delete previous
        comps = {}

        # Create selection if none is defined
        if not self.selection:
            self.selection = \
                  SelectionTags.SingleSelectionGroup(self, self.inspector, self)

        self.model.editor.statusBar.setHint('Creating frame')

        try:
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
                
                self.OnRelayoutDesigner(None)

                if len(depLnks):
                    wxLogWarning(pprint.pformat(depLnks))
                    wxLogWarning('These links were not resolved (Details...)')

            finally:
                self.inspector.vetoSelect = false

            self.model.editor.statusBar.progress.SetValue(80)
            self.refreshContainment()
            self.model.editor.statusBar.progress.SetValue(0)
            self.model.editor.statusBar.setHint('Designer refreshed')
            self.opened = true
        except:
            self.model.editor.statusBar.progress.SetValue(0)
            #self.model.editor.statusBar.setHint('Error opening the Designer', 'Error')
            raise

    def refreshModel(self):
        """ Update model with streamed out controls """
        # Make source r/w
        self.model.views['Source'].disableSource(false)

        if self.saveOnClose:
            oldData = self.model.data

            module = self.model.getModule()
            # Stream out everything to Module & update model
            otherRefs = self.dataView.objectOrder[:]
            if self.sizersView:
                otherRefs.extend(self.sizersView.objectOrder[:])
            self.saveCtrls(otherRefs, module)
            self.dataView.saveCtrls([], module)
            if self.sizersView:
                self.sizersView.saveCtrls([], module)
            self.model.refreshFromModule()

            # Close data view before updates
            self.dataView.deleteFromNotebook('Source', 'Data')
            if self.sizersView:
                self.sizersView.deleteFromNotebook('Source', 'Sizers')

            # Update state (if changed)
            newData = self.model.data
            self.model.modified = self.model.modified or newData != oldData
            self.model.editor.updateModulePage(self.model)

            # Update other views
            InspectableObjectView.refreshModel(self)

            # Put the cursor somewhere (ideally at the first generated event)
            module = self.model.getModule()
            if module:
                self.model.views['Source'].GotoLine(module.classes[\
                  self.model.main].methods['__init__'].start)

            self.model.editor.setStatus('Designer session Posted.')
        else:
            self.dataView.deleteFromNotebook('Source', 'Data')
            if self.sizersView:
                self.sizersView.deleteFromNotebook('Source', 'Sizers')

            self.model.editor.setStatus('Designer session Cancelled.', 'Warning')

    def initSelection(self):
        """ Create a selection group """
        self.selection = SelectionTags.SingleSelectionGroup(self, self.inspector, self)

    def loadControl(self, CtrlClass, CtrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl
        """

        args = self.setupArgs(ctrlName, params, CtrlCompanion.handledConstrParams,
              compClass=CtrlCompanion, evalDct=self.model.specialAttrs)

        parent = Utils.ctrlNameFromSrcRef(params[CtrlCompanion.windowParentName])

        # Create control and companion
        companion = CtrlCompanion(ctrlName, self, None, CtrlClass)

        self.addObject(ctrlName, companion,
          companion.designTimeControl(None, None, args), parent)

        return ctrlName

    def newControl(self, parent, CtrlClass, CtrlCompanion, position = None, size = None):
        """ At design time, when adding a new ctrl from the palette, create and
            register given control and companion.
            See also: loadControl
        """
        self.checkHost(CtrlCompanion)

        ctrlName = self.newObjName(CtrlClass.__name__)
        companion = CtrlCompanion(ctrlName, self, parent, CtrlClass)
        params = companion.designTimeSource('wx.Point(%d, %d)' % (position.x, position.y))
        parentName, params[companion.windowParentName] = self.getParentNames(parent)

        self.addObject(ctrlName, companion,
          companion.designTimeControl(position, size), parentName)

        if not companion.suppressWindowId:
            params[companion.windowIdName] = companion.id

        companion.persistConstr(Utils.getWxPyNameForClass(CtrlClass), params)

        self.refreshContainment()

        return ctrlName

    def initObjCreator(self, constrPrs):
        # decorate class_name if it's a factory constructor
        if not constrPrs.class_name and constrPrs.factory:
            factoryObj, factoryMeth = constrPrs.factory
            constrPrs.class_name = self.dataView.objects[factoryObj][0].factory(factoryMeth)
        InspectableObjectView.initObjCreator(self, constrPrs)

    def initSizers(self, sizersView):
        self.sizersView = sizersView
        self.sizersView.controllerView = self

    def getParentNames(self, parent):
        if parent.GetName() != self.GetName():
            return parent.GetName(), 'self.'+parent.GetName()
        else:
            return '', 'self'

    def removeEvent(self, name):
        # XXX Remove event!
        self.inspector.eventUpdate(name, true)

    def getObjectsOfClass(self, theClass):
        """ Overridden to also add objects from the other views """
        results = InspectableObjectView.getObjectsOfClass(self, theClass)
        otherResults = {}
        for objName in self.dataView.objects.keys():
            if isinstance(self.dataView.objects[objName][1], theClass):
                otherResults['self.'+objName] = self.dataView.objects[objName][1]
        if self.sizersView:
            for objName in self.sizersView.objects.keys():
                if isinstance(self.sizersView.objects[objName][1], theClass):
                    otherResults['self.'+objName] = self.sizersView.objects[objName][1]
        results.update(otherResults)
        return results

    def getAllObjects(self):
        """ Overridden to also add objects from other views """
        results = InspectableObjectView.getAllObjects(self)
        for objName in self.dataView.objects.keys():
            results[Utils.srcRefFromCtrlName(objName)] = \
                  self.dataView.objects[objName][1]
        if self.sizersView:
            for objName in self.sizersView.objects.keys():
                results[Utils.srcRefFromCtrlName(objName)] = \
                      self.sizersView.objects[objName][1]
        return results

    def selectParent(self, ctrl):
        """ Change the selection to the parent of the currently selected control. """
        if self.selection or self.multiSelection:
            if self.multiSelection:
                self.clearMultiSelection()
                self.assureSingleSelection()

            if ctrl and ctrl != self:
                parentName, dummy = self.getParentNames(ctrl.GetParent())
                self.inspector.containment.selectName(parentName)


    def deleteCtrl(self, name, parentRef = None):
        """ Delete a control, update selection and parent tree """
        ctrlInfo = self.objects[name]
        if ctrlInfo[1] == self:
            wxMessageBox("Can't delete frame", style=wxOK|wxICON_ERROR, parent=self)
            return
        parRel = None
        # build relationship, this will only happen for the first call
        if not parentRef:
            # select parent so long, pretty soon won't be able to ask who
            # the parent is
            parentName, dummy = self.getParentNames(ctrlInfo[1].GetParent())

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

    def notifyAction(self, compn, action):
        InspectableObjectView.notifyAction(self, compn, action)
        self.dataView.notifyAction(compn, action)
        if self.sizersView:
            self.sizersView.notifyAction(compn, action)

    def close(self):
        self.Close()
    
    def focus(self):
        self.restore()

    def getSizerConnectList(self):
        if self.sizersView:
            return self.sizersView.sizerConnectList
        else:
            return None

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
            pos = childCtrl.GetPosition()
            sze = childCtrl.GetSize()
            realParent = childCtrl.GetParent()
            # Compensate for BlankWindowPages's offset
            if realParent.this[:8] != \
                  self.objects[officialParent][1].this[:8]:
                offset[0] += realParent.GetPosition().x
                offset[1] += realParent.GetPosition().y

            # Check for intersection
            if childCtrl.IsShown() and realParent.IsShown() and \
                  wxIntersectRect(wxRect(clickPos.x - offset[0],
                                   clickPos.y - offset[1], 1, 1),
                                  wxRect(pos.x, pos.y, max(sze.x, 1),
                                   max(sze.y, 1))) is not None:

                #print clickPos, offset, pos, sze

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
            self.selection = SelectionTags.SingleSelectionGroup(self, self.inspector, self)

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

        #colLst = filter(\
        #    lambda name, names=ctrlNames, objs=self.objects: \
        #        objs[name][2] not in names, ctrlNames)

        colLst = [name for name in ctrlNames 
                  if self.objects[name][2] not in ctrlNames]

        return colLst

    def selectControlByPos(self, ctrl, pos, multiSelect):
        """ Handle selection of a control from a users click of creation
            of a new one if a component was selected on the palette.

            Some ctrls do not register clicks, the click is then
            picked up from the parent which checks if a click
            intersects any child regions. For efficiency this
            is only applied for 2 levels.

            Also handles single and multiple selection logic.
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

                CtrlClass, CtrlCompanion = self.compPal.selection[1:3]
                if CtrlCompanion.host in ('Data', 'Sizers'):
                    view = self.model.views[CtrlCompanion.host]
                    view.focus()
                    view.OnSelectOrAdd()
                    return

                ctrlName = self.newControl(parent, CtrlClass, CtrlCompanion, pos)
                self.compPal.selectNone()

                if self.selection:
                    ctrl = self.objects[ctrlName][1]
                    self.selection.selectCtrl(ctrl, self.objects[ctrlName][0])
            # Select ctrl
            else:
                if self.selection or self.multiSelection:
                    # Multi selection
                    if multiSelect:
                        # Verify that it's a legal multi selection
                        # They must have the same parent
                        if self.selection:
                            if selCtrl.GetParent() != self.selection.selection.GetParent():
                                return
                        elif self.multiSelection:
                            if selCtrl.GetParent() != self.multiSelection[0].selection.GetParent():
                                return

                        if not self.multiSelection:
                            # don't select if multiselecting single selection
                            if selCtrl == self.selection.selection:
                                return

                            newSelection = SelectionTags.MultiSelectionGroup(self,
                                  self.inspector, self)
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
                                            self.inspector, self)

                                        self.selection.assign(self.multiSelection[0])
                                        self.selection.selectCtrl(self.multiSelection[0].selection,
                                              self.multiSelection[0].selCompn)
                                        self.clearMultiSelection()
                                    return

                        newSelection = SelectionTags.MultiSelectionGroup(self,
                              self.inspector, self)
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

                        return
        finally:
            self.vetoResize = false

    def OnFramePos(self, event):
        """ Called when frame is repositioned """
#        self.assureSingleSelection()
#        self.selection.selectCtrl(self, self.companion)
        if self.selection and self.selection.selection == self:
            self.inspector.constructorUpdate('Position')
            self.inspector.propertyUpdate('Position')
        event.Skip()

    def OnCloseWindow(self, event):
        """ When the Designer closes, the code generation process is started.
            General Inspector and Designer clean-up """

        if not self.saveOnClose and self.confirmCancel and wxMessageBox(
              'Cancel Designer session?', 'Cancel',
              wxYES_NO | wxICON_WARNING, parent=None) == wxNO:
            self.saveOnClose = true
            self.confirmCancel = false
            return

        if self.IsIconized():
            self.Iconize(false)

        # XXX Should handle errors more gracefully here
        self.destroying = true
        self.vetoResize = true
        try:
            if self.selection:
                self.selection.destroy()
                self.selection = None
            if self.multiSelection:
                for sel in self.multiSelection:
                    sel.destroy()
                self.multiSelection = None

            self.inspector.cleanup()
            self.inspector.containment.cleanup()

            # generate source
            self.refreshModel()
        except:
            self.destroying = false
            self.vetoResize = false
            raise

        self.menu.Destroy()
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
        ctrl = event.GetEventObject()
        screenPos = ctrl.ClientToScreen(wxPoint(event.GetX(), event.GetY()))
        parentPos = self.ScreenToClient(screenPos)
        self.popx = parentPos.x
        self.popy = parentPos.y

    def OnEditor(self, event):
        """ Bring Editor to the front """
        self.model.editor.restore()
        self.model.editor.modules[self.model.filename].focus()

    def OnInspector(self, event):
        """ Bring Inspector to the front """
        self.inspector.restore()
        if self.inspector.pages.GetSelection() > 3:
            self.inspector.pages.SetSelection(0)


    def OnControlDelete(self, event):
        """ Delete the currently selected controls """
        if self.deletingCtrl: return
        self.deletingCtrl = true
        try:
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
        finally:
            self.deletingCtrl = false

    def OnCtrlHelp(self, event):
        """ Show help for the selected control """
        if self.inspector.selCmp:
            Help.showCtrlHelp(self.inspector.selCmp.GetClass())

    def OnAlignSelected(self, event=None):
        """ Show alignment dialog for multi selections"""
        if self.multiSelection:
            dlg = CtrlAlign.ControlAlignmentFrame(self, self.multiSelection)
            try: dlg.ShowModal()
            finally: dlg.Destroy()

    def OnSizeSelected(self, event=None):
        """ Show size dialog for multi selections"""
        if self.multiSelection:
            dlg = CtrlSize.ControlSizeFrame(self, self.multiSelection)
            try: dlg.ShowModal()
            finally: dlg.Destroy()

    def OnSelectParent(self, event=None):
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

        Utils.writeTextToClipboard(os.linesep.join(output))

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

        Utils.writeTextToClipboard(os.linesep.join(output))

    def OnPasteSelected(self, event):
        """ Paste current clipboard contents into the current selection """
        if self.selection:
            # If the selection is not a container, select it's parent (a container)
            if not self.selection.selCompn.container:
                self.selectParent(self.selection.selection)

            pasted = self.pasteCtrls(self.selection.name,
                  str(Utils.readTextFromClipboard()).split(os.linesep))

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
                                  self.inspector, self)
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
            parentName, dummy = self.getParentNames(parent)

            self.cutCtrls([ctrlName], [], output)
            self.pasteCtrls(parentName, output)
            
            self.refreshContainment()
            self.inspector.containment.selectName(ctrlName)

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

#---Cursor selection------------------------------------------------------------
    def selectInDimentionDirection(self, selctrl, dim, dir):
        def compSides(selctrl, ctrl, dim, dir):
            selpos, selsize = selctrl.GetPosition(), selctrl.GetSize()
            pos, size = ctrl.GetPosition(), ctrl.GetSize()
            selMidPoint = wxPoint(selpos.x + selsize.x/2, selpos.y + selsize.y/2)
            ctrlMidPoint = wxPoint(pos.x + size.x/2, pos.y + size.y/2)
            if (dim, dir) == ('x', 1):
                return (wxPoint(selpos.x + selsize.x, selpos.y), selMidPoint,
                        wxPoint(selpos.x + selsize.x, selpos.y + selsize.y),
                        wxPoint(pos.x, pos.y), ctrlMidPoint,
                        wxPoint(pos.x, pos.y + size.y) )
            if (dim, dir) == ('x', -1):
                return (wxPoint(selpos.x, selpos.y), selMidPoint,
                        wxPoint(selpos.x, selpos.y + selsize.y),
                        wxPoint(pos.x + size.x, pos.y), ctrlMidPoint,
                        wxPoint(pos.x + size.x, pos.y + size.y) )
            if (dim, dir) == ('y', 1):
                return (wxPoint(selpos.x, selpos.y + selsize.y), selMidPoint,
                        wxPoint(selpos.x + selsize.x, selpos.y + selsize.y),
                        wxPoint(pos.x, pos.y), ctrlMidPoint,
                        wxPoint(pos.x + size.x, pos.y) )
            if (dim, dir) == ('y', -1):
                return (wxPoint(selpos.x, selpos.y), selMidPoint,
                        wxPoint(selpos.x + selsize.x, selpos.y),
                        wxPoint(pos.x, pos.y + size.y), ctrlMidPoint,
                        wxPoint(pos.x + size.x, pos.y + size.y) )

        dims = ['x', 'y']
        otherdim = dims[not dims.index(dim)]
        parentName, dummy = self.getParentNames(selctrl.GetParent())
        selName = selctrl.GetName()

        distLo = -1
        nearestCtrl = None
        for objName in self.objects.keys():
            ctrl, parent = self.objects[objName][1:3]
            if parent == parentName and objName != selName:

                pos1p, pos0p, pos2p, cpos1p, cpos0p, cpos2p = compSides(selctrl, ctrl, dim, dir)
                pos, otherpos1, otherpos2  = getattr(pos1p, dim), \
                      getattr(pos1p, otherdim), getattr(pos2p, otherdim)
                pos0, otherpos0 = getattr(pos0p, dim), getattr(pos0p, otherdim)
                cpos, cotherpos1, cotherpos2 = getattr(cpos1p, dim), \
                      getattr(cpos1p, otherdim), getattr(cpos2p, otherdim)
                cpos0, cotherpos0 = getattr(cpos0p, dim), getattr(cpos0p, otherdim)

                dpos, dotherpos1, dotherpos2 = cpos - pos, \
                      cotherpos1 - otherpos1, cotherpos2 - otherpos2
                dpos0, dotherpos0 = cpos0 - pos0, cotherpos0 - otherpos0

                if (abs(dpos) >= min(abs(dotherpos1), abs(dotherpos2)) and \
                    (not dpos or dpos/abs(dpos) == dir)) or \
                   (abs(dpos0) >= abs(dotherpos0) and \
                    (not dpos0 or dpos0/abs(dpos0) == dir)):
                    dist = min(math.sqrt(dpos*dpos+dotherpos1*dotherpos1),
                               math.sqrt(dpos0*dpos0+dotherpos0*dotherpos0),
                               math.sqrt(dpos*dpos+dotherpos2*dotherpos2))

                    if distLo == -1 or dist < distLo:
                        distLo = dist
                        nearestCtrl = ctrl

        if nearestCtrl:
            self.inspector.containment.selectName(nearestCtrl.GetName())

    def OnSelectLeft(self, event):
        sel = self.selection
        if sel and sel.selection != self:
            self.selectInDimentionDirection(sel.selection, 'x', -1)

    def OnSelectRight(self, event):
        sel = self.selection
        if sel and sel.selection != self:
            self.selectInDimentionDirection(sel.selection, 'x', 1)

    def OnSelectUp(self, event):
        sel = self.selection
        if sel and sel.selection != self:
            self.selectInDimentionDirection(sel.selection, 'y', -1)

    def OnSelectDown(self, event):
        sel = self.selection
        if sel and sel.selection != self:
            self.selectInDimentionDirection(sel.selection, 'y', 1)

#-------------------------------------------------------------------------------

    def OnSnapToGrid(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.x = SelectionTags.granularise(sel.position.x)
                sel.position.y = SelectionTags.granularise(sel.position.y)
                sel.startPos.x = sel.position.x
                sel.startPos.y = sel.position.y
                self.moveUpdate(sel)

    def relayoutCtrl(self, ctrl):
        self.forceResize = true # cleared by the event
        sizer = ctrl.GetSizer()
        if sizer:
            sizer.Layout()
        wxPostEvent(ctrl, wxSizeEvent(ctrl.GetSize(), ctrl.GetId()))
        wxCallAfter(ctrl.Refresh)

    def OnRelayoutSelection(self, event):
        # for ctrl in [sel.selection for sel in self.getSelAsList()]:
        for sel in self.getSelAsList():
            self.relayoutCtrl(sel.selection)

    def OnRelayoutDesigner(self, event):
        self.relayoutCtrl(self)

    def OnFitSizer(self, event):
        for sel in self.getSelAsList():
            sizer = sel.selection.GetSizer()
            if sizer:
                sizer.Fit(sel.selection)

    def OnCreationOrder(self, event):
        sel = self.selection
        if sel:
            selName = sel.selection.GetName()
            if selName == self.GetName():
                selName = ''
            self.showCreationOrderDlg(selName)

#---Inspector session-----------------------------------------------------------
    def doPost(self, inspector):
        self.saveOnClose = true
        self.Close()

    def doCancel(self, inspector):
        self.saveOnClose = false
        self.confirmCancel = true
        self.Close()


class DesignerNamespace:
    def __init__(self, designer):
        self._designer = designer
        
    def __getattr__(self, name):
        designer = self.__dict__['_designer']
        if designer.objects.has_key(name):
            return designer.objects[name][1]
        elif designer.dataView.objects.has_key(name):
            return designer.dataView.objects[name][1]
        elif designer.sizersView and \
              designer.sizersView.objects.has_key(name):
            return designer.sizerView.objects[name][1]
        else:
            raise AttributeError, name
        
        

class DesignerControlsEvtHandler(wxEvtHandler):
    def __init__(self, designer):
        wxEvtHandler.__init__(self)
        self.designer = designer

        self.drawGridMethods = {'lines' : self.drawGrid_intersectingLines,
                                'dots'  : self.drawGrid_dots,
                                'bitmap': self.drawGrid_bitmap,
                                'grid'  : self.drawGrid_grid}
        self._points = (0, 0), []

    def connectEvts(self, ctrl, connectChildren=false):
        ctrls = [ctrl]
        if connectChildren:
            ctrls.extend(ctrl.GetChildren())
        for ctrl in ctrls:
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
            ctrl = event.GetEventObject()

            if dsgn.selection:
                dsgn.selection.moving(ctrl, pos)
            elif dsgn.multiSelection:
                for sel in dsgn.multiSelection:
                    sel.moving(ctrl, pos, dsgn.mainMultiDrag)

        event.Skip()

    def getCtrlAndPosFromEvt(self, event):
        pos = event.GetPosition()
        ctrl = event.GetEventObject()
        # XXX only here for when testing
        if not ctrl:
            ctrl = self.designer
        else:
            if hasattr(ctrl, '_composite_child'):
                pos = ctrl.ClientToScreen(pos)
                ctrl = ctrl.GetParent()
                pos = ctrl.ScreenToClient(pos)
        return ctrl, pos

    def OnControlSelect(self, event):
        """ Control is clicked. Either select it or add control from palette """
        dsgn = self.designer
        ctrl, pos = self.getCtrlAndPosFromEvt(event)
##        ctrl = event.GetEventObject()
##        # XXX only here for when testing
##        if not ctrl:
##            ctrl = dsgn
##        else:
##            if hasattr(ctrl, '_composite_child'):
##                pos = ctrl.ClientToScreen(pos)
##                ctrl = ctrl.GetParent()
##                pos = ctrl.ScreenToClient(pos)
##
        if dsgn.selectControlByPos(ctrl, pos, event.ShiftDown()):
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
        """ Control is resized, emulate native wxWidgets layout behaviour """
        dsgn = self.designer
        try:
            if dsgn.vetoResize:
                return
            if event.GetId() == dsgn.GetId():
                if event.GetSize().Get() == dsgn.lastSize and not dsgn.forceResize:
                    return
                dsgn.lastSize = event.GetSize().Get()

                if dsgn.selection:
                    dsgn.selection.selectCtrl(dsgn, dsgn.companion)
                elif dsgn.multiSelection:
                    dsgn.clearMultiSelection()
                    dsgn.assureSingleSelection()
                    dsgn.selection.selectCtrl(dsgn, dsgn.companion)
                    return

                # Compensate for autolayout=false and 1 ctrl on frame behaviour
                # Needed because incl selection tags there are actually 5 ctrls

                if not dsgn.GetAutoLayout() and not dsgn.companion.dialogLayout:
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
                s, p = dsgn.selection.size, dsgn.selection.position
                dsgn.selection.sizeFromCtrl()
                dsgn.selection.setSelection()

                if (s, p) != (dsgn.selection.size, dsgn.selection.position):
                    dsgn.selection.sizeUpdate()
                    dsgn.selection.positionUpdate()

        finally:
            dsgn.forceResize = false
            dsgn.Refresh()
            event.Skip()

    def OnControlDClick(self, event):
        dsgn = self.designer

        if dsgn.selection:
            #ctrl = event.GetEventObject()
            ctrl, pos = self.getCtrlAndPosFromEvt(event)

            dsgn.selectControlByPos(ctrl, pos, event.ShiftDown())
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
        ctrl = event.GetEventObject()
        # Prevent infinite event loop by not sending siz events to statusbar
        # Only applies to sizered statusbars
        if ctrl and not isinstance(ctrl, wxStatusBar):
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
        lines = []
        for y in range(sze.y / sg + 1):
            lines.append( (0, y * sg, sze.x, y * sg) )

        for x in range(sze.x / sg + 1):
            lines.append( (x * sg, 0, x * sg, sze.y) )

        dc.DrawLineList(lines)

    def drawGrid_intersectingLines(self, dc, sze, sg):
        """ Cute hack to draw dots by intersecting lines
        """
        bgCol = dc.GetBackground().GetColour()
        xorBgCol = wxColour(255^bgCol.Red(), 255^bgCol.Green(), 255^bgCol.Blue())

        self._drawLines(dc, xorBgCol, wxCOPY, sze, sg)
        self._drawLines(dc, wxWHITE, wxXOR, sze, sg)

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
        pen1 = wxPen(wxBLACK)
        dc.SetPen(pen1)
        (szex, szey), points = self._points
        if (szex, szey) != (sze.x, sze.y):
            points = []
            for y in range(sze.y / sg + 1):
                for x in range(sze.x / sg + 1):
                    points.append( (x * sg, y * sg) )
            self._points = (szex, szey), points
        dc.DrawPointList(points)

    def drawGrid_bitmap(self, dc, sze, sg):
        """ This should be the most efficient method, when the granularity is
            changed, a new (possibly +-32x32) bitmap should be created with
            transparent background and black grid points. This can then be
            blitted over background
        """
        pass

    def updateDCProps(self, dc, sizer, validCol):
        if sizer.__class__.__name__ == 'BlankSizer':
            pen = wxPen(wxRED)
            brush = wxBrush(wxRED, wxFDIAGONAL_HATCH)
        else:
            pen = wxPen(validCol, 3, wxSOLID)
            brush = wxTRANSPARENT_BRUSH
        dc.SetPen(pen)
        dc.SetBrush(brush)
        
    def drawSizerInfo(self, dc, sizer):
        self.updateDCProps(dc, sizer, Preferences.dsHasSizerCol)

        sp = sizer.GetPosition()
        ss = sizer.GetSize()
        dc.DrawRectangle(sp.x, sp.y, ss.width, ss.height)
        
        c = sizer.GetChildren()
        for sc in c:
            if sc.IsSizer():
                self.drawSizerInfo(dc, sc.GetSizer())
            else:
                self.updateDCProps(dc, sizer, Preferences.dsInSizerCol)
                sp = sc.GetPosition()
                ss = sc.GetSize()
                dc.DrawRectangle(sp.x, sp.y, ss.width, ss.height)


    def OnPaint(self, event):
        # XXX Paint event fired after destruction, should remove EVT ?
        ctrl = event.GetEventObject()
        if ctrl:
            dc = wxPaintDC(ctrl)
#            sze = ctrl.GetClientSize()
            sze = ctrl.GetSize()
            sg = Preferences.dsGridSize

            drawGrid = self.drawGridMethods[Preferences.drawGridMethod]

            dc.BeginDrawing()
            try:
                drawGrid(dc, sze, sg)

                sizer = ctrl.GetSizer()
                if sizer:
                    self.drawSizerInfo(dc, sizer)

            finally:
                dc.EndDrawing()


        event.Skip()
