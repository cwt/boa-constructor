#-----------------------------------------------------------------------------
# Name:        InspectableViews.py
# Purpose:     View base class for GUI builder designer classes than can be
#              inspected and edited in the object inspector.
#              Currently: frame designer, data view and collection editors
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Views.InspectableViews'

import string, copy, os, pprint

from wxPython.wx import *

import Preferences, Utils

import PaletteMapping, EditorViews
from ObjCollection import ObjectCollection, getCollName

import methodparse, sourceconst


class InspectorSessionMix:
    def doPost(self, inspector):
        pass

    def doCancel(self, inspector):
        pass

    def promptPostOrCancel(self, inspector):
        pass

    # Up is included because it can exit a session
    def doUp(self, inspector):
        pass

class InspectableObjectView(EditorViews.EditorView, InspectorSessionMix):
    """ Base class for Designers

    A designer visually maintains one _init_* method in the source.
    """
    viewName = 'InspectableObject'
    collectionMethod = 'init_'
    collectionParams = 'self'
##    handledProps = []
    supportsParentView = false

    def setupArgs(self, ctrlName, params, dontEval, evalDct):
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
                args[paramKey] = PaletteMapping.evalCtrl(params[paramKey], evalDct)

        return args

    def __init__(self, inspector, model, compPal, actions = (), dclickActionIdx = -1, editorIsWindow = true):
        self.compPal = compPal
        EditorViews.EditorView.__init__(self, model, actions, dclickActionIdx, editorIsWindow)
        self.selection = None
        self.inspector = inspector
        self.controllerView = None
        self.objects = {}
        self.objectOrder = []
        self.collEditors = {}
        self.opened = false

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
        EditorViews.EditorView.destroy(self)

    def doUp(self, inspector):
        self.controllerView.OnSelectParent()

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

    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
        pass

    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):#, definedCtrls):
        collDeps = {}
        for constr in creators:
            self.initObjCreator(constr)
            self.initObjProps(objColl.propertiesByName, constr.comp_name, constr, dependents, depLinks)
            self.initObjColls(objColl.collectionsByName, constr.comp_name, constr, collDeps)
            self.initObjEvts(objColl.eventsByName, constr.comp_name, constr)

            self.applyDepsForCtrl(constr.comp_name, depLinks)

        for ctrlName in collDeps.keys():
            for collInit in collDeps[ctrlName]:
                self.addCollView(ctrlName, collInit.method, false)

    def initObjCreator(self, constrPrs):
        # Assumes all design time ctrls are imported in global scope
        ctrlClass = PaletteMapping.evalCtrl(constrPrs.class_name, self.model.customClasses)
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
                elif len(prop.params) and prop.params[0][:11] == 'self._init_':
                    collItem = methodparse.CollectionInitParse(prop.params[0])
                    self.addCollView(name, collItem.method, false)
                # Check for custom evaluator
                elif comp.customPropEvaluators.has_key(prop.prop_name):
                    args = comp.customPropEvaluators[prop.prop_name](prop.params, self.getAllObjects())
                    # XXX This is a hack !!!
                    # XXX argument list with more than one prop value are
                    # XXX initialised thru the companion instead of the control
                    if prop.prop_name in comp.initPropsThruCompanion:
                        apply(getattr(comp, prop.prop_setter), (args,))
                    else:
                        apply(getattr(ctrl, prop.prop_setter), args)
                # Check for pops which don't update the control
                elif prop.prop_name in comp.onlyPersistProps():
                    continue
                # Normal property, eval value and apply it
                else:
                    try:
                        value = PaletteMapping.evalCtrl(prop.params[0], self.model.specialAttrs)
                    except AttributeError, name:
                        if self.objects.has_key(name):
                            value = self.objects[name][1]
                        else:
                            raise
                    except:
                        print 'Problem with: %s' % prop.asText()
                        raise

                    if prop.prop_name in comp.initPropsThruCompanion:
                        getattr(comp, prop.prop_setter)(value)
                    else:
                        getattr(ctrl, prop.prop_setter)(value)

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

    def initIdOnlyObjEvts(self, events, creators):
        for crt in creators:
            name = crt.comp_name
            if crt.params.has_key('id'):
                wId = crt.params['id']
                for evt in events:
                    if evt.windowid and evt.windowid == wId:
                        self.objects[name][0].setEvents([evt])

    def addCollView(self, name, collInitMethod, create):
        comp, ctrl = self.objects[name][:2]
        collName = getCollName(collInitMethod, name)
        collCompClass = comp.subCompanions[collName]
        # decl collComp -> CollectionDTC
        collComp = collCompClass(name, self, comp, ctrl)
        if create:
            collComp.persistCollInit(collInitMethod, name, collName)

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
            allCtrlsDefined = true#len(refs) > 0
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
                    comp, ctrl = self.objects[prop.comp_name][:2]
                    if len(prop.params) == 1:
                        if ctrlName is None:
                            value = self.companion.eval(prop.params[0])
                        elif ctrlName == '':
                            value = self
                        else:
                            ord, objs = self.model.allObjects()

                            if objs.has_key(ctrlName):
                                value = objs[ctrlName][1]
                            else:
                                continue
                        if prop.prop_name in comp.initPropsThruCompanion:
                            getattr(comp, prop.prop_setter)(value)
                        else:
                            getattr(ctrl, prop.prop_setter)(value)
                    else:
                        refs = []
                        # Build lst of ctrl references from property
                        for param in prop.params:
                            ctrlSrcName = Utils.ctrlNameFromSrcRef(param)
                            if len(param) >= 4 and param[:4] == 'self' and \
                                  self.objects.has_key(ctrlSrcName):
                                refs.append(self.objects[ctrlSrcName][1])
                            else:
                                refs.append(self.companion.eval(param))

                        apply(getattr(ctrl, prop.prop_setter), refs)

            del depLinks[ctrlName]

    def addDepLink(self, prop, name, dependents, depLinks):
        refs = self.getRefsFromProp(prop)
        # Handle the case where ref is not a designer obj but a constant
        # all such constansts will be grouped under 'None'
        if not refs:
            if not depLinks.has_key(None):
                depLinks[None] = []
            depLinks[None].append( (prop, ()) )
        else:
            for link in refs:
                if not depLinks.has_key(link):
                    depLinks[link] = []
                otherRefs = refs[:]
                otherRefs.remove(link)
                depLinks[link].append( (prop, otherRefs) )

    def finaliseDepLinks(self, depLinks):
        for ctrlName in depLinks.keys():
            self.applyDepsForCtrl(ctrlName, depLinks)

    def renameEventMeth(self, oldName, newName):
        pass

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


    def renameFrame(self, oldName, newName):
        # update windowids & ctrls
        for comp, ctrl, dummy in self.objects.values():
            if not comp.suppressWindowId:
                comp.updateWindowIds()

    def saveCtrls(self, definedCtrls, module=None):
        """ Replace current source of method in collectionMethod with values from
            constructors, properties and events.
        """

        newBody = []
        deps = {}
        depLinks = {}
        collDeps = []
        imports = []

        if not module:
            module = self.model.getModule()

        for collView in self.collEditors.values():
            collView.saveCtrls(module)

        # XXX Move toolbar up to the 1st position after the frame

        for ctrlName in self.objectOrder:
            definedCtrls.append(ctrlName)
            compn = self.objects[ctrlName][0]

            compn.writeConstructor(newBody, self.collectionMethod)
            compn.writeProperties(newBody, ctrlName, definedCtrls, deps, depLinks)
            compn.writeCollections(newBody, collDeps)
            compn.writeEvents(newBody, module=module)

            compn.writeDependencies(newBody, ctrlName, depLinks, definedCtrls)

            imp = compn.writeImports()
            if imp and imp not in imports:
                imports.append(imp)

            if Preferences.cgEmptyLineBetweenObjects:
                newBody.append('')

        if not newBody or newBody[-1]:
            newBody.append('')

        if collDeps:
            newBody.extend(collDeps + [''])

        for imp in imports:
            module.addImportStatement(imp)

        emptyCodeBlock = newBody == ['']

        if Preferences.cgAddInitMethodWarning:
            newBody.insert(0, '%s# %s'%(sourceconst.bodyIndent, 
                                        sourceconst.code_gen_warning))

        if module.classes[self.model.main].methods.has_key(\
          self.collectionMethod):
            # Add doc string
            docs = module.getClassMethDoc(self.model.main,
              self.collectionMethod)
            if (len(docs) > 0) and docs[0]:
                newBody.insert(0, '%s""" %s """'%(sourceconst.bodyIndent, docs))
                emptyCodeBlock = false

            if emptyCodeBlock:
                newBody[-1:-1] = [sourceconst.bodyIndent+'pass']

            module.replaceMethodBody(self.model.main,
                  self.collectionMethod, newBody)
        else:
            if not emptyCodeBlock:
                module.addMethod(self.model.main,
                  self.collectionMethod, self.collectionParams, newBody, 0)

    def copyCtrls(self, selCtrls, definedCtrls, output):
        """ Write out current source of selection to a text line list.
        """

        ctrlsAndContainedCtrls = self.expandNamesToContainers(selCtrls)
        deps = {}
        depLinks = {}
        collDeps = []

        collMeths = []
        for compName, collProp in self.collEditors.keys():
            if compName in ctrlsAndContainedCtrls:
                collView = self.collEditors[(compName, collProp)]
                collMeth = []
                collView.copyCtrls(collMeth)
                collMeths.append(collMeth)

        output.insert(0, '%sdef %s(%s):'% (sourceconst.methodIndent, 
              self.collectionMethod, self.collectionParams))
        for ctrlName in ctrlsAndContainedCtrls:
            definedCtrls.append(ctrlName)
            compn = self.objects[ctrlName][0]

            compn.updatePosAndSize()

            frmName = self.model.main
            compn.writeConstructor(output, self.collectionMethod, stripFrmId=frmName)
            compn.writeProperties(output, ctrlName, definedCtrls, deps, depLinks, stripFrmId=frmName)
            compn.writeCollections(output, collDeps, stripFrmId=frmName)
            compn.writeEvents(output, stripFrmId=frmName)

            compn.writeDependencies(output, ctrlName, depLinks, definedCtrls, stripFrmId=frmName)

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
            elif line[:5] == '\tdef ':
                meth = line[5:string.find(line, '(', 6)]
                currMeth = [meth]
                methList.append(currMeth)
            else:
                try:
                    currMeth.append(line)
                except NameError:
                    print 'PASTE ERROR', input
        if not methList:
            raise 'Nothing to paste'

        collObjColls = []
        pastedCtrls = []
        collMethod = ''
        # find main method
        idx = -1
        for meth in methList[:]:
            idx = idx + 1
            if meth[0] == self.collectionMethod:
                collMethod = meth[0]
                methBody = meth[1:]
            else:
                # XXX not good :(
                ctrlName = methodparse.ctrlNameFromMeth(meth[0])
                newObjColl = self.model.readDesignerMethod(meth[0], meth[1:])
                methodparse.decorateParseItems(
                      newObjColl.creators + newObjColl.events,
                      ctrlName, self.model.main)

                for plp in newObjColl.creators + newObjColl.events + \
                      newObjColl.properties + newObjColl.collections:
                    plp.prependFrameWinId(self.model.main)

                collObjColls.append( (meth[0], ctrlName, newObjColl) )

        if not collMethod:
            raise 'Method % not found' % self.collectionMethod

        # Parse input source
        objCol = self.model.readDesignerMethod(collMethod, methBody)

        if not len(objCol.creators):
            return []

        # Fixup window ids
        for plp in objCol.creators + objCol.events + objCol.properties + \
              objCol.collections:
            plp.prependFrameWinId(self.model.main)

        # Rename possible name clashes
        objCol.indexOnCtrlName()
        pasteNameClasses = objCol.getCtrlNames()
        newNames = []
        oldNames = []
        # Preserve order, but determine all new names before creating objs
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
                if self.collEditors[(ctrlName, propName)].frame:
                    self.collEditors[(ctrlName, propName)].frame.Close()
                del self.collEditors[(ctrlName, propName)]

    def cleanup(self):
        if self == self.inspector.prevDesigner[0]:
            self.inspector.prevDesigner = (None, None)

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
                  isinstance(self.objects[objName][1], theClass):
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
              'This component must be created in the '+ctrlCompanion.host+' view',
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

    def showCreationOrderDlg(self, selName):
        sibs = []
        allNames = []
        idx = -1
        for objName in self.objectOrder:
            idx = idx + 1
            ctrl, parent = self.objects[objName][1:3]
            if parent == selName:
                sibs.append( (idx, objName) )
                allNames.append(objName)

        allNames = self.expandNamesToContainers(allNames)
        allSibs = []
        for name in allNames:
            allSibs.append( (self.objectOrder.index(name), name) )

        from CreationOrdDlg import CreationOrderDlg
        dlg = CreationOrderDlg(self, sibs, allSibs)
        if dlg.ShowModal() == wxID_OK:
            for idx, name in map(None, dlg.allCtrlIdxs, dlg.allCtrlNames):
                self.objectOrder[idx] = name


import CollectionEdit
