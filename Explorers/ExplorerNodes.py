from os import path
import string, sys, os, time, stat, copy, pprint
import EditorHelper, Utils, Preferences
import scrm
false = 0
true = 1
from wxPython.wx import EVT_MENU, wxMessageBox, wxPlatform, wxMenu

sensitive_properties = ('passwd', 'scp_pass')

# Folderish objects are creators
# Folderish objects are connected to a clipboard and maintain their children

# XXX Active models open in the editors should be returned on list queries

# XXX Add protocol on resourcename level; protocol://resourcename
# XXX Open models should show their protocol in the title bar

# XXX define a filtering interface

# Guidelines
#  Creation of a node should be cheap and not significant resources
#  Opening/getting the contents/sublists should start connections/resources
    
class GlobalClipper:
    def __init__(self):
        self.currentClipboard = None

class ClipboardException(Exception):
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

class DirectPastingNotSupportedClipError(ClipboardException):
    pass

class ExplorerClipboard:
    # XXX Maybe the clipboard should only have to define a convertToCommon
    # XXX and convertToType method.
    # XXX This would add an extra possibly expensive intermediate step
    # XXX but would simplify creation of new clipboards

    # XXX Base class should implement recursive traversal by using explorer intf

    def __init__(self, globClip):
        self.globClip = globClip
        self.clipNodes = []
        self.clipMode = ''
    def clipCut(self, node, nodes):
        self.globClip.currentClipboard = self
        self.clipNodes = nodes
        self.clipMode = 'cut'
    def clipCopy(self, node, nodes):
        self.globClip.currentClipboard = self
        self.clipNodes = nodes
        self.clipMode = 'copy'
    def clipPaste(self, node):
        if self.globClip.currentClipboard:
            methName = 'clipPaste_'+self.globClip.currentClipboard.__class__.__name__
            try:
                clipMeth = eval('self.%s' % methName)
            except AttributeError, message:
                raise Exception('Pasting from %s not supported (%s)'% \
                    (self.globClip.currentClipboard.__class__.__name__, message) )
            else:
                clipMeth(node, self.globClip.currentClipboard.clipNodes,
                    self.globClip.currentClipboard.clipMode)

class Controller:
    def __del__(self):
        pass
#        print '__del__', self.__class__.__name__
    def __init__(self, editor):
        self.editor = editor

    def setupMenu(self, menu, win, menus):
        for wId, help, method, bmp in menus:
            if help != '-':
                if help[0] == '+':
                    canCheck = true
                    help = help[1:]
                else:
                    canCheck = false

                menu.Append(wId, help, checkable = canCheck)
                EVT_MENU(win, wId, method)
                EVT_MENU(self.editor, wId, method)
            else:
                menu.AppendSeparator()

    def destroy(self):
        # break circular references here
        pass

    def groupToggleCheckMenu(self, menu, menuDef, wCheckId):
        checked = not menu.IsChecked(wCheckId)
        self.groupCheckMenu(menu, menuDef, wCheckId, checked)

    def groupCheckMenu(self, menu, menuDef, wCheckId, checked):
        for wId, help, method, bmp in menuDef:
            if wId == wCheckId:
                menu.Check(wId, checked)
            else:
                menu.Check(wId, not checked)

    def getName(self, item):
        if item.name:
            return item.name
        else:
            return item.treename

    def getNamesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.getName(self.list.items[idx]))
        return res

    def getNodesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.list.items[idx])
        return res

(wxID_CLIPCUT, wxID_CLIPCOPY, wxID_CLIPPASTE, wxID_CLIPDELETE, wxID_CLIPRENAME) \
 = Utils.winIdRange(5)

class ClipboardControllerMix:
    cutBmp = 'Images/Shared/Cut.bmp'
    copyBmp = 'Images/Shared/Copy.bmp'
    pasteBmp = 'Images/Shared/Paste.bmp'
    deleteBmp = 'Images/Shared/Delete.bmp'
    def __init__(self):
        self.clipMenuDef = ( (wxID_CLIPCUT, 'Cut', self.OnCutItems, self.cutBmp),
                             (wxID_CLIPCOPY, 'Copy', self.OnCopyItems, self.copyBmp),
                             (wxID_CLIPPASTE, 'Paste', self.OnPasteItems, self.pasteBmp),
                             (-1, '-', None, ''),
                             (wxID_CLIPDELETE, 'Delete', self.OnDeleteItems, self.deleteBmp),
                             (wxID_CLIPRENAME, 'Rename', self.OnRenameItems, '-') )
    def destroy(self):
        self.clipMenuDef = ()

    def OnCutItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            self.list.node.clipCut(nodes)

    def OnCopyItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            self.list.node.clipCopy(nodes)

    def OnPasteItems(self, event):
        if self.list.node:
            self.list.node.clipPaste()
            self.list.refreshCurrent()

    def OnDeleteItems(self, event):
        if self.list.node:
            names = self.getNamesForSelection(self.list.getMultiSelection())
            self.list.node.deleteItems(names)
            self.list.refreshCurrent()

    def OnRenameItems(self, event):
        self.list.EditLabel(self.list.selected)

    def OnOpenItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if not node.isFolderish():
                    node.open(self.editor)


class TransportError(Exception):
    def __str__(self): 
        return str(self.args[0])

class TransportLoadError(TransportError): 
    pass
class TransportSaveError(TransportError): 
    pass   
 

class ExplorerNode:
    protocol = None
    images = None
    viewMode = 'list'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent = None, properties = None):
        self.name = name
        self.resourcepath = resourcepath
        self.imgIdx = imgIdx
        if properties is None: properties = {}
        self.properties = properties
        self.clipboard = clipboard
        self.parent = parent
        self.treename = name
        self.bold = false
        self.vetoRequery = false
        self.upImgIdx = EditorHelper.imgFolderUp
        self.parentOpensChildren = false
    def __del__(self): pass
        #print '__del__', self.__class__.__name__
    def destroy(self):pass
    def createParentNode(self): pass
    def createChildNode(self, value): pass
    def openList(self): pass
    def closeList(self): pass
    def isFolderish(self): return false
    def getTitle(self):
        if self.resourcepath: return self.resourcepath
        else: return self.name
    def getDescription(self):
        return self.getTitle()
    def notifyBeginLabelEdit(self, event):
        pass
#---Default item actions--------------------------------------------------------
    def open(self, editor):
        return editor.openOrGotoModule(self.resourcepath, transport = self)
    def openParent(self, editor): return false

#---Methods on sub items--------------------------------------------------------
    def deleteItems(self, names): pass
    def renameItem(self, name, newName): pass
    def newFolder(self, name): pass

#---Clipboard methods-----------------------------------------------------------
    def clipCut(self, nodes):
        self.clipboard.clipCut(self, nodes)
    def clipCopy(self, nodes):
        self.clipboard.clipCopy(self, nodes)
    def clipPaste(self):
        self.clipboard.clipPaste(self)

    def canAdd(self, paletteName):
        return false

#---Persistance (loading and saving)--------------------------------------------
    def load(self, mode='r'):
        """ Return item data from appropriate transport """
        return None
    def save(self, filename, data, mode='w'):
        """ Persist data on appropriate transport. Should handle renames """
        pass

class CachedNodeMixin:
    """ Only read from datasource when uninitialised or invalidated
        Not used yet
    """
    def __init__(self):
        self.valid = false
        self.cache = None

    def openList(self):
        if self.valid:
            return self.cache
        else:
            # define this method
            self.cache = self.openList_cache()

            self.valid = true
            return self.cache

class ContainerNode(ExplorerNode):
    def __init__(self, name, imgIdx):
        ExplorerNode.__init__(self, name, '', None, imgIdx, None)
        self.entries = []
        self.vetoRequery = true
    def destroy(self): pass
    def isFolderish(self): return true
    def createParentNode(self): return self
    def createChildNode(self, value): return value
    def openList(self): return self.entries
    def getTitle(self): return self.name
    def notifyBeginLabelEdit(self, event):
        event.Veto()

class RootNode(ContainerNode):
    def __init__(self, name):
        ContainerNode.__init__(self, name, EditorHelper.imgBoaLogo)
        
cat_section = 0
cat_option = 1
class CategoryNode(ExplorerNode):
    protocol = 'config'
    defName = 'config'
    defaultStruct = {}
    def __init__(self, name, resourcepath, clipboard, config, parent, imgIdx = EditorHelper.imgFolder):
        ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent)
        self.config = config
        self.bold = true
        self.refresh()

    def destroy(self):
        pass

    def isFolderish(self):
        return true

    def getTitle(self):
        return self.name

    def refresh(self):
        try:
            self.entries = eval(self.config.get(self.resourcepath[cat_section],
                  self.resourcepath[cat_option]))
        except:
            message = sys.exc_info()[1]
            print 'invalid config entry for', \
                  self.resourcepath[cat_option], message
            self.entries = copy.copy(self.defaultStruct)
        else:
            # unscramble sensitive properties
            if type(self.entries) == type({}):
                for item in self.entries.keys():
                    if type(self.entries[item]) == type({}):
                        dict = self.entries[item]
                        for name in dict.keys():
                            if name in sensitive_properties:
                                dict[name] = scrm.scramble(dict[name])[2:]
#                                print 'unscrambled', name, dict[name]
#        print self.entries

    def openList(self):
        res = []
        entries = self.entries.keys()
        entries.sort()
        for entry in entries:
            res.append(self.createChildNode(entry, self.entries[entry]))
        return res

    def deleteItems(self, names):
        for name in names:
            del self.entries[name]
        self.updateConfig()

    def renameItem(self, name, newName):
        if self.entries.has_key(newName):
            raise Exception, 'Name exists'
        self.entries[newName] = self.entries[name]
        del self.entries[name]
        self.updateConfig()

    def newItem(self):
        name = Utils.getValidName(self.entries.keys(), self.defName)
        self.entries[name] = copy.copy(self.defaultStruct)
        self.updateConfig()
        return name

    def updateConfig(self):
        self.config.set(self.resourcepath[cat_section],
                  self.resourcepath[cat_option], pprint.pformat(self.entries))
        self.config.write(open(self.config.confFile, 'w'))

(wxID_CATNEW, wxID_CATINSPECT, wxID_CATDELETE, wxID_CATRENAME) \
 = Utils.winIdRange(4)

class CategoryController(Controller):
    newBmp = 'Images/Shared/NewItem.bmp'
    inspectBmp = 'Images/Shared/Inspector.bmp'
    deleteBmp = 'Images/Shared/Delete.bmp'

    def __init__(self, editor, list, inspector, menuDefs = ()):
        Controller.__init__(self, editor)
        self.list = list
        self.menu = wxMenu()
        self.inspector = inspector

        self.catMenuDef = ( (wxID_CATNEW, 'New', self.OnNewItem, self.newBmp),
                            (wxID_CATINSPECT, 'Inspect', self.OnInspectItem, self.inspectBmp),
                            (-1, '-', None, ''),
                            (wxID_CATDELETE, 'Delete', self.OnDeleteItems, self.deleteBmp),
                            (wxID_CATRENAME, 'Rename', self.OnRenameItem, '-') )

        self.setupMenu(self.menu, self.list, self.catMenuDef + menuDefs)
        self.toolbarMenus = [self.catMenuDef + menuDefs]

    def __del__(self):
        pass#self.menu.Destroy()

    def destroy(self):
        self.catMenuDef = ()
        self.toolbarMenus = ()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            catItem = self.list.getSelection()
            if not catItem: return #zopeItem = self.list.node
            catComp = self.list.node.createCatCompanion(catItem)
            catComp.updateProps()

            # Select in inspector
            if self.inspector.pages.GetSelection() != 1:
                self.inspector.pages.SetSelection(1)
            self.inspector.selectObject(catComp, false)

    def OnNewItem(self, event):
        if self.list.node:
            name = self.list.node.newItem()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            # XXX Also select in inspector
            self.list.EditLabel(self.list.selected)

    def OnDeleteItems(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            names = self.getNamesForSelection(ms)
            self.list.node.deleteItems(names)
            self.list.refreshCurrent()

    def OnRenameItem(self, event):
        self.list.EditLabel(self.list.selected)

from Companions.BaseCompanions import Companion
from PropEdit.PropertyEditors import StrConfPropEdit, EvalConfPropEdit, PasswdStrConfPropEdit
import RTTI
import types

class ExplorerCompanion(Companion):
    def __init__(self, name):
        Companion.__init__(self, name)
        # list of (name, value) tuples
        self.propItems = []
        self.designer = None
        self.control = None
        self.mutualDepProps = ()
    def constructor(self):
        return {}
    def extraConstrProps(self):
        return {}
    def events(self):
        return ()
    def getEvents(self):
        return ()
    def getPropEditor(self, prop):
        return None
    def getPropOptions(self, prop):
        return ()
    def getPropNames(self, prop):
        return ()
    def checkTriggers(self, name, oldValue, value):
        pass
    def persistProp(self, name, setterName, value):
        pass
    def propIsDefault(self, name, setterName):
        return true
    def persistedPropVal(self, name, setterName):
        return ''
    
    def getPropList(self):
        propLst = []
        for prop in self.propItems:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        return {'constructor':[], 'properties': propLst}

    def findProp(self, name):
        for idx in range(len(self.propItems)):
            if self.propItems[idx][0] == name:
                return self.propItems[idx], idx
        else:
            return None, -1

    def GetProp(self, name):
        return self.findProp(name)[0][1]

    def SetProp(self, name, value):
        prop, idx = self.findProp(name)
        if self.setPropHook(name, value, prop):
            self.propItems[idx] = (name, value) + prop[2:]
    
    def GetClass(self, dummy=None):
        return 'Explorer Item'
        
    def SetClass(self, value):
        pass

    def updateProps(self):
        self.propItems = self.getPropertyItems()

    def addProperty(self, name, value, tpe):
        pass

    def delProperty(self, name):
        pass

    def setPropHook(self, name, value, oldProp = None):
        """ Override to do something before a property is set """
        pass

    def getPropertyItems(self):
        """ Override this to read the properties of the object, and return it

            Should return a list of tuples where the first two items are the
            property name and value, the rest of the items may store other
            propery information. """
        return []

class CategoryCompanion(ExplorerCompanion):
    """ Inspectable objects, driven from config files """
    propMapping = {type('') : StrConfPropEdit,
                   'password' : PasswdStrConfPropEdit,
                   'default': EvalConfPropEdit}
    def __init__(self, name, catNode):
        ExplorerCompanion.__init__(self, name)
        self.catNode = catNode

    def getPropEditor(self, prop):
        if prop in sensitive_properties:
            return self.propMapping['password']
        else:
            return self.propMapping.get(type(self.GetProp(prop)), self.propMapping['default'])


class CategoryDictCompanion(CategoryCompanion):
#    scramble = ()
    def getPropertyItems(self):
        return self.catNode.entries[self.name].items()

    def setPropHook(self, name, value, oldProp = None):
        # scramble sensitive properties before saving
        entry = self.catNode.entries[self.name]
        entry[name] = value

        scrams = []
        for entry in self.catNode.entries.values():
            for key in entry.keys():
                if key in sensitive_properties:
                    val = entry[key]
                    entry[key] = scrm.scramble(val)
                    scrams.append((entry, key, val))

        self.catNode.updateConfig()
        # unscramble sensitive properties
        for entry, key, val in scrams:
            entry[key] = val

        return true

class CategoryStringCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return [ ('Item', self.catNode.entries[self.name]) ]

    def setPropHook(self, name, value, oldProp = None):
        self.catNode.entries[self.name] = value
        self.catNode.updateConfig()


class BookmarksCatNode(CategoryNode):
#    protocol = 'config.bookmark'
    defName = 'Bookmark'
    defaultStruct = Preferences.explorerFileSysRootDefault[1]
    def __init__(self, clipboard, config, parent):
        CategoryNode.__init__(self, 'Bookmarks', ('explorer', 'bookmarks'),
              clipboard, config, parent)

    def createChildNode(self, name, value):
        import FileExplorer
        return FileExplorer.PyFileNode(name, value, self.clipboard,
              EditorHelper.imgFolderBookmark, self, self)

    def getDefault(self):
        try:
            return self.entries[self.config.get(self.resourcepath[0],
                  'defaultbookmark')]
        except KeyError:
            return ''

    def add(self, respath):
        name = path.splitext(path.basename(respath))[0]
        if self.entries.has_key(name):
            name = Utils.getValidName(self.entries.keys(), name)
        self.entries[name] = respath
        self.updateConfig()

    def createCatCompanion(self, catNode):
        comp = CategoryStringCompanion(catNode.treename, self)
        return comp


class SysPathNode(ExplorerNode):
    protocol = 'syspath'
    def __init__(self, clipboard, parent, bookmarks):
        ExplorerNode.__init__(self, 'sys.path', '', clipboard,
              EditorHelper.imgFolder, parent)
        self.bookmarks = bookmarks
        self.bold = true
        self.refresh()

    def isFolderish(self):
        return true

    def createChildNode(self, shpth, pth):
        import FileExplorer
        return FileExplorer.PyFileNode(shpth, pth, self.clipboard,
              EditorHelper.imgPathFolder, self, self.bookmarks)

    def refresh(self):
        self.entries = []
        pythonDir = path.dirname(sys.executable)
        for pth in sys.path:
            pth = path.abspath(pth)
            shortPath = pth
            if pth:
                if pth[0:len(pythonDir)] == pythonDir:
                    shortPath = pth[len(pythonDir):]
                    if not shortPath:
                        shortPath = '<Python root>'
                self.entries.append( (shortPath, pth) )

    def openList(self):
        res = []
        for short, entry in self.entries:
            res.append(self.createChildNode(short, entry))
        return res
