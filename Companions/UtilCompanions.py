#-----------------------------------------------------------------------------
# Name:        UtilCompanions.py
# Purpose:     Companion classes for non visible objects
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.UtilCompanions'
import os, copy

from wxPython.wx import *

import Preferences, Utils

from BaseCompanions import UtilityDTC, CollectionDTC, CollectionIddDTC, wxNullBitmap, NYIDTC
from Constructors import *
from PropEdit.PropertyEditors import IntConstrPropEdit, StrConstrPropEdit, CollectionPropEdit, BitmapConstrPropEdit, EnumConstrPropEdit, LCCEdgeConstrPropEdit, WinEnumConstrPropEdit, BoolConstrPropEdit, MenuEnumConstrPropEdit, BoolPropEdit
from PropEdit import Enumerations
import EventCollections, RTTI, methodparse
import PaletteStore

PaletteStore.paletteLists['Utilities (Data)'] = []
PaletteStore.palette.append(['Utilities (Data)', 'Editor/Tabs/Utilities',
                             PaletteStore.paletteLists['Utilities (Data)']])

class ImageListDTC(ImageListConstr, UtilityDTC):
    #wxDocs = HelpCompanions.wxImageListDocs
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

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Images')
        if nv:
            nv.propEditor.edit(None)

class ImageListImagesCDTC(ImageListImagesConstr, CollectionDTC):
    #wxDocs = HelpCompanions.wxImageListDocs
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

    def designTimeDefaults(self, vals):
        dtd = CollectionDTC.designTimeDefaults(self, vals)

        # resize wxNullBitmap if different size than the imagelist
        ix, iy = self.parentCompanion.control.GetSize(0)
        for param in vals.keys():
            if vals[param] == 'wxNullBitmap' and (\
                  dtd[param].GetWidth() != ix or\
                  dtd[param].GetHeight() != iy):
                newbmp = wxEmptyBitmap(ix, iy)
                mdc = wxMemoryDC()
                mdc.SelectObject(newbmp)
                mdc.DrawBitmap(dtd[param], 0, 0, false)
                mdc.SelectObject(wxNullBitmap)
                dtd[param] = newbmp

        return dtd

    def applyDesignTimeDefaults(self, params):
        dtparams = {}; dtparams.update(params)
        if dtparams['mask'] == 'wxNullBitmap':
            del dtparams['mask']
        CollectionDTC.applyDesignTimeDefaults(self, dtparams)

# This class handles window id magic which should be done by a base class
# UtilityIddDTC or maybe an IddDTCMix for everyone
EventCollections.EventCategories['TimerEvent'] = (EVT_TIMER,)
EventCollections.commandCategories.append('TimerEvent')
class TimerDTC(UtilityDTC):
    handledConstrParams = ('id',)
    #wxDocs = HelpCompanions.wxTimerDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.id = self.getWinId()
    def constructor(self):
        return {'EventHandler': 'evtHandler', 'Id': 'id'}
    def designTimeSource(self):
        return {'evtHandler': 'self', 'id': self.id}
    def designTimeObject(self, args=None):
        return UtilityDTC.designTimeObject(self, self.designTimeDefaults())
    def designTimeDefaults(self):
        return {'evtHandler': self.designer, 'id': wxNewId()}
    def events(self):
        return ['TimerEvent']
    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('TimerEvent', 'EVT_TIMER')
#-------------------------------------------------------------------------------
    def getWinId(self):
        return Utils.windowIdentifier(self.designer.model.main, self.name)
    def SetName(self, oldValue, newValue):
        UtilityDTC.SetName(self, oldValue, newValue)
        self.updateWindowIds()
    def updateWindowIds(self):
        self.id = self.getWinId()
        self.textConstr.params['id'] = self.id
        self.renameEventListIds(self.id)

class AcceleratorTableDTC(ChoicesConstr, NYIDTC):
#class AcceleratorTableDTC(ChoicesConstr, UtilityDTC):
    #wxDocs = HelpCompanions.wxAcceleratorTableDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Entries': CollectionPropEdit})
        self.subCompanions['Entries'] = AcceleratorTableEntriesCDTC

    def designTimeSource(self):
        return {'choices':'[]'}

class AcceleratorTableEntriesCDTC(AcceleratorTableEntriesConstr, CollectionDTC):
    #wxDocs = HelpCompanions.wxIndividualLayoutConstraintDocs
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
        return ['%s%s = []'%(sourceconst.bodyIndent, self.__class__.sourceObjName), '']

    def finaliser(self):
        return ['', '%sreturn %s' %(sourceconst.bodyIndent, self.__class__.sourceObjName)]

    def applyDesignTimeDefaults(self, params):
        return

EventCollections.EventCategories['MenuEvent'] = (EVT_MENU,)
EventCollections.commandCategories.append('MenuEvent')

class MenuDTC(MenuConstr, UtilityDTC):
    #wxDocs = HelpCompanions.wxMenuDocs
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Title': StrConstrPropEdit,
                             'Items': CollectionPropEdit})
        self.subCompanions['Items'] = MenuItemsCIDTC
        self.adtSubCompanions = {'Items': (MenuItemsSepCIDTC, MenuItemsMenuCIDTC)}

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Items':  ('NoneRoute', None, None)})
        return props

    def designTimeSource(self):
        return {'title': `''`}

    def hideDesignTime(self):
        return ['NextHandler', 'PreviousHandler', 'EventHandler', 'Id',
                'Parent', 'InvokingWindow']

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Items')
        if nv:
            nv.propEditor.edit(None)

class MenuItemsConstr(PropertyKeywordConstructor):
    def constructor(self):
        if wxVERSION > (2, 3, 2):
            return {'Label': 'item', 'HelpString': 'helpString',
                    'Kind': 'kind', 'ItemId': 'id'}
        else:
            return {'Label': 'item', 'HelpString': 'helpString',
                    'Checkable': 'checkable', 'ItemId': 'id'}

class MenuItemsSepConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {}

class MenuItemsMenuConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Label': 'item', 'HelpString': 'helpString',
                'Menu': 'aMenu', 'ItemId': 'id'}

class BaseMenuItemsCIDTC(CollectionIddDTC):
    propName = 'Items'
    displayProp = 'item'
    indexProp = '(None)'
    idProp = 'id'
    idPropNameFrom = 'item'
    deletionMethod = 'Remove'
    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionIddDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Label': StrConstrPropEdit,
                             'HelpString': StrConstrPropEdit,
                            })
    def deleteItem(self, idx):
        menuItm = self.control.GetMenuItems()[idx]
        self.control.RemoveItem(menuItm)
        self.deleteItemEvents(idx)
        del self.textConstrLst[idx]

        self.updateWindowIds()

class MenuItemsCIDTC(MenuItemsConstr, BaseMenuItemsCIDTC):
    #wxDocs = HelpCompanions.wxMenuDocs
    propName = 'Items'
    displayProp = 'item'
    indexProp = '(None)'
    insertionMethod = 'Append'
    idProp = 'id'
    idPropNameFrom = 'item'

    def __init__(self, name, designer, parentCompanion, ctrl):
        BaseMenuItemsCIDTC.__init__(self, name, designer, parentCompanion, ctrl)
        if wxVERSION > (2, 3, 2):
            self.editors['Kind'] = EnumConstrPropEdit
            self.names['Kind'] = ['wxITEM_NORMAL', 'wxITEM_CHECK', 'wxITEM_RADIO']
        else:
            self.editors['Checkable'] = BoolConstrPropEdit

    def properties(self):
        props = BaseMenuItemsCIDTC.properties(self)
        #props['Label'] = ('IndexRoute', wxMenu.GetLabel, wxMenu.SetLabel)
        return props

    def applyDesignTimeDefaults(self, params):
        # XXX Overridden only to warn users of API changes
        try:
            BaseMenuItemsCIDTC.applyDesignTimeDefaults(self, params)
        except TypeError, err:
            errStr = "'%s' is an invalid keyword argument for this function"
            if wxVERSION > (2, 3, 2):
                if str(err) == errStr%'checkable':
                    wxLogWarning("For wxPython 2.3.3 replace the 'checkable = false' with 'kind = wxITEM_NORMAL'")
                raise
        except NameError, err:
            _1, name, _2 = string.split(str(err), "'")
            if name in ['wxITEM_NORMAL', 'wxITEM_CHECK', 'wxITEM_RADIO']:
                wxLogWarning("To downgrade your wxPython 2.3.3 code to earlier versions, change 'kind = wxITEM_NORMAL' to 'checkable = false'")
            raise

    def designTimeSource(self, wId):
        newItemName, winId = self.newUnusedItemNames(wId)

        if wxVERSION > (2, 3, 2):
            return {'id': winId,
                    'item': `newItemName`,
                    'helpString': `''`,
                    'kind': 'wxITEM_NORMAL'}
        else:
            return {'id': winId,
                    'item': `newItemName`,
                    'helpString': `''`,
                    'checkable': 'false'}

    def events(self):
        return ['MenuEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('MenuEvent', 'EVT_MENU')


class MenuItemsSepCIDTC(MenuItemsSepConstr, CollectionDTC):
    #wxDocs = HelpCompanions.wxMenuDocs
    propName = 'Items'
    displayProp = 'item'
    indexProp = '(None)'
    insertionMethod = 'AppendSeparator'
    idProp = 'id'
    idPropNameFrom = 'item'

    def properties(self):
        props = CollectionDTC.properties(self)
        del props['ItemId']
        return props

    def designTimeSource(self, wId):
        return {}

    def events(self):
        return []


class MenuItemsMenuCIDTC(MenuItemsMenuConstr, BaseMenuItemsCIDTC):
    #wxDocs = HelpCompanions.wxMenuDocs
    propName = 'Items'
    displayProp = 'item'
    indexProp = '(None)'
    insertionMethod = 'AppendMenu'
    idProp = 'id'
    idPropNameFrom = 'item'

    def __init__(self, name, designer, parentCompanion, ctrl):
        BaseMenuItemsCIDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Menu': BoolConstrPropEdit,
                            })

    def properties(self):
        props = BaseMenuItemsCIDTC.properties(self)
        props['Label'] = ('IndexRoute', wxMenu.GetLabel, wxMenu.SetLabel)
        return props

    def designTimeSource(self, wId):
        newItemName, winId = self.newUnusedItemNames(wId)

        return {'id': winId,
                'item': `newItemName`,
                'helpString': `''`,
                'aMenu': 'None'}

    def events(self):
        return []

    def defaultAction(self):
        # select sub menu obj in data view
        pass
##        insp = self.designer.inspector
##        insp.pages.SetSelection(2)
##        insp.events.doAddEvent('MenuEvent', 'EVT_MENU')

class MenuBarDTC(MenuBarConstr, UtilityDTC):#DesignTimeCompanion):
    #wxDocs = HelpCompanions.wxMenuBarDocs

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
    #wxDocs = HelpCompanions.wxMenuBarDocs
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
                dtd[param] = self.eval(vals[param])

        return dtd

    def vetoedMethods(self):
        return CollectionDTC.vetoedMethods(self)+['GetPosition', 'SetPosition', 'GetSize', 'SetSize']

    def GetMenu(self):
        return self.textConstrLst[self.index].params['menu']

    def SetMenu(self, value):
        self.textConstrLst[self.index].params['menu'] = value

class LayoutConstraintsDTC(EmptyConstr, UtilityDTC):
    #wxDocs = HelpCompanions.wxLayoutConstraintsDocs
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

# XXX Support for Constraints have been dropped
# XXX This class left for educational purposes
class IndividualLayoutConstraintOCDTC(LayoutConstraintsConstr, OwnedCollectionDTC):
    #wxDocs = HelpCompanions.wxIndividualLayoutConstraintDocs
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
        return ['%s%s = wxLayoutConstraints()'%(sourceconst.bodyIndent, 
                self.__class__.sourceObjName), '']

    def finaliser(self):
        return ['', '%sreturn %s' %(sourceconst.bodyIndent, 
                self.__class__.sourceObjName)]

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
            getattr(self.control, self.deletionMethod)(idx)

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
    #wxDocs = HelpCompanions.wxSizerDocs

    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Controls': CollectionPropEdit})
        self.subCompanions['Controls'] = SizerControlsCDTC

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Controls': ('NoneRoute', None, None)})
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
    #wxDocs = HelpCompanions.wxSizerDocs
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

cursorIconTypes = ['wxBITMAP_TYPE_XBM', 'wxBITMAP_TYPE_CUR',
                   'wxBITMAP_TYPE_CUR_RESOURCE', 'wxBITMAP_TYPE_ICO']

class CursorDTC(UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'CursorName': StrConstrPropEdit,
                             'Flags': EnumConstrPropEdit,
                             'HotSpotX': IntConstrPropEdit,
                             'HotSpotY': IntConstrPropEdit,
                             'Visible': BoolPropEdit})
        self.names['Flags'] = cursorIconTypes

    def constructor(self):
        return {'CursorName': 'cursorName', 'Flags': 'flags',
                'HotSpotX': 'hotSpotX', 'HotSpotY': 'hotSpotY'}
    def designTimeSource(self, position='wxDefaultPos', size='wxDefaultSize'):
        return {'cursorName': "''",
                'flags': 'wxBITMAP_TYPE_CUR',
                'hotSpotX': '0',
                'hotSpotY': '0'}

stockCursorIds = ['wxCURSOR_ARROW', 'wxCURSOR_BULLSEYE', 'wxCURSOR_CHAR',
      'wxCURSOR_CROSS', 'wxCURSOR_HAND', 'wxCURSOR_IBEAM', 'wxCURSOR_LEFT_BUTTON',
      'wxCURSOR_MAGNIFIER', 'wxCURSOR_MIDDLE_BUTTON', 'wxCURSOR_NO_ENTRY',
      'wxCURSOR_PAINT_BRUSH', 'wxCURSOR_PENCIL', 'wxCURSOR_POINT_LEFT',
      'wxCURSOR_POINT_RIGHT', 'wxCURSOR_QUESTION_ARROW', 'wxCURSOR_RIGHT_BUTTON',
      'wxCURSOR_SIZENESW', 'wxCURSOR_SIZENS', 'wxCURSOR_SIZENWSE', 'wxCURSOR_SIZEWE',
      'wxCURSOR_SIZING', 'wxCURSOR_SPRAYCAN', 'wxCURSOR_WAIT', 'wxCURSOR_WATCH',
      'wxCURSOR_ARROWWAIT']

class StockCursorDTC(UtilityDTC):
    handledConstrParams = ()
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'CursorId': EnumConstrPropEdit,
                             'Visible': BoolPropEdit})
        self.names['CursorId'] = stockCursorIds

    def hideDesignTime(self):
        return ['Handle']
    def constructor(self):
        return {'CursorId': 'id'}
    def designTimeSource(self, position='wxDefaultPos', size='wxDefaultSize'):
        return {'id': 'wxCURSOR_ARROW'}


PaletteStore.paletteLists['Utilities (Data)'].extend([wxMenuBar, wxMenu, wxImageList,
    wxTimer, wxStockCursor]) #wxCursor, causes problems on wxGTK

PaletteStore.compInfo.update({wxMenuBar: ['wxMenuBar', MenuBarDTC],
    wxImageList: ['wxImageList', ImageListDTC],
    wxAcceleratorTable: ['wxAcceleratorTable', AcceleratorTableDTC],
    wxMenu: ['wxMenu', MenuDTC],
    wxCursor: ['wxCursor', CursorDTC],
    wxStockCursor: ['wxStockCursor', StockCursorDTC],

    # these objects need design time inheritance
    wxTimer: ['wxTimer', TimerDTC],
    wxTextDropTarget: ['wxTextDropTarget', NYIDTC],
    wxFileDropTarget: ['wxFileDropTarget', NYIDTC],
})
