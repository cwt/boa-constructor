#-----------------------------------------------------------------------------
# Name:        DAVExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001/06/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001
# Licence:     GPL
#-----------------------------------------------------------------------------

import string, os, sys
from xml.parsers import expat

from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform, wxOK, wxNewId

#sys.path.append('..')
import ExplorerNodes, EditorModels, EditorHelper
from ExternalLib.WebDAV import client

# XXX Filenames with spaces (broken)
# XXX Zope properties may contain invalid XML content strings (should be encoded)

true = 1
false = 0

class XMLListBuilder:
    def __init__(self, data):
        self.lists = []
        self.nodeStack = [self.lists]

        # Parse XML
        parser = expat.ParserCreate()

        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characterData

        self.status = parser.Parse(data, 1)

        #import pprint
        #pprint.pprint(self.lists)

    def startElement(self, name, attrs):
        name = name.encode()
        id = []
        self.nodeStack[-1].append( (name, id) )
        self.nodeStack.append(id)

    def endElement(self, name):
        self.nodeStack = self.nodeStack[:-1]

    def characterData(self, data):
        if string.strip(data):
            data = data.encode()
            self.nodeStack[-1].append(data)

#---Explorer classes------------------------------------------------------------

wxID_DAVOPEN = wxNewId()
wxID_DAVINSPECT = wxNewId()

class DAVController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()
        self.inspector = inspector

        self.setupMenu(self.menu, self.list,
              ( (wxID_DAVOPEN, 'Open', self.OnOpenItems, '-'),
                (wxID_DAVINSPECT, 'Inspect', self.OnInspectItem, '-'),
                (-1, '-', None, '') ) + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            davItem = self.list.getSelection()
            davComp = DAVCompanion(davItem.name, davItem)
##            if not catItem: return #zopeItem = self.list.node
##            catComp = self.list.node.createCatCompanion(catItem)
            davComp.updateProps()

            # Select in inspector
            self.inspector.Raise()
            if self.inspector.pages.GetSelection() != 1:
                self.inspector.pages.SetSelection(1)
            self.inspector.selectObject(davComp, false)


class DAVCatNode(ExplorerNodes.CategoryNode):
    defName = 'DAV'
    defaultStruct = {'username': '',
                     'passwd': '',
                     'host': 'localhost',
                     'port': '80',
                     'path': ''}
    def __init__(self, clipboard, config, parent):
        ExplorerNodes.CategoryNode.__init__(self, 'DAV', ('explorer', 'dav'),
              clipboard, config, parent)

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        return DAVItemNode(name, props, props['path'], self.clipboard, true,
              EditorHelper.imgFSDrive, self)

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp

class DAVItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'dav'
    def __init__(self, name, props, resourcepath, clipboard, isFolder, imgIdx, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent, props)
        self.isFolder = isFolder
        self.resource = client.Resource(('http://%(host)s:%(port)s/'+\
              resourcepath) % props, props['username'], props['passwd'])

    def isFolderish(self):
        return self.isFolder

    def createChildNode(self, name, isFolder, props):
        item = DAVItemNode(os.path.basename(name), props, name, self.clipboard,
              isFolder, isFolder and EditorHelper.imgFolder or \
              EditorHelper.imgTextModel, self)
        if not isFolder:
            item.imgIdx = \
                  EditorModels.identifyFile(name, localfs=false)[0].imgIdx
        return item

    def openList(self):
        res = []
        resp = self.resource.propfind('', 1)
        l = XMLListBuilder(resp.body).lists

        responses = l[0][1]
        if len(responses) > 0:
            for resp in l[0][1][1:]:
                assert string.strip(resp[1][0][0]) == 'd:href',\
                      'Unexpected xml format'
                name = string.strip(resp[1][0][1][0])
                if len(name) > 1:
                    name = name[1:]
                    if name[-1] == '/':
                        name = name[:-1]
                        isFolder = true
                    else:
                        isFolder = false
                    res.append(self.createChildNode(name, isFolder,
                          self.properties))
        return res

    def copyFromFS(self, fsNode, fn=''):
        if not fn:
            fn = os.path.basename(fsNode.resourcepath)
        if fsNode.isFolderish():
            self.newFolder(fn)
        else:
            newNode = self.createChildNode(self.resourcepath+'/'+fn, 0, self.properties)
            newNode.resource.put(fsNode.load())

    def copyToFS(self, fsFolderNode, fn=''):
        if not fn:
            fn = os.path.basename(self.resourcepath)
        if self.isFolderish():
            fsFolderNode.newFolder(fn)
        else:
            open(os.path.join(fsFolderNode.resourcepath, fn), 'wb').write(self.load())

    def moveFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        other.resource.move(self.resourcepath + '/' + fn)

    def copyFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        other.resource.copy(self.resourcepath + '/' + fn)

    def deleteItems(self, names):
        absNames = []
        for name in names:
            self.createChildNode(self.resourcepath+'/'+name,
                0, self.properties).resource.delete()

    def renameItem(self, name, newName):
        self.createChildNode(self.resourcepath+'/'+name,
            0, self.properties).resource.move(self.resourcepath+'/'+newName)

    def load(self, mode='rb'):
        try:
            return self.resource.get().body
        # XXX Catch only loading errors
        except Exception, error:
            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb'):
        try:
            self.resource.put(data)
        # XXX Catch only saving errors
        # XXX Invalid dtml does not raise an exception. WebDAV.client problem
        except Exception, error:
            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)

    def newFolder(self, name):
        self.createChildNode(self.resourcepath+'/'+name,
            1, self.properties).resource.mkcol()

class DAVExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)

    def clipPaste_DAVExpClipboard(self, node, nodes, mode):
        for davNode in nodes:
            if mode == 'cut':
                node.moveFileFrom(davNode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(davNode)

#---Companion classes-----------------------------------------------------------

from Companions.BaseCompanions import HelperDTC
from ExplorerNodes import ExplorerCompanion
from PropEdit import PropertyEditors
#import RTTI
import types

class DAVContConfPropEdit(PropertyEditors.ContainerConfPropEdit):
    def getSubCompanion(self):
        return DAVSubCompanion

class DAVPropReaderMixin:
    propMapping = {type(()) : DAVContConfPropEdit,
                   type([]) : DAVContConfPropEdit,
                   type('') : PropertyEditors.StrConfPropEdit,
                   'password' : PropertyEditors.PasswdStrConfPropEdit,
                   'default': PropertyEditors.EvalConfPropEdit}
    def getPropEditor(self, prop):
        return self.propMapping.get(type(self.GetProp(prop)),
              self.propMapping['default'])

    def buildItems(self, items, propList):
        for name, value in propList:
            if not value: value = ''
            elif types.StringType is type(value[0]):
                value = value[0]

            items.append( (string.split(name, ':')[1], value) )
        return items

class DAVCompanion(DAVPropReaderMixin, ExplorerCompanion):
    def __init__(self, name, davNode):
        ExplorerCompanion.__init__(self, name)
        self.davNode = davNode

    def getPropertyItems(self):
        l = XMLListBuilder(self.davNode.resource.getprops().body).lists

        items = []
        props = l[0][1][0][1]
        if len(props) > 1:
            for propSet in props[1:]:
                items = self.buildItems(items, propSet[1][0][1])
        return items

    def SetProp(self, name, value):
        raise 'Property editing not supported yet'

# XXX Helper is already slightly contaminated by the Designer
class DAVSubCompanion(DAVPropReaderMixin, HelperDTC):
    def __init__(self, name, designer, ownerCompanion, obj, ownerPropWrap):
        HelperDTC.__init__(self, name, designer, ownerCompanion, obj,
              ownerPropWrap)
        self.propItems = []

    def getPropList(self):
        propLst = []
        if type(self.obj) is types.ListType:
            props = self.obj
        else:
            props = [self.obj]
        subProps = self.buildItems([], props)
        for prop in subProps:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        self.propItems = subProps
        return {'constructor': [], 'properties': propLst}

    def GetProp(self, name):
        for prop in self.propItems:
            if prop[0] == name: return prop[1]

    def SetProp(self, name, value):
        raise 'Property editing not supported yet'
##        print 'SetProp', name, value
##        return
##        for idx in range(len(self.propItems)):
##            if self.propItems[idx][0] == name:
##                self.propItems[idx] = (name, value)
##                break
