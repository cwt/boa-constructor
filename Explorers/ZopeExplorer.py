#-----------------------------------------------------------------------------
# Name:        ZopeExplorer.py
# Purpose:
#
# Author:      Riaan Booysen & Robert Boulanger
#
# Created:     2001/02/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, urllib, urlparse, string, time, socket

from wxPython.wx import *

import EditorHelper, ExplorerNodes, ZopeLib.LoginDialog, ZopeEditorModels
from ExternalLib import xmlrpclib, BasicAuthTransport
from ZopeLib import ImageViewer, Client, ExtMethDlg
from Companions.ZopeCompanions import ZopeConnection, ZopeCompanion, FolderZC
from Preferences import IS, wxFileDialog
import Utils
import Views
from Views import ZopeViews
import PaletteStore, HTMLResponse

# XXX Add owner property

# XXX Problem with opening objects with '.' in their name !!
# XXX root attribute is no longer really necessary

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
        self.callAndSetRef(node.resourcepath, 'manage_cutObjects', nodes)
    def clipCopy(self, node, nodes):
        ExplorerNodes.ExplorerClipboard.clipCopy(self, node, nodes)
        self.callAndSetRef(node.resourcepath, 'manage_copyObjects', nodes)
#    def clipPaste(self, node):
#        ExplorerNodes.ExplorerClipboard.clipPaste(self, node)

    def clipPaste_ZopeEClip(self, node, nodes, mode):
        mime, res = self.zc.call(node.resourcepath,
              'manage_pasteObjects', cb_copy_data = self.clipRef)

##    def pasteFileSysFolder(self, folderpath, nodepath, node):
##        # XXX Should use http commands to paste
##        # XXX FTP does not want to upload binary correctly
##        # XXX rewrite to use explorer interfaces
##        node.newFolder(os.path.basename(folderpath))
###        node.zopeConn.add_folder(os.path.basename(folderpath), nodepath)
##
###        node.newItem(os.path.basename(folderpath), FolderZC, false)
##
##        files = os.listdir(folderpath)
##        folder = os.path.basename(folderpath)
##        newNodepath = nodepath+'/'+folder
##        for file in files:
##            file = os.path.join(folderpath, file)
##            if os.path.isdir(file):
##                self.pasteFileSysFolder(file, newNodepath, node)
##            else:
##                node.uploadFromFS(file, newNodepath)

    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        nodepath = node.resourcepath+'/'+node.name
        for file in nodes:
            if file.isDir():
                node.newFolder(file.name)
                folderNode = node.createChildNode('Folder', file.name)
                self.clipPaste_FileSysExpClipboard(folderNode,
                                                   file.openList(), mode)
            else:
                node.uploadFromFS(file)#, nodepath)

class ZopeCatNode(ExplorerNodes.CategoryNode):
    protocol = 'config.zope'

    defName = 'Zope'
    defaultStruct = {'ftpport': 8021,
                     'host': 'localhost',
                     'httpport': 8080,
                     'localpath': '',
                     'name': '',
                     'passwd': '',
                     'path': '/',
                     'username': '',
                     'servicename': ''}
    def __init__(self, config, parent, globClip):
        ExplorerNodes.CategoryNode.__init__(self, 'Zope', ('explorer', 'zope'), None, config,
              None)#parent)
        self.globClip = globClip

    def createChildNode(self, name, props):
        # Zope clipboards should be global but unique on site / user
        clipboard = ZopeEClip(self.globClip, props)
        #return ZopeConnectionNode(name, props, clipboard, self)
        zin = ZopeItemNode('', props['path'], clipboard,
            EditorHelper.imgZopeConnection, self, None, None, props, 'Folder')
#        zin.root = zin
        zin.treename = name
        return zin

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp

class ZopeItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'zope'
    Model = ZopeEditorModels.ZopeBlankEditorModel
    defaultViews = ()
    additionalViews = (ZopeViews.ZopeSecurityView,
                       ZopeViews.ZopeUndoView)
    itemsSubPath = ''

    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, xmlrpcsvr, root, properties, metatype):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, None, properties)
        self.metatype = metatype
        self.image = imgIdx
        self.root = None#root
        self.cache = {}
        self.server = xmlrpcsvr
        self.entries = None
        self.entryIds = None
        self.url = self.buildUrl()
        self.typ = None

    def buildUrl(self):
        return ('%(host)s:%(httpport)d/') % self.properties +urllib.quote(self.resourcepath)

##        root = self.root
##        tmp = self
##        if tmp == root:
##            return self.properties['host'] + ':' + str(self.properties['httpport']) +'/'
##        url = ''
##        while tmp != root:
##            url = string.strip(tmp.name) + '/' + url
##            tmp = tmp.parent
##        url = self.properties['host'] + ':' + str(self.properties['httpport']) + '/' + urllib.quote(url)
##        tmp = string.split(url, '/')
##
##        if len(tmp) >=6 :
##            if tmp[0] + '/' + tmp[1] + '/' + tmp[2] + '/' == self.properties['host'] + ':' + str(self.properties['httpport']) + '/Control_Panel/Products/':
##                #tmp.insert(6,"propertysheets/methods")
##                tmp[4]=tmp[4] + '/propertysheets/methods'
##                url=string.join(tmp, '/')#[:-2]+"/"
##
##        return url


    def destroy(self):
        #print 'Item destroyed'
        self.cache = {}
        self.root = None
        self.parent = None

    def canAdd(self, paletteName):
        return paletteName == 'Zope'

    def createChildNode(self, metatype, id):
        # XXX Append All my Icons correctly
        # CheckEntry Code here !
        if self.resourcepath =="/":
            tmppath = self.resourcepath + self.itemsSubPath + id
        else:
            tmppath = self.resourcepath + self.itemsSubPath + '/' + id

        itm = self.checkentry(id, metatype, tmppath)
        itm.imgIdx = ZopeEditorModels.ZOAIcons.get(metatype,
                     ZopeEditorModels.ZOAIcons['unknown'])
        return itm

    def checkentry(self, name, entry, path):
        ZopeNodeClass = zopeClassMap.get(entry, ZopeItemNode)
        return apply(ZopeNodeClass, (name, path, self.clipboard, -1, self,
            self.server, self.root, self.properties, entry))

    def whole_name(self):
        return self.resourcepath

    def getResource(self, url = ''):
        if not url:
            url = self.url
        return getServer(url, self.properties['username'],
               self.properties['passwd'])

    def openList(self, root = None):
        self.server = self.getResource(self.url+self.itemsSubPath)
        try:
            self.entries, self.entryIds = self.server.ZOA('items')
        except xmlrpclib.Fault, error:
            frm = HTMLResponse.create(None, error.faultString)
            frm.Show(true)
            # XXX Add Errorhandler here
            raise 'Zope Error: '+str(error.faultCode)

        self.cache = {}
        result = []
        if self.entryIds:
#            if not root: root = self.root

            for i in range(len(self.entries)):
                z = self.createChildNode(self.entries[i], self.entryIds[i] )
                if z:
                    result.append(z)
                    self.cache[self.entryIds[i]] = z
        return result

    def isFolderish(self):
        return true

    def getTitle(self):
        return 'Zope - '+self.resourcepath

    def open(self, editor):
        editor.openOrGotoZopeDocument(self)

    def deleteItems(self, names):
        mime, res = self.clipboard.zc.call(self.resourcepath,
              'manage_delObjects', ids = names)

    def renameItem(self, name, newName):
        mime, res = self.clipboard.zc.call(self.resourcepath,
              'manage_renameObject', id = name, new_id = newName)

    def exportObj(self):
        mime, res = self.clipboard.zc.call(os.path.dirname(self.resourcepath),
              'manage_exportObject', download = 1, id = self.name)
        return res

    def uploadObj(self, content):
        mime, res = self.clipboard.zc.call(self.resourcepath,
              'manage_upload', file = content)
        return res

    def listImportFiles(self):
        if self.properties.has_key('localpath'):
            return filter(lambda f: os.path.splitext(f)[1] == '.zexp', os.listdir(\
                os.path.join(self.properties['localpath'], 'import')))
        else:
            return []

    def importObj(self, name):
        try:
            mime, res = self.clipboard.zc.call(self.resourcepath, 'manage_importObject', file = name)
        except Exception, message:
            wxMessageBox(`message.args`, 'Error on import')
            #raise

    def newItem(self, name, Compn, getNewValidName = true):
        props = self.properties
        if getNewValidName:
            name = Utils.getValidName(self.cache.keys(), name)
        cmp = Compn(name, self.resourcepath, props.get('localpath', ''))
        cmp.connect(props['host'], props['httpport'],
                    props['username'], props['passwd'])
        cmp.create()

        return cmp.name

    def getUndoableTransactions(self):
        from ZopeLib.DateTime import DateTime
        if self.server._Server__handler == "/":
            return eval(self.getResource().ZOA('undoR/%s' % (self.name) ))
        else:
            return eval(self.getResource().ZOA('undo'))

    def undoTransaction(self, transactionIds):
        print self.getResource().manage_undo_transactions(transactionIds)

    def getPermissions(self):
        return self.getResource().permission_settings()#ZOA('permissions')

    def getRoles(self):
        return self.getResource().valid_roles()

    def load(self):
        return self.getResource().document_src()

    def save(self, filename, data):
        """ Saves contents of data to Zope """
        self.getResource().manage_upload(data)

    def newFolder(self, foldername):
        self.getResource().manage_addFolder(foldername)

    def uploadFromFS(self, filenode):
        props = self.properties
        from ExternalLib.WebDAV.client import Resource
        r = Resource(('http://%(host)s:%(httpport)s/'+self.resourcepath+'/'+\
            filenode.name) % props, props['username'], props['passwd'])
        r.put(filenode.load())


##class ZopeConnectionNode(ZopeItemNode):
##    protocol = 'zope'
##    def __init__(self, name, properties, clipboard, parent):
###        xmlrpcsvr = getServer(properties['host'] + ":" + str(properties['httpport']) + "/","",properties['username'],properties['passwd'])
##        ZopeItemNode.__init__(self, '', '', clipboard, #zopeObj.name, zopeObj.path, clipboard,
##            EditorModels.imgZopeConnection, parent, None, self, properties, 'Folder')
###        self.connected = false
##        self.treename = name

##    def openList(self):
##        if not self.connected:
##            if not string.strip(self.properties['username']):
##                ld = ZopeLib.LoginDialog.create(None)
##                try:
##                    ld.setup(self.properties['host'], self.properties['ftpport'],
##                      self.properties['httpport'], self.properties['username'],
##                      self.properties['passwd'])
##                    if ld.ShowModal() == wxOK:
##                        self.properties['host'], self.properties['ftpport'],\
##                          self.properties['httpport'], self.properties['username'],\
##                          self.properties['passwd'] = ld.getup()
##                finally:
##                    ld.Destroy()
####            try:
####                self.zopeConn.connect(self.properties['username'],
####                      self.properties['passwd'], self.properties['host'],
####                      self.properties['ftpport'])
####                # XXX AutoImport
####                #Can't work with zexp files :( must make it manually.. later
####                #try:
####                #    self.importObj('BOA_Ext.zexp')
####                #except:
####                #    pass
####            except Exception, message:
####                wxMessageBox(`message.args`, 'Error on connect')
####                raise
##        return ZopeItemNode.openList(self, self)

##    def closeList(self):
##        if self.connected:
##            self.zopeConn.disconnect()
##        self.connected = false

(wxID_ZOPEUP, wxID_ZOPECUT, wxID_ZOPECOPY, wxID_ZOPEPASTE, wxID_ZOPEDELETE,
 wxID_ZOPERENAME, wxID_ZOPEEXPORT, wxID_ZOPEIMPORT, wxID_ZOPEINSPECT,
 wxID_ZOPEUPLOAD, wxID_ZOPESECURITY, wxID_ZOPEUNDO,
 wxID_ZCCSTART, wxID_ZCCRESTART, wxID_ZCCSHUTDOWN, wxID_ZCCTEST,
) = map(lambda x: wxNewId(), range(16))

class ZopeCatController(ExplorerNodes.CategoryController):
    protocol = 'config.zope'
    def __init__(self, editor, list, inspector, menuDefs = ()):
        zccMenuDef = ( (-1, '-', None, '-'),
                       (wxID_ZCCSTART, 'Start', self.OnStart, '-'),
                       (wxID_ZCCRESTART, 'Restart', self.OnRestart, '-'),
                       (wxID_ZCCSHUTDOWN, 'Shutdown', self.OnShutdown, '-'),
                       (wxID_ZCCTEST, 'Test', self.OnTest, '-'),
                     )
        ExplorerNodes.CategoryController.__init__(self, editor, list, inspector,
            menuDefs = menuDefs + zccMenuDef)

    def checkAvailability(self, props, timeout = 10, showDlg = true):
        if showDlg:
            dlg = wxProgressDialog('Testing %s'% props['host'],
                           'Checking availability...', 100, self.editor,
                           wxPD_CAN_ABORT | wxPD_APP_MODAL | wxPD_AUTO_HIDE)
        try:
            now = time.time()
            res = ''
            while not timeout or time.time() < now + timeout:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect( (props['host'], props['httpport']) )
                except socket.error, err:
                    if err[0] == 10061:
                        # not running
                        res = 'The server is not running'
                    else:
                        res = 'Socket error: '+err[1]
                else:
                    res = 'The server is available'

                if not timeout:
                    break
        finally:
            if showDlg:
                dlg.Destroy()

        return res

    def getControlPanel(self, props):
        return getServer('%(host)s:%(httpport)d/Control_Panel' % props,
            props['username'], props['passwd'])

    def callControlPanelMethod(self, props, meth):
        zc = ZopeConnection()
        zc.connect(props['host'], props['httpport'],
                            props['username'], props['passwd'])
        zc.call('/Control_Panel', meth)

    def OnStart(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            props = node.properties
            if props['servicename']:
                os.system('net start "%s"'%props['servicename'])
                self.checkAvailability(node.properties, 10)
            elif props['localpath']:
                if string.find(props['localpath'], ' ') != -1:
                    wxLogError('Localpath property may not contain spaces')
                else:
                    os.system('start %s\\start.bat'%props['localpath'])
                    self.checkAvailability(node.properties, 10)
            else:
                wxLogError('Unable to start '+node.treename)

    def OnRestart(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            try:
#                self.getControlPanel(node.properties).manage_restart()
                self.callControlPanelMethod(node.properties, 'manage_restart')
                self.checkAvailability(node.properties, 10)
            except Exception, error:
                wxLogError('Restart not supported for '+node.treename+'\n'+str(error))

    def OnShutdown(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            self.callControlPanelMethod(node.properties, 'manage_shutdown')
            #self.getControlPanel(node.properties).manage_shutdown()

    def OnTest(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            wxLogMessage( '%s : %s' % (node.treename,
                self.checkAvailability(node.properties, 0)))


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
            (wxID_ZOPEIMPORT, 'Import', self.OnImportZopeItem, self.importBmp),
            (-1, '-', None, ''),
            (wxID_ZOPESECURITY, 'Security', self.OnSecurityZopeItem, '-'),
            (wxID_ZOPEUNDO,     'Undo',     self.OnUndoZopeItem, '-'),
          )

        self.setupMenu(self.menu, self.list, self.zopeMenuDef)
        self.toolbarMenus = [self.zopeMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.zopeMenuDef = ()
        self.toolbarMenus = ()

    def __del__(self):
        self.menu.Destroy()

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
            props = zopeItem.properties
            #print 'zopeItem.name', zopeItem.name, zopeItem.resourcepath
            try:
                ZComp = PaletteStore.compInfo[zopeItem.metatype][1]
            except KeyError:
                ZComp = ZopeCompanion

            zc = ZComp(zopeItem.name, zopeItem.resourcepath)#+'/'+zopeItem.name)
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

    def OnSecurityZopeItem(self, event):
        if self.list.node:
            zopeItem = self.list.getSelection()
            if zopeItem:
                model = self.editor.openOrGotoZopeDocument(zopeItem)
                viewName = ZopeViews.ZopeSecurityView.viewName
                if not model.views.has_key(viewName):
                    resultView = self.editor.addNewView(viewName,
                          ZopeViews.ZopeSecurityView)
                else:
                    resultView = model.views[viewName]
                resultView.refresh()
                resultView.focus()

    def OnUndoZopeItem(self, event):
        if self.list.node:
            zopeItem = self.list.getSelection()
            if zopeItem and ZopeViews.ZopeUndoView in zopeItem.additionalViews:
                model = self.editor.openOrGotoZopeDocument(zopeItem)
                viewName = ZopeViews.ZopeUndoView.viewName
                if not model.views.has_key(viewName):
                    resultView = self.editor.addNewView(viewName,
                          ZopeViews.ZopeUndoView)
                else:
                    resultView = model.views[viewName]
                resultView.refresh()
                resultView.focus()


def getServer(url, user, password):
    return xmlrpclib.Server('http://' + url,
              BasicAuthTransport.BasicAuthTransport(user, password) )
    #print user, password
##    try:
##        return xmlrpclib.Server('http://' + host,
##                  BasicAuthTransport.BasicAuthTransport(user, password) )
##    except:
##        return 'error'

class ZopeNode(ZopeItemNode):
    def isFolderish(self):
        return false

class ZopeImageNode(ZopeNode):
    pass

class DirNode(ZopeNode):
    def isFolderish(self):
        return true


class UserFolderNode(ZopeNode):
    def isFolderish(self):
        return true

class ControlNode(DirNode):
    def checkentry(self, id, entry, path):
        if entry == 'Product Management':
            childnode = PMNode(id, path, self.clipboard, -1, self,
                self.server, self.root, self.properties, entry)
        else:
            childnode = DirNode.checkentry(self, id, entry, path)
        return childnode

class PMNode(ControlNode):
    def checkentry(self,id,entry,path):
        if entry == 'Product' :
            childnode = ProductNode(id, path, self.clipboard, -1, self,
            self.server, self.root, self.properties, entry)
        else:
            childnode = ControlNode.checkentry(self, id, entry, path)
        return childnode

class ProductNode(DirNode):
    def checkentry(self, id, entry, path):
        if entry == 'Z Class' :
            childnode = ZClassNode(id, path, self.clipboard, -1, self,
                self.server, self.root, self.properties, entry)
        else:
            childnode = DirNode.checkentry(self, id, entry, path)
        return childnode

class ZClassNode(DirNode):
    itemsSubPath = '/propertysheets/methods'
##    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, xmlrpcsvr, root, properties, metatype):
##        resourcepath = resourcepath + '/propertysheets/methods'
##        DirNode.__init__(self, name, resourcepath, clipboard, imgIdx, parent,
##              xmlrpcsvr, root, properties, metatype)

class ZSQLNode(ZopeNode):
    Model = ZopeEditorModels.ZopeDocumentModel
    defaultViews = (Views.SourceViews.HTMLSourceView,)
    additionalViews = (ZopeViews.ZopeSecurityView, Views.EditorViews.ToDoView,
                       ZopeViews.ZopeUndoView)
    def save(self, filename, data):
        """ Saves contents of data to Zope """
        try:
            self.getResource().PUT({'BODY':data})
        except xmlrpclib.ProtocolError, error:
            # Getting a zero content warning is not an error
            if error.errcode != 204:
                raise

class PythonNode(ZopeNode):
    Model = ZopeEditorModels.ZopePythonScriptModel
    defaultViews = (Views.PySourceView.PythonSourceView,)
    additionalViews = (ZopeViews.ZopeSecurityView, Views.EditorViews.ToDoView,
                       ZopeViews.ZopeUndoView)

    def getParams(self, data):
        return data[string.find(data, '(')+1 : string.find(data, '):')]

    def getBody(self, data):
        tmp = string.split(data[string.find(data, ':')+2:], '\n')
        tmp2 = []
        for  l in tmp:
            # Handle comments which may be indented less
            if string.strip(l[:4]):
                l = string.lstrip(l)
            else:
                l = l[4:]
            tmp2.append(l)
        return string.join(tmp2, '\n')

    def save(self, filename, data):
        self.getResource().manage_edit(self.name, self.getParams(data),
              self.getBody(data))

    def getUndoableTransactions(self):
        from ZopeLib.DateTime import DateTime
        if self.server._Server__handler == '/':
            all = eval(self.server.ZOA('undoR/%s' % (self.name) ))
        else:
            all = eval(self.server.ZOA('undo'))
        undos = []
        for u in all:
            if self.name == string.split(u['description'], '/')[-2]:
                undos.append(u)
        return undos

    def undoTransaction(self, transactionIds):
        print self.server.manage_undo_transactions(transactionIds)

class PythonScriptNode(PythonNode):
    additionalViews = (ZopeViews.ZopeSecurityView,
          ZopeViews.ZopeUndoView, Views.EditorViews.ToDoView)

    def preparedata(self, data):
        tmp=string.split(data, '\n')
        tmp2=[]
        h=1
        for l in tmp:
            if l[:2] <> '##' :
                h=0
            if l[:12] == '##parameters':
                params = l[string.find(l, '=')+1:]
            if h:
                pass # perhaps we need this anytime
            else:
                tmp2.append('    ' + l)
        return 'def %s(%s):\n%s' % (self.name, params, string.join(tmp2, '\n'))

    def load(self):
        data = PythonNode.load(self)
        return self.preparedata(data)

    def save(self, filename, data):
        self.getResource().ZPythonScriptHTML_editAction('fake',
              self.name, self.getParams(data), self.getBody(data))

class ExtPythonNode(PythonNode):
    Model = ZopeEditorModels.ZopeExternalMethodModel
    defaultViews = (Views.PySourceView.PythonSourceView,
                    Views.EditorViews.ExploreView)
    additionalViews = (Views.EditorViews.HierarchyView,
                       Views.EditorViews.ModuleDocView,
                       ZopeViews.ZopeSecurityView, Views.EditorViews.ToDoView,
                       ZopeViews.ZopeUndoView)
    # XXX Should open the Python module if it is available on the
    # XXX local FS (later any FS) specified by localpath in properties

    # XXX Consider routing to a normal file open instead of just loading/saving
    # XXX the data
    def load(self):
        zopePath = self.properties['localpath']
        if not os.path.exists(zopePath):
            raise 'Property localpath of the Zope connection is not a valid path'

        path, name = os.path.split(self.name)
        res = self.getResource(os.path.dirname(self.url)).ZOA('ExtMethod_Props', name)
        module = res['module']

        from ZopeLib import ExtMethDlg
        emf = ExtMethDlg.ExternalMethodFinder(zopePath)
        extPath = emf.getExtPath(module)

        return open(extPath).read()

    def save(self, filename, data):
        zopePath = self.properties['localpath']
        if not os.path.exists(zopePath):
            raise 'Property localpath of the Zope connection is not a valid path'

        path, name = os.path.split(self.name)
        res = self.getResource(os.path.dirname(self.url)).ZOA('ExtMethod_Props', name)
        module = res['module']

        emf = ExtMethDlg.ExternalMethodFinder(zopePath)
        extPath = emf.getExtPath(module)

        return open(extPath, 'w').write(data)

class DTMLDocNode(ZopeNode):
    Model = ZopeEditorModels.ZopeDTMLDocumentModel
    defaultViews = (Views.SourceViews.HTMLSourceView,)
    additionalViews = (ZopeViews.ZopeUndoView,
          ZopeViews.ZopeSecurityView, ZopeViews.ZopeHTMLView,)

class DTMLMethodNode(ZopeNode):
    Model = ZopeEditorModels.ZopeDTMLMethodModel
    defaultViews = (Views.SourceViews.HTMLSourceView,)
    additionalViews = (ZopeViews.ZopeUndoView,
          ZopeViews.ZopeSecurityView, ZopeViews.ZopeHTMLView)

class LFSNode(DirNode):
    def checkentry(self,id,entry,path):
        #print entry
        if entry == 'directory' or entry == 'Local Directory':
            childnode=LFDirNode(id, path, self.clipboard, -1, self,
                self.server, self.root, self.properties, entry)
        else:
            childnode=LFNode(id, path, self.clipboard, -1, self,
                self.server, self.root, self.properties, entry)
        return childnode

class LFNode(LFSNode):
    def isFolderish(self):
        return false

class LFDirNode(LFSNode):
    def isFolderish(self):
        return true

zopeClassMap = { 'Folder': DirNode,
        'Product Help': DirNode,
        'User Folder': UserFolderNode,
        'Control Panel': ControlNode,
        'Local File System': LFSNode,
        'Local Directory': LFSNode,
        'directory': LFSNode,
        'Z SQL Method': ZSQLNode,
        'DTML Document': DTMLDocNode,
        'DTML Method': DTMLMethodNode,
        'Python Method': PythonNode,
        'External Method': ExtPythonNode,
        'Script (Python)': PythonScriptNode,
        'Image': ZopeImageNode,
       }
