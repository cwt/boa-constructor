from os import path
import string, sys, os, time, stat, copy, pprint
import EditorModels, Utils, Preferences
false = 0
true = 1
from wxPython.wx import EVT_MENU, wxMessageBox, wxPlatform, wxMenu

# Folderish objects are creators
# Folderish objects are connected to a clipboard and maintain their children

class GlobalClipper:
    def __init__(self):
        self.currentClipboard = None

class ExplorerClipboard:
    # XXX Maybe the clipboard should only have to define a convertToCommon
    # XXX and convertToType method.
    # XXX This would add an extra possibly expensive intermediate step
    # XXX but would simplify creation of new clipboards
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
                exec 'self.%s(node, self.globClip.currentClipboard.clipNodes, self.globClip.currentClipboard.clipMode)' % methName
            except AttributeError:
                raise Exception('Pasting from %s not supported'% self.globClip.currentClipboard.__class__.__name__)

class Controller:
#    def __del__(self):
#        print '__del__', self.__class__.__name__
        
    def setupMenu(self, menu, win, menus):
        for wId, help, method in menus:
            if help != '-':
                menu.Append(wId, help)
                EVT_MENU(win, wId, method)
            else:
                menu.AppendSeparator()

    def getName(self, item):
        if item.name:
            return item.name
        else:
            return item.treename

    def getNamesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.getName(self.list.items[idx]))
        print res
        return res

    def getNodesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.list.items[idx])
        return res

(wxID_CLIPCUT, wxID_CLIPCOPY, wxID_CLIPPASTE, wxID_CLIPDELETE, wxID_CLIPRENAME) \
 = Utils.winIdRange(5)

class ClipboardControllerMix:
    def __init__(self):
        self.clipMenuDef = ( (wxID_CLIPCUT, 'Cut', self.OnCutItems),
                             (wxID_CLIPCOPY, 'Copy', self.OnCopyItems),
                             (wxID_CLIPPASTE, 'Paste', self.OnPasteItems),
                             (-1, '-', None),
                             (wxID_CLIPDELETE, 'Delete', self.OnDeleteItems),
                             (wxID_CLIPRENAME, 'Rename', self.OnRenameItems) )
                         
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
                        
class ExplorerNode:
    protocol = None
    images = None
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
        self.upImgIdx = EditorModels.imgFolderUp
                
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

#---Default item actions--------------------------------------------------------
    def open(self, editor): pass
    def openParent(self, editor): return false
    
#---Methods on sub items--------------------------------------------------------
    def deleteItems(self, names): pass
    def renameItem(self, name, newName): pass

#---Clipboard methods-----------------------------------------------------------
    def clipCut(self, nodes):
        self.clipboard.clipCut(self, nodes)
    def clipCopy(self, nodes):
        self.clipboard.clipCopy(self, nodes)
    def clipPaste(self):
        self.clipboard.clipPaste(self)
    
    def canAdd(self, paletteName):
        return false

class RootNode(ExplorerNode):
    def __init__(self, name):
        ExplorerNode.__init__(self, name, '', None, EditorModels.imgBoaLogo, None)
        self.entries = []
        self.vetoRequery = true
    def isFolderish(self): return true
    def createChildNode(self, value): return value    
    def openList(self): return self.entries
    def getTitle(self): return 'Boa Constructor'
    
cat_section = 0
cat_option = 1
class CategoryNode(ExplorerNode):
    protocol = 'config'
    defName = 'config'
    defaultStruct = {}
    def __init__(self, name, resourcepath, clipboard, config, parent, imgIdx = EditorModels.FolderModel.imgIdx):
        ExplorerNode.__init__(self, name, resourcepath, clipboard, 
              imgIdx, parent)
        self.config = config
        self.bold = true
        self.refresh()
    
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
    def __init__(self, list, inspector):
        self.list = list
        self.menu = wxMenu()
        self.inspector = inspector

        self.catMenuDef = ( (wxID_CATNEW, 'New', self.OnNewItem),
                            (wxID_CATINSPECT, 'Inspect', self.OnInspectItem),
                            (-1, '-', None),
                            (wxID_CATDELETE, 'Delete', self.OnDeleteItems),
                            (wxID_CATRENAME, 'Rename', self.OnRenameItem) )

        self.setupMenu(self.menu, self.list, self.catMenuDef)
    
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
            print ms
            names = self.getNamesForSelection(ms)
            self.list.node.deleteItems(names)
            self.list.refreshCurrent()
    
    def OnRenameItem(self, event):
        self.list.EditLabel(self.list.selected)

from Companions.BaseCompanions import Companion
from PropEdit.PropertyEditors import StrConfPropEdit, EvalConfPropEdit
import RTTI
import types

# XXX Refactor this and ZopeCompanion
class CategoryCompanion(Companion):
    propMapping = {type('') : StrConfPropEdit,
                   'default': EvalConfPropEdit}
    def __init__(self, name, catNode):
        Companion.__init__(self, name)
        self.catNode = catNode
        self.propItems = []
        self.designer = None
        self.control = None

    def constructor(self):
        return {}
    def events(self):
        return []
    def getEvents(self):
        return []
    def getPropEditor(self, prop):
        return self.propMapping.get(type(self.GetProp(prop)), self.propMapping['default'])
#        return StrConfPropEdit
    def getPropOptions(self, prop):
        return []
    def getPropNames(self, prop):
        return []
    def checkTriggers(self, name, oldValue, value):
        pass
    def persistProp(self, name, setterName, value):
        pass

    def updateProps(self):
        self.propItems = self.getPropertyItems()
        
    def getPropList(self):
        propLst = []
        for prop in self.propItems:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute', 
                  self.GetProp, self.SetProp))
        return {'constructor':[], 'properties': propLst}
                
    def addProperty(self, name, value, tpe):
        pass

    def delProperty(self, name):
        pass

    def GetProp(self, name):
        for prop in self.propItems:
            if prop[0] == name: return prop[1]
    
    def SetProp(self, name, value):
        for idx in range(len(self.propItems)):
            if self.propItems[idx][0] == name:
                self.setCatProp(name, value)
                self.propItems[idx] = (name, value)
                break

class CategoryDictCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return self.catNode.entries[self.name].items()

    def setCatProp(self, name, value):
        self.catNode.entries[self.name][name] = value
        self.catNode.updateConfig()

class CategoryStringCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return [ ('Item', self.catNode.entries[self.name]) ]

    def setCatProp(self, name, value):
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
              EditorModels.imgFolderBookmark, self, self)

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
              EditorModels.FolderModel.imgIdx, parent)
        self.bookmarks = bookmarks
        self.bold = true
        self.refresh()
    
    def isFolderish(self):
        return true

    def createChildNode(self, shpth, pth):
        import FileExplorer
        return FileExplorer.PyFileNode(shpth, pth, self.clipboard, 
              EditorModels.SysPathFolderModel.imgIdx, self, self.bookmarks)
        
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


