#-----------------------------------------------------------------------------
# Name:        ZopeExplorer.py
# Purpose:
#
# Author:      Riaan Booysen & Robert Boulanger
#
# Created:     2001/02/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing ZopeLib.ZopeExplorer'

import os, urllib, urlparse, string, time, socket

from wxPython.wx import *

from Explorers import ExplorerNodes
from Models import EditorHelper, Controllers
from ExternalLib import xmlrpclib, BasicAuthTransport
from ZopeLib import ZopeEditorModels, ZopeViews, Client, ExtMethDlg
from ZopeLib.ZopeCompanions import ZopeConnection, ZopeCompanion, FolderZC
from Preferences import IS
import Utils, Preferences
import Views
import Views.PySourceView
import Views.SourceViews
import PaletteStore

# XXX Add owner property

# XXX root attribute is no longer really necessary

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

    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for file in nodes:
            if file.isDir():
                node.newFolder(file.name)
                folderNode = node.createChildNode('Folder', file.name)
                self.clipPaste_FileSysExpClipboard(folderNode,
                                                   file.openList(), mode)
            else:
                node.uploadFromFS(file)

class ZopeCatNode(ExplorerNodes.CategoryNode):
    protocol = 'config.zope'
    itemProtocol = 'zope'

    defName = 'Zope'
    defaultStruct = {'ftpport': 8021,
                     'host': 'localhost',
                     'httpport': 8080,
                     'localpath': '',
                     'name': '',
                     'passwd': '',
                     'path': '/',
                     'username': '',
                     'servicename': '',
                     'startuptimeout': 30}
    def __init__(self, globClip, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'Zope', ('explorer', 'zope'),
              None, config, None)
        self.globClip = globClip
        self.bookmarks = bookmarks

    def createChildNode(self, name, props):
        # Zope clipboards should be global but unique on site / user
        clipboard = ZopeEClip(self.globClip, props)
        zin = ZopeItemNode('', props['path'], clipboard,
            EditorHelper.imgZopeConnection, self, None, None, props, 'Folder')
        zin.category = name
        zin.treename = name
        zin.bookmarks = self.bookmarks
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
    connection = false
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, xmlrpcsvr,
          root, properties, metatype):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, None, properties)
        self.metatype = metatype
        self.image = imgIdx
        self.root = None
        self.cache = {}
        self.server = xmlrpcsvr
        self.entries = None
        self.entryIds = None
        self.url = self.buildUrl()
        self.typ = None
#        self.bookmarks = None

    def getURI(self):
        return '%s://%s/<%s>%s'%(self.protocol, self.category, self.metatype, self.getTitle())

    def buildUrl(self):
        return ('%(host)s:%(httpport)d/') % self.properties +urllib.quote(self.resourcepath)

    def destroy(self):
        self.cache = {}
        self.root = None
        self.parent = None

    def canAdd(self, paletteName):
        return paletteName == 'Zope'

    def createChildNode(self, metatype, id, respath=None):
        if respath is None:
            respath = self.resourcepath

        if respath == '/':
            tmppath = respath + self.itemsSubPath + id
        else:
            tmppath = respath + self.itemsSubPath + '/' + id

        itm = self.checkentry(id, metatype, tmppath)
        if itm.imgIdx == -1:
            itm.imgIdx = ZopeEditorModels.ZOAIcons.get(metatype,
                         ZopeEditorModels.ZOAIcons['unknown'])
        itm.category = self.category
        itm.bookmarks = self.bookmarks
        return itm

    def checkentry(self, name, metatype, path):
        ZopeNodeClass = zopeClassMap.get(metatype, ZopeItemNode)
        return apply(ZopeNodeClass, (name, path, self.clipboard, -1, self,
            self.server, self.root, self.properties, metatype))

    def whole_name(self):
        return self.resourcepath

    def getResource(self, url=''):
        if not url:
            url = self.url
        return getServer(url, self.properties['username'],
               self.properties['passwd'])

    def getParentResource(self):
        path, name = os.path.split(self.name)
        return self.getResource(os.path.dirname(self.url)), name

    def openList(self, root = None):
        url = self.url+self.itemsSubPath
        if url[-1] == '/':
            url = url[:-1]
        self.server = self.getResource(url)
        try:
            self.entries, self.entryIds = self.server.zoa.items()
        except xmlrpclib.Fault, error:
            #print str(error)
            # see if ZOA is installed
            try:
#                print 'http://%s/zoa'%self.buildUrl()
                Client.call('http://%s/zoa'%self.buildUrl(),
                      self.properties['username'], self.properties['passwd'],
                      function='version')
            except Client.NotFound:
                raise 'The zoa object not found in the root of your Zope tree.\n'\
                      'Please use a browser and import the file '\
                      'ZopeLib/zoa.zexp into your Zope root.'
                #raise 'zoa obj missing
##                    try:
##                        Client.call('http://%s/manage_addProduct/PythonScripts/'\
##                              'manage_addPythonScript'%self.buildUrl(),
##                              self.properties['username'],
##                              self.properties['passwd'], id = 'ZOA')
##                    except Client.ServerError, error:
##                        if error.http_code == 302:
##                            Client.call('http://%s/ZOA/ZPythonScriptHTML_editAction'\
##                                %self.buildUrl(), self.properties['username'],
##                                self.properties['passwd'],
##                                title = 'ZOA (Boa component)',
##                                params = 'self, function, args=None',
##                                body = open(Preferences.pyPath+'/ZopeLib/ZOA.py').read())
##                    try:
##                        self.entries, self.entryIds = self.server.ZOA('items')
##                    except xmlrpclib.Fault, error:
##                        raise zopeHtmlErr2Strs(error.faultString)
##                else:
##                    raise 'The ZOA component must be installed'
            else:
                err = error.faultString
                raise zopeHtmlErr2Strs(err)

        self.cache = {}
        result = []
        if self.entryIds:
            for i in range(len(self.entries)):
                z = self.createChildNode(self.entries[i], self.entryIds[i] )
                if z:
                    result.append(z)
                    self.cache[self.entryIds[i]] = z
        return result

    def isFolderish(self):
        return true

    def getTitle(self):
        return self.resourcepath

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
            from Explorers import Explorer
            return Explorer.listdirEx(self.properties['localpath']+'/import', '.zexp')
##        filter(lambda f: string.lower(os.path.splitext(f)[1]) == '.zexp',
##                          map(lambda n: n.treename, Explorer.openEx(\
##                          self.properties['localpath']+'/import').openList()))
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
        svr, name = self.getParentResource()
        return eval(svr.zoa.undo(name))

    def undoTransaction(self, transactionIds):
        print self.getResource().manage_undo_transactions(transactionIds)

    def getPermissions(self):
        return self.getResource().permission_settings()#ZOA('permissions')

    def getRoles(self):
        return self.getResource().valid_roles()

    def load(self, mode='rb'):
        return ''#return self.getResource().document_src()


    def save(self, filename, data, mode='wb'):
        """ Saves contents of data to Zope """
        pass#self.getResource().manage_upload(data)

    def newFolder(self, name):
        self.getResource().manage_addFolder(name)

    def newBlankDocument(self, name=''):
        try:
            self.getResource().manage_addDTMLDocument(name)
        except xmlrpclib.ProtocolError, error:
            if error.errcode != 302:
                raise

    def uploadFromFS(self, filenode):
        props = self.properties
        from ExternalLib.WebDAV.client import Resource
        r = Resource(('http://%(host)s:%(httpport)s/'+self.resourcepath+'/'+\
            filenode.name) % props, props['username'], props['passwd'])
        r.put(filenode.load())

    def downloadToFS(self, filename):
        props = self.properties
        from ExternalLib.WebDAV.client import Resource
        r = Resource(('http://%(host)s:%(httpport)s/'+self.resourcepath) % props,
            props['username'], props['passwd'])
        open(filename, 'wb').write(r.get().body)

    def getNodeFromPath(self, respath, metatype):
        return self.createChildNode(metatype, os.path.basename(respath),
              os.path.dirname(respath))

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

(wxID_ZOPEEXPORT, wxID_ZOPEIMPORT, wxID_ZOPEINSPECT, wxID_ZOPEOPENINEDITOR,
 wxID_ZOPEUPLOAD, wxID_ZOPESECURITY, wxID_ZOPEUNDO, wxID_ZOPEVIEWBROWSER,
 wxID_ZCCSTART, wxID_ZCCRESTART, wxID_ZCCSHUTDOWN, wxID_ZCCTEST, wxID_ZCCOPENLOG,
 wxID_ZACONFZ2, wxID_ZOPEMANAGEBROWSER,
) = Utils.wxNewIds(15)

class ZopeCatController(ExplorerNodes.CategoryController):
    protocol = 'config.zope'
    zopeStatupTimeout = 60 # default when not read from property
    zopeRunning = 'The server is available'
    err_zopeNotRunning = 'The server is not running'
    err_localpathBlank = 'The "localpath" property must be defined'
    def __init__(self, editor, list, inspector, controllers, menuDefs = ()):
        zccMenuDef = ( (-1, '-', None, '-'),
                       (wxID_ZCCSTART, 'Start', self.OnStart, '-'),
                       (wxID_ZCCRESTART, 'Restart', self.OnRestart, '-'),
                       (wxID_ZCCSHUTDOWN, 'Shutdown', self.OnShutdown, '-'),
                       (wxID_ZCCTEST, 'Test', self.OnTest, '-'),
                       (-1, '-', None, '-'),
                       (wxID_ZCCOPENLOG, 'Open Zope log', self.OnOpenZopeLog, '-'),
                       (wxID_ZACONFZ2, 'Configure z2.py', self.OnConfigureZ2py, '-'),
                     )
        ExplorerNodes.CategoryController.__init__(self, editor, list, inspector,
              controllers, menuDefs = menuDefs + zccMenuDef)

    def checkAvailability(self, props, timeout=10, showDlg=true):
        retry = true
        dlg = None
        while retry:
            retry = false
            if showDlg and not dlg:
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
                            res = self.err_zopeNotRunning
                            if time.time() > now + timeout and \
                                  wxMessageBox('Keep checking for Zope to become available',
                                  'Retry?', style=wxYES_NO | wxICON_QUESTION) == wxYES:
                                retry = true
                        else:
                            res = 'Socket error: '+err[1]
                    else:
                        res = self.zopeRunning

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
            try: zopeStatupTimeout = props['startuptimeout']
            except KeyError: zopeStatupTimeout = self.zopeStatupTimeout

            if props['servicename']:
                os.system('net start "%s"'%props['servicename'])
                self.checkAvailability(node.properties, zopeStatupTimeout)
            elif props['localpath']:
                if string.find(props['localpath'], ' ') != -1:
                    wxLogError('Localpath property may not contain spaces (use SHORT~1 version if necessary)')
                else:
                    os.system('start %s\\start.bat'%props['localpath'])
                    self.checkAvailability(node.properties, zopeStatupTimeout)
            else:
                wxLogError('Unable to start '+node.treename)

    def OnRestart(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            props = node.properties
            try: zopeStatupTimeout = props['startuptimeout']
            except KeyError: zopeStatupTimeout = self.zopeStatupTimeout
            try:
                self.callControlPanelMethod(node.properties, 'manage_restart')
                resp = self.checkAvailability(node.properties, zopeStatupTimeout)
                if resp == 'The server is available':
                    self.editor.setStatus(resp)
                else:
                    self.editor.setStatus(resp, 'Warning')
            except Exception, error:
                wxLogError('Restart not supported for '+node.treename+'\n'+str(error))

    def OnShutdown(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            self.callControlPanelMethod(node.properties, 'manage_shutdown')

    def OnTest(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            wxLogMessage( '%s : %s' % (node.treename,
                self.checkAvailability(node.properties, 0)))

    def OnOpenZopeLog(self, event):
        for node in self.getNodesForSelection(self.list.getMultiSelection()):
            props = node.properties
            if props['localpath']:
                self.editor.openOrGotoModule(os.path.join(props['localpath'],
                      'var', 'Z2.log'))
            else:
                wxLogError(self.err_localpathBlank)

    def OnConfigureZ2py(self, event):
        node = self.getNodesForSelection(self.list.getMultiSelection())
        if len(node):
            node = node[0]
        else:
            print 'Nothing selected'

        props = node.properties
        if props['localpath']:
            cfgZ2SrcNode = ZopeZ2pySourceBasedPrefColNode('Z2.py',
                  ('*',), props['localpath']+'/z2.py', -1, node)
            cfgZ2SrcNode.open(self.editor)
        else:
            wxLogError(self.err_localpathBlank)


# XXX Better field validation and hints as to when path props shound end in / or not !!
class ZopeController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    inspectBmp = 'Images/Shared/Inspector.png'
    importBmp = 'Images/Shared/ZopeImport.png'
    exportBmp = 'Images/Shared/ZopeExport.png'
    uploadBmp = 'Images/ZOA/upload_doc.png'
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()
        self.inspector = inspector

        self.zopeMenuDef = (\
            (wxID_ZOPEINSPECT, 'Inspect', self.OnInspectItem, self.inspectBmp),
            (-1, '-', None, '') ) +\
            self.clipMenuDef +\
          ( (-1, '-', None, ''),
            (wxID_ZOPEUPLOAD, 'Upload', self.OnUploadZopeItem, self.uploadBmp),
            (wxID_ZOPEEXPORT, 'Export', self.OnExportZopeItem, self.exportBmp),
            (wxID_ZOPEIMPORT, 'Import', self.OnImportZopeItem, self.importBmp),
            (-1, '-', None, '-'),
            (wxID_ZOPEOPENINEDITOR, 'Open in Editor', self.OnOpenInEditorZopeItem, '-'),
            (wxID_ZOPESECURITY, 'Security', self.OnSecurityZopeItem, '-'),
            (wxID_ZOPEUNDO,     'Undo',     self.OnUndoZopeItem, '-'),
            (-1, '-', None, '-'),
            (wxID_ZOPEVIEWBROWSER,'View in browser', self.OnViewInBrowser, '-'),
            (wxID_ZOPEMANAGEBROWSER,'Manage in browser', self.OnManageInBrowser, '-'),
          )

        self.setupMenu(self.menu, self.list, self.zopeMenuDef)
        self.toolbarMenus = [self.zopeMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.zopeMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnExportZopeItem(self, event):
        if self.list.node:
            idxs = self.list.getMultiSelection()
            currPath = '.'
            for idx in idxs:
                item = self.list.items[idx]
                if item:
                    zexp = item.exportObj()

                    from FileDlg import wxFileDialog
                    dlg = wxFileDialog(self.list, 'Save as...', currPath,
                          item.name+'.zexp', '', wxSAVE | wxOVERWRITE_PROMPT)
                    try:
                        if dlg.ShowModal() == wxID_OK:
                            zexpFile = dlg.GetFilePath()
                            open(zexpFile, 'wb').write(zexp)
                            currPath = os.path.dirname(zexpFile)
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

    def doInspectZopeItem(self, zopeItem):
        props = zopeItem.properties
        try:
            ZComp = PaletteStore.compInfo[zopeItem.metatype][1]
        except KeyError:
            ZComp = ZopeCompanion

        zc = ZComp(zopeItem.name, zopeItem.resourcepath)
        zc.connect(props['host'], props['httpport'],
                   props['username'], props['passwd'])
        zc.updateZopeProps()

        # Select in inspector
        if self.inspector.pages.GetSelection() != 1:
            self.inspector.pages.SetSelection(1)
        self.inspector.selectObject(zc, false)

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            zopeItem = self.list.getSelection()
            if not zopeItem: zopeItem = self.list.node
            self.doInspectZopeItem(zopeItem)

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
                                # XXX Update to handle all transports
                                item.uploadObj(open(dlg.GetFilePath(), 'rb'))#.read())
                            except Client.NotFound:
                                wxMessageBox('Object does not support uploading', 'Error on upload')
                            currPath = dlg.GetDirectory()
                    finally:
                        dlg.Destroy()

    def OnSecurityZopeItem(self, event):
        if self.list.node:
            zopeItem = self.list.getSelection()
            if zopeItem:
                model, cntrlr = self.editor.openOrGotoZopeDocument(zopeItem)
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
                model, cntrlr = self.editor.openOrGotoZopeDocument(zopeItem)
                viewName = ZopeViews.ZopeUndoView.viewName
                if not model.views.has_key(viewName):
                    resultView = self.editor.addNewView(viewName,
                          ZopeViews.ZopeUndoView)
                else:
                    resultView = model.views[viewName]
                resultView.refresh()
                resultView.focus()

    def openSelItemInBrowser(self, addToUrl=''):
        if self.list.node:
            zopeItem = self.list.getSelection()
            try:
                import webbrowser
                webbrowser.open('http://%s%s'%(zopeItem.buildUrl(), addToUrl))
            except ImportError:
                raise 'Python 2.0 or higher required'

    def OnViewInBrowser(self, event):
        self.openSelItemInBrowser()

    def OnManageInBrowser(self, event):
        self.openSelItemInBrowser('/manage')

    def OnOpenInEditorZopeItem(self, event):
        if self.list.node:
            zopeItem = self.list.getSelection()
            if zopeItem:
                model, cntrlr = self.editor.openOrGotoZopeDocument(zopeItem)


def getServer(url, user, password):
    return xmlrpclib.Server('http://' + url,
              BasicAuthTransport.BasicAuthTransport(user, password) )

class ZopeNode(ZopeItemNode):
    def load(self, mode='rb'):
        return self.getResource().document_src()

    def save(self, filename, data, mode='wb'):
        """ Saves contents of data to Zope """
        self.getResource().manage_upload(data)

    def isFolderish(self):
        return false

class ZopeImageNode(ZopeNode):
    pass

class DirNode(ZopeItemNode): pass

class UserFolderNode(ZopeItemNode):
    def deleteItems(self, names):
        print 'User Folder delete: %s'%names
#        mime, res = self.clipboard.zc.call(self.resourcepath,
#              'manage_delObjects', ids = names)

class ZopeUserNode(ZopeNode):
    def isFolderish(self):
        return false
    def open(self, editor):
        print 'Should inspect'
        #editor.openOrGotoZopeDocument(self)

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

# Thanks to M. Adam Kendall (akendall) for fixing save
class ZSQLNode(ZopeNode):
    Model = ZopeEditorModels.ZopeSQLMethodModel
    defaultViews = (ZopeViews.ZopeHTMLSourceView,)
    additionalViews = (ZopeViews.ZopeSecurityView, ZopeViews.ZopeUndoView)
    def getParams(self, data):
        return string.split(string.split(data, '<params>')[1], '</params>')[0]
    def getBody(self, data):
        return string.lstrip(string.split(data, '</params>')[1])
    def save(self, filename, data, mode='wb'):
        """ Saves contents of data to Zope """
        props = self.getResource().zoa.props.SQLMethod()
        try:
            title = props['title']
            connection_id = props['connection_id']
            arguments = self.getParams(data)
            template = self.getBody(data)
            self.getResource().manage_edit(title, connection_id, arguments, template)
        except xmlrpclib.ProtocolError, error:
            # Getting a zero content warning is not an error
            if error.errcode != 204:
                raise ExplorerNodes.TransportSaveError(error, filename)
        except Exception, error:
            raise ExplorerNodes.TransportSaveError(error, filename)

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

    def save(self, filename, data, mode='wb'):
        self.getResource().manage_edit(self.name, self.getParams(data),
              self.getBody(data))

##    def getUndoableTransactions(self):
##        from ZopeLib.DateTime import DateTime
##        if self.server._Server__handler == '/':
##            all = eval(self.server.ZOA('undoR/%s' % (self.name) ))
##        else:
##            all = eval(self.server.ZOA('undo'))
##        undos = []
##        for u in all:
##            if self.name == string.split(u['description'], '/')[-2]:
##                undos.append(u)
##        return undos

##    def undoTransaction(self, transactionIds):
##        print self.server.manage_undo_transactions(transactionIds)

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

    def load(self, mode='rb'):
        data = PythonNode.load(self, mode)
        return self.preparedata(data)

    def save(self, filename, data, mode='wb'):
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


    def openTransportFromProperties(self):
        zopePath = self.properties['localpath']

        svr, name = self.getParentResource()
        res = svr.zoa.props.ExternalMethod(name)

        module = res['module']

        emf = ExtMethDlg.ExternalMethodFinder(zopePath)
        extPath = emf.getExtPath(module)

        from Explorers import Explorer
        return Explorer.openEx(extPath)

    def load(self, mode='rb'):
        return self.openTransportFromProperties().load(mode=mode)

    def save(self, filename, data, mode='wb'):
        transp = self.openTransportFromProperties()
        transp.save(transp.currentFilename(), data, mode)

class DTMLDocNode(ZopeNode):
    Model = ZopeEditorModels.ZopeDTMLDocumentModel
    defaultViews = (ZopeViews.ZopeHTMLSourceView,)
    additionalViews = (ZopeViews.ZopeUndoView,
          ZopeViews.ZopeSecurityView, ZopeViews.ZopeHTMLView,)

class DTMLMethodNode(ZopeNode):
    Model = ZopeEditorModels.ZopeDTMLMethodModel
    defaultViews = (ZopeViews.ZopeHTMLSourceView,)
    additionalViews = (ZopeViews.ZopeUndoView,
          ZopeViews.ZopeSecurityView, ZopeViews.ZopeHTMLView)

from Explorers.PrefsExplorer import SourceBasedPrefColNode
class ZopeZ2pySourceBasedPrefColNode(SourceBasedPrefColNode):
    pass

def findBetween(strg, startMarker, endMarker):
    strL = string.lower(strg)
    found = ''
    idx = string.find(strL, startMarker)
    idx2 = -1
    if idx != -1:
        idx2 = string.find(strL, endMarker, idx)
        if idx2 != -1:
            found = strg[idx + len(startMarker)+1: idx2]
    return idx, idx2, found

class ZopeError(Exception):
    def __init__(self, htmlFaultStr):
        self.htmlFault = htmlFaultStr

        # find possible traceback
        idx, idx2, tracebk = findBetween(htmlFaultStr, '<pre>', '</pre>')
        if tracebk:
            tracebk = 'Traceback:\n'+tracebk
        self.traceback = tracebk

        txt = Utils.html2txt(htmlFaultStr)
        self.textFault = '%s\n%s\n' % (txt, tracebk)

        idx, idx1, self.ErrorType = findBetween(txt, 'Error Type:', '\n')
        idx, idx1, self.ErrorValue = findBetween(txt, 'Error Value:', '\n')

    def __str__(self):
        return self.ErrorType and ('%s:%s' % (self.ErrorType, self.ErrorValue)) or self.textFault

#        return self.textFault


def zopeHtmlErr2Strs(faultStr):
    sFaultStr = str(faultStr)
    fs = string.lower(sFaultStr)
    idx = string.find(fs, '<pre>')
    traceBk = ''
    if idx != -1:
        idx2 = string.find(fs, '</pre>', idx)
        if idx2 != -1:
            traceBk = '\nTraceback:\n'+sFaultStr[idx + 5: idx2]
    txt = Utils.html2txt(sFaultStr)
    return txt+traceBk

#-------------------------------------------------------------------------------
# maps meta types to ExplorerNodes
zopeClassMap = { 'Folder': DirNode,
        'Product Help': DirNode,
        'User Folder': UserFolderNode,
        'Control Panel': ControlNode,
        'Z SQL Method': ZSQLNode,
        'DTML Document': DTMLDocNode,
        'DTML Method': DTMLMethodNode,
        'Python Method': PythonNode,
        'External Method': ExtPythonNode,
        'Script (Python)': PythonScriptNode,
        'Image': ZopeImageNode,
        'User': ZopeUserNode,
       }

ExplorerNodes.register(ZopeCatNode, controller=ZopeCatController)
ExplorerNodes.register(ZopeItemNode, clipboard='global',
  confdef=('explorer', 'zope'), controller=ZopeController, category=ZopeCatNode)
