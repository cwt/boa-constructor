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
from SelectionTags import SingleSelectionGroup, MultiSelectionGroup, granularise
from EditorModels import init_ctrls, init_utils, ObjectCollection, isInitCollMeth, getCollName
import CtrlAlign, CtrlSize
import RTTI, PrefsKeys, pprint
import methodparse

bodyIndent = ' '*8

[wxID_CTRLPARENT, wxID_EDITCUT, wxID_EDITCOPY, wxID_EDITPASTE, wxID_EDITDELETE,
 wxID_SHOWINSP, wxID_SHOWEDTR, wxID_CTRLHELP, wxID_EDITALIGN, wxID_EDITSIZE,
 wxID_EDITRECREATE, 
] = map(lambda _init_ctrls: wxNewId(), range(11))

class InspectableObjectCollectionView(EditorViews.EditorView):
    viewName = 'InspectableObjectCollection'
    collectionMethod = 'init_'
    collectionParams = 'self'
    handledProps = []
    supportsParentView = false

    def setupArgs(self, ctrlName, params, dontEval):
        """ Create a dictionary of parameters for the constructor of the        
            control from a dictionary of string/source parameters.              
            Catches design time parameter overrides.                         """

        args = {}
        # Build dictionary of params
        for paramKey in params.keys():
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
        print 'DESTROY InspectableObjectCollectionView', self.__class__.__name__
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

##  decl buildParentRelationship(self) -> (dict, dict)
    def buildParentRelationship(self):
        """ Build a nested dictionary of key = name, value = dict pairs
            describing parental relationship.
            Assuming parents are created before children
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
        
    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):
        collDeps = {}
        for ctrl in creators:
            self.initObjCreator(ctrl)
            self.initObjProps(objColl.propertiesByName, ctrl.comp_name, ctrl, dependents, depLinks)
            self.initObjColls(objColl.collectionsByName, ctrl.comp_name, ctrl, collDeps)
            self.initObjEvts(objColl.eventsByName, ctrl.comp_name, ctrl)
            
            self.applyDepsForCtrl(ctrl.comp_name, depLinks)

#        self.initObjDeps(dependents)
                
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
#                    from methodparse import CollectionInitParse
                    collItem = methodparse.CollectionInitParse(prop.params[0])
                    self.addCollView(name, collItem.method, false)
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
        
        collEditView = CollectionEdit.CollectionEditorView(self, self.inspector, 
            self.model, collComp)
        collEditView.initialise()
                
        self.collEditors[(comp.name, collName)] = collEditView
        
    def checkAndAddDepLink(self, ctrlName, prop, dependentProps, deps, depLinks, definedCtrls):
        if prop.prop_name in dependentProps:
            # Don't postpone if target ctrl already defined
            target = Utils.ctrlNameFromSrcRef(prop.params[0])
            if target not in definedCtrls:
                self.addDepLink(prop, ctrlName, deps, depLinks)
                return true
        return false

    def applyDepsForCtrl(self, ctrlName, depLinks):
        if depLinks.has_key(ctrlName):
            for prop in depLinks[ctrlName]:
                ctrl = self.objects[prop.comp_name][1] 
                if ctrlName == '': 
                    value = self
                else:
                    ord, objs = self.model.allObjects()
                    
                    if objs.has_key(ctrlName):
                        value = objs[ctrlName][1]
                    else:
                        continue
                RTTI.getFunction(ctrl, prop.prop_setter)(ctrl, value)
            del depLinks[ctrlName]

    def addDepLink(self, prop, name, dependents, depLinks):
        if not dependents.has_key(name):
            dependents[name] = []
        dependents[name].append(prop)

        link = Utils.ctrlNameFromSrcRef(prop.params[0])

        if not depLinks.has_key(link):
            depLinks[link] = []
        depLinks[link].append(prop)
    
    def finaliseDepLinks(self, depLinks):
        for ctrlName in depLinks.keys()[:]:
            self.applyDepsForCtrl(ctrlName, depLinks)

    def renameCtrl(self, oldName, newName):
        """ Rename a control and update all its properties and events."""

        ctrl = self.objects[oldName]
        del self.objects[oldName]
        self.objects[newName] = ctrl
        
        idx = self.objectOrder.index(oldName)
        del self.objectOrder[idx]
        self.objectOrder.insert(idx, newName)
        # self.objectOrder[self.objectOrder.index(oldName)] = newName

        companion = self.objects[newName][0]
        companion.renameCtrl(oldName, newName)

        for name, prop in self.collEditors.keys():
            if name == oldName:
                collEditor = self.collEditors[(name, prop)]
                collEditor.renameCtrl(oldName, newName)
                del self.collEditors[(name, prop)]
                self.collEditors[(newName, prop)] = collEditor

                        
    def saveCtrls(self, definedCtrls):
        """ Replace current source of method in collectionMethod with values from
            constructors, properties and events. 
        """

        newBody = []
        deps = {}
        depLinks = {}
        collDeps = []

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

            compn.writeDependencies(newBody, ctrlName, depLinks)
                
            newBody.append('')

        if collDeps:
            newBody.extend(collDeps + [''])
        
        module = self.model.getModule()
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
            
            compn.writeConstructor(output, self.collectionMethod)
            compn.writeProperties(output, ctrlName, definedCtrls, deps, depLinks) 
            compn.writeCollections(output, collDeps)
            compn.writeEvents(output, addModuleMethod = false)

            compn.writeDependencies(output, ctrlName, depLinks)
                
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
                except:
                    print 'PASTE ERROR', input
        
        print methList

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
        
        if not len(objCol.creators):
            print 'Empty clipboard'
            return []
            #return 0

        # Rename possible name clashes
        objCol.indexOnCtrlName()
        pns = objCol.getCtrlNames()
        newNames = []
        for name, clss in pns:
            if name in self.objectOrder:
                newName = self.newObjName(clss, newNames)
                newNames.append(newName)
                objCol.renameCtrl(name, newName)
                pastedCtrls.append(newName)
                for idx in range(len(collObjColls)):
                    meth, collCtrlName, collObjColl = collObjColls[idx]
                    if collCtrlName == name:
                        print 'renaming Coll Obj Coll'
                        itms = string.split(meth, '_')
                        itms[3:-1] = [newName]
                        collObjColl.renameCtrl(name, newName)
                        collObjColls[idx] = (string.join(itms, '_'), newName, collObjColl)
            else:
                pastedCtrls.append(name)

        # Update model's object collections
        print 'Update models object collections'
        for meth, collCtrlName, collObjColl in collObjColls:
            print meth, collCtrlName
            self.model.objectCollections[meth] = collObjColl

        # Get previous parent, 1st item in the group's parent will always be
        # the root parent
        # XXX Not working
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
                results['self.'+objName] = self.objects[objName][1]
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
            self.SetIcon(wxIcon(path.join(Preferences.toPyPath(\
              'Images/Icons/Designer.ico')), wxBITMAP_TYPE_ICO))

        EVT_MOVE(self, self.OnFramePos)

        self.pageIdx = -1
        self.dataView = dataView
        self.dataView.controllerView = self
        self.controllerView = self
        self.saveOnClose = true
        
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
        # Key bindings
        accLst = []
        for name, wId in (('Delete', wxID_EDITDELETE), 
                          ('Inspector', wxID_SHOWINSP), 
                          ('Editor', wxID_SHOWEDTR), 
                          ('ContextHelp', wxID_CTRLHELP),
                          ('Escape', wxID_CTRLPARENT),
                          ('Copy', wxID_EDITCOPY),
                          ('Paste', wxID_EDITPASTE)):
            tpe, key = PrefsKeys.keyDefs[name]
            accLst.append((tpe, key, wId))

        self.SetAcceleratorTable(wxAcceleratorTable(accLst))
                    
    def saveCtrls(self, definedCtrls):
        # Remove all collection methods
        for oc in self.model.identifyCollectionMethods(): 
            if len(oc) > len('_init_coll_') and oc[:11] == '_init_coll_':
                module = self.model.getModule()
                module.removeMethod(self.model.main, oc)

        InspectableObjectCollectionView.saveCtrls(self, definedCtrls) 

        companions = map(lambda i: i[0], self.objects.values())
        self.model.writeWindowIds(self.collectionMethod, companions)

    def renameCtrl(self, oldName, newName):
        InspectableObjectCollectionView.renameCtrl(self, oldName, newName)
        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = newName

        self.refreshContainment(selName)

    def refreshCtrl(self):
        if self.destroying: return

        # Delete previous
        comps = {}
        
        # Create selection if none is defined
        if not self.selection:
            self.selection = SingleSelectionGroup(self, self.senderMapper, 
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
        self.selection = SingleSelectionGroup(self, self.senderMapper, 
              self.inspector, self)

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
           
    def CtrlAnchored(self, ctrl):
        result = (ctrl == self)

    def getObjectsOfClass(self, theClass):
        results = InspectableObjectCollectionView.getObjectsOfClass(self, theClass)
        dataResults = {}
        for objName in self.dataView.objects.keys():
            if self.dataView.objects[objName][1].__class__ is theClass:
                dataResults['self.'+objName] = self.dataView.objects[objName][1]
        results.update(dataResults)
        return results

    def getAllObjects(self):#, theClass):
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
            
        children = parRef[name]
        for child in children.keys():
            self.deleteCtrl(child, parRef)
        
        InspectableObjectCollectionView.deleteCtrl(self, name)

        ctrlInfo[1].Destroy()
        
        if parRel is not None:
            self.refreshContainment(parentName)
        
    def selectNone(self):
        if self.selection: self.selection.selectNone()
                
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
                if wxIntersectRect((clickPos.x, clickPos.y + tbOffset, 1, 1),
                      (pos.x, pos.y, sze.x, sze.y)) is not None:
                    selCtrl = childCtrl
                    selCompn = childCompn
                    selPos = wxPoint(clickPos.x - pos.x, 
                          clickPos.y + tbOffset - pos.y)
                    break;

        return selCtrl, selCompn, selPos
    
    def clearMultiSelection(self):
        for sel in self.multiSelection:
            sel.destroy()
        self.multiSelection = []

    def assureSingleSelection(self):
        if not self.selection:
            self.selection = SingleSelectionGroup(self, self.senderMapper, 
                  self.inspector, self)
    
    def flattenParentRelationship(self, rel, lst):
        for itm in rel.keys():
            lst.append(itm)
            self.flattenParentRelationship(rel[itm], lst)
        
    def expandNamesToContainers(self, ctrlNames):
        exp = ctrlNames[:]
        rel, ref = self.buildParentRelationship()
        for ctrl in ctrlNames:
            children = []
            self.flattenParentRelationship(ref[ctrl], children)
            exp.extend(children)
        
        return exp

    def OnMouseOver(self, event):
        if event.Dragging():
            pos = event.GetPosition()
            ctrl = self.senderMapper.getObject(event)

            if self.selection: 
                self.selection.moving(ctrl, pos)
            elif self.multiSelection:
                for sel in self.multiSelection:
                    sel.moving(ctrl, pos, self.mainMultiDrag)
                    
        event.Skip()

    def OnControlSelect(self, event):
        """ Control is clicked. Either select it or add control from palette """
        
        ctrl = self.senderMapper.getObject(event)

        if ctrl == self:
            companion = self.companion
        else: 
            companion = self.objects[ctrl.GetName()][0]
        # Component on palette selected, create it
        if self.compPal.selection:
            pos = event.GetPosition()
            if companion.container:
                parent = ctrl
            else:
                parent = ctrl.GetParent()
                screenPos = ctrl.ClientToScreen(pos)
                pos = parent.ScreenToClient(screenPos)

            # Workaround toolbar offset bug
            if parent == self:
                tb = self.GetToolBar()
                if tb:
                    pos.y = pos.y - tb.GetSize().y

            # Granularise position
            pos = wxPoint(granularise(pos.x), granularise(pos.y))
                        
            ctrlName = self.newControl(parent, self.compPal.selection[1], self.compPal.selection[2], pos)
            self.compPal.selectNone()
            
            if self.selection:
                ctrl = self.objects[ctrlName][1]
                self.selection.selectCtrl(ctrl, self.objects[ctrlName][0])
        # Select ctrl
        else:
            if self.selection or self.multiSelection:
                evtPos = event.GetPosition()    
                ctrlName = companion.name

                selCtrl, selCompn, selPos = \
                      self.checkChildCtrlClick(ctrlName, ctrl, companion, evtPos)
                                       
                # Multi selection
                if event.ShiftDown():
                    # Verify that it's a legal multi selection
                    # They must have the same parent
                    if self.selection:
                        if ctrl.GetParent().this != self.selection.selection.GetParent().this:
                            return
                    elif self.multiSelection:
                        if ctrl.GetParent().this != self.multiSelection[0].selection.GetParent().this:
                            return
                        
                    if not self.multiSelection:
                        # don't select if multiselecting single selection
                        if ctrl == self.selection.selection:
                            return

                        newSelection = MultiSelectionGroup(self, self.senderMapper, 
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
                                    self.selection = SingleSelectionGroup(self, 
                                        self.senderMapper, self.inspector, self)
                                    
                                    self.selection.assign(self.multiSelection[0])
                                    self.selection.selectCtrl(self.multiSelection[0].selection, 
                                          self.multiSelection[0].selCompn)
                                    self.clearMultiSelection()
                                return   

                    newSelection = MultiSelectionGroup(self, self.senderMapper, 
                          self.inspector, self)
                    newSelection.selectCtrl(selCtrl, selCompn)
                    self.multiSelection.append(newSelection)
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
#                                    capSel.showFrameTags()
                                return
                        
                        self.clearMultiSelection()

                    self.assureSingleSelection()

                    self.selection.selectCtrl(selCtrl, selCompn)
                    self.selection.moveCapture(selCtrl, selCompn, selPos)
    
    def OnControlRelease(self, event):
        if self.selection:
            self.selection.moveRelease()
        elif self.multiSelection:
            for sel in self.multiSelection:
                sel.moveRelease()
            self.mainMultiDrag = None
        event.Skip()
        
    def OnControlResize(self, event):
        try:
            if event.GetId() == self.GetId():
                self.selection.selectCtrl(self, self.companion)

                # Granularise frame sizing so that controls inside main frame
                # fits exactly
                sze = self.GetSize()
                granSze = granularise(sze.x), granularise(sze.y)+3
                self.SetSize(granSze)

                # Compensate for autolayout=false and 1 ctrl on frame behaviour
                # Needed because incl selection tags there are actually 5 ctrls
                
                if not self.GetAutoLayout():
                    # Count children
                    c = 0
                    ctrl = None
                    for ctrlLst in self.objects.values():
                        if len(ctrlLst) > 2 and ctrlLst[2] == '' and \
                          (ctrlLst[1].__class__ not in self.ignoreWindows):
                            c = c + 1
                            ctrl = ctrlLst[1]
                    
                    if c == 1:
                        s = self.GetClientSize()
                        ctrl.SetDimensions(0, 0, s.x, s.y)
                        
            if self.selection:
                self.selection.sizeFromCtrl()
                self.selection.setSelection()
        finally:
            event.Skip()
            self.Layout()

    def OnControlDClick(self, event):
        pass

    def OnFramePos(self, event):
        # Called when frame repositioned
        self.assureSingleSelection()
        self.selection.selectCtrl(self, self.companion)
        self.inspector.constructorUpdate('Position')
        event.Skip()
        
    def OnCloseWindow(self, event):
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
        ctrl = self.senderMapper.getObject(event)
        screenPos = ctrl.ClientToScreen(wxPoint(event.GetX(), event.GetY()))
        parentPos = self.ScreenToClient(screenPos)
        self.popx = parentPos.x
        self.popy = parentPos.y
    
    def OnInspector(self, event):
        self.inspector.Show(true)
        self.inspector.Raise()
        
    def OnControlDelete(self, event):
        ctrls = []
        if self.selection:
            ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)
        
        #map(self.deleteCtrl, ctrls)
        for ctrlName in ctrls:
            self.deleteCtrl(ctrlName)
        
    def OnEditor(self, event):
        self.model.editor.Show(true)
        self.model.editor.Raise()
    
    def OnCtrlHelp(self, event):
        if self.inspector.selCmp:
            Help.showHelp(self, Help.wxWinHelpFrame, 
              self.inspector.selCmp.wxDocs, None)
    
    def OnAlignSelected(self, event):
        if self.multiSelection:
            dlg = CtrlAlign.ControlAlignmentFrame(self, self.multiSelection)
            try: dlg.ShowModal()
            finally: dlg.Destroy()
        
    def OnSizeSelected(self, event):
        if self.multiSelection:
            dlg = CtrlSize.ControlSizeFrame(self, self.multiSelection)
            try: dlg.ShowModal()
            finally: dlg.Destroy()
    
    def OnSelectParent(self, event):
        if self.selection:
            self.selectParent(self.selection.selection)        
        elif self.multiSelection:
            self.selectParent(self.multiSelection[0].selection)        
        
    def OnCutSelected(self, event):
        if self.selection:
            ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        output = []
        self.cutCtrls(ctrls, [], output)
        
        clip = wxTheClipboard
        clip.Open()
        try:
            clip.SetData(wxTextDataObject(string.join(output, os.linesep)))
        finally:
            clip.Close()
        
        self.refreshContainment()

    def OnCopySelected(self, event):
        if self.selection:
            ctrls = [self.selection.name]
        elif self.multiSelection:
            ctrls = map(lambda sel: sel.name, self.multiSelection)

        output = []
        self.copyCtrls(ctrls, [], output)

        clip = wxTheClipboard
        clip.Open()
        try:
            clip.SetData(wxTextDataObject(string.join(output, os.linesep)))
        finally:
            clip.Close()

    def OnPasteSelected(self, event):
        if self.selection:
            clip = wxTheClipboard
            clip.Open()
            try:
                data = wxTextDataObject()
                clip.GetData(data)
            finally:
                clip.Close()

            pasted = self.pasteCtrls(self.selection.name, 
                  string.split(data.GetText(), os.linesep))
            if len(pasted):
                self.refreshContainment()
                # XXX not selecting root component
                self.selection.selectCtrl(self.objects[pasted[0]][1], 
                      self.objects[pasted[0]][0])        

    def OnRecreateSelected(self, event):
        if self.selection and self.selection.selection != self:
            output = []
            ctrlName = self.selection.name
            # XXX Boa should be able to tell me this
            parent = self.selection.selection.GetParent()
            print parent
            if parent.GetId() == self.GetId():
                parentName = ''
            else:
                parentName = parent.GetName()
                
            self.cutCtrls([ctrlName], [], output)
            self.pasteCtrls(parentName, output)
