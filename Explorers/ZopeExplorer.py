from wxPython.wx import *
import ExplorerNodes, ZopeLib.LoginDialog, EditorModels
import ftplib, os
from ZopeLib.ZopeFTP import ZopeFTP
from ZopeLib import ImageViewer, Client
from Companions.ZopeCompanions import ZopeConnection, ZopeCompanion, FolderZC
from Preferences import IS, wxFileDialog
import Utils

ctrl_pnl = 'Control_Panel'
prods = 'Products'
acl_usr = 'acl_users'

class ZopeEClip(ExplorerNodes.ExplorerClipboard):
    def __init__(self, globClip, props):
        ExplorerNodes.ExplorerClipboard.__init__(self, globClip)
        self.clipRef = ''

        self.props = props
        self.zc = ZopeConnection()
        self.zc.connect(props['host'], props['httpport'], 
                        props['username'], props['passwd'])
    def callAndSetRef(self, objpath, method, nodes):
        names = map(lambda n :n.name, nodes)
        mime, res = self.zc.call(objpath, method, ids = names)
        self.clipRef = string.split(mime.get('Set-Cookie'), '"')[1]
    def clipCut(self, node, nodes):
        ExplorerNodes.ExplorerClipboard.clipCut(self, node, nodes)
        self.callAndSetRef(node.zopeObj.whole_name(), 'manage_cutObjects', nodes)
    def clipCopy(self, node, nodes):
        ExplorerNodes.ExplorerClipboard.clipCopy(self, node, nodes)
        self.callAndSetRef(node.zopeObj.whole_name(), 'manage_copyObjects', nodes)
#    def clipPaste(self, node):
#        ExplorerNodes.ExplorerClipboard.clipPaste(self, node)
        
    def clipPaste_ZopeEClip(self, node, nodes, mode):
        mime, res = self.zc.call(node.zopeObj.whole_name(), 
              'manage_pasteObjects', cb_copy_data = self.clipRef)
    
    def pasteFileSysFolder(self, folderpath, nodepath, node):
        # XXX Should use http commands to paste
        # XXX FTP does not want to upload binary correctly
        node.zopeConn.add_folder(os.path.basename(folderpath), nodepath)
#        node.newItem(os.path.basename(folderpath), FolderZC, false)
        files = os.listdir(folderpath)
        folder = os.path.basename(folderpath)
        newNodepath = nodepath+'/'+folder
        for file in files:
            file = os.path.join(folderpath, file)
            if os.path.isdir(file):
                self.pasteFileSysFolder(file, newNodepath, node)
            else:
                node.zopeConn.upload(file, newNodepath)
    
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        nodepath = node.resourcepath+'/'+node.name
        for file in nodes:
            if file.isDir():
                self.pasteFileSysFolder(file.resourcepath, nodepath, 
                      node)
            else:
                node.zopeConn.upload(file.resourcepath, nodepath)

class ZopeCatNode(ExplorerNodes.CategoryNode):
#    protocol = 'config.zope'
    defName = 'Zope'
    defaultStruct = {'ftpport': 8021,
                     'host': 'localhost',
                     'httpport': 8080,
                     'localpath': '',
                     'name': '',
                     'passwd': '',
                     'path': '/',
                     'username': ''}
    def __init__(self, config, parent, globClip):
        ExplorerNodes.CategoryNode.__init__(self, 'Zope', ('explorer', 'zope'), None, config, 
              parent)
        self.globClip = globClip

    def createChildNode(self, name, props):
        # Zope clipboards should be global but unique on site / user
        clipboard = ZopeEClip(self.globClip, props)
        return ZopeConnectionNode(name, props, clipboard, self)

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp
        
class ZopeItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'zope'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, zftp, zftpi, root, properties):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, properties)
        self.zopeConn = zftp
        self.zopeObj = zftpi
        self.root = root
        self.cache = []
    
    def destroy(self):
        self.cache = {}
    
    def canAdd(self, paletteName):
        return paletteName == 'Zope'

    def createChildNode(self, obj, root):
        def getZopeFolderImg(node):
            if node.name == '..': return EditorModels.imgZopeFolder
            elif node.name == ctrl_pnl: return EditorModels.imgZopeControlPanel
            elif node.name == prods and node.parent.name == ctrl_pnl : 
                return EditorModels.imgZopeProductFolder
            elif node.parent.name == prods and \
                  node.parent.parent.name == ctrl_pnl: 
                return EditorModels.imgZopeInstalledProduct
            return EditorModels.imgZopeFolder

        if obj.name != '..':
            itm = ZopeItemNode(obj.name, obj.path, self.clipboard, -1, 
                  self, self.zopeConn, obj, root, self.properties)

            if itm.isFolderish(): imgIdx = getZopeFolderImg(itm)
            elif itm.name == acl_usr: imgIdx = EditorModels.imgZopeUserFolder
            elif string.lower(os.path.splitext(itm.name)[1]) in ImageViewer.imgs.keys(): 
                imgIdx = EditorModels.imgZopeImage
            elif itm.zopeObj.isSysObj(): imgIdx = EditorModels.imgZopeSystemObj
            else: imgIdx = EditorModels.imgZopeDTMLDoc
            
            itm.imgIdx = imgIdx

            return itm
        else:
            return None
        
    def openList(self, root = None):
        try:
            wxBeginBusyCursor()
            try:
                items = self.zopeConn.dir(self.zopeObj.whole_name())
            finally:
                wxEndBusyCursor()
        except ftplib.error_perm, resp:
            Utils.ShowMessage(None, 'Zope Error', `resp`)
            raise
        
#        itmTyps =
        if not root: root = self.root
        self.cache = {}
        result = []
        for obj in items:
            z = self.createChildNode(obj, self.root)
            if z:
                result.append(z)
                self.cache[obj.name] = z
        
        return result
    
    def isFolderish(self): 
        return self.zopeObj.isFolder()

    def getTitle(self):
        return 'Zope - '+self.zopeObj.whole_name()

    def open(self, editor):
        editor.openOrGotoZopeDocument(self.zopeConn, self.zopeObj)

    def deleteItems(self, names):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_delObjects', ids = names)

    def renameItem(self, name, newName):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_renameObject', id = name, new_id = newName)

    def exportObj(self):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_exportObject', download = 1)
        return res

    def uploadObj(self, content):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_upload', file = content)
        return res

    def listImportFiles(self):
        if self.properties.has_key('localpath'):
            return filter(lambda f: os.path.splitext(f)[1] == '.zexp', os.listdir(\
                os.path.join(self.properties['localpath'], 'import')))
        else:
            return []

    def importObj(self, name):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_importObject', file = name)

    def newItem(self, name, Compn, getNewValidName = true):
        props = self.root.properties
        if getNewValidName:
            name = Utils.getValidName(self.cache.keys(), name)
        cmp = Compn(name, self.zopeObj.whole_name(), props.get('localpath', ''))
        cmp.connect(props['host'], props['httpport'], 
                    props['username'], props['passwd'])
        cmp.create()
        
        return cmp.name

class ZopeConnectionNode(ZopeItemNode):
    protocol = 'zope'
    def __init__(self, name, properties, clipboard, parent):
        zopeConn = ZopeFTP()
        zopeObj = zopeConn.folder_item(properties['name'], properties['path'])
        ZopeItemNode.__init__(self, zopeObj.name, zopeObj.path, clipboard, 
            EditorModels.imgZopeConnection, parent, zopeConn, zopeObj, self, properties)
        self.connected = false
        self.treename = name
        
    def openList(self):
        if not self.connected:
            if not string.strip(self.properties['username']):
                ld = ZopeLib.LoginDialog.create(None)
                try:
                    ld.setup(self.properties['host'], self.properties['ftpport'],
                      self.properties['httpport'], self.properties['username'], 
                      self.properties['passwd'])
                    if ld.ShowModal() == wxOK:
                        self.properties['host'], self.properties['ftpport'],\
                          self.properties['httpport'], self.properties['username'],\
                          self.properties['passwd'] = ld.getup()
                finally:
                    ld.Destroy()
            try:
                self.zopeConn.connect(self.properties['username'], 
                      self.properties['passwd'], self.properties['host'],
                      self.properties['ftpport'])
            except Exception, message:
                wxMessageBox(`message.args`, 'Error on connect')
                raise
        return ZopeItemNode.openList(self, self)
    
    def closeList(self):
        if self.connected:
            self.zopeConn.disconnect
        self.connected = false

(wxID_ZOPEUP, wxID_ZOPECUT, wxID_ZOPECOPY, wxID_ZOPEPASTE, wxID_ZOPEDELETE, 
 wxID_ZOPERENAME, wxID_ZOPEEXPORT, wxID_ZOPEIMPORT, wxID_ZOPEINSPECT,
 wxID_ZOPEUPLOAD) = map(lambda x: wxNewId(), range(10))

class ZopeController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    inspectBmp = 'Images/Shared/Inspector.bmp'
    importBmp = 'Images/Shared/ZopeImport.bmp'
    exportBmp = 'Images/Shared/ZopeExport.bmp'
    uploadBmp = 'Images/Zope/upload_doc.bmp'
    def __init__(self, editor, list, inspector):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()
        self.inspector = inspector
        
        self.zopeMenuDef = (\
            (wxID_ZOPEINSPECT, 'Inspect', self.OnInspectZopeItem, self.inspectBmp),
            (-1, '-', None, '') ) +\
            self.clipMenuDef +\
          ( (-1, '-', None, ''),
            (wxID_ZOPEUPLOAD, 'Upload', self.OnUploadZopeItem, self.uploadBmp),
            (wxID_ZOPEEXPORT, 'Export', self.OnExportZopeItem, self.exportBmp),
            (wxID_ZOPEIMPORT, 'Import', self.OnImportZopeItem, self.importBmp) )

        self.setupMenu(self.menu, self.list, self.zopeMenuDef)
        self.toolbarMenus = [self.zopeMenuDef]
            
    def OnExportZopeItem(self, event):
        if self.list.node:
            idxs = self.list.getMultiSelection()
            currPath = '.'
            for idx in idxs:
                item = self.list.items[idx]
                if item:
                    zexp = item.exportObj()
        
                    dlg = wxFileDialog(self.list, 'Save as...', currPath, 
                          item.name+'.zexp', '', wxSAVE | wxOVERWRITE_PROMPT)
                    try:
                        if dlg.ShowModal() == wxID_OK:
                            open(dlg.GetPath(), 'wb').write(zexp)
                            currPath = dlg.GetDirectory()
                    finally: 
                        dlg.Destroy()
            
    def OnImportZopeItem(self, event):
        fls = self.list.node.listImportFiles()
        
        if fls:
            dlg = wxSingleChoiceDialog(self.list, 'Choose the file to import', 'Import object', fls)
            try:
                if dlg.ShowModal() == wxID_OK:
                    zexp = dlg.GetStringSelection()
                else:
                    return
            finally:
                dlg.Destroy()
        else:
            dlg = wxTextEntryDialog(self.list, 'Enter file to import', 'Import object', '.zexp')
            try:
                if dlg.ShowModal() == wxID_OK:
                    zexp = dlg.GetValue()
                else:
                    return
            finally:
                dlg.Destroy()

        self.list.node.importObj(zexp)
        self.list.refreshCurrent()
    
    def OnInspectZopeItem(self, event):
        if self.list.node:
            # Create new companion for selection
            zopeItem = self.list.getSelection()
            if not zopeItem: zopeItem = self.list.node
            props = zopeItem.root.properties
            zc = ZopeCompanion(zopeItem.name, zopeItem.resourcepath+'/'+zopeItem.name)
            zc.connect(props['host'], props['httpport'], 
                       props['username'], props['passwd'])
            zc.updateZopeProps()
    
            # Select in inspector
            if self.inspector.pages.GetSelection() != 1:
                self.inspector.pages.SetSelection(1)
            self.inspector.selectObject(zc, false)
    
    def OnUploadZopeItem(self, event):
        if self.list.node:
            idxs = self.list.getMultiSelection()
            currPath = '.'
            for idx in idxs:
                item = self.list.items[idx]
                if item:
                    dlg = wxFileDialog(self.list, 'Upload '+item.name, currPath, 
                          item.name, '', wxOPEN)
                    try:
                        if dlg.ShowModal() == wxID_OK:
                            try:
                                item.uploadObj(open(dlg.GetPath(), 'rb'))#.read())
                            except Client.NotFound:
                                wxMessageBox('Object does not support uploading', 'Error on upload')
                            currPath = dlg.GetDirectory()
                    finally: 
                        dlg.Destroy()
        
