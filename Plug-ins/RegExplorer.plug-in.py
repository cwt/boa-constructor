#-----------------------------------------------------------------------------
# Name:        RegExplorer.py
# Purpose:     Classes for exploring the windows registry
#
# Author:      Riaan Booysen
#
# Created:     2001/06/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.RegExplorer'

import string, os, sys

import wx

import Preferences, Utils, Plugins

from Explorers import ExplorerNodes
from Models import EditorModels, EditorHelper
import RTTI

try:
    import _winreg
except ImportError:
    raise Plugins.SkipPluginSilently, 'Requires windows'

#---Explorer classes------------------------------------------------------------

wxID_REGOPEN, wxID_REGINSPECT = Utils.wxNewIds(2)

class RegController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wx.Menu()
        self.inspector = inspector

        self.setupMenu(self.menu, self.list,
              [ (wxID_REGOPEN, 'Open', self.OnOpenItems, '-'),
                (wxID_REGINSPECT, 'Inspect', self.OnInspectItem, '-'),
                (-1, '-', None, '') ] + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            regItem = self.list.getSelection()
            regComp = RegCompanion(regItem.name, regItem)
            regComp.updateProps()

            # Select in inspector
            self.inspector.restore()
            if self.inspector.pages.GetSelection() != 1:
                self.inspector.pages.SetSelection(1)
            self.inspector.selectObject(regComp, False)


class RegCatNode(ExplorerNodes.CategoryNode):
    itemProtocol = 'reg'
    defName = 'Registry'
    defaultStruct = {'path': 'HKEY_LOCAL_MACHINE',
                     'computername': ''}
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'Registry', ('explorer', 'reg'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        itm = RegItemNode(name, props, props['path'], self.clipboard,
              EditorHelper.imgFolder, self)
        itm.category = name
        itm.bookmarks = self.bookmarks
        return itm

##    def createCatCompanion(self, catNode):
##        comp = DAVCatDictCompanion(catNode.treename, self)
##        return comp

##class DAVCatDictCompanion(ExplorerNodes.CategoryDictCompanion):
##    """ Prop validator for 'path' prop """
##    def setPropHook(self, name, value, oldProp = None):
##        ExplorerNodes.CategoryDictCompanion.setPropHook(self, name, value, oldProp)
##        if name == 'path' and value and value != '/':
##            if value[-1] != '/': raise Exception('DAV paths must end in "/"')
##            if value[0] == '/': raise Exception('DAV paths shouldn\'t start with "/"')

class RegItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'reg'
    connection = False
    def __init__(self, name, props, resourcepath, clipboard, imgIdx, parent):
        if not resourcepath:
            resourcepath = '/'
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent, props)

        self.hkey = None
        #self.initResource()

##    def initResource(self):
##        props = self.properties
##        self.resource = client.Resource(('http://%(host)s:%(port)s/'%props)+\
##              self.resourcepath, props['username'], props['passwd'])

    def initHkey(self):
        key, subkey = string.split(self.resourcepath, '\\', 1)
        key =_winreg.__dict__[key]
        if self.properties['computername']:
            compName = self.properties['computername']
        else:
            compName = None

        #hdl = _winreg.ConnectRegistry(compName, )
        self.hkey = _winreg.CreateKey(key, subkey)


    def getURI(self):
        return '%s://%s' % (self.protocol, self.resourcepath)

    def isFolderish(self):
        return True

    def createChildNode(self, name, props):
        newname = os.path.join(self.resourcepath, name)
        #isFolder = tpe == 'key'
        item = RegItemNode(name, props, newname, self.clipboard,
              EditorHelper.imgFolder, self)
        item.category = self.category
        item.bookmarks = self.bookmarks
        return item

    def enumReg(self, func, key):
        idx = 0
        res = []
        #vals = []
        #for res, func in ((keys, _winreg.EnumKey), (vals, _winreg.EnumValue)):
        while 1:
            try: res.append(func(key, idx))
            except EnvironmentError: break
            else: idx = idx + 1
        return res

    def openList(self):
        self.initHkey()

        idx = 0
        res = []
        for skey in self.enumReg(_winreg.EnumKey, self.hkey):
            res.append(self.createChildNode(skey, self.properties))

        return res

    def deleteItems(self, names):
        absNames = []
##        for name in names:
##            self.checkResp(self.createChildNode(self.resourcepath+name,
##                  self.properties).resource.delete())

    def renameItem(self, name, newName):
        pass
##        self.checkResp(self.createChildNode(self.resourcepath+name,
##            self.properties).resource.move(self.resourcepath+newName))

    def load(self, mode='rb'):
        return ''
##        try:
##            return self.checkResp(self.resource.get()).body
##        except Exception, error:
##            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb'):
        pass
##        if filename != self.resourcepath:
##            self.name = os.path.basename(filename)
##            self.resourcepath = filename
##            self.initResource()
##        try:
##            self.checkResp(self.resource.put(data))
##        except Exception, error:
##            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)

    def newFolder(self, name):
        # add key
        pass

##        self.checkResp(self.createChildNode(self.resourcepath+name+'/',
##              self.properties).resource.mkcol())

    def newBlankDocument(self, name):
        # add blank string
        pass
##        self.checkResp(self.createChildNode(self.resourcepath+name,
##              self.properties).resource.put(' '))

    def getNodeFromPath(self, respath):
        return self.createChildNode(respath, self.properties)

##    def checkResp(self, resp):
##        assert resp.code < 300, '%s %d %s' %(resp.version, resp.code, resp.msg)
##        return resp


class RegExpClipboard(ExplorerNodes.ExplorerClipboard):
    pass
##    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
##        for clipnode in nodes:
##            if mode == 'cut':
##                node.copyFromFS(clipnode)
##                self.clipNodes = []
##            elif mode == 'copy':
##                node.copyFromFS(clipnode)
##
##    def clipPaste_DAVExpClipboard(self, node, nodes, mode):
##        for davNode in nodes:
##            if mode == 'cut':
##                node.moveFileFrom(davNode)
##                self.clipNodes = []
##            elif mode == 'copy':
##                node.copyFileFrom(davNode)

#---Companion classes-----------------------------------------------------------

from Companions.BaseCompanions import HelperDTC
from PropEdit import PropertyEditors
import RTTI
import types

class RegPropReaderMixin:
    propMapping = {'default': PropertyEditors.EvalConfPropEdit}
    def getPropEditor(self, prop):
        return self.propMapping.get(type(self.GetProp(prop)),
              self.propMapping['default'])

    def buildItems(self, items, propList):
        #print propList
        for name, value in propList:
            if not value: value = ''
            elif types.StringType is type(value[0]):
                value = value[0]

            items.append( (string.split(name, ':')[1], value) )
        return items

class RegCompanion(RegPropReaderMixin, ExplorerNodes.ExplorerCompanion):
    def __init__(self, name, regNode):
        ExplorerNodes.ExplorerCompanion.__init__(self, name)
        self.regNode = regNode

    def getPropertyItems(self):
        res = []
        self.regNode.initHkey()
        for name, val, tpe in self.regNode.enumReg(_winreg.EnumValue, self.regNode.hkey):
            res.append( (name, val) )
        return res

    def SetProp(self, name, value):
        raise 'Property editing not supported yet'

### XXX Helper is already slightly contaminated by the Designer
##class SubCompanion(DAVPropReaderMixin, HelperDTC):
##    def __init__(self, name, designer, ownerCompanion, obj, ownerPropWrap):
##        HelperDTC.__init__(self, name, designer, ownerCompanion, obj,
##              ownerPropWrap)
##        self.propItems = []
##
##    def getPropList(self):
##        propLst = []
##        if type(self.obj) is types.ListType:
##            props = self.obj
##        else:
##            props = [self.obj]
##        subProps = self.buildItems([], props)
##        for prop in subProps:
##            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
##                  self.GetProp, self.SetProp))
##        self.propItems = subProps
##        return {'constructor': [], 'properties': propLst}
##
##    def GetProp(self, name):
##        for prop in self.propItems:
##            if prop[0] == name: return prop[1]
##
##    def SetProp(self, name, value):
##        raise 'Property editing not supported yet'

#-------------------------------------------------------------------------------
ExplorerNodes.register(RegItemNode, clipboard=RegExpClipboard,
      confdef=('explorer', 'reg'), controller=RegController, category=RegCatNode)
