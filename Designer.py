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
from wxPython.wx import *
import string, copy
import sender
import Companions, EditorViews, PaletteMapping, RTTI, Preferences, Utils
from SelectionTags import SelectionGroup, granularise
from EditorModels import init_ctrls, init_utils
from os import path

tPopupIDUp = 200
tPopupIDCut = 201
tPopupIDCopy = 202
tPopupIDPaste = 203
tPopupIDDelete = 204

bodyIndent = '        '

#Utility Objects
#
#                    Events    GetSetProps    OtherProps
# wxApp                 *
# wxMenu                * 
#
# wxImageList
# wxAcceleratorTable


# XXX Maybe the frame code creation should be handled by another internal view ?

class InspectableObjectCollectionView(EditorViews.EditorView):
    viewName = 'InspectableObjectCollection'
    collectionMethod = 'init_'
    handledProps = []
    supportsParentView = false

    def setupArgs(self, ctrlName, params, dontEval):
        """ Create a dictionary of parameters for the constructor of the
            control from a dictionary of string/source parameters.
            Catches design time parameter overrides.
        """
        args = {}
        # Build dictionary of params
        for paramKey in params.keys():
            if paramKey in dontEval:
                args[paramKey] = params[paramKey]
            else:
                args[paramKey] = eval(params[paramKey])
                    
        return args

    def __init__(self, inspector, model, compPal, companionClass, actions = [], dclickActionIdx = -1):
        self.compPal = compPal
        EditorViews.EditorView.__init__(self, actions, dclickActionIdx)
        self.selection = None
        self.model = model
        self.senderMapper = sender.SenderMapper()
        self.inspector = inspector
        self.controllerView = None
        self.objects = {}
        self.objectOrder = []

    def buildParentRelationship(self):
        """ Build a nested dictionary of key = name, value = dict pairs
            describing parental relationship.
            Assuming parents are created before children"""
        parRel = {}
        parRef = {}
        for ctrl in self.objectOrder:
            ce = self.objects[ctrl]
            if ce[2] is None:
                parRel[ctrl] = {}
                parRef[ctrl] = parRel[ctrl]
            else:
                parRef[ce[2]][ctrl] = {}
                parRef[ctrl] = parRef[ce[2]][ctrl]

        return  parRel, parRef

    def organiseCollection(self):
        ctrls = self.model.objectCollections[self.collectionMethod]

        props = {}
        for prop in ctrls.properties:
            if not props.has_key(prop.comp_name):
                props[prop.comp_name] = []
            props[prop.comp_name].append(prop)

        events = {}
        for evt in ctrls.events:
            if not events.has_key(evt.comp_name):
                events[evt.comp_name] = []
            events[evt.comp_name].append(evt)

        return ctrls, props, events



    def initObjectsAndCompanions(self, creators, props, events) :
        for ctrl in creators:
            # Assumes all design time ctrls are imported in global scope
            ctrlClass = eval(ctrl.class_name)
            ctrlCompnClass = PaletteMapping.compInfo[ctrlClass][1]
            ctrlName = self.loadControl(ctrlClass, ctrlCompnClass, 
              ctrl.comp_name, ctrl.params)            
            ctrlCompn = self.objects[ctrlName][0]
            ctrlCompn.setConstr(ctrl)
 
            self.initObjProps(props, ctrl.comp_name, ctrl)
            self.initObjEvts(events, ctrl.comp_name, ctrl)

    def initObjProps(self, props, name, creator):
        """ Initialise property list by evaluating 1st parameter and calling
            prop's setter with it. 
        """
        if props.has_key(name):
            comp = self.objects[name][0]
            ctrl = self.objects[name][1]
            # initialise live component's properies
            for prop in props[name]:
                value = eval(prop.params[0])
                RTTI.getFunction(ctrl, prop.prop_setter)(ctrl, value)

            # store default prop vals
            comp.setProps(props[name])
        
    def initObjEvts(self, events, name, creator):
        if events.has_key(name):
            self.objects[name][0].setEvents(events[name])
                
    def saveCtrls(self):
        """ Replace current source of method _init_create with values from
            constructors, properties and events. """
        newBody = []

        for ctrlName in self.objectOrder:
            try:
                # Add constructor
                if self.objects[ctrlName][0].textConstr:
                    newBody.append(bodyIndent + self.objects[ctrlName][0].textConstr.asText())
            except: print 'no constr:', ctrlName

            # Add properties
            for prop in self.objects[ctrlName][0].textPropList:
                newBody.append(bodyIndent + prop.asText())

            # Add events connections and methods
            for evt in self.objects[ctrlName][0].textEventList:
                if evt.trigger_meth != '(delete)':
                    newBody.append(bodyIndent + evt.asText())
                    if not self.model.module.classes[self.model.main].methods.has_key(evt.trigger_meth):
                        self.model.module.addMethod(self.model.main, evt.trigger_meth, 'self, event', ['        pass'])
                
            newBody.append('')
        # Add doc string
        docs = self.model.module.getClassMethDoc(self.model.main, self.collectionMethod)
        if (len(docs) > 0) and docs[0]:
            newBody.insert(0, '%s""" %s """'%(bodyIndent, docs))

        self.model.module.replaceMethodBody(self.model.main, self.collectionMethod, newBody)
        self.model.refreshFromModule()
            
    def newObjName(self , className):
        """ Return a name for a control unique in the scope of the model."""
        # XXX Now that there is multiple maintained methods is may fail because
        # XXX it's only unique in the method.
        num = 1
        newName = '%s%s'%(string.lower(className[2:3]), className[3:])
        while self.objects.has_key(newName + `num`):
            num = num + 1
        return newName + `num`

    def newObject(self, objClass, objCompanionClass):
        """ At design time, when adding a new ctrl from the palette, create and
            register given control and companion.
            See also: loadControl """

        objName = self.newObjName(objClass.__name__)
        companion = objCompanionClass(objName, self, objClass)

        params = companion.designTimeSource()

        self.objects[objName] = [companion, companion.designTimeObject()]
        self.objectOrder.append(objName)
        
        companion.persistConstr(objClass.__name__, params)
                
        return objName

    def selectObject(self):
        pass

    def selectNone(self):
        pass

    def cleanup(self):
        if self == self.inspector.prevDesigner:
            self.inspector.prevDesigner = None

    def close(self):
        self.controllerView.close()
    
    def refreshContainment(self, selectName = None):        
        parRelations, parReference = self.buildParentRelationship()
        self.inspector.containment.refreshCtrl(self.model.main, parRelations, self)
        if selectName is not None:
             self.inspector.containment.selectName(selectName)
        return parRelations, parReference
    
class DesignerView(wxFrame, InspectableObjectCollectionView):
    """ Factory to create new controls """
    viewName = 'Designer'
    docked = false
    collectionMethod = init_ctrls
    handledProps = ['parent', 'id']
    supportsParentView = true
    
    def setupArgs(self, ctrlName, params, dontEval, parent = None):
        """ Create a dictionary of parameters for the constructor of the
            control from a dictionary of string/source parameters."""

        args = InspectableObjectCollectionView.setupArgs(self, ctrlName, params, dontEval)

        # Determine parent
        if parent:
            args['parent'] = parent
        else:
            srcPrnt = args['parent']
            if srcPrnt == 'None':
                args['parent'] = None
            elif srcPrnt == 'self':
                args['parent'] = self
            else:
                dot = string.find(srcPrnt, '.')
                if dot != -1:
                    srcPrnt = srcPrnt[dot + 1:]
                else: raise 'Component name illegal '+ srcPrnt
                args['parent'] = self.objects[srcPrnt][1]
            
        
        args['id'] = NewId()
        args['name'] = ctrlName
        
        return args
        
    def __init__(self, parent, inspector, model, compPal, companionClass, dataView):
        args = self.setupArgs(model.main, model.mainConstr.params, 
          ['parent', 'id'], parent)
        wxFrame.__init__(self, parent, -1, args['title'], args['pos'], args['size'])#, args['style'], args['name'])
        InspectableObjectCollectionView.__init__(self, inspector, model, compPal, companionClass)

        if wxPlatform == '__WXMSW__':
            self.icon = wxIcon(path.join(Preferences.toPyPath(\
              'Images/Icons/Designer.ico')), wxBITMAP_TYPE_ICO)
            self.SetIcon(self.icon)

        EVT_MOVE(self, self.OnFramePos)

        self.dataView = dataView
        self.dataView.controllerView = self
        self.saveOnClose = true
        
        self.companion = companionClass(self.model.main, self, self)
        self.companion.id = Utils.windowIdentifier(self.model.main, '')
        
        self.companion.control = self
        
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
        
        self.menu.Append(tPopupIDUp, "Up")
        self.menu.Append(-1, "-")
        self.menu.Append(tPopupIDCut, "Cut")
        self.menu.Append(tPopupIDCopy, "Copy")
        self.menu.Append(tPopupIDPaste, "Paste")
        self.menu.Append(tPopupIDDelete, "Delete")
        
        self.selection = None
                    
    def saveCtrls(self):
        InspectableObjectCollectionView.saveCtrls(self) 
        self.model.writeWindowIds(self.collectionMethod, self.objects, self.objectOrder)

    def refreshCtrl(self):
        if self.destroying: return

        # XXX delete previous
        
        comps = {}
        
        # Reorder props and events into components
        
        if not self.selection:
            self.selection = SelectionGroup(self, self.senderMapper, 
              self.inspector, self)

        self.model.editor.statusBar.hint.SetLabel('Creating frame')
        
        ctrls, props, events = self.organiseCollection()

        self.model.editor.statusBar.progress.SetValue(20)
                
        stepsDone = 20.0
        step = (90 - stepsDone) / len(ctrls.creators)

        # Initialise the design time controls and
        # companion with default values
        # initObjectsAndCompanions(creators, props, events) 

        self.companion.setConstr(self.model.mainConstr)
        ctrlCompn = self.companion
        self.initObjProps(props, '', ctrls.creators[0])
        self.initObjEvts(events, '', ctrls.creators[0])
         
        if len(ctrls.creators) > 1:
            self.initObjectsAndCompanions(ctrls.creators[1:], props, events)

            stepsDone = stepsDone + step
            self.model.editor.statusBar.progress.SetValue(int(stepsDone))
            
        self.model.editor.statusBar.progress.SetValue(80)
        self.refreshContainment()
        self.model.editor.statusBar.progress.SetValue(0)
        self.model.editor.statusBar.hint.SetLabel(' ')
                
    def initSelection(self):
        self.selection = SelectionGroup(self, self.senderMapper, self.inspector, self)

    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl """
        dontEval = ['parent', 'id']
        
        args = self.setupArgs(ctrlName, params, dontEval)
        
        if params['parent'] == 'self':
            parent = ''
        else:
            parent = string.split(params['parent'], '.')[1]
                
        # Create control and companion
        companion = ctrlCompanion(ctrlName, self, None, ctrlClass)
        self.objects[ctrlName] = [companion, 
         companion.designTimeControl(None, None, args), parent]
        self.objectOrder.append(ctrlName)
        
        return ctrlName

    def newControl(self, parent, ctrlClass, ctrlCompanion, position = None, size = None):
        """ At design time, when adding a new ctrl from the palette, create and
            register given control and companion.
            See also: loadControl """

        ctrlName = self.newObjName(ctrlClass.__name__)
        companion = ctrlCompanion(ctrlName, self, parent, ctrlClass)

        params = companion.designTimeSource('wxPoint(%d, %d)' % (position.x, position.y))
        if parent != self:
            parentName = parent.GetName()
            params['parent'] = 'self.'+parentName
        else:
            parentName = ''
            params['parent'] = 'self'

        self.objects[ctrlName] = [companion, companion.designTimeControl(position, size), parentName]
        self.objectOrder.append(ctrlName)
        
        params['id'] = companion.id
        companion.persistConstr(ctrlClass.__name__, params)
                
        self.refreshContainment()

        return ctrlName
	    
    def removeEvent(self, name):
        # XXX Remove event!
        self.inspector.eventUpdate(name, true)
           
    def CtrlAnchored(self, ctrl):
	result = (ctrl == self)

    def selectParent(self, ctrl):
        """ Change the selection to the parent of the currently selected control. """
        if self.selection:
            if ctrl != self:
                parent = ctrl.GetParent()
                parentName = parent.GetName()
                if parentName == self.GetName():
                    parentName = ''
                self.inspector.containment.selectName(parentName)
    
    def renameFrame(self, oldName, newName):
        self.SetName(newName)

        # update windowids & ctrls
        for comp, ctrl, dummy in self.objects.values():
            comp.updateWindowIds()
        
        # update ctrls

        # propagate rename to model
        self.model.renameMain(oldName, newName)

        # propagate rename to inspector
        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = ''

        self.refreshContainment(selName)

    def renameCtrl(self, oldName, newName):
        """ Rename a control and update all its properties and events."""
        ctrl = self.objects[oldName]
        del self.objects[oldName]
        self.objects[newName] = ctrl
        
        idx = self.objectOrder.index(oldName)
        del self.objectOrder[idx]
        self.objectOrder.insert(idx, newName)

        companion = self.objects[newName][0]
        companion.textConstr.comp_name = newName
        for prop in companion.textPropList:
            prop.comp_name = newName
        for evt in companion.textEventList:
            evt.comp_name = newName

        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = newName

        self.refreshContainment(selName)

    def deleteCtrl(self, name, parentRef = None):
        ctrlInfo = self.objects[name]
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
            
        children = parRef[name]
        for child in children.keys():
            self.deleteCtrl(child, parRef)
        
        del self.objectOrder[self.objectOrder.index(name)]
        ctrlInfo[1].Destroy()
        del self.objects[name]
        
        if parRel is not None:
            self.refreshContainment(parentName)

    def selectNone(self):
        if self.selection: self.selection.selectNone()
                
    def close(self):
        self.Close()

    def OnMouseOver(self, event):
    	if event.Dragging():
     	    pos = event.GetPosition()
     	    ctrl = self.senderMapper.getObject(event)
	    self.selection.moving(ctrl, pos)
	event.Skip()
	    	      	          
    def OnControlSelect(self, event):
        """ Control is clicked. Either select it or add control from palette """
        # XXX Frame name '' or name ?
        ctrl = self.senderMapper.getObject(event)
        if ctrl == self:
            companion = self.companion
        else:
            companion = self.objects[ctrl.GetName()][0]
        # Component on palette selected, create it
        if self.compPal.selection:
            if companion.container: parent = ctrl
            else: parent = ctrl.GetParent()
            # Granularise position
            pos = event.GetPosition()
            pos = wxPoint(granularise(pos.x), granularise(pos.y))
                        
            ctrlName = self.newControl(parent, self.compPal.selection[1], self.compPal.selection[2], pos)
            self.compPal.selectNone()

            if self.selection:
                ctrl = self.objects[ctrlName][1]
                self.selection.selectCtrl(ctrl, self.objects[ctrlName][0])
                self.inspector.selectObject(ctrl, self.objects[ctrlName][0])
        # Select ctrl
        else:
            if self.selection:
                ctrlName = companion.name
                self.selection.selectCtrl(ctrl, companion)
                self.inspector.selectObject(ctrl, companion)
                self.selection.moveCapture(ctrl, companion, event.GetPosition())
    
    def OnControlRelease(self, event):
        if self.selection:
            self.selection.moveRelease()
        event.Skip()
        
    def OnControlResize(self, event):
        try:
	    if self.selection:
     	        self.selection.sizeFromCtrl()
    	        self.selection.setSelection()
    	finally:
    	    event.Skip()
    	    self.Layout()

    def OnControlDClick(self, event):
	pass

    def OnFramePos(self, event):
        self.inspector.constructorUpdate('Position')
        event.Skip()
        
    def OnCloseWindow(self, event):
        self.destroying = true
        if self.saveOnClose:
            self.saveCtrls()
            self.model.modified = true
            self.model.editor.updateModulePage(self.model)

        self.dataView.saveCtrls()
        self.dataView.deleteFromNotebook()
        del self.model.views['Data']
        self.cleanup() 
        self.inspector.cleanup()
        self.inspector.containment.cleanup()
        self.Show(false)
        self.Destroy()
        del self.model.views['Designer']
        event.Skip()
    
    def OnRightDown(self, event):
        ctrl = self.senderMapper.getObject(event)
        screenPos = ctrl.ClientToScreen(wxPoint(event.GetX(), event.GetY()))
        parentPos = self.ScreenToClient(screenPos)
        self.popx = parentPos.x
        self.popy = parentPos.y
        
