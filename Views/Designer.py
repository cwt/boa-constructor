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
import string, copy, os
from os import path
import sender
import EditorViews, PaletteMapping, Preferences, Utils, Help
from Preferences import IS
import SelectionTags
from EditorModels import init_ctrls, init_utils, ObjectCollection, isInitCollMeth, getCollName
import CtrlAlign, CtrlSize
import RTTI, PrefsKeys, pprint
import methodparse

bodyIndent = ' '*8

[wxID_CTRLPARENT, wxID_EDITCUT, wxID_EDITCOPY, wxID_EDITPASTE, wxID_EDITDELETE,
 wxID_SHOWINSP, wxID_SHOWEDTR, wxID_CTRLHELP, wxID_EDITALIGN, wxID_EDITSIZE,
 wxID_EDITRECREATE, wxID_EDITSNAPGRID,
] = map(lambda _init_ctrls: wxNewId(), range(12))

[wxID_EDITMOVELEFT, wxID_EDITMOVERIGHT, wxID_EDITMOVEUP, wxID_EDITMOVEDOWN,
 wxID_EDITWIDTHINC, wxID_EDITWIDTHDEC, wxID_EDITHEIGHTINC, wxID_EDITHEIGHTDEC,
] = map(lambda _keys_move_size: wxNewId(), range(8))

class DesignerControlsEvtHandler(wxEvtHandler):
    def __init__(self, designer):
        wxEvtHandler.__init__(self)
        self.designer = designer

    def connectEvts(self, ctrl):
        EVT_MOTION(ctrl, self.OnMouseOver)
        EVT_LEFT_DOWN(ctrl, self.OnControlSelect)
        EVT_LEFT_UP(ctrl, self.OnControlRelease)
        EVT_LEFT_DCLICK(ctrl, self.OnControlDClick)
        EVT_SIZE(ctrl, self.OnControlResize)

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
        """ Control is clicked. Either select it or add control from palette """
        dsgn = self.designer
        ctrl = dsgn.senderMapper.getObject(event)

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
            if event.GetId() == dsgn.GetId():
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
            #self.Layout()

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
                  dsgn.checkChildCtrlClick(ctrlName, ctrl, companion, event.GetPosition())
    
            selCompn.defaultAction()

class InspectableObjectCollectionView(EditorViews.EditorView):
    viewName = 'InspectableObjectCollection'
    collectionMethod = 'init_'
    collectionParams = 'self'
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
            value = params[paramKey]
            if len(value) >= 11 and value[:11] == 'self._init_':
                collItem = methodparse.CollectionInitParse(value)
                self.addCollView(paramKey, collItem.method, false)
            if paramKey in dontEval:
                args[paramKey] = params[paramKey]
            else:
                args[paramKey] = PaletteMapping.evalCtrl(params[paramKey])
                    
        return args

    def __init__(self, inspector, model, compPal, actions = (), dclickActionIdx = -1, editorIsWindow = true):
        self.compPal = compPal
        EditorViews.EditorView.__init__(self, model, actions, dclickActionIdx, editorIsWindow)
        self.selection = None
        self.senderMapper = sender.SenderMapper()
        self.inspector = inspector
        self.controllerView = None
        self.objects = {}
        self.objectOrder = []
        self.collEditors = {}
    
    def destroy(self):
#        print 'DESTROY InspectableObjectCollectionView', self.__class__.__name__
        del self.controllerView
        del self.inspector
        for objval in self.objects.values():
            objval[0].destroy()
        for coll in self.collEditors.values():
            coll.destroy()
        del self.collEditors
        del self.objects
        del self.senderMapper
        EditorViews.EditorView.destroy(self)

# XXX Consider building subsets of the tree where possible
# XXX may become an issue on frames with many controls
##  decl buildParentRelationship(self) -> (dict, dict)
    def buildParentRelationship(self):
        """ Build a nested dictionary of key = name, value = dict pairs
            describing parental relationship.
            Assuming parents are created before children
            
            parRel : Nested relationship dictionary
            parRef : Flat reference dictionary
        """
     
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
            
    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):#, definedCtrls):
        collDeps = {}
        for constr in creators:
            self.initObjCreator(constr)
            self.initObjProps(objColl.propertiesByName, constr.comp_name, constr, dependents, depLinks)
            self.initObjColls(objColl.collectionsByName, constr.comp_name, constr, collDeps)
            self.initObjEvts(objColl.eventsByName, constr.comp_name, constr)
            
            self.applyDepsForCtrl(constr.comp_name, depLinks)
            
            #definedControls.append(constr.comp_name

        for ctrlName in collDeps.keys():
            for collInit in collDeps[ctrlName]:
                self.addCollView(ctrlName, collInit.method, false)

    def initObjCreator(self, constrPrs):
        # Assumes all design time ctrls are imported in global scope
        ctrlClass = PaletteMapping.evalCtrl(constrPrs.class_name)
        ctrlCompnClass = PaletteMapping.compInfo[ctrlClass][1]
        ctrlName = self.loadControl(ctrlClass, ctrlCompnClass, 
          constrPrs.comp_name, constrPrs.params)            
        ctrlCompn = self.objects[ctrlName][0]
        ctrlCompn.setConstr(constrPrs)
            
    def initObjProps(self, props, name, creator, dependents, depLinks):
        """ Initialise property list by evaluating 1st parameter and calling    
            prop's setter with it.                                              
            Also associate companion name with prop parse objs               """    
        
        if props.has_key(name):
            comp, ctrl = self.objects[name][0:2]
            # initialise live component's properies
            for prop in props[name]:
                prop.prop_name = comp.getPropNameFromSetter(prop.prop_setter)
                # Dependent properties
                if prop.prop_name in comp.dependentProps():
                    self.addDepLink(prop, name, dependents, depLinks)
                # Collection initialisers
                elif prop.params[0][:11] == 'self._init_':
                    collItem = methodparse.CollectionInitParse(prop.params[0])
                    self.addCollView(name, collItem.method, false)
                # Check for custom evaluator
                elif comp.customPropEvaluators.has_key(prop.prop_name):
                    args = comp.customPropEvaluators[prop.prop_name](prop.params, self.getAllObjects())
                    apply(RTTI.getFunction(ctrl, prop.prop_setter), (ctrl, )+ args)
                # Normal property, eval value and apply it
                else:                     
                    try:
                        value = PaletteMapping.evalCtrl(prop.params[0])
                    except AttributeError, name:
                        if self.objects.has_key(name):
                            value = self.objects[name][1]
                        else:
                            raise
                    RTTI.getFunction(ctrl, prop.prop_setter)(ctrl, value)

            # store default prop vals
            comp.setProps(props[name])

    def initObjColls(self, collInits, name, creator, dependents = None):
        """ Initialise collection properties by creating a collection view     
            for it and applying it.                                            
            Also associate companion name with prop parse objs               """    

        if collInits.has_key(name):
            if dependents is None: dependents = {}
            comp = self.objects[name][0]
            for collInit in collInits[name]:
                if collInit.getPropName() in comp.dependentProps():
                    if not dependents.has_key(name):
                        dependents[name] = []
                    dependents[name].append(collInit)
                else:
                    self.addCollView(name, collInit.method, false)

            # store default collection initialisers
            comp.setCollInits(collInits[name])

    def initObjEvts(self, events, name, creator):
        if events.has_key(name):
            self.objects[name][0].setEvents(events[name])

    def addCollView(self, name, collInitMethod, create):
##        print 'addCollView' , name, collInitMethod, create
        import CollectionEdit
        
        comp, ctrl = self.objects[name][:2]
        collName = getCollName(collInitMethod, name)
        collCompClass = comp.subCompanions[collName]
        # decl collComp -> CollectionDTC
        collComp = collCompClass(name, self, comp, ctrl)
        if create:
            collComp.persistCollInit(collInitMethod, name, collName)
        else:
            pass
        
        collInit = self.model.objectCollections[collInitMethod]
        collComp.setConstrs(collInit.creators, collInit.initialisers,
          collInit.finalisers)

        # init DTCtrl
        for crt in collComp.textConstrLst:
            collComp.applyDesignTimeDefaults(crt.params)
        collComp.initCollection()
        
        comp.collections[collName] = collComp
        
        collEditView = CollectionEdit.CollectionEditorView(self, self.inspector, 
            self.model, collComp)
        collEditView.initialise()
                
        self.collEditors[(comp.name, collName)] = collEditView

    def getRefsFromProp(self, prop):
        refs = []
        # Build lst of ctrl references from property
        for param in prop.params:
            if len(param) >= 4 and param[:4] == 'self':
                refs.append(Utils.ctrlNameFromSrcRef(param))
        return refs
        
    def checkAndAddDepLink(self, ctrlName, prop, dependentProps, deps, depLinks, definedCtrls):
        if prop.prop_name in dependentProps:
            refs = self.getRefsFromProp(prop)
            # Postpone if target ctrls not yet defined
            allCtrlsDefined = len(refs) > 0
            for ref in refs:
                if ref not in definedCtrls:
                    allCtrlsDefined = false
            
            if not allCtrlsDefined:
                self.addDepLink(prop, ctrlName, deps, depLinks)
                return true

        return false

    def applyDepsForCtrl(self, ctrlName, depLinks):
        if depLinks.has_key(ctrlName):
            for prop, otherRefs in depLinks[ctrlName]:
                for oRf in otherRefs:
                    if not oRf in self.objectOrder:
                        break
                else:
                    # Dependent properties are usually one parameter name
                    # references
                    ctrl = self.objects[prop.comp_name][1] 
                    if len(prop.params) == 1:
                        if ctrlName == '': 
                            value = self
                        else:
                            ord, objs = self.model.allObjects()
                            
                            if objs.has_key(ctrlName):
                                value = objs[ctrlName][1]
                            else:
                                continue
                        RTTI.getFunction(ctrl, prop.prop_setter)(ctrl, value)
                    else:
                        refs = []
                        # Build lst of ctrl references from property
                        for param in prop.params:
                            if len(param) >= 4 and param[:4] == 'self':
                                refs.append(self.objects[Utils.ctrlNameFromSrcRef(param)][1])
                            else:
                                refs.append(eval(param))
                        
                        apply(RTTI.getFunction(ctrl, prop.prop_setter), [ctrl,]+refs)
            
            del depLinks[ctrlName]
                                            
    def addDepLink(self, prop, name, dependents, depLinks):
        # XXX dependents does not seem to be used anymore ????
##        if not dependents.has_key(name):
##            dependents[name] = []
##        dependents[name].append(prop)

        refs = self.getRefsFromProp(prop)
        for link in refs:
            if not depLinks.has_key(link):
                depLinks[link] = []
            otherRefs = refs[:]
            otherRefs.remove(link)
            depLinks[link].append( (prop, otherRefs) )
            
##        link = Utils.ctrlNameFromSrcRef(prop.params[0])
##        if not depLinks.has_key(link):
##            depLinks[link] = []
##        depLinks[link].append(prop)
    
    def finaliseDepLinks(self, depLinks):
        for ctrlName in depLinks.keys()[:]:
            self.applyDepsForCtrl(ctrlName, depLinks)

    def renameCtrl(self, oldName, newName):
        """ Rename a control and update all its properties and events."""

##        prl, prf = self.buildParentRelationship()
##        children = prf[oldName].keys()

        ctrl = self.objects[oldName]
        del self.objects[oldName]
        self.objects[newName] = ctrl
        
        idx = self.objectOrder.index(oldName)
        del self.objectOrder[idx]
        self.objectOrder.insert(idx, newName)
        # self.objectOrder[self.objectOrder.index(oldName)] = newName

        companion = self.objects[newName][0]
        companion.renameCtrl(oldName, newName)
        companion.renameCtrlRefs(oldName, newName)
        
        for name, prop in self.collEditors.keys():
            if name == oldName:
                collEditor = self.collEditors[(name, prop)]
                collEditor.renameCtrl(oldName, newName)
                del self.collEditors[(name, prop)]
                self.collEditors[(newName, prop)] = collEditor
##
##        # rename ctrl references like parent
##        for ctrl in children:
##            self.objects[ctrl][0].renameCtrlRefs(oldName, newName)
##            self.objects[ctrl][2] = newName

    def saveCtrls(self, definedCtrls):
        """ Replace current source of method in collectionMethod with values from
            constructors, properties and events. 
        """

        newBody = []
        deps = {}
        depLinks = {}
        collDeps = []
        imports = []

        for collView in self.collEditors.values():
            collView.saveCtrls()
        
        # XXX Move toolbar up to the 1st position after the frame

        for ctrlName in self.objectOrder:
            definedCtrls.append(ctrlName)
            compn = self.objects[ctrlName][0]
            
            compn.writeConstructor(newBody, self.collectionMethod)
            compn.writeProperties(newBody, ctrlName, definedCtrls, deps, depLinks) 
            compn.writeCollections(newBody, collDeps)
            compn.writeEvents(newBody, addModuleMethod = true)

            compn.writeDependencies(newBody, ctrlName, depLinks, definedCtrls)
            
            imp = compn.writeImports()
            if imp and imp not in imports:
                imports.append(imp)
                
            newBody.append('')

        if collDeps:
            newBody.extend(collDeps + [''])
        
        module = self.model.getModule()

        for imp in imports:
            module.addImportStatement(imp)
            
        if module.classes[self.model.main].methods.has_key(\
          self.collectionMethod):
            # Add doc string
            docs = module.getClassMethDoc(self.model.main, 
              self.collectionMethod)
            if (len(docs) > 0) and docs[0]:
                newBody.insert(0, '%s""" %s """'%(bodyIndent, docs))
        
            if len(newBody):
                module.replaceMethodBody(self.model.main, 
                  self.collectionMethod, newBody)
            else:
                module.replaceMethodBody(self.model.main, 
                  self.collectionMethod, [bodyIndent+'pass', ''])
        else:
            if len(newBody):
                module.addMethod(self.model.main, 
                  self.collectionMethod, self.collectionParams, newBody, 0)

        self.model.refreshFromModule()

    def copyCtrls(self, selCtrls, definedCtrls, output):
        """ Replace current source of method in collectionMethod with values from
            constructors, properties and events. 
        """
        
        ctrlsAndContainedCtrls = self.expandNamesToContainers(selCtrls)
        deps = {}
        depLinks = {}
        collDeps = []

#        for collView in self.collEditors.values():
#            collView.saveCtrls()
        collMeths = []
        for compName, collProp in self.collEditors.keys():
            if compName in ctrlsAndContainedCtrls:
                collView = self.collEditors[(compName, collProp)]
                collMeth = []
                collView.copyCtrls(collMeth)
                collMeths.append(collMeth)
#                ctrlsAndContainedCtrls.remove(compName)

        output.insert(0, '    def %s(%s):'% (self.collectionMethod, self.collectionParams))
        for ctrlName in ctrlsAndContainedCtrls:
            definedCtrls.append(ctrlName)
            compn = self.objects[ctrlName][0]
            
            compn.updatePosAndSize()

            compn.writeConstructor(output, self.collectionMethod)
            compn.writeProperties(output, ctrlName, definedCtrls, deps, depLinks) 
            compn.writeCollections(output, collDeps)
            compn.writeEvents(output, addModuleMethod = false)

            compn.writeDependencies(output, ctrlName, depLinks, definedCtrls)
                
            output.append('')

        if collDeps:
            output.extend(collDeps + [''])
        
        collMeths.reverse()
        for methBody in collMeths:
            output[0:0] = methBody + ['']

    def cutCtrls(self, selCtrls, definedCtrls, output):
        # Copy to output
        self.copyCtrls(selCtrls, definedCtrls, output)
        self.selectNone()
        
        # Delete ctrls
        for ctrl in selCtrls:
            self.deleteCtrl(ctrl)
        
    def pasteCtrls(self, destCtrlName, input):
        # Split up into methods
        methList = []
        for line in input:
            if line[:8] == '    def ':
                meth = line[8:string.find(line, '(', 9)]
                currMeth = [meth]
                methList.append(currMeth)
            else:
                try:
                    currMeth.append(line)
                except NameError:
                    print 'PASTE ERROR', input
        
        collObjColls = []
        pastedCtrls = []            
        # find main method
        idx = -1
        for meth in methList[:]:
            idx = idx + 1
            if meth[0] == self.collectionMethod:
                collMethod = meth[0]
                methBody = meth[1:]
            else:
                # XXX not good :(
                ctrlName = string.join(string.split(meth[0], '_')[3:-1], '_')
                newObjColl = self.model.readDesignerMethod(meth[0], meth[1:])
                methodparse.decorateCollItemInitsWithCtrl(newObjColl.creators, ctrlName)
                collObjColls.append( (meth[0], ctrlName, newObjColl) )

        # Parse input source
        objCol = self.model.readDesignerMethod(collMethod, methBody)
##        print 'read desgn meth', collMethod, methBody
        
        if not len(objCol.creators):
            return []

        # Rename possible name clashes
        objCol.indexOnCtrlName()
        pasteNameClasses = objCol.getCtrlNames()
        newNames = []
        oldNames = []
        # Preserve order, but determine all new names before 
        for name, clss in pasteNameClasses:
            if name in self.objectOrder:
                newName = self.newObjName(clss, newNames)
                newNames.append(newName)
                oldNames.append(name)
            else:
                newNames.append(name)
                oldNames.append(name)

        for oldName, newName in map(None, oldNames, newNames):
            if newName != oldName:
                objCol.renameCtrl(oldName, newName)
                pastedCtrls.append(newName)
                for idx in range(len(collObjColls)):
                    meth, collCtrlName, collObjColl = collObjColls[idx]
                    collObjColl.renameCtrl(oldName, newName)
                    if collCtrlName == oldName:
                        itms = string.split(meth, '_')
                        itms[3:-1] = [newName]
                        collObjColls[idx] = (string.join(itms, '_'), newName, collObjColl)
            else:
                pastedCtrls.append(oldName)

##        # Update references to renamed controls
##        for oldName, oldName in map(None, oldNames, newNames):
##            for name, clss in pasteNameClasses:
##                if name != oldName:
##                    self.objects[newName][0].renameCtrlRefs(oldName, newName)

        # Update model's object collections' collections
        for meth, collCtrlName, collObjColl in collObjColls:
            self.model.objectCollections[meth] = collObjColl

        # Get previous parent, 1st item in the group's parent will always be
        # the root parent
        # Only reparent visual controls
        if objCol.creators[0].params.has_key('parent'):
            copySource = objCol.creators[0].params['parent']
            objCol.reparent(copySource, Utils.srcRefFromCtrlName(destCtrlName))
        
        # create controls
        deps = {}
        depLnks = {}
        self.inspector.vetoSelect = true
        try:
            self.initObjectsAndCompanions(objCol.creators, objCol, deps, depLnks)
        finally:
            self.inspector.vetoSelect = false

        # merge pasted controls with current controls
        self.model.objectCollections[collMethod].merge(objCol)
    
        return pastedCtrls
        
    def addObject(self, ctrlName, companion, designTimeCtrl, parentName = None):
        self.objects[ctrlName] = [companion, designTimeCtrl]
        if parentName is not None: self.objects[ctrlName].append(parentName)
        self.objectOrder.append(ctrlName)
                    
    def newObjName(self, className, additionalNames = None):
        """ Return a name for a control unique in the scope of the model. """
        
        if additionalNames is None: additionalNames = []
        # XXX Now that there is multiple maintained methods is may fail because
        # XXX it's only unique in the method.
        num = 1
        if className[:2] == 'wx':
            newName = '%s%s'%(string.lower(className[2:3]), className[3:])
        else:
            newName = '%s%s'%(string.lower(className[0]), className[1:])

        return Utils.getValidName(self.objects.keys() + additionalNames, newName)

    def newObject(self, objClass, objCompanionClass):
        """ At design time, when adding a new ctrl from the palette, create and
            register given control and companion.
        """

        # XXX Only DataView uses this, refc
        objName = self.newObjName(objClass.__name__)

        self.checkHost(objCompanionClass)            

        companion = objCompanionClass(objName, self, objClass)
        params = companion.designTimeSource()
        self.addObject(objName, companion, companion.designTimeObject(), '')
        companion.persistConstr(objClass.__name__, params)
        return objName


    def addCtrlToObjectCollection(self, textConstr):
        colMeth = self.collectionMethod
        if not self.model.objectCollections.has_key(colMeth):
            self.model.objectCollections[colMeth] = ObjectCollection()
            
        self.model.objectCollections[colMeth].creators.append(textConstr)

    def addCollToObjectCollection(self, collInitParse):
        colMeth = self.collectionMethod
        self.model.objectCollections[colMeth].collections.append(collInitParse)
        # Add a new method to maintained methods
        newObjColl = ObjectCollection()
        self.model.objectCollections[collInitParse.method] = newObjColl
        return newObjColl

    def selectObject(self):
        pass

    def selectNone(self):
        pass

    def deleteCtrl(self, name, parentRef = None):
        self.model.objectCollections[self.collectionMethod].deleteCtrl(name)
        del self.objectOrder[self.objectOrder.index(name)]
        del self.objects[name]
        
        for ctrlName, propName in self.collEditors.keys()[:]:
            if ctrlName == name:
#                self.collEditors[(ctrlName, propName)].close()
                del self.collEditors[(ctrlName, propName)]

    def cleanup(self):
        if self == self.inspector.prevDesigner:
            self.inspector.prevDesigner = None

    def close(self):
        if self.controllerView != self:
            self.controllerView.close()

        # OnCloseWindow destroys everything, don't call inherited
##        EditorViews.EditorView.close(self)
    
    def refreshContainment(self, selectName = None):
        """ Rebuild parent tree and optionally select given control """        
        parRelations, parReference = self.buildParentRelationship()
        self.inspector.containment.refreshCtrl(self.model.main, parRelations, self)
        if selectName is not None:
             self.inspector.containment.selectName(selectName)
        return parRelations, parReference
    
##  decl getObjectsOfClass(self, theClass: class) -> dict
    def getObjectsOfClass(self, theClass):
        results = {}
        for objName in self.objects.keys():
            if issubclass(self.objects[objName][1].__class__, theClass):
                if objName:
                    results['self.'+objName] = self.objects[objName][1]
                else:    
                    results['self'] = self.objects[objName][1]
        return results

    def getObjectsOfClassWithParent(self, theClass, theParentName):
        results = {}
        for objName in self.objects.keys():
            if self.objects[objName][2] == theParentName and \
                  issubclass(self.objects[objName][1].__class__, theClass):
                if objName:
                    results['self.'+objName] = self.objects[objName][1]
                else:    
                    results['self'] = self.objects[objName][1]
        return results

    def getAllObjects(self):
        results = {}
        for objName in self.objects.keys():
            if objName:
                results['self.'+objName] = self.objects[objName][1]
            else:
                results['self'] = self.objects[objName][1]
        return results

    def getObjectsOfClassOwnedBy(self, theClass, theOwner):#XXX
        results = {}
        for objName in self.objects.keys():
            if self.objects[objName][1].__class__ is theClass:
                results['self.'+objName] = self.objects[objName][1]
        return results

    def showCollectionEditor(self, ctrlName, propName):
        """ Show the Collection Editor frame for given name and prop """
        # XXX param ctrlName is actually wrong!
        if ctrlName == self.GetName():
            ctrlName = ''
             
        if not self.collEditors.has_key((ctrlName, propName)):
            self.addCollView(ctrlName, '_init_coll_%s_%s'%(ctrlName, propName), true)

        self.collEditors[(ctrlName, propName)].show()

    def checkHost(self, ctrlCompanion):
        """ Checks that the companion may be hosted in this designer """
        if ctrlCompanion.host == 'Not Implemented':
            dlg = wxMessageDialog(self, 'This component is not yet implemented',
                              'Not Implemented', wxOK | wxICON_ERROR)
            try: dlg.ShowModal()
            finally: dlg.Destroy()
            raise 'Not Implemented'
        if ctrlCompanion.host != self.viewName:
            dlg = wxMessageDialog(self, 
              'This component must be created in '+ctrlCompanion.host,
              'Wrong Designer', wxOK | wxICON_ERROR)
            try: dlg.ShowModal()
            finally: dlg.Destroy()
            raise 'Wrong Designer'

    def expandNamesToContainers(self, ctrlNames):
        """ Expand set of names to include the names of all their children """
        return ctrlNames

    def collapseNamesToContainers(self, ctrlNames):
        """ Collapse set of names to exclude the names of all their children """
        return ctrlNames
    
    def notifyAction(self, compn, action):
        # notify components
        for otherCompn, otherCtrl, otherPrnt in self.objects.values():
            otherCompn.notification(compn, action)
        
        # notify collections
        for collView in self.collEditors.values():
            collView.companion.notification(compn, action)
            
                        
class DesignerView(wxFrame, InspectableObjectCollectionView):
    """ Frame Designer for design-time creation/manipulation of visual controls 
        on frames. """
    viewName = 'Designer'
    docked = false
    collectionMethod = init_ctrls
    handledProps = ['parent', 'id']
    supportsParentView = true
    
    def setupArgs(self, ctrlName, params, dontEval, parent = None, compClass = None):
        """ Create a dictionary of parameters for the constructor of the
            control from a dictionary of string/source parameters.
        """

        args = InspectableObjectCollectionView.setupArgs(self, ctrlName, params, dontEval)

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
        InspectableObjectCollectionView.__init__(self, inspector, model, compPal)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Designer.ico'))

        EVT_MOVE(self, self.OnFramePos)
        if Preferences.drawDesignerGrid:
            EVT_PAINT(self, self.OnPaint)

        self.drawGridMethods = {'lines' : self.drawGrid_intersectingLines,
                                'dots'  : self.drawGrid_dots,
                                'bitmap': self.drawGrid_bitmap,
                                'grid'  : self.drawGrid_grid}
        
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
        
        self.menu.Append(wxID_CTRLPARENT, 'Up')
        self.menu.Append(-1, "-")
        self.menu.Append(wxID_EDITCUT, 'Cut')
        self.menu.Append(wxID_EDITCOPY, 'Copy')
        self.menu.Append(wxID_EDITPASTE, 'Paste')
        self.menu.Append(wxID_EDITDELETE, 'Delete')
        self.menu.Append(-1, "-")
        self.menu.Append(wxID_EDITRECREATE, 'Recreate')
        self.menu.Append(-1, "-")
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
        InspectableObjectCollectionView.saveCtrls(self, definedCtrls) 

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

        InspectableObjectCollectionView.renameCtrl(self, oldName, newName)
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
        
        if params[ctrlCompanion.windowParentName] == 'self':
            parent = ''
        else:
            parent = string.split(params[ctrlCompanion.windowParentName], '.')[1]
                
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
           
##    def CtrlAnchored(self, ctrl):
##        result = (ctrl == self)

    def getObjectsOfClass(self, theClass):
        """ Overridden to also add objects from the DataView """
        results = InspectableObjectCollectionView.getObjectsOfClass(self, theClass)
        dataResults = {}
        for objName in self.dataView.objects.keys():
            if self.dataView.objects[objName][1].__class__ is theClass:
                dataResults['self.'+objName] = self.dataView.objects[objName][1]
        results.update(dataResults)
        return results

    def getAllObjects(self):
        """ Overridden to also add objects from the DataView """
        results = InspectableObjectCollectionView.getAllObjects(self)
        for objName in self.dataView.objects.keys():
            if objName:
                results['self.'+objName] = self.dataView.objects[objName][1]
            else:
                results['self'] = self.dataView.objects[objName][1]
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

##            print 'Selecting parent'
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
        
        InspectableObjectCollectionView.deleteCtrl(self, name)

        ctrlInfo[1].Destroy()
        
        if parRel is not None:
##            print 'refreshing containment'
            self.refreshContainment(parentName)
        
    def selectNone(self):
        if self.selection:
            self.selection.selectNone()
            self.selection = None
        elif self.multiSelection:
            for sel in self.multiSelection:
                sel.selectNone()
                sel.destroy()
            self.multiSelection = []
                            
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
            
        # Workaround toolbar offset bug
        tbOffset = 0
        if parent == self:
            tb = self.GetToolBar()
            if tb:
                tbOffset = tb.GetSize().y * -1

        # XXX Is this going to become to slow for frames with many ctrls?
        parRel, parRef = self.buildParentRelationship()
        if ctrl == self:
            children = parRef['']
        else:
            children = parRef[ctrlName]
        for childName in children.keys():
            childCompn, childCtrl = self.objects[childName][:2]
            try:
                pos = childCtrl.GetPosition()
                sze = childCtrl.GetSize()
            except:
                print 'could not get child ctrl size', childCtrl
            else:
                if childCtrl.IsShown() and wxIntersectRect((clickPos.x, clickPos.y + tbOffset, 1, 1),
                      (pos.x, pos.y, sze.x, sze.y)) is not None:
                    selCtrl = childCtrl
                    selCompn = childCompn
                    selPos = wxPoint(clickPos.x - pos.x, 
                          clickPos.y + tbOffset - pos.y)
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
        
#        rel, ref = self.buildParentRelationship()
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
            
            Returns true if the ctrl also wants the click event
        """
        if ctrl == self:
            companion = self.companion
        else: 
            companion = self.objects[ctrl.GetName()][0]
            
        ctrlName = companion.name

        selCtrl, selCompn, selPos = \
              self.checkChildCtrlClick(ctrlName, ctrl, companion, pos)
        
        #print 'selectControlByPos', selCtrl, selCompn, selPos
            
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
                        
            ctrlName = self.newControl(parent, self.compPal.selection[1], self.compPal.selection[2], pos)
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
        
    def OnFramePos(self, event):
        """ Called when frame is repositioned """
#        self.assureSingleSelection()
#        self.selection.selectCtrl(self, self.companion)
        if self.selection and self.selection.selection == self:
            self.inspector.constructorUpdate('Position')
        event.Skip()
    
    def _drawLines(self, dc, col, loglFunc, sze, sg):
        pen1 = wxPen(col)
        dc.SetPen(pen1)
        dc.SetLogicalFunction(loglFunc)
        for y in range(sze.y / sg):
            dc.DrawLine(0, y * sg, sze.x, y * sg)
        
        for x in range(sze.x / sg):
            dc.DrawLine(x * sg, 0, x * sg, sze.y)

    def drawGrid_intersectingLines(self, dc, sze, sg):
        bgCol = dc.GetBackground().GetColour()
        xorBgCol = wxColour(255^bgCol.Red(), 255^bgCol.Green(), 255^bgCol.Blue())
        
        self._drawLines(dc, xorBgCol, wxCOPY, sze, sg)
        self._drawLines(dc, wxNamedColour('WHITE'), wxXOR, sze, sg)
    
    darken = 20    
    def drawGrid_grid(self, dc, sze, sg):
        bgCol = dc.GetBackground().GetColour()
        darkerBgCol = wxColour(max(bgCol.Red()   -self.darken, 0), 
                               max(bgCol.Green() -self.darken, 0), 
                               max(bgCol.Blue()  -self.darken, 0))

        self._drawLines(dc, darkerBgCol, wxCOPY, sze, sg)
    
    def drawGrid_dots(self, dc, sze, sg):
        pen1 = wxPen(wxNamedColour('BLACK'))
        dc.SetPen(pen1)
        for y in range(sze.y / sg + 1):
            for x in range(sze.x / sg + 1):
                dc.DrawPoint(x * sg, y * sg)
    
    def drawGrid_bitmap(self, dc, sze, sg):
        pass
    
    def OnPaint(self, event):
        dc = wxPaintDC(self)
        sze = self.GetSize()
        sg = SelectionTags.screenGran
        
        drawGrid = self.drawGridMethods[Preferences.drawGridMethod]
        
        dc.BeginDrawing()
        try:
            drawGrid(dc, sze, sg)
        finally:
            dc.EndDrawing()

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
            ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        output = []
        self.cutCtrls(ctrls, [], output)
        
        Utils.writeTextToClipboard(string.join(output, os.linesep))
        
        self.refreshContainment()

    def OnCopySelected(self, event):
        """ Copy current selection to the clipboard """
        if self.selection:
            ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        output = []
        self.copyCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(string.join(output, os.linesep))

    def OnPasteSelected(self, event):
        """ Paste current clipboard contents into the current selection """
        if self.selection:
            if not self.selection.selCompn.container:
                self.selectParent(self.selection.selection)
            pasted = self.pasteCtrls(self.selection.name, 
                  string.split(Utils.readTextFromClipboard(), os.linesep))
            if len(pasted):
                self.refreshContainment()
                pasted = self.collapseNamesToContainers(pasted)
                if len(pasted) == 1:
                    self.selection.selectCtrl(self.objects[pasted[0]][1], 
                          self.objects[pasted[0]][0])        
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
        sel.resizeCtrl()
        sel.setSelection(true)
        #sel.positionUpdate()
        
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
#        sel.positionUpdate()

    def OnWidthInc(self, event): 
        sel = self.selection 
        if sel and sel.selection != self:
            sel.size.x = sel.size.x + 1
            sel.startSize.x = sel.startSize.x + 1
            self.sizeUpdate(sel)
    def OnWidthDec(self, event): 
        sel = self.selection 
        if sel and sel.selection != self and sel.size.x > 0:
            sel.size.x = sel.size.x - 1
            sel.startSize.x = sel.startSize.x - 1
            self.sizeUpdate(sel)
    def OnHeightInc(self, event): 
        sel = self.selection 
        if sel and sel.selection != self:
            sel.size.y = sel.size.y + 1
            sel.startSize.y = sel.startSize.y + 1
            self.sizeUpdate(sel)
    def OnHeightDec(self, event): 
        sel = self.selection 
        if sel and sel.selection != self and sel.size.y > 0:
            sel.size.y = sel.size.y - 1
            sel.startSize.y = sel.startSize.y - 1
            self.sizeUpdate(sel)

    def OnSnapToGrid(self, event):
        for sel in self.getSelAsList():
            if sel.selection != self:
                sel.position.x = SelectionTags.granularise(sel.position.x)
                sel.position.y = SelectionTags.granularise(sel.position.y)
                sel.startPos.x = sel.position.x
                sel.startPos.y = sel.position.y
                self.moveUpdate(sel)


