from wxPython.wx import *
import ExplorerNodes, ZopeLib.LoginDialog, EditorModels
import ftplib, os
import urlparse,string
from ZopeLib.ZopeFTP import ZopeFTP
from ExternalLib import xmlrpclib, BasicAuthTransport
from ZopeLib import ImageViewer, Client
from Companions.ZopeCompanions import ZopeConnection, ZopeCompanion, FolderZC
from Preferences import IS, wxFileDialog
import Utils
import Views

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
        self.callAndSetRef(node.whole_name(), 'manage_cutObjects', nodes)
    def clipCopy(self, node, nodes):
        ExplorerNodes.ExplorerClipboard.clipCopy(self, node, nodes)
        self.callAndSetRef(node.whole_name(), 'manage_copyObjects', nodes)
#    def clipPaste(self, node):
#        ExplorerNodes.ExplorerClipboard.clipPaste(self, node)
        
    def clipPaste_ZopeEClip(self, node, nodes, mode):
        mime, res = self.zc.call(node.whole_name(), 
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
    Model = None
    defaultViews = ()
    additionalViews = ()

    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, zftp, zftpi, root, properties):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, properties)
        self.zopeConn = zftp
        self.zopeObj = zftpi
        self.name = name
        self.image=imgIdx
        #test
        self.root = root
        self.cache = []
        self.user=self.properties['username']
        self.pwd=self.properties['passwd']
        self.parent=parent
        #self.item=item
        self.server=zftpi
        self.entries=None
        self.entryIds=None
        self.url=self.buildUrl()
        self.typ = None
        


    def buildUrl(self):
        root = self.root
        tmp=self
        if tmp==root:
            return self.properties['host'] + ":" + str(self.properties['httpport']) +"/"
        url=""
        while tmp!=root:
            url = string.strip(tmp.name) + "/" + url
            tmp = tmp.parent
        url=self.properties['host'] + ":" + str(self.properties['httpport']) + "/" + url
        tmp=url.split("/")
        
        if len(tmp) >=6 :
            if tmp[0] + "/" + tmp[1] + "/" + tmp[2] + "/" == self.properties['host'] + ":" + str(self.properties['httpport']) + "/Control_Panel/Products/":
                #tmp.insert(6,"propertysheets/methods")
                # XXX Check out from the fucking trailing blanks are coming
                tmp[4]=tmp[4] + "/propertysheets/methods"
                #tmp[:-2]=string.strip(tmp[:-2])
                url=string.join(tmp,"/")#[:-2]+"/"
#        wxLogMessage("request " +string.join(tmp,"/"))    
#        wxLogMessage(url)
        ## tmp=urlparse.urlparse("http://" + url)
        ## if tmp[2] == "" : url=url +  "/"
        
        return url
    
    
    def destroy(self):
        self.cache = {}
    
    def canAdd(self, paletteName):
        return paletteName == 'Zope'

    def createChildNode(self,typ,id):
        # XXX Append All my Icons correctly
        # CheckEntry Code here !
        if self.path =="/":
            tmppath = self.path +  id
        else:
            tmppath = self.path + '/' + id
        itm = self.checkentry(id,typ,tmppath)
        
        itm.typ=typ
        
        if EditorModels.ZOAIcons.has_key(typ):
            itm.imgIdx=EditorModels.ZOAIcons[typ]
        else:
            itm.imgIdx=EditorModels.ZOAIcons["unknown"]
        return itm
        
    def checkentry(self,id,entry,path):
##        if  entry == 'Folder'  or entry == 'Product Help':
##            childnode=DirNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'User Folder':
##            childnode=UserFolderNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'Control Panel':
##            childnode=ControlNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'Local File System' or entry == 'Local Directory' or entry == 'directory':
##            childnode=LFSNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'Z SQL Method':
##            childnode=ZSQLNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'DTML Document':
##            childnode=DTMLDocNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'DTML Method':
##            childnode=DTMLMethodNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'Python Method':
##            childnode=PythonNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        elif entry == 'External Method':
##            childnode=ExtPythonNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)    
##        elif entry == 'Script (Python)':
##            childnode=PythonScriptNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)    
##        else:
##            childnode=ZopeItemNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
##        return childnode

         ZopeNodeClass = zopeClassMap.get(entry, ZopeItemNode)
         return apply(ZopeNodeClass, (id, path, self.clipboard, -1, self, 
             self.zopeConn, self.server, self.root, self.properties))
        
    def whole_name(self):
        tmp1=self.buildUrl()
        tmp=urlparse.urlparse("http://" + tmp1)
        self.path=tmp[2]
        return tmp[2]
            
        
    def openList(self, root = None):
        
        tmp=urlparse.urlparse("http://" + self.url)
        self.path=tmp[2]
        self.server=getServer(self.url,"",self.user,self.pwd)
        try:
            self.entries = self.server.ZOA("getvalues")
            self.entryIds= self.server.ZOA("objectids")
        except xmlrpclib.Fault,f:
            # XXX Add Errorhandler here
            pass
        self.cache = {}
        result = []
        if self.entryIds:
            if not root: root = self.root
            
            for i in range(len(self.entries)):
                z = self.createChildNode(self.entries[i],self.entryIds[i])
                if z:
                    result.append(z)
                    self.cache[self.entryIds[i]] = z
        return result 
    
    def getDocument(self):
        #self.data = self.zopeConn.load(self)
        self.data = self.server.__getattr__(self.name).document_src()
        print "correct"
        return self.data
    
    def saveDocument(self,data):
        self.data = data
        #self.zopeConn.save(self,self.data)
        self.server.__getattr__(self.name).manage_upload(self.data)
        pass
        
    def isFolderish(self): 
        return true

    def getTitle(self):
        return 'Zope - '+self.whole_name()

    def open(self, editor):
        editor.openOrGotoZopeDocument(self)   #self.zopeConn,self.zopeObj)

    def deleteItems(self, names):
        mime, res = self.clipboard.zc.call(self.whole_name(), 
              'manage_delObjects', ids = names)

    def renameItem(self, name, newName):
        mime, res = self.clipboard.zc.call(self.whole_name(), 
              'manage_renameObject', id = name, new_id = newName)

    def exportObj(self):
        mime, res = self.clipboard.zc.call(self.whole_name(), 
              'manage_exportObject', download = 1)
        return res

    def uploadObj(self, content):
        mime, res = self.clipboard.zc.call(self.whole_name(), 
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
            mime, res = self.clipboard.zc.call(self.whole_name(), 'manage_importObject', file = name)
            print res
        except Exception, message:
            wxMessageBox(`message.args`, 'Error on import')
            #raise

    def newItem(self, name, Compn, getNewValidName = true):
        props = self.root.properties
        if getNewValidName:
            name = Utils.getValidName(self.cache.keys(), name)
        cmp = Compn(name, self.whole_name(), props.get('localpath', ''))
        cmp.connect(props['host'], props['httpport'], 
                    props['username'], props['passwd'])
        cmp.create()
        
        return cmp.name
    # I put the ZopeFTPItem functions in here. When subclassing I need to overwrite
    
    def cmd(self, cmd):
        pd=self.path[0:-1]
        return '%s %s' % (cmd, pd)
    
    def prepareAsFile(self, data):
        self.lines = string.split(data, '\n')
        self.lines.reverse()
 
    def readline(self):
        try: return self.lines.pop()+'\n'
        except IndexError: return ''

class ZopeConnectionNode(ZopeItemNode):
    protocol = 'zope'
    def __init__(self, name, properties, clipboard, parent):
        zopeConn = ZopeFTP()
        zopeObj = getServer(properties['host'] + ":" + str(properties['httpport']) + "/","",properties['username'],properties['passwd'])
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
                # XXX AutoImport
                #Can't work with zexp files :( must make it manually.. later
                #try:
                #    self.importObj('BOA_Ext.zexp')
                #except:
                #    pass    
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
                        

def getServer(host,Url,User,Password):
    try:
        if Url != "":
            s=xmlrpclib.Server("http://" + host + "/" + Url,BasicAuthTransport.BasicAuthTransport(User,Password) )
        else:
            s=xmlrpclib.Server("http://" + host ,BasicAuthTransport.BasicAuthTransport(User,Password) )
        return s 
    except:
        return "error"

class ZopeNode(ZopeItemNode):        
    def isFolderish(self): 
        return false

       
class DirNode(ZopeNode):

    def isFolderish(self): 
        return true
    

class UserFolderNode(ZopeNode):
    pass

class ControlNode(DirNode):
    
    def checkentry(self,id,entry,path):

        if entry == 'Product Management':
            childnode=PMNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
        
        else:
            childnode=DirNode.checkentry(self,id,entry,path)
        return childnode
    
class PMNode(ControlNode):
    
    def checkentry(self,id,entry,path):

        if entry == 'Product' :
            childnode=ProductNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
        else:
            childnode=ControlNode.checkentry(self,id,entry,path)
        return childnode
    
class ProductNode(DirNode):
    
    def checkentry(self,id,entry,path):

        if entry == 'Z Class' :
            childnode=ZClassNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
        else:
            childnode=DirNode.checkentry(self,id,entry,path)
        return childnode
    
class ZClassNode(DirNode):
    
    pass        


    
class ZSQLNode(ZopeNode):
    pass

class PythonNode(ZopeNode):
    Model = EditorModels.ZopePythonScriptModel
    defaultViews = (Views.PySourceView.PythonSourceView,)
    additionalViews = ()

      #manage_edit("newschas","self,p","return 'hello'"
    def getParams(self):
        return self.data[string.find(self.data,"(")+1:string.find(self.data,")")]    
    def getBody(self):
        tmp = string.split(self.data[string.find(self.data,":")+2:],"\n")
        tmp2=[]
        for  l in tmp:
            l = l[4:]
            tmp2.append(l)
        return string.join(tmp2,'\n')
    
    def saveDocument(self,data):
        self.data = data
        eatandforget=self.server.__getattr__(self.name).manage_edit(self.name,self.getParams(),self.getBody())
    
class PythonScriptNode(PythonNode):
   
    def preparedata(self):
        tmp=string.split(self.rawdata,"\n")
        tmp2=[]
        h=1
        for l in tmp:
            if l[:2] <> "##" : 
                h=0
            if l[:12] == "##parameters": 
                params=l[string.find(l,"=")+1:]
            if h:
                pass # perhaps we need this anytime
            else:
                tmp2.append("    " + l)
        return "def %s(%s):\n%s" % (self.name, params, string.join(tmp2,"\n"))
    def saveDocument(self,data):
        self.data = data
        # I wonder why the write function doesn't work :(
        eatandforget=self.server.__getattr__(self.name).ZPythonScriptHTML_editAction("fake",self.name,self.getParams(),self.getBody())
    
    def getDocument(self):
        #self.data = self.zopeConn.load(self)
        self.rawdata = self.server.__getattr__(self.name).document_src()
        self.data = self.preparedata()
        return self.data    

class ExtPythonNode(ZopeNode):
    pass

class DTMLDocNode(ZopeNode):
    Model = EditorModels.ZopeDocumentModel
    defaultViews = (Views.PySourceView.HTMLSourceView,)
    additionalViews = (Views.EditorViews.ZopeHTMLView,)

class DTMLMethodNode(ZopeNode):
    Model = EditorModels.ZopeDocumentModel
    defaultViews = (Views.PySourceView.HTMLSourceView,)
    additionalViews = (Views.EditorViews.ZopeHTMLView,)
            
class LFSNode(DirNode):
    
    def checkentry(self,id,entry,path):
        print entry
        if entry == 'directory' or entry == 'Local Directory':
            childnode=LFDirNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
        else:
            childnode=LFNode(id, path, self.clipboard, -1,self, self.zopeConn, self.server, self.root, self.properties)
        return childnode
            
class LFNode(LFSNode):
    def isFolderish(self): 
        return false
    
class LFDirNode(LFSNode):
    def isFolderish(self): 
        return true   

zopeClassMap = { 'Folder': DirNode, 'Product Help': DirNode,
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
       }
    