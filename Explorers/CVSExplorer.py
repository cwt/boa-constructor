from wxPython.lib.dialogs import wxScrolledMessageDialog
from wxPython.wx import *
import string, time, stat, os
import ExplorerNodes, EditorModels
from Preferences import IS
import Views.EditorViews

true = 1
false = 0

cvs_environ_vars = ['CVSROOT', 'CVS_RSH', 'HOME']
cvs_environ_ids  = map(lambda x: wxNewId(), range(len(cvs_environ_vars)))

(wxID_CVSUPDATE, wxID_CVSCOMMIT, wxID_CVSADD, wxID_CVSADDBINARY, wxID_CVSREMOVE,
 wxID_CVSDIFF, wxID_CVSLOG, wxID_CVSSTATUS, wxID_FSCVSIMPORT, wxID_FSCVSCHECKOUT,
 wxID_FSCVSLOGIN, wxID_FSCVSLOGOUT, wxID_FSCVSENV, wxID_CVSTAG, wxID_CVSBRANCH,
 wxID_CVSLOCK, wxID_CVSUNLOCK, wxID_CVSTEST) = map(lambda x: wxNewId(), range(18))

cvsFolderImgIdx = 6

def isCVS(filename):
    file = os.path.basename(filename)
    return string.lower(file) == string.lower('cvs') and \
                      os.path.exists(os.path.join(filename, 'Entries')) and \
                      os.path.exists(os.path.join(filename, 'Repository')) and \
                      os.path.exists(os.path.join(filename, 'Root'))

def scramble(str):
    """ Directly but unrecognisably translated from CVS' scramble.c ;) """
    shifts = (0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              114,120, 53, 79, 96,109, 72,108, 70, 64, 76, 67,116, 74, 68, 87,
              111, 52, 75,119, 49, 34, 82, 81, 95, 65,112, 86,118,110,122,105,
              41, 57, 83, 43, 46,102, 40, 89, 38,103, 45, 50, 42,123, 91, 35,
              125, 55, 54, 66,124,126, 59, 47, 92, 71,115, 78, 88,107,106, 56,
              36,121,117,104,101,100, 69, 73, 99, 63, 94, 93, 39, 37, 61, 48,
              58,113, 32, 90, 44, 98, 60, 51, 33, 97, 62, 77, 84, 80, 85,223,
              225,216,187,166,229,189,222,188,141,249,148,200,184,136,248,190,
              199,170,181,204,138,232,218,183,255,234,220,247,213,203,226,193,
              174,172,228,252,217,201,131,230,197,211,145,238,161,179,160,212,
              207,221,254,173,202,146,224,151,140,196,205,130,135,133,143,246,
              192,159,244,239,185,168,215,144,139,165,180,157,147,186,214,176,
              227,231,219,169,175,156,206,198,129,164,150,210,154,177,134,127,
              182,128,158,208,162,132,167,209,149,241,153,251,237,236,171,195,
              243,233,253,240,194,250,191,155,142,137,245,235,163,242,178,152 )

    return 'A'+string.join(map(lambda c,shifts=shifts: chr(shifts[ord(c)]), list(str)), '')

class CVSController(ExplorerNodes.Controller):
    def __init__(self, list):
        self.list = list
        self.menu = wxMenu()
        self.cvsOptions = '-z7'

        self.setupMenu(self.menu, self.list, (\
              (wxID_CVSUPDATE, 'Update', self.OnUpdateCVSItems),
              (wxID_CVSCOMMIT, 'Commit', self.OnCommitCVSItems),
              (-1, '-', None),
              (wxID_CVSADD, 'Add', self.OnAddCVSItems),
              (wxID_CVSADDBINARY, 'Add binary', self.OnAddBinaryCVSItems),
              (wxID_CVSREMOVE, 'Remove', self.OnRemoveCVSItems),
              (-1, '-', None),
              (wxID_CVSDIFF, 'Diff', self.OnDiffCVSItems),
              (wxID_CVSLOG, 'Log', self.OnLogCVSItems),
              (wxID_CVSSTATUS, 'Status', self.OnStatusCVSItems),
              (wxID_CVSTEST, 'TEST', self.OnTest),
              (-1, '-', None),
              (wxID_CVSTAG, 'Tag', self.OnTagCVSItems),
              (wxID_CVSBRANCH, 'Branch', self.OnBranchCVSItems),
              (wxID_CVSLOCK, 'Lock', self.OnLockCVSItems),
              (wxID_CVSLOCK, 'Unlock', self.OnUnlockCVSItems) ))

        self.fileCVSMenu = wxMenu()
        self.setupMenu(self.fileCVSMenu, self.list, (\
              (wxID_FSCVSIMPORT, 'Import', self.OnImportCVSFSItems),
              (wxID_FSCVSCHECKOUT, 'Checkout', self.OnCheckoutCVSFSItems),
              (-1, '-', None),
              (wxID_FSCVSLOGIN, 'Login', self.OnLoginCVS),
              (wxID_FSCVSLOGOUT, 'Logout', self.OnLogoutCVS), 
              (-1, '-', None),
        ))
        
        self.cvsEnvMenu = wxMenu()
        menus = []
        for env, id in map(lambda x, v = cvs_environ_vars, i = cvs_environ_ids: \
            (v[x], i[x]), range(len(cvs_environ_vars))):
              menus.append( (id, env, self.OnEditEnv) )  
        self.setupMenu(self.cvsEnvMenu, self.list, menus)

        self.fileCVSMenu.AppendMenu(wxID_FSCVSENV, 'CVS shell environment vars', self.cvsEnvMenu)

        self.images = wxImageList(16, 16)
        self.images.Add(IS.load('Images/CVSPics/File.bmp'))
        self.images.Add(IS.load('Images/CVSPics/BinaryFile.bmp'))
        self.images.Add(IS.load('Images/CVSPics/ModifiedFile.bmp'))
        self.images.Add(IS.load('Images/CVSPics/ModifiedBinaryFile.bmp'))
        self.images.Add(IS.load('Images/CVSPics/MissingFile.bmp'))
        self.images.Add(IS.load('Images/CVSPics/ConflictingFile.bmp'))
        self.images.Add(IS.load('Images/CVSPics/Dir.bmp'))
        self.images.Add(IS.load('Images/Modules/FolderUp_s.bmp'))
        self.images.Add(IS.load('Images/CVSPics/UnknownDir.bmp'))
        self.images.Add(IS.load('Images/CVSPics/UnknownFile.bmp'))
        
        FSCVSFolderNode.images = self.images

    def __del__(self):
        self.menu.Destroy()
        self.fileCVSMenu.Destroy()
        self.cvsEnvMenu.Destroy()
    
    def setupListCtrl(self):
        self.list.SetWindowStyleFlag(wxLC_REPORT)
        self.list.InsertColumn(0, 'Name', wxLIST_FORMAT_LEFT, 150) 
        self.list.InsertColumn(1, 'Rev.', wxLIST_FORMAT_LEFT, 50)
        self.list.InsertColumn(2, 'Date', wxLIST_FORMAT_LEFT, 150)
        self.list.InsertColumn(3, 'Status', wxLIST_FORMAT_LEFT, 150)
        self.list.InsertColumn(4, 'Options', wxLIST_FORMAT_LEFT, 50)
    
    def cleanupListCtrl(self):
        cols = range(5)
        cols.reverse()
        for col in cols:
            self.list.DeleteColumn(col)
            
    def showMessage(self, cmd, msg):
        dlg = wxScrolledMessageDialog(self.list, msg, cmd)
        try: dlg.ShowModal()
        finally: dlg.Destroy()

    def cvsCmd(self, command, options, files):
        return 'cvs %s %s %s %s' % (self.cvsOptions, command, options, string.join(files, ' '))
    
    def cvsCmdPrompt(self, wholeCommand, inDir, help = ''):
        print help
        dlg = wxTextEntryDialog(self.list, 'CVSROOT: %s\nCVS_RSH: %s\n(in dir %s)\n\n%s'\
              %(os.environ.get('CVSROOT', '(not defined)'), 
                os.environ.get('CVS_RSH', '(not defined)'), inDir, help), 
              'CVS command line', wholeCommand)
        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetValue()
            else:
                return ''
        finally:
            dlg.Destroy()
    
    def getCvsHelp(self, cmd, option = '-H'):
        from popen2import import popen3
        inp, outp, errp = popen3('cvs %s %s'% (option, cmd))
        # remove last line
        return string.join(errp.readlines()[:-1])

    def doCvsCmd(self, cmd, cvsDir, stdinput = ''):
        from popen2import import popen3
            
        cwd = os.getcwd()
        try:
            os.chdir(cvsDir)

            inp, outp, errp = popen3(cmd)

            if stdinput:
                wxBeginBusyCursor()
                try: inp.write(stdinput)
                finally: wxEndBusyCursor()

            outls = []
            wxBeginBusyCursor()
            try:
                while 1:
                    ln = outp.readline()
                    if not ln: break
                    print string.strip(ln)
                    outls.append(ln)
            finally: 
                wxEndBusyCursor()

            wxBeginBusyCursor()
            try: err = errp.read()
            finally: wxEndBusyCursor()
                        
            if string.strip(err):
                dlg = wxMessageDialog(self.list, err,
                  'Server response or Error', wxOK | wxICON_EXCLAMATION)
                try: dlg.ShowModal()
                finally: dlg.Destroy()
                
            if outls:
                self.showMessage(cmd, string.join(outls, ''))

        finally:
            os.chdir(cwd)

    def doCvsCmdOnSelection(self, cmd, cmdOpts, preCmdFunc = None, postCmdFunc = None):
        if self.list.node:
            names = self.getNamesForSelection(self.list.getMultiSelection())
            cvsDir = os.path.dirname(self.list.node.resourcepath)
            if not names: names = ['.']
##                names = ['']
##                cvsDir, names[0] = os.path.split(cvsDir)
            cmdStr = self.cvsCmdPrompt(self.cvsCmd(cmd, cmdOpts, names), cvsDir, 
                  self.getCvsHelp(cmd))
            if cmdStr: 
                if preCmdFunc: preCmdFunc(names)
                self.doCvsCmd(cmdStr, cvsDir)
                if postCmdFunc: postCmdFunc(names)

    def doCvsCmdInDir(self, cmd, cmdOpts, cvsDir, items):
        cmdStr = self.cvsCmdPrompt(self.cvsCmd(cmd, cmdOpts, items), 
              cvsDir, self.getCvsHelp(cmd))
        if cmdStr:
            self.doCvsCmd(cmdStr, cvsDir)

    def importCVSItems(self):
        # Imports are called from normal folders not CVS folders
        
        # XXX Check if CVS folder exists ?
        cvsDir = self.list.node.resourcepath
        self.doCvsCmdInDir('import', '', cvsDir, ['[MODULE]', 'VENDOR', 'RELEASE'])

        self.list.refreshCurrent()


    def checkoutCVSItems(self):
        # Checkouts are called from normal folders not CVS folders
        cvsDir = self.list.node.resourcepath
        self.doCvsCmdInDir('checkout', '-P', cvsDir, ['[MODULE]'])

        self.list.refreshCurrent()
    
    def updateCVSItems(self):
        self.doCvsCmdOnSelection('update', '')
        self.list.refreshCurrent()

    def OnUpdateCVSItems(self, event):
        self.updateCVSItems()
            
    def OnCommitCVSItems(self, event):
        self.doCvsCmdOnSelection('commit', '-m "no message"')
        self.list.refreshCurrent()

    def OnAddCVSItems(self, event):
        self.doCvsCmdOnSelection('add', '')
        self.list.refreshCurrent()

    def OnAddBinaryCVSItems(self, event):
        self.doCvsCmdOnSelection('add', '-kb')
        self.list.refreshCurrent()

    def selPreCmd_remove(self, list):
        dir = os.path.dirname(self.list.node.resourcepath)
        for name in list:
            os.remove(os.path.join(dir, name))

    def OnRemoveCVSItems(self, event):
        self.doCvsCmdOnSelection('remove', '', self.selPreCmd_remove)
        self.list.refreshCurrent()

    def OnDiffCVSItems(self, event):
        self.doCvsCmdOnSelection('diff', '')

    def OnLogCVSItems(self, event):
        self.doCvsCmdOnSelection('log', '')

    def OnStatusCVSItems(self, event):
        self.doCvsCmdOnSelection('status', '')

    def OnImportCVSFSItems(self, event):
        self.importCVSItems()
            
    def OnCheckoutCVSFSItems(self, event): 
        self.checkoutCVSItems()

    def OnTagCVSItems(self, event):
        self.doCvsCmdOnSelection('tag', '[TAG]')

    def OnBranchCVSItems(self, event):
        self.doCvsCmdOnSelection('tag', '-b')

    def OnLockCVSItems(self, event):
        self.doCvsCmdOnSelection('admin', '-l[REV]')

    def OnUnlockCVSItems(self, event):
        self.doCvsCmdOnSelection('admin', '-u[REV]')
    
    def OnLoginCVS(self, event):
        cvsDir = self.list.node.resourcepath
#                self.doCvsCmdInDir('login', '', cvsDir, [], answer + '\n')
        
        # Login can be called from file system folders and cvs folders
        if isinstance(self.list.node, FSCVSFolderNode):
            cvsroot = self.list.node.root
        else:
            if os.environ.has_key('CVSROOT'):
                cvsroot = os.environ['CVSROOT']
            else:
                cvsroot = ''

        cvsroot = self.cvsCmdPrompt(cvsroot, cvsDir, help = 'Change the CVSROOT if necessary:')

        dlg = wxTextEntryDialog(self.list, 'Enter cvs password for '+cvsroot, 'CVS login', '',
              style = wxOK | wxCANCEL | wxCENTRE | wxTE_PASSWORD)
        try:
            if dlg.ShowModal() == wxID_OK:
                password = scramble(dlg.GetValue())
            else:
                return
        finally:
            dlg.Destroy()


        # Read .cvspass file
        if os.environ.has_key('HOME') and os.path.isdir(os.environ['HOME']):
            cvspass = os.path.join(os.environ['HOME'], '.cvspass')
            if os.path.exists(cvspass):
                passfile = open(cvspass, 'r+')
                passwds = passfile.readlines()
            else:
                passfile = open(cvspass, 'w')
                passwds = []
        else:
            raise Exception('HOME env var is not defined or not legal')

        passln = cvsroot + ' ' +password + '\n'
        
        if passln not in passwds:
            passfile.write(passln)
        passfile.close()    
        
    def OnLogoutCVS(self, event):
        cvsDir = self.list.node.resourcepath
        self.doCvsCmdInDir('logout', '', cvsDir, [])
    
    def OnEditEnv(self, event):
        envKey = cvs_environ_vars[cvs_environ_ids.index(event.GetId())]
        envVal = os.environ.get(envKey, '(not defined)')
        dlg = wxTextEntryDialog(self.list, 'Edit CVS shell environment variable: %s\nA blank entry will remove the variable.'% envKey, 
            'CVS shell environment variables', envVal)
        try:
            if dlg.ShowModal() == wxID_OK:
                answer = dlg.GetValue()
                if answer and answer != '(not defined)':
                    try:
                        os.environ[envKey] = answer
                    except:
                        wxMessageBox('Changing environment variables is not supported on this OS\nConsult CVS howtos on how to set these globally')
                else:
                    if os.environ.has_key(envKey):
                        del os.environ[envKey]
        finally:
            dlg.Destroy()
    
    def OnTest(self, event):
        print 'TEST'
#        self.list.SetWindowStyleFlag(wxLC_REPORT)    
        self.setupListCtrl()
    
class CVSFolderNode(ExplorerNodes.ExplorerNode):
    protocol = 'cvs'
    def __init__(self, entriesLine, resourcepath, dirpos, parent):
        if entriesLine:
            name, self.revision, self.timestamp, self.options, self.tagdate = \
              string.split(entriesLine[2:], '/')
        else:
            name=self.revision=self.timestamp=self.options=self.tagdate = ''
    
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, cvsFolderImgIdx, parent)
        
        self.dirpos = dirpos

    def text(self):
        return string.join(('D', self.name, self.revision, self.timestamp, self.options, self.tagdate), '/')

    def isFolderish(self): 
        return false

    def createParentNode(self):
        parent = os.path.abspath(os.path.join(self.resourcepath, '..'))
        return PyFileNode(os.path.basename(parent), parent, self.clipboard,
                  EditorModels.FolderModel.imgIdx, self)

    def open(self, editor):
        tree = editor.explorer.tree
        par = tree.GetItemParent(tree.GetSelection())
        chd = tree.getChildNamed(par, self.name)
        if not tree.IsExpanded(chd):
            tree.Expand(chd)
        cvsChd = tree.getChildNamed(chd, 'CVS')
        tree.SelectItem(cvsChd)
#        editor.openOrGotoModule(self.resourcepath)

class CVSFileNode(ExplorerNodes.ExplorerNode):
    protocol = 'cvs'
    def __init__(self, entriesLine, resourcepath, parent):
        if entriesLine:
            name , self.revision, self.timestamp, self.options, self.tagdate = \
              string.split(string.strip(entriesLine)[1:], '/')
        else:
            name=self.revision=self.timestamp=self.options=self=tagdate = ''

        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, -1, parent)

        self.missing = false
        self.modified = false
        self.conflict = false
        self.imgIdx = 0
        if self.timestamp:
            filename = os.path.abspath(os.path.join(self.resourcepath, '..', name))
            if os.path.exists(filename):
                filets = time.strftime('%a %b %d %H:%M:%S %Y', 
                      time.gmtime(os.stat(filename)[stat.ST_MTIME]))
                self.modified = self.timestamp != filets
                self.conflict = string.split(self.timestamp, '+')[0] == 'Result of merge'
                print name, self.modified
            else:
                self.missing = true
        
        self.imgIdx = self.missing and self.missing << 2 \
                      or (self.options == '-kb' and not self.modified) \
                      or (self.options == '-kb' and self.modified and 3) \
                      or self.conflict *5 or self.modified << 1 

    def isFolderish(self): 
        return false

    def getDescription(self):
        return '%s, (%s, %s)'%(self.name, self.revision, self.timestamp)#, self.options, self.tagdate), '/')

    def open(self, editor):
        tree = editor.explorer.tree
        tree.SelectItem(tree.GetItemParent(tree.GetSelection()))
        editor.explorer.list.selectItemNamed(self.name)
        if self.conflict:
            model = editor.openOrGotoModule(editor.explorer.list.getSelection().resourcepath)
            if not model.views.has_key(CVSConflictsView.viewName):
                resultView = editor.addNewView(CVSConflictsView.viewName, CVSConflictsView)
            else:
                resultView = self.model.views[CVSConflictsView.viewName]
            resultView.refresh()
            resultView.focus()        
        
        
    def text(self):
        return string.join(('', self.name, self.revision, self.timestamp, self.options, self.tagdate), '/')

class CVSUnAddedItem(ExplorerNodes.ExplorerNode):
    def __init__(self, name, resourcepath, parent, isFolder):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, isFolder and 8 or 9, parent)

    def open(self, editor):
        tree = editor.explorer.tree
        tree.SelectItem(tree.GetItemParent(tree.GetSelection()))
        editor.explorer.list.selectItemNamed(self.name)
    
class FSCVSFolderNode(ExplorerNodes.ExplorerNode):
    protocol = 'cvs'
    def __init__(self, name, resourcepath, clipboard, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, 
              EditorModels.CVSFolderModel.imgIdx, parent)
        self.dirpos = 0
        self.upImgIdx = 7
    
    def getDescription(self):
        try:
            return '%s'% (self.root)
        except AttributeError:
            return ExplorerNodes.ExplorerNode.getDescription(self)

    def getTitle(self):
        try:
            return '%s'% (self.repository)
        except AttributeError:
            return ExplorerNodes.ExplorerNode.getTitle(self)

    def isFolderish(self): 
        return true

    def createParentNode(self):
        if self.parent:
            return self.parent
        else:
            parent = os.path.abspath(os.path.join(self.resourcepath, os.path.join('..', 'CVS')))
            return FSCVSFolderNode(os.path.basename(parent), parent, self.clipboard,
                      EditorModels.CVSFolderModel.imgIdx, self)

    def createChildNode(self, txtEntry):
        if not txtEntry or txtEntry == 'D':
            return None
            # XXX Maybe add all dirs?   
        elif txtEntry[0] == 'D':
            return CVSFolderNode(txtEntry, self.resourcepath, self.dirpos, self)
            self.dirpos = self.dirpos + 1
        else:
            try:
                return CVSFileNode(txtEntry, self.resourcepath, self)
            except IOError:
                return None

    def openList(self):
        def readFile(self, name):
            return string.strip(open(os.path.join(self.resourcepath, name)).read())

        self.root = readFile(self, 'Root')
        self.repository = readFile(self, 'Repository')
        self.entries = []

        res = {}
        self.dirpos = 0
        fileEntries = self.parent.openList()
        txtEntries = open(os.path.join(self.resourcepath, 'Entries')).readlines()
        filenames = map(lambda x: x.name, fileEntries)
        missingEntries = []

        for txtEntry in txtEntries:
            cvsNode = self.createChildNode(string.strip(txtEntry))
            if cvsNode:
                res[cvsNode.name] = cvsNode
                if cvsNode.name not in filenames:
                    missingEntries.append(cvsNode)
        
        lst = []         
        for entry in fileEntries:
            node = res.get(entry.name, CVSUnAddedItem(entry.name, entry.resourcepath, self, entry.isFolderish()))    
            if node:
                lst.append(node)
        
        for missing in missingEntries:
            lst.append(missing)
        
        self.entries = lst
        return lst

    def open(self, editor):
        editor.openOrGotoModule(self.resourcepath)

    def openParent(self, editor): 
        tree = editor.explorer.tree
        cvsParentItemParent = tree.GetItemParent(tree.GetItemParent(tree.GetSelection()))

        cvsChd = tree.getChildNamed(cvsParentItemParent, 'CVS')
        if cvsChd.IsOk():
            tree.SelectItem(cvsChd)
            return true
        else:
            return false


#---------------------------------------------------------------------------

class CVSConflictsView(Views.EditorViews.ListCtrlView):
    viewName = 'CVS conflicts'
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    def __init__(self, parent, model):
        Views.EditorViews.ListCtrlView.__init__(self, parent, model, wxLC_REPORT, 
          (('Goto line', self.OnGoto, self.gotoLineBmp, ()),), 0)
        self.InsertColumn(0, 'Rev')
        self.InsertColumn(1, 'Line#')
        self.InsertColumn(2, 'Size')
        self.SetColumnWidth(0, 40)
        self.SetColumnWidth(1, 40)
        self.SetColumnWidth(2, 40)

        self.conflicts = []        

    def refreshCtrl(self):
        Views.EditorViews.ListCtrlView.refreshCtrl(self)
        
        self.conflicts = self.model.getCVSConflicts()

        confCnt = 0
        for rev, lineNo, size in self.conflicts:
            self.InsertStringItem(confCnt, rev)
            self.SetStringItem(confCnt, 1, `lineNo`)
            self.SetStringItem(confCnt, 2, `size`)
            confCnt = confCnt + 1


        self.pastelise()

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            srcView.focus()
            lineNo = int(self.conflicts[self.selected][1]) -1
            print 'Going to line', lineNo
            srcView.gotoLine(lineNo)

