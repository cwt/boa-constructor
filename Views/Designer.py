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
import EditorViews, PaletteMapping, Preferences, Utils
from SelectionTags import SelectionGroup, granularise
from EditorModels import init_ctrls, init_utils, ObjectCollection
import RTTI, PrefsKeys
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
        del self.objects
        del self.senderMapper
        EditorViews.EditorView.destroy(self)

#  decl buildParentRelationship(self) -> (dict, dict)
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

    def organiseCollection(self): # deprc
        """ Restructures an ObjectCollection into propery and event dicts       
            keyed on the control name.                                       """

        props = {}
        events = {}
        objColl = ObjectCollection()
        if self.model.objectCollections.has_key(self.collectionMethod):
            objColl = self.model.objectCollections[self.collectionMethod]
            objColl.indexOnCtrlName()
            
            props = objColl.propertiesByName
            events = objColl.eventsByName
    
        return objColl, props, events
        
    def initObjectsAndCompanions(self, creators, objColl, dependents = {}) :
        collDeps = {}
        for ctrl in creators:
            self.initObjCreator(ctrl)
            self.initObjProps(objColl.propertiesByName, ctrl.comp_name, ctrl, dependents)
            self.initObjColls(objColl.collectionsByName, ctrl.comp_name, ctrl, collDeps)
            self.initObjEvts(objColl.eventsByName, ctrl.comp_name, ctrl)

        for ctrlName in dependents.keys():
            ctrl = self.objects[ctrlName][1] 
            for prop in dependents[ctrlName]:
                name = string.strip(prop.params[0])
                if name == 'self':
                    value = self
                elif len(name) > 5 and name[:5] == 'self.':
                    ord, objs = self.model.allObjects()
                    name = name[5:]
                    if objs.has_key(name):
                        value = objs[name][1]
                else:
                    continue
                
##                print 'InitDeps', ctrl, prop.prop_setter, value
                RTTI.getFunction(ctrl, prop.prop_setter)(ctrl, value)
        
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

    def initObjProps(self, props, name, creator, dependents = {}):
        """ Initialise property list by evaluating 1st parameter and calling    
            prop's setter with it.                                              
            Also associate companion name with prop parse objs               """    
##        print 'INITOBJPROPS', props, name, creator
    
        if props.has_key(name):
            comp = self.objects[name][0]
            ctrl = self.objects[name][1]
            # initialise live component's properies
            for prop in props[name]:
##                print 'initObjProps: propname', prop
                prop.prop_name = comp.getPropNameFromSetter(prop.prop_setter)
                if prop.prop_name in comp.dependentProps():
                    if not dependents.has_key(name):
                        dependents[name] = []
                    dependents[name].append(prop)
                elif prop.params[0][:11] == 'self._init_':
                    from methodparse import CollectionInitParse
                    collItem = CollectionInitParse(prop.params[0])
                    self.addCollView(name, collItem.method, false)
                else:                     
                    try:
                        value = PaletteMapping.evalCtrl(prop.params[0])
                    except AttributeError, name:
##                        print self.objects.keys(), prop.prop_name
                        if self.objects.has_key(name):
                            value = self.objects[name][1]
                        else:
                            raise
                    RTTI.getFunction(ctrl, prop.prop_setter)(ctrl, value)

            # store default prop vals
            comp.setProps(props[name])

    def initObjColls(self, collInits, name, creator, dependents = {}):
        """ Initialise collection properties by creating a collection view     
            for it and applying it.                                            
            Also associate companion name with prop parse objs               """    

##        print 'DESGN: initObjColls1', name, collInits.keys()
        if collInits.has_key(name):
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
                
    def addCollView(self, name, collInitMethod, create):
        import CollectionEdit
        
##        print self.__class__.__name__, self.objects.keys()
        comp, ctrl = self.objects[name][:2]
        collName = collInitMethod[len('_init_coll_'+name)+1:]
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

##        print 'ADDCOLLVIEW:', collInitMethod, id(self.model.objectCollections[collInitMethod].creators), id(collComp.textConstrLst)
        
        # init DTCtrl
        for crt in collComp.textConstrLst:
            collComp.applyDesignTimeDefaults(crt.params)
        collComp.initCollection()
        
        collEditView = CollectionEdit.CollectionEditorView(self, self.inspector, 
            self.model, collComp)
        collEditView.initialise()
                
        self.collEditors[(comp.name, collName)] = collEditView
        
    def initObjEvts(self, events, name, creator):
##        print 'initObjEvts', name, events
        if events.has_key(name):
            self.objects[name][0].setEvents(events[name])

    def renameCtrl(self, oldName, newName):
        """ Rename a control and update all its properties and events."""
##        print 'IOC rename ctrl'
        ctrl = self.objects[oldName]
        del self.objects[oldName]
        self.objects[newName] = ctrl
        
        idx = self.objectOrder.index(oldName)
        del self.objectOrder[idx]
        self.objectOrder.insert(idx, newName)
        # self.objectOrder[self.objectOrder.index(oldName)] = newName

        companion = self.objects[newName][0]
        companion.renameCtrl(oldName, newName)

##        companion.textConstr.comp_name = newName
##        for prop in companion.textPropList:
##            prop.comp_name = newName
##        for evt in companion.textEventList:
##            evt.comp_name = newName

        for name, prop in self.collEditors.keys():
            if name == oldName:
##                print 'renaming collEditor'
                collEditor = self.collEditors[(name, prop)]
                collEditor.renameCtrl(oldName, newName)
                del self.collEditors[(name, prop)]
                self.collEditors[(newName, prop)] = collEditor


            # Add events connections and methods
    def saveEvts(self, compn, newBody):
        for evt in compn.textEventList:
            if evt.trigger_meth != '(delete)':
                newBody.append(bodyIndent + evt.asText())
                if not self.model.module.classes[\
                  self.model.main].methods.has_key(evt.trigger_meth):
                    self.model.module.addMethod(self.model.main, 
                      evt.trigger_meth, 'self, event', ['        pass'])
                        
    def saveCtrls(self):
        """ Replace current source of method in collectionMethod with values from
            constructors, properties and events. 
        """
   
        newBody = []
        deps = []

        for collView in self.collEditors.values():
            collView.saveCtrls()

##        print 'Save:', self.objectOrder
        for ctrlName in self.objectOrder:
            compn = self.objects[ctrlName][0]
            try:
                # Add constructor
                if compn.textConstr:
                    newBody.append(bodyIndent + compn.textConstr.asText())
                    # XXX HACK attack
                    if compn.textConstr.comp_name == '' and \
                      self.collectionMethod == '_init_ctrls':
                        newBody.append(bodyIndent + 'self._init_utils()')
            except: 
                print 'no constr:', ctrlName

            # Add properties
            for prop in compn.textPropList:
##                print prop.params
		if prop.prop_name in compn.dependentProps():
                    deps.append(bodyIndent + prop.asText())
                else:
                    newBody.append(bodyIndent + prop.asText())

            # Add collection initialisers
            for collInit in compn.textCollInitList:
                if collInit.getPropName() in compn.dependentProps():
                    deps.append(bodyIndent + collInit.asText())
                else:
                    newBody.append(bodyIndent + collInit.asText())

            # Add events connections and methods
            self.saveEvts(compn, newBody)
                
            newBody.append('')

        if deps:
            newBody.extend(deps + [''])
        
        if self.model.module.classes[self.model.main].methods.has_key(\
          self.collectionMethod):
            # Add doc string
            docs = self.model.module.getClassMethDoc(self.model.main, 
              self.collectionMethod)
            if (len(docs) > 0) and docs[0]:
                newBody.insert(0, '%s""" %s """'%(bodyIndent, docs))
        
            if len(newBody):
##                for i in self.model.module.source: print i[:60]
                self.model.module.replaceMethodBody(self.model.main, 
                  self.collectionMethod, newBody)
##                for i in self.model.module.source: print i[:60]
        else:
            if len(newBody):
##                print 'DESIGNER adding new method!!!'
                self.model.module.addMethod(self.model.main, 
                  self.collectionMethod, self.collectionParams, newBody, 0)

##        print 'OCK', self.model.objectCollections.keys()
##        srcMeths = self.model.identifyCollectionMethods()
##        for meth in srcMeths:
##            print meth
##            if not self.model.objectCollections.has_key(meth):
##                self.module.removeMethod(self.model.main, meth)
                
        self.model.refreshFromModule()
                
    def addObject(self, ctrlName, companion, designTimeCtrl, parentName = None):
        self.objects[ctrlName] = [companion, designTimeCtrl]
        if parentName is not None: self.objects[ctrlName].append(parentName)
        self.objectOrder.append(ctrlName)
            
    def newObjName(self , className):
        """ Return a name for a control unique in the scope of the model. """

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
        """

        # XXX Only DataView uses this, refc
        
        objName = self.newObjName(objClass.__name__)

        self.checkHost(objCompanionClass)            

        companion = objCompanionClass(objName, self, objClass)

        params = companion.designTimeSource()

        self.addObject(objName, companion, companion.designTimeObject(), '')
#        self.objects[objName] = [companion, companion.designTimeObject()]
#        self.objectOrder.append(objName)
        
##        print self.__class__.__name__, self.objects.keys()

        companion.persistConstr(objClass.__name__, params)
##        print 'newObj', objName, params, companion.textConstr.asText()
        return objName

        
##        self.objects[ctrlName] = [companion, companion.designTimeControl(position, size), parentName]
##        self.objectOrder.append(ctrlName)
##        
##        params['id'] = companion.id
##        companion.persistConstr(ctrlClass.__name__, params)

        ### loadControl
##        companion = ctrlCompanion(ctrlName, self, None, ctrlClass)
##        self.objects[ctrlName] = [companion, 
##         companion.designTimeControl(None, None, args), parent]
##        self.objectOrder.append(ctrlName)


    def addCtrlToObjectCollection(self, textConstr):
        colMeth = self.collectionMethod
        if not self.model.objectCollections.has_key(colMeth):
            self.model.objectCollections[colMeth] = ObjectCollection()
            
        self.model.objectCollections[colMeth].creators.append(textConstr)

    def addCollToObjectCollection(self, collInitParse):
        colMeth = self.collectionMethod
##        print 'IOC: addCollToObjectCollection, ', collInitParse
        self.model.objectCollections[colMeth].collections.append(collInitParse)
##        self.
        # Add a new method to maintained methods
        newObjColl = ObjectCollection()
        self.model.objectCollections[collInitParse.method] = newObjColl
        return newObjColl

    def selectObject(self):
        pass

    def selectNone(self):
        pass

    def deleteCtrl(self, name, parentRef = None):
##        print 'DELETE CTRL', name
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
##        print 'INSPOBJCOL CLOSE' mbd
        self.controllerView.close()
        # OnCloseWindow destroys everything, don't call inherited
##        EditorViews.EditorView.close(self)
    
    def refreshContainment(self, selectName = None):        
        parRelations, parReference = self.buildParentRelationship()
##        print 'before refreshContainment'
        self.inspector.containment.refreshCtrl(self.model.main, parRelations, self)
##        print 'after refreshContainment'
        if selectName is not None:
             self.inspector.containment.selectName(selectName)
        return parRelations, parReference
    
##  decl getObjectsOfClass(self, theClass: class) -> dict
    def getObjectsOfClass(self, theClass):
        results = {}
        for objName in self.objects.keys():
            if issubclass(self.objects[objName][1].__class__, theClass):
                results['self.'+objName] = self.objects[objName][1]
##                print 'is subclass'
##            else: print 'not subclass', self.objects[objName][1].__class__, theClass
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
        if not self.collEditors.has_key((ctrlName, propName)):
            self.addCollView(ctrlName, '_init_coll_%s_%s'%(ctrlName, propName), true)

##        print '$$$$$ SCE', id(self.collEditors[(ctrlName, propName)].companion.textConstrLst),
        self.collEditors[(ctrlName, propName)].show()

    def checkHost(self, ctrlCompanion):
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
    """ Factory to create new controls """
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
                
        self.menu.Append(tPopupIDUp, 'Up')
        self.menu.Append(-1, "-")
        self.menu.Append(tPopupIDCut, 'Cut')
        self.menu.Append(tPopupIDCopy, 'Copy')
        self.menu.Append(tPopupIDPaste, 'Paste')
        self.menu.Append(tPopupIDDelete, 'Delete')
        EVT_MENU(self, tPopupIDDelete, self.OnControlDelete)
        
        self.selection = None

 	EVT_CLOSE(self, self.OnCloseWindow)

        shInsp = wxNewId()
        EVT_MENU(self, shInsp, self.OnInspector)
        accLst = []
        tpe, key = PrefsKeys.keyDefs['Delete']
        accLst.append((tpe, key, tPopupIDDelete))
        tpe, key = PrefsKeys.keyDefs['Inspector']
        accLst.append((tpe, key, shInsp))
        
        self.SetAcceleratorTable(wxAcceleratorTable(accLst))
                    
    def saveCtrls(self):
        # Remove all collection methods
        for oc in self.model.identifyCollectionMethods(): 
            if len(oc) > len('_init_coll_') and oc[:11] == '_init_coll_':
                self.model.module.removeMethod(self.model.main, oc)

        InspectableObjectCollectionView.saveCtrls(self) 

        companions = map(lambda i: i[0], self.objects.values())
        self.model.writeWindowIds(self.collectionMethod, companions)

    def renameCtrl(self, oldName, newName):
        InspectableObjectCollectionView.renameCtrl(self, oldName, newName)
        selName = self.inspector.containment.selectedName()
        if selName == oldName: selName = newName

##        print 'refresh constainment', `selName`
        self.refreshContainment(selName)
##        print 'refreshed constainment'

    def refreshCtrl(self):
##        print 'Designer refreshCtrl'
        if self.destroying: return

        # XXX delete previous
        
        comps = {}
        
        # Reorder props and events into components
        
        if not self.selection:
            self.selection = SelectionGroup(self, self.senderMapper, 
              self.inspector, self)

        self.model.editor.statusBar.setHint('Creating frame')
        
        objCol = self.model.objectCollections[self.collectionMethod]
        objCol.indexOnCtrlName()
        
##        print 'DESIGNER:', objCol

##        ctrls, props, events = self.organiseCollection()
##        print 'DESGN:', objCol

        self.model.editor.statusBar.progress.SetValue(20)
                
        stepsDone = 20.0

        # Initialise the design time controls and
        # companion with default values
        # initObjectsAndCompanions(creators, props, events) 

        self.companion.setConstr(self.model.mainConstr)
        ctrlCompn = self.companion
        deps = {}
        self.initObjProps(objCol.propertiesByName, '', objCol.creators[0], deps)
##        print 'FRAME_INIT', objCol.eventsByName
        self.initObjEvts(objCol.eventsByName, '', objCol.creators[0])
         
        if len(objCol.creators) > 1:
            step = (90 - stepsDone) / len(objCol.creators)
            self.initObjectsAndCompanions(objCol.creators[1:], objCol, deps)

            stepsDone = stepsDone + step
            self.model.editor.statusBar.progress.SetValue(int(stepsDone))
            
        self.model.editor.statusBar.progress.SetValue(80)
        self.refreshContainment()
        self.model.editor.statusBar.progress.SetValue(0)
        self.model.editor.statusBar.setHint(' ')
        
##        print '$$$$ INIT'
##        for i in self.collEditors.values():
##            print id(i.companion.textConstrLst),
##            print id(self.model.objectCollections[i.companion.collectionMethod].creators)
                
    def initSelection(self):
        self.selection = SelectionGroup(self, self.senderMapper, self.inspector, self)

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

##        self.objects[ctrlName] = [companion, 
##         companion.designTimeControl(None, None, args), parent]
##        self.objectOrder.append(ctrlName)
        
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

##        self.objects[ctrlName] = [companion, companion.designTimeControl(position, size), parentName]
##        self.objectOrder.append(ctrlName)

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
        
        InspectableObjectCollectionView.deleteCtrl(self, name)

        ctrlInfo[1].Destroy()
        
        if parRel is not None:
            self.refreshContainment(parentName)
        
##        print self.model.objectCollections[self.collectionMethod]

    def selectNone(self):
        if self.selection: self.selection.selectNone()
                
    def close(self):
        self.Close()
    
    def OnMouseOver(self, event):
    	if event.Dragging():
     	    pos = event.GetPosition()
     	    ctrl = self.senderMapper.getObject(event)

## Try to determine the client offset of the frame,
##            if ctrl.GetName() == self.GetName():
##                dcs = self.GetPosition()
##            else:
##                dcs = ctrl.GetParent().ClientToScreen(ctrl.GetPosition())
##                
##            dccs = ctrl.ClientToScreen((0, 0))
##            
##            offsetX = dccs.x - dcs.x
##            offsetY = dccs.y - dcs.y
##
##     	    print 'dragOffset:', offsetX, offsetY

	    self.selection.moving(ctrl, pos)
	event.Skip()
	    	      	          
    def OnControlSelect(self, event):
        """ Control is clicked. Either select it or add control from palette """
##        print 'OnControlSelect', event.GetEventObject()
        ctrl = self.senderMapper.getObject(event)

        if ctrl == self:
            companion = self.companion
        else:
            companion = self.objects[ctrl.GetName()][0]
        # Component on palette selected, create it
        if self.compPal.selection:
            # Granularise position
            pos = event.GetPosition()
            pos = wxPoint(granularise(pos.x), granularise(pos.y))
            if companion.container:
                parent = ctrl
            else:
                parent = ctrl.GetParent()
                screenPos = ctrl.ClientToScreen(pos)
                pos = parent.ScreenToClient(screenPos)
                        
            ctrlName = self.newControl(parent, self.compPal.selection[1], self.compPal.selection[2], pos)
            self.compPal.selectNone()
            
            if self.selection:
                ctrl = self.objects[ctrlName][1]
                self.selection.selectCtrl(ctrl, self.objects[ctrlName][0])
        # Select ctrl
        else:
            # Check for child ctrls that don't catch clicks
            if self.selection:
                ctrlName = companion.name
                parRel, parRef = self.buildParentRelationship()
                if ctrl == self:
                    children = parRef['']
                else:
                    children = parRef[ctrlName]
                evtPos = event.GetPosition()    
                for childName in children.keys():
                    childCompn, childCtrl = self.objects[childName][:2]
                    try:
                        pos = childCtrl.GetPosition()
                        sze = childCtrl.GetSize()
                    except:
                        print 'could not get child ctrl size', childCtrl
                    else:
                        if wxIntersectRect((evtPos.x, evtPos.y, 1, 1),
                          (pos.x, pos.y, sze.x, sze.y)) is not None:
                            self.selection.selectCtrl(childCtrl, childCompn)
                            self.selection.moveCapture(childCtrl, childCompn, 
                              wxPoint(evtPos.x - pos.x, evtPos.y - pos.y))
                            print 'intersect select', childCtrl
                            return
                                       
                self.selection.selectCtrl(ctrl, companion)
                self.selection.moveCapture(ctrl, companion, evtPos)
    
    def OnControlRelease(self, event):
        if self.selection:
            self.selection.moveRelease()
        event.Skip()
    
    ignoreWindows = [wxToolBar, wxStatusBar]
    def OnControlResize(self, event):
        try:
            if event.GetId() == self.GetId():
                self.selection.selectCtrl(self, self.companion)

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
        self.selection.selectCtrl(self, self.companion)
        self.inspector.constructorUpdate('Position')
        event.Skip()
        
    def OnCloseWindow(self, event):
        self.destroying = true
        if self.selection:
            self.selection.destroy()
        
        self.selection = None

        self.inspector.cleanup()
        self.inspector.containment.cleanup()
            
        if self.saveOnClose:
            self.saveCtrls()
            self.model.modified = true
            self.model.editor.updateModulePage(self.model)

            self.dataView.saveCtrls()
            
        self.dataView.deleteFromNotebook('Source')
        self.dataView.destroy()
        del self.model.views['Data']

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
        pass
        
        
        
        
   
   