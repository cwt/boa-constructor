import ExplorerNodes, EditorModels
import string, os
from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform

true = 1
false = 0


##(wxID_FSOPEN, wxID_FSTEST, wxID_FSNEW, wxID_FSNEWFOLDER, wxID_FSCVS ) \
## = map(lambda x: wxNewId(), range(5))

class SSHController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()

        self.setupMenu(self.menu, self.list, self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]
        
        
class SSHCatNode(ExplorerNodes.CategoryNode):
    defName = 'SSH'
    defaultStruct = {'username': '',
                     'cipher': '',
                     'host': '',
                     'scp_pass': '',
                     'root': '~'}
    def __init__(self, clipboard, config, parent):
        ExplorerNodes.CategoryNode.__init__(self, 'SSH', ('explorer', 'ssh'),
              clipboard, config, parent)

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        return SSHItemNode(name, props, props['root'], self.clipboard, true, 
              EditorModels.imgFSDrive, self)
        
    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp

class SSHItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'ssh'
    def __init__(self, name, props, resourcepath, clipboard, isFolder, imgIdx, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, props)
        self.isFolder = isFolder

    def isFolderish(self):
        return self.isFolder

    def createChildNode(self, name, isFolder, props):
        return SSHItemNode(name, props, self.resourcepath+'/'+name, self.clipboard, 
              isFolder, isFolder and EditorModels.FolderModel.imgIdx or \
              EditorModels.TextModel.imgIdx, self)
        
    def openList(self):
        from popen2import import popen3

        res = []
        inp, outp, errp = popen3(self.sshCmd('ls %s -la' % self.resourcepath))
        
        print 'STDERR:', errp.read()
            
        ls = outp.readlines()[1:]
        for line in ls:
            name = string.strip(string.split(line, ' ')[-1])
            if name not in ('.', '..'):
                res.append(self.createChildNode(name, line[0] == 'd', self.properties))
        return res
    
    def sshCmd(self, command):
        return 'ssh -l %(username)s -c %(cipher)s %(host)s '% self.properties + command
    
    def remotePath(self, filename):
        return '%(username)s@%(host)s:'%self.properties + self.resourcepath+\
               (filename and '/'+filename or '')
    
    def execSCP(self, cmd):
        from popen2import import popen3

        res = []
        inp, outp, errp = popen3(cmd)
        ls = outp.read()
        print ls
    
    def copyFromFS(self, fsNode):
        fn = os.path.basename(fsNode.resourcepath)
        cmd = 'pscp -pw %s %s %s' %(self.properties['scp_pass'], 
              fsNode.resourcepath,  self.remotePath(fn))
        self.execSCP(cmd)

    def copyToFS(self, fsFolderNode):
        fn = os.path.basename(self.resourcepath)
        cmd = 'pscp -pw %s %s %s' %(self.properties['scp_pass'], 
              self.remotePath(''), os.path.join(fsFolderNode.resourcepath, fn))
        self.execSCP(cmd)

class SSHExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode): 
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
#                node.moveFileFrom(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)
#                node.copyFileFrom(clipnode)

    def clipPaste_SSHExpClipboard(self, node, nodes, mode):
        pass
##        for sshNode in nodes:
##            if mode == 'cut':
##                node.moveFileFrom(clipnode)
##                self.clipNodes = []
##            elif mode == 'copy':
##                node.copyFileFrom(clipnode)


    
