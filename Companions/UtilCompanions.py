#-----------------------------------------------------------------------------
# Name:        UtilCompanions.py
# Purpose:     Companion classes for non visible objects
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 2000, 2001 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
from wxPython.wx import *

from BaseCompanions import UtilityDTC, CollectionDTC, CollectionIddDTC, wxNullBitmap, NYIDTC
from Constructors import *
#ImageListConstr, EmptyConstr, MenuConstr, MenuBarConstr, ImageListImagesConstr, LayoutConstraintsConstr, ChoicesConstr, AcceleratorTableEntriesConstr
from PropEdit.PropertyEditors import IntConstrPropEdit, StrConstrPropEdit, CollectionPropEdit, BitmapConstrPropEdit, EnumConstrPropEdit, LCCEdgeConstrPropEdit, WinEnumConstrPropEdit, BoolConstrPropEdit, MenuEnumConstrPropEdit
import HelpCompanions, methodparse
from PropEdit import Enumerations
import EventCollections, RTTI
import os, copy
import PaletteStore

PaletteStore.paletteLists['Utilities'] = []
PaletteStore.palette.append(['Utilities', 'Editor/Tabs/Utilities',
                             PaletteStore.paletteLists['Utilities']])

class ImageListDTC(ImageListConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxImageListDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Width': IntConstrPropEdit,
                        'Height': IntConstrPropEdit,
                        'Images': CollectionPropEdit})
        self.subCompanions['Images'] = ImageListImagesCDTC

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Images': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self):
        return {'width': '16',
                'height': '16'}
#                  'mask': 'true',
#                  'initialCount': '1'}

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Images')
        if nv:
            nv.propEditor.edit(None)

class ImageListImagesCDTC(ImageListImagesConstr, CollectionDTC):
    wxDocs = HelpCompanions.wxImageListDocs
    propName = 'Images'
    displayProp = 'bitmap'
    indexProp = '(None)'
    insertionMethod = 'Add'
    deletionMethod = 'Remove'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Bitmap': BitmapConstrPropEdit,
                        'Mask': BitmapConstrPropEdit}
        from Views.CollectionEdit import ImageListCollectionEditor
        self.CollEditorFrame = ImageListCollectionEditor

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Bitmap':  ('CompnRoute', None, self.setBitmap),
                      'Mask':    ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, wId):
        return {'bitmap': 'wxNullBitmap',
                'mask':   'wxNullBitmap'}

    def getDisplayProp(self):
        value = self.textConstrLst[self.index].params[self.displayProp]
        if value != 'wxNullBitmap':
            value = os.path.basename(value[10:-21])
        return value

    def setBitmap(self, value):
        if value != wxNullBitmap:
            self.control.Replace(self.index, value)
            self.designer.collEditors[(self.name, self.propName)].refreshCtrl(true)

    def defaultAction(self):
        nv = self.designer.inspector.constr.getNameValue('Bitmap')
        if nv:
            nv.propEditor.edit(None)

# XXX Needs ctrl derivation before it can be implemented
class TimerDTC(EmptyConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxTimerDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
    def designTimeSource(self):
        return {}

class AcceleratorTableDTC(ChoicesConstr, NYIDTC):
#class AcceleratorTableDTC(ChoicesConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxAcceleratorTableDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Entries': CollectionPropEdit})
        self.subCompanions['Entries'] = AcceleratorTableEntriesCDTC

    def designTimeSource(self):
        return {'choices':'[]'}

class AcceleratorTableEntriesCDTC(AcceleratorTableEntriesConstr, CollectionDTC):
    wxDocs = HelpCompanions.wxIndividualLayoutConstraintDocs
    propName = 'Entries'
    displayProp = 'flags'
    indexProp = '(None)'
    insertionMethod = 'append'
    deletionMethod = '(None)'
    sourceObjName = 'list'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)

        self.editors.update({'Flags':   IntConstrPropEdit,
                        'KeyCode': IntConstrPropEdit,
                        'Command': IntConstrPropEdit})

    def persistCollInit(self, method, ctrlName, propName, params = {}):

        collInitParse = methodparse.CollectionInitParse(None, ctrlName, method,
          [], propName)

        self.parentCompanion.textConstr.params = {'choices': collInitParse.asText()}

        self.designer.addCollToObjectCollection(collInitParse)

    def SetName(self, oldName, newName):
        CollectionDTC.SetName(self, oldName, newName)

    def designTimeSource(self, idx):
        return {'flags': '0', 'keyCode': '0', 'cmd': '0'}

    def getDisplayProp(self):
        return `self.textConstrLst[self.index].params.values()`

    def initialiser(self):
        return ['        %s = []'%self.__class__.sourceObjName, '']

    def finaliser(self):
        return ['', '        return %s' %self.__class__.sourceObjName]

    def applyDesignTimeDefaults(self, params):
        return

EventCollections.EventCategories['MenuEvent'] = (EVT_MENU,)
EventCollections.commandCategories.append('MenuEvent')

class MenuDTC(MenuConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxMenuDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Title': StrConstrPropEdit,
                             'Items': CollectionPropEdit})
        self.subCompanions['Items'] = MenuItemsCIDTC

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Items':  ('NoneRoute', None, None)})
        return props

    def designTimeSource(self):
        return {'title': `self.name`}

    def hideDesignTime(self):
        return ['NextHandler', 'PreviousHandler', 'EventHandler', 'Id',
                'Parent', 'InvokingWindow']

    def updateWindowIds(self):
        pass

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Items')
        if nv:
            nv.propEditor.edit(None)

class MenuItemsCIDTC(MenuItemsConstr, CollectionIddDTC):
    wxDocs = HelpCompanions.wxMenuDocs
    propName = 'Items'
    displayProp = 'item'
    indexProp = '(None)'
    insertionMethod = 'Append'
    deletionMethod = 'Remove'
    idProp = 'id'
    idPropNameFrom = 'item'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Label': StrConstrPropEdit,
                             'HelpString': StrConstrPropEdit,
                             'Checkable': BoolConstrPropEdit})

    def properties(self):
        props = CollectionIddDTC.properties(self)
        props.update({'Label':  ('IndexRoute', wxMenu.GetLabel, wxMenu.SetLabel)})
        return props

    def designTimeSource(self, wId):
        newItemName = '%s%d'%(self.propName, wId)
        return {'id': self.newWinId(newItemName),
                'item': `newItemName`,
                'helpString': `newItemName`,
                'checkable': 'false'}

    def deleteItem(self, idx):
        menuId = self.control.GetMenuItems()[idx].GetId()
        self.control.Remove(menuId)

        # remove event references
        self.deleteItemEvents(idx)
##        wIdStr = self.textConstrLst[idx].params['id']
##        for evt in self.textEventList[:]:
##            if evt.windowid == wIdStr:
##                self.textEventList.remove(evt)

        # remove menu reference
        del self.textConstrLst[idx]

        self.updateWindowIds()

    def events(self):
        return ['MenuEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('MenuEvent', 'EVT_MENU')

class MenuBarDTC(MenuBarConstr, UtilityDTC):#DesignTimeCompanion):
    wxDocs = HelpCompanions.wxMenuBarDocs

    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Menus': CollectionPropEdit})
        self.subCompanions['Menus'] = MenuBarMenusCDTC

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Menus':  ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return UtilityDTC.dependentProps(self) + ['Menus']

    def designTimeSource(self, position = 'wxDefaultPos', size = 'wxDefaultSize'):
        return {}

    def initDesignTimeControl(self):
        pass

    def vetoedMethods(self):
        return UtilityDTC.vetoedMethods(self)+['GetPosition', 'SetPosition',
               'GetSize', 'SetSize', 'GetRect', 'SetRect']

    def hideDesignTime(self):
        return []

    def defaultAction(self):
        nv  = self.designer.inspector.props.getNameValue('Menus')
        if nv:
            nv.propEditor.edit(None)

class MenuBarMenusCDTC(MenuBarMenusConstr, CollectionDTC):
    wxDocs = HelpCompanions.wxMenuBarDocs
    propName = 'Menus'
    displayProp = 'title'
    indexProp = '(None)'
    insertionMethod = 'Append'
    deletionMethod = 'Remove'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Menu': MenuEnumConstrPropEdit,
                             'Title': StrConstrPropEdit})

    def designTimeSource(self, wId):
        return {'menu': 'wxMenu()',
                'title': `'%s%d'%(self.propName, wId)`}

    def designTimeDefaults(self, vals):
        dtd = {}
        for param in vals.keys():
            if param == 'menu':
                name = vals[param]
                if name[:4] == 'self':
                    dtd[param] = self.designer.objects[name[5:]][1]
                elif name == 'wxMenu()':
                    dtd[param] = wxMenu()
                else:
                    raise 'Invalid menu reference'
            else:
                try:
                    dtd[param] = eval(vals[param])
                except Exception, message:
                    print 'could not eval 4', vals[param], message

        return dtd

    def vetoedMethods(self):
        return CollectionDTC.vetoedMethods(self)+['GetPosition', 'SetPosition', 'GetSize', 'SetSize']

    def GetMenu(self):
        return self.textConstrLst[self.index].params['menu']

    def SetMenu(self, value):
        self.textConstrLst[self.index].params['menu'] = value

class LayoutConstraintsDTC(EmptyConstr, UtilityDTC):
    wxDocs = HelpCompanions.wxLayoutConstraintsDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Constraints': CollPropEdit})
        self.subCompanions['Constraints'] = IndividualLayoutConstraintCDTC

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Constraints': ('NoneRoute', None, None)})
        return props

class OwnedCollectionDTC(CollectionDTC):
    linkProperty = 'undefined'
    def persistCollInit(self, method, ctrlName, propName, params = {}):
        """ Define a new collection init method for source code, and a
            property initialised by it
        """

        collInitParse = methodparse.CollectionInitParse(None, ctrlName, method,
          [], propName)

        self.parentCompanion.textPropList.append(methodparse.PropertyParse( None,
          self.parentCompanion.name, self.linkProperty,
          [collInitParse.asText()], self.propName))

        self.designer.addCollToObjectCollection(collInitParse)

    def SetName(self, oldName, newName):
        CollectionDTC.SetName(self, oldName, newName)

        collInitParse = methodparse.CollectionInitParse(None, newName,
          self.collectionMethod, [], self.propName)

        for textProp in self.parentCompanion.textPropList:
            if textProp.prop_setter == self.linkProperty:
                textProp.params[0] = collInitParse.asText()


class IndividualLayoutConstraintOCDTC(LayoutConstraintsConstr, OwnedCollectionDTC):
    wxDocs = HelpCompanions.wxIndividualLayoutConstraintDocs
    propName = 'Constraints'
    displayProp = '(None)'
    indexProp = '(None)'
    insertionMethod = 'Set'
    deletionMethod = '(None)'
    sourceObjName = 'item'
    linkProperty = 'SetConstraints'

    def __init__(self, name, designer, parentCompanion, ctrl):
        OwnedCollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
#        self.constraints = wxLayoutConstraints()

        self.editors.update({'Value':        IntConstrPropEdit,
                        'Margin':       IntConstrPropEdit,
                        'OtherEdge':    EnumConstrPropEdit,
                        'Relationship': EnumConstrPropEdit,
                        'Edge':         LCCEdgeConstrPropEdit,
                        'OtherWindow':  WinEnumConstrPropEdit})

        self.names = {'OtherEdge':    Enumerations.constraintEdges,
                      'Relationship': Enumerations.constraintRelationships}
        self.inited = false

    def applyConstraints(self):
        nullConstr = ['wxUnconstrained']
        if self.inited and len(self.textConstrLst) >= 4:
            constraints = wxLayoutConstraints()
            validConstr = 0
            for constrt in self.textConstrLst:
                if constrt.params['rel'] not in nullConstr:
                    validConstr = validConstr + 1

            if validConstr == 4:
                for constrt in self.textConstrLst:
                    params = copy.copy(constrt.params)
                    otherWin = params['otherWin'][5:]
                    if params['otherWin'] == 'None':
                        params = self.designTimeDefaults(params)
                    elif self.designer.objects.has_key(otherWin):
                        del params['otherWin']
                        params = self.designTimeDefaults(params)
                        if otherWin == 'self':
                            params['otherWin'] = self.designer.objects[''][1]
                        else:
                            params['otherWin'] = self.designer.objects[otherWin][1]

                    attr = getattr(constraints,
                      string.split(constrt.comp_name, '.')[1])
                    apply(attr.Set, [], params)

                self.parentCompanion.control.SetConstraints(constraints)

    def designTimeSource(self, wId):
        return {'rel':       'wxUnconstrained',
                'otherWin':  'None',
                'otherEdge': 'wxLeft',
                'value':     '0',
                'margin':    '0'}

    def initialiser(self):
        return ['        %s = wxLayoutConstraints()'%self.__class__.sourceObjName, '']

    def finaliser(self):
        return ['', '        return %s' %self.__class__.sourceObjName]

    def availableItems(self):
        result = ['left', 'right', 'top', 'bottom', 'width', 'height', 'centreX', 'centreY']
        for item in self.textConstrLst:
            try: result.remove(string.split(item.comp_name, '.')[1])
            except: pass
        return result

    def appendItem(self):
        if len(self.textConstrLst) == 4:
            raise 'Only 4 constraints allowed'
        ai = self.availableItems()
        if not ai:
            raise 'All constraints set'

        self.sourceObjName = '%s.%s'%(self.__class__.sourceObjName, ai[0])

        OwnedCollectionDTC.appendItem(self)
        self.applyConstraints()

    def deleteItem(self, idx):
        # remove from ctrl
        if self.deletionMethod != '(None)':
            f = RTTI.getFunction(self.control, self.deletionMethod)
            apply(f, [self.control, idx])

        del self.textConstrLst[idx]
        # renumber items following deleted one
        if self.indexProp != '(None)':
            for constr in self.textConstrLst[idx:]:
                constr.params[self.indexProp] = `int(constr.params[self.indexProp]) -1`

    def applyDesignTimeDefaults(self, params):
        return
        attr = getattr(self.constraints,
          string.split(self.textConstrLst[self.index].comp_name, '.')[1])

        params = copy.copy(params)
        otherWin = params['otherWin'][5:]
        if params['otherWin'] == 'None':
            params = self.designTimeDefaults(params)
        elif self.designer.objects.has_key(otherWin):
            del params['otherWin']
            params = self.designTimeDefaults(params)
            if otherWin == 'self':
                params['otherWin'] = self.designer.objects[''][1]
            else:
                params['otherWin'] = self.designer.objects[otherWin][1]

        apply(attr.Set, [], params)

        self.applyConstraints()

    def getDisplayProp(self):
        return string.split(self.textConstrLst[self.index].comp_name, '.')[1]

#    def SetName(self, oldName, newName):
#        OwnedCollectionDTC.SetName(self, oldName, newName)


    def GetEdge(self):
        return self.textConstrLst[self.index].comp_name

    def SetEdge(self, value):
        self.textConstrLst[self.index].comp_name = value
        self.applyConstraints()

    def GetOtherWin(self):
        return self.textConstrLst[self.index].params['otherWin']

    def SetOtherWin(self, value):
        self.textConstrLst[self.index].params['otherWin'] = value
        self.applyConstraints()

    def initCollection(self):
        self.inited = true
        self.applyConstraints()

class SizerDTC(EmptyConstr, UtilityDTC):#DesignTimeCompanion):
    wxDocs = HelpCompanions.wxSizerDocs

    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Controls': CollectionPropEdit})
        self.subCompanions['Controls'] = SizerControlsCDTC

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Controls':  ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return UtilityDTC.dependentProps(self) + ['Controls']

    def designTimeSource(self, position = 'wxDefaultPos', size = 'wxDefaultSize'):
        return {}

    def initDesignTimeControl(self):
        pass

    def vetoedMethods(self):
        return UtilityDTC.vetoedMethods(self)+['GetPosition', 'SetPosition', 'GetSize', 'SetSize']

    def hideDesignTime(self):
        return []

class BoxSizerDTC(SizerDTC):
    pass

class SizerControlsCDTC(SizerControlsConstr, CollectionDTC):
    wxDocs = HelpCompanions.wxSizerDocs
    propName = 'Controls'
#    displayProp = 'title'
    indexProp = '(None)'
    insertionMethod = 'AddWindow'
    deletionMethod = 'Remove'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Window': WinEnumConstrPropEdit,
                             'Option': IntConstrPropEdit,
                             'Flag':   IntConstrPropEdit,
                             'Border': IntConstrPropEdit})

    def designTimeSource(self, wId):
        return {'window': 'None',
                'option': '0',
                'flag':   '0',
                'border': '0'}

class wxComModule:
    def __init__(self, GUID = '{00000000-0000-0000-0000-000000000000}', LCID = 0x0, Major = 0, Minor = 0):
        self._ComModule = None
        self._GUID = GUID
        self._LCID = LCID
        self._Major = Major
        self._Minor = Minor

    def GetGUID(self):
        return self._GUID
    def SetGUID(self, GUID):
        self._GUID = GUID

    def GetLCID(self):
        return self._LCID
    def SetLCID(self, LCID):
        self._LCID = LCID

    def GetMajor(self):
        return self._Major
    def SetMajor(self, Major):
        self._Major = Major

    def GetMinor(self):
        return self._Minor
    def SetMinor(self, Minor):
        self._Minor = Minor

    def GetComModule(self):
        if self._ComModule:
            return self._ComModule

    def EnsureModule(self):
        self._ComModule = win32com.client.gencache.EnsureModule(self._GUID, self._LCID, self._Major, self._Minor)


class ComModuleDTC(EmptyConstr, UtilityDTC):
    pass

PaletteStore.paletteLists['Utilities'].extend([wxMenuBar, wxMenu, wxImageList])

PaletteStore.compInfo.update({wxMenuBar: ['wxMenuBar', MenuBarDTC],
    wxImageList: ['wxImageList', ImageListDTC],
    wxAcceleratorTable: ['wxAcceleratorTable', AcceleratorTableDTC],
    wxMenu: ['wxMenu', MenuDTC],
    wxTimer: ['wxTimer', TimerDTC],
    wxTextDropTarget: ['wxTextDropTarget', NYIDTC],
    wxFileDropTarget: ['wxFileDropTarget', NYIDTC],
})
