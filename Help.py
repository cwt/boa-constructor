#----------------------------------------------------------------------
# Name:        Help.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999, rewritten 2001
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2005 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:FramePanel:PyDocHelpPage

import os, sys, marshal, string, socket, webbrowser

from wxPython.wx import *
from wxPython.html import *
from wxPython.htmlhelp import *
from wxPython.lib.anchors import LayoutAnchors

import Preferences, Utils

[wxID_PYDOCHELPPAGE, wxID_PYDOCHELPPAGEBOXRESULTS, 
 wxID_PYDOCHELPPAGEBTNSEARCH, wxID_PYDOCHELPPAGEBTNSTOP, 
 wxID_PYDOCHELPPAGECHKRUNSERVER, wxID_PYDOCHELPPAGEPNLSTATUS, 
 wxID_PYDOCHELPPAGESTXSTATUS, wxID_PYDOCHELPPAGETXTSEARCH, 
] = map(lambda _init_ctrls: wxNewId(), range(8))

class PyDocHelpPage(wxPanel):
    def _init_utils(self):
        # generated method, don't edit
        self.scrBrowse = wxStockCursor(id=wxCURSOR_HAND)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPanel.__init__(self, id=wxID_PYDOCHELPPAGE, name='PyDocHelpPage',
              parent=prnt, pos=wxPoint(443, 285), size=wxSize(259, 456),
              style=wxTAB_TRAVERSAL)
        self._init_utils()
        self.SetClientSize(wxSize(251, 429))
        self.SetAutoLayout(True)

        self.txtSearch = wxTextCtrl(id=wxID_PYDOCHELPPAGETXTSEARCH,
              name='txtSearch', parent=self, pos=wxPoint(10, 10),
              size=wxSize(231, 21), style=0, value='')
        self.txtSearch.SetConstraints(LayoutAnchors(self.txtSearch, True, True,
              True, False))
        self.txtSearch.SetToolTipString('Enter name to search for')
        EVT_TEXT_ENTER(self.txtSearch, wxID_PYDOCHELPPAGETXTSEARCH,
              self.OnTxtsearchTextEnter)

        self.boxResults = wxListBox(choices=[], id=wxID_PYDOCHELPPAGEBOXRESULTS,
              name='boxResults', parent=self, pos=wxPoint(2, 89),
              size=wxSize(247, 338), style=0, validator=wxDefaultValidator)
        self.boxResults.SetConstraints(LayoutAnchors(self.boxResults, True,
              True, True, True))
        EVT_LISTBOX(self.boxResults, wxID_PYDOCHELPPAGEBOXRESULTS,
              self.OnBoxresultsListboxDclick)

        self.btnSearch = wxButton(id=wxID_PYDOCHELPPAGEBTNSEARCH,
              label='Search', name='btnSearch', parent=self, pos=wxPoint(89,
              41), size=wxSize(75, 23), style=0)
        self.btnSearch.SetConstraints(LayoutAnchors(self.btnSearch, False, True,
              True, False))
        EVT_BUTTON(self.btnSearch, wxID_PYDOCHELPPAGEBTNSEARCH,
              self.OnBtnsearchButton)

        self.btnStop = wxButton(id=wxID_PYDOCHELPPAGEBTNSTOP, label='Stop',
              name='btnStop', parent=self, pos=wxPoint(166, 41), size=wxSize(75,
              23), style=0)
        self.btnStop.SetConstraints(LayoutAnchors(self.btnStop, False, True,
              True, False))
        self.btnStop.Enable(False)
        EVT_BUTTON(self.btnStop, wxID_PYDOCHELPPAGEBTNSTOP,
              self.OnBtnstopButton)

        self.chkRunServer = wxCheckBox(id=wxID_PYDOCHELPPAGECHKRUNSERVER,
              label='Server', name='chkRunServer', parent=self, pos=wxPoint(3,
              72), size=wxSize(73, 13), style=0)
        self.chkRunServer.SetValue(self.runServer)
        EVT_CHECKBOX(self.chkRunServer, wxID_PYDOCHELPPAGECHKRUNSERVER,
              self.OnChkrunserverCheckbox)

        self.pnlStatus = wxPanel(id=wxID_PYDOCHELPPAGEPNLSTATUS,
              name='pnlStatus', parent=self, pos=wxPoint(80, 72),
              size=wxSize(168, 16), style=wxTAB_TRAVERSAL | wxNO_BORDER)

        self.stxStatus = wxStaticText(id=wxID_PYDOCHELPPAGESTXSTATUS,
              label='Server not running ', name='stxStatus',
              parent=self.pnlStatus, pos=wxPoint(0, 0), size=wxSize(168, 16),
              style=wxST_NO_AUTORESIZE | wxALIGN_RIGHT)
        self.stxStatus.SetConstraints(LayoutAnchors(self.stxStatus, True, True,
              True, False))
        EVT_LEFT_DOWN(self.stxStatus, self.OnStxstatusLeftDown)

    def __init__(self, parent, helpFrame):
        #print 'creating new PyDocPage'
        self.runServer = False
        self.runServer = helpFrame.pdRunServer
        
        self._init_ctrls(parent)
        
        self.helpFrame = helpFrame
        
        self.scanner = None
        self.server = self.helpFrame.controller.server = None
        self.url = ''

        self.statusHyperlinked = 0
        self.waiting = 0

        if self.runServer:
            self.chkRunServer.Disable()
            self.startPydocServer()
        
    def startPydocServer(self):
        # silence warnings
        import warnings
        warnings.filterwarnings('ignore', '', DeprecationWarning, 'pydoc')

        self.stxStatus.SetLabel('Starting pydoc server... ')

        if not testPydocServerAddress('localhost', 7464):
            self.stxStatus.SetLabel('Address in use, ')            

            self.chkRunServer.Enable(True)
            self.chkRunServer.SetValue(False)
            self.runServer = False

            self.url = 'http://localhost:%d/'%7464
        else:    
            self.waiting = 1
            import threading, pydoc
            threading.Thread(
                target=pydoc.serve, args=(7464, self.OnServerReady, 
                    self.OnServerQuit)).start()

    # called from thread
    def OnServerReady(self, server):
        if self and self.helpFrame:
            self.server = self.helpFrame.controller.server = server
            self.url = server.url
            self.runServer = True
            self.waiting = 0

            Utils.wxCallAfter(self.chkRunServer.Enable, True)
            Utils.wxCallAfter(self.chkRunServer.SetValue, True)
            Utils.wxCallAfter(self.hyperlinkLabel, 
                              'http://localhost:%d/'%server.server_port)


    # called from thread
    def OnServerQuit(self):
        if self and self.stxStatus:
            self.server.server_close()
            self.server = None
            self.runServer = False
            self.url = ''
            self.waiting = 0

            Utils.wxCallAfter(self.chkRunServer.Enable, True)
            Utils.wxCallAfter(self.chkRunServer.SetValue, False)
            Utils.wxCallAfter(self.stxStatus.SetLabel, 'Server quit. ')

    def OnBtnsearchButton(self, event):
        self.doSearch()

    def OnBtnstopButton(self, event):
        self.doStop()

    def doSearch(self):
        key = self.txtSearch.GetValue()
        self.btnStop.Enable(True)
        self.boxResults.Clear()

        import threading, pydoc
        if self.scanner:
            self.scanner.quit = 1
        self.scanner = pydoc.ModuleScanner()
        threading.Thread(target=self.scanner.run,
                         args=(self.OnUpdateResults, key, 
                               self.OnFinishedResults)).start()

    # called from thread
    def OnUpdateResults(self, path, modname, desc):
        if self:
            if modname[-9:] == '.__init__':
                modname = modname[:-9] + ' (package)'
            Utils.wxCallAfter(self.boxResults.Append, 
                              modname + ' - ' + (desc or '(no description)'))

    def doStop(self):
        if self and self.scanner:
            self.scanner.quit = 1
            self.scanner = None

    # called from thread
    def OnFinishedResults(self):
        if self:
            self.scanner = None
            Utils.wxCallAfter(self.btnStop.Disable)

    def OnBoxresultsListboxDclick(self, event):
        selection = self.boxResults.GetStringSelection()
        if selection and self.url:
            modname = selection.split()[0]
            self.helpFrame.html.LoadPage(self.url + modname + '.html')

    def OnTxtsearchTextEnter(self, event):
        self.doSearch()

    def OnChkrunserverCheckbox(self, event):
        self.chkRunServer.Disable()

        self.runServer = event.IsChecked()

        if self.runServer:
            self.startPydocServer()
        else:
            if self.server:
                self.restoreLabel('Stopping server...')
                self.server.quit = 1
                self.server.server_close()
    
    def hyperlinkLabel(self, text):
        f = self.stxStatus.GetFont()
        f.SetUnderlined(1)
        self.stxStatus.SetFont(f)
        self.stxStatus.SetForegroundColour(wxColour(0x11,0x22,0x88))
        self.stxStatus.SetLabel(text)
        self.pnlStatus.SetCursor(self.scrBrowse)
        self.statusHyperlinked = 1
            
    def restoreLabel(self, text):
        f = self.stxStatus.GetFont()
        f.SetUnderlined(0)
        self.stxStatus.SetFont(f)
        self.stxStatus.SetForegroundColour(wxBLACK)
        self.stxStatus.SetLabel(text)
        self.pnlStatus.SetCursor(wxSTANDARD_CURSOR)
        self.statusHyperlinked = 0
            
    def OnStxstatusLeftDown(self, event):
        if self.statusHyperlinked:
            webbrowser.open(self.stxStatus.GetLabel())


#-------------------------------------------------------------------------------


def tagEater(strg):
    res = ''
    inTag = 0
    for i in range(len(strg)-1, -1, -1):
        if strg[i] == '>':
            inTag = 1
            continue
        elif strg[i] == '<':
            inTag = 0
            continue
        if not inTag:
            res = strg[i] + res
    return res

def showMainHelp(bookname):
    getHelpController().Display(bookname).ExpandBook(bookname)

def showCtrlHelp(wxClass, method=''):
    getHelpController().Display(wxClass).ExpandCurrAsWxClass(method)

def showHelp(filename):
    getHelpController().Display(filename)

def showContextHelp(word):
    if word.startswith('EVT_'):
        word = 'wx%sEvent' % string.join(map(lambda s: string.capitalize(string.lower(s)),
                                string.split(word[4:], '_')), '')
    elif word in sys.builtin_module_names:
        word = '%s (built-in module)'%word
    else:
        try:
            libPath = os.path.dirname(os.__file__)
        except AttributeError, error:
            pass
        else:
            if os.path.isfile('%s/%s.py'%(libPath, word)):
                word = '%s (standard module)'%word
    if string.strip(word):
        getHelpController().Display(word).IndexFind(word)
    else:
        getHelpController().DisplayContents()

def decorateWxPythonWithDocStrs(dbfile):
    namespace = Utils.getEntireWxNamespace()

    try:
        db = marshal.load(open(dbfile, 'rb'))
    except IOError:
        print 'wxPython Doc strings: %s failed to load'%dbfile
    else:
        for name, doc in db['classes'].items():
            try:
                wxClass = namespace[name]
                wxClass.__doc__ = doc

                wxClass = namespace[name+'Ptr']
                wxClass.__doc__ = doc
            except:
                pass

        for name, doc in db['methods'].items():
            try:
                cls, mth = string.split(name, '.')
                wxMeth = getattr(namespace[cls], mth)
                wxMeth.im_func.__doc__ = doc

                wxMeth = getattr(namespace[cls+'Ptr'], mth)
                wxMeth.im_func.__doc__ = doc
            except:
                pass

class wxHtmlHelpControllerEx(wxHtmlHelpController):
    frameX = None
    def Display(self, text):
        wxHtmlHelpController.Display(self, text)
        if not self.frameX:
            self.frameX = wxHelpFrameEx(self)
        #frameX.restore()
        frame = self.frameX.frame
        if not frame.IsShown():
            frame.Show(True)
        if frame.IsIconized():
            frame.Iconize(False)
        frame.Raise()
        return self.frameX

    def UseConfig(self, config):
        # Fix config file if stored as minimised
        if config.ReadInt('hcX') == -32000:
            map(config.DeleteEntry, ('hcX', 'hcY', 'hcW', 'hcH'))

        wxHtmlHelpController.UseConfig(self, config)
        
        self.config = config

class _CloseEvtHandler(wxEvtHandler):
    def __init__(self, frameEx):
        wxEvtHandler.__init__(self)
        EVT_CLOSE(frameEx.frame, self.OnClose)
        self.frameEx = frameEx
        self.frame = frameEx.frame

    def OnClose(self, event):
        if hasattr(self.frameEx, 'pydocPage') and self.frameEx.pydocPage:
            config = self.frameEx.controller.config
            config.WriteInt('pdRunServer', self.frameEx.pydocPage.runServer)
            config.Flush()

        # catching the close event when running standalone
        if __name__ == '__main__':
            if not canClosePydocServer():
                if pydocWarning():
                    return
            event.Skip()
            self.frame.PopEventHandler().Destroy()

        self.frame.Hide()

wxID_COPYTOCLIP = wxNewId()

# Note, this works nicely because of OOR
class wxHelpFrameEx:
    def __init__(self, helpctrlr):
        self.controller = helpctrlr
        self.frame = helpctrlr.GetFrame()
        #self.frame.frameEx = self

        wxID_QUITHELP, wxID_FOCUSHTML = wxNewId(), wxNewId()
        EVT_MENU(self.frame, wxID_QUITHELP, self.OnQuitHelp)
        EVT_MENU(self.frame, wxID_FOCUSHTML, self.OnFocusHtml)

        self.frame.PushEventHandler(_CloseEvtHandler(self))

        # helpfrm.cpp defines no accelerators so this is ok
        self.frame.SetAcceleratorTable(
              wxAcceleratorTable([(0, WXK_ESCAPE, wxID_QUITHELP),
                                  (wxACCEL_CTRL, ord('H'), wxID_FOCUSHTML),]))

        _none, self.toolbar, self.splitter = self.frame.GetChildren()

        self.html, nav = self.splitter.GetChildren()

        # handle 2.3.3 change
        if isinstance(nav, wxNotebookPtr):
            self.navPages = nav

            # Extend toolbar
            if self.toolbar.GetToolShortHelp(wxID_COPYTOCLIP) != \
                  'Copy contents as text to clipboard':
                self.toolbar.AddSeparator()
                self.copyToClipId = wxID_COPYTOCLIP
                self.toolbar.AddTool(id = self.copyToClipId, isToggle=0,
                    bitmap=Preferences.IS.load('Images/Shared/CopyHelp.png'),
                    pushedBitmap=wxNullBitmap,
                    shortHelpString='Copy contents as text to clipboard',
                    longHelpString='')
                EVT_TOOL(self.frame, self.copyToClipId, self.OnCopyPage)
                self.toolbar.Realize()

        else:
            self.navPages = nav.GetChildren()[0]

        assert self.navPages.GetPageText(0) == 'Contents'
        self.contentsPanel = self.navPages.GetPage(0)

        self.contentsAddBookmark, self.contentsDelBookmark, \
              self.contentsChooseBookmark, self.contentsTree = \
              self.contentsPanel.GetChildren()

        assert self.navPages.GetPageText(1) == 'Index'
        self.indexPanel = self.navPages.GetPage(1)

        self.indexTextCtrl, btn1, btn2 = \
              self.indexPanel.GetChildren()[:3]

        # done this way to work on 2.3.2 and 2.3.3
        if btn1.GetLabel() == 'Show all':
            self.indexShowAllBtn, self.indexFindBtn = btn1, btn2
        else:
            self.indexShowAllBtn, self.indexFindBtn = btn2, btn1

        if Preferences.usePydocHelp and self.navPages.GetPageCount() == 3:
            self.pdRunServer = self.controller.config.ReadInt('pdRunServer', False)

            self.pydocPage = PyDocHelpPage(self.navPages, self)
            self.navPages.AddPage(self.pydocPage, 'Pydoc')
        else:
            self.pydocPage = None
            
##    def restore(self):
##        Utils.FrameRestorerMixin.restore(self.frame)

    def IndexFind(self, text):
        self.controller.DisplayIndex()
        self.indexTextCtrl.SetValue(text)

        wxPostEvent(self.frame, wxCommandEvent(wxEVT_COMMAND_BUTTON_CLICKED,
              self.indexFindBtn.GetId()))

    def ShowNavPanel(self, show = true):
        if show:
            self.splitter.SplitVertically(self.navPages, self.html)
        else:
            self.splitter.Unsplit(self.navPages)

    def ExpandBook(self, name):
        self.navPages.SetSelection(0)
        rn = self.contentsTree.GetRootItem()
        nd, ck = self.contentsTree.GetFirstChild(rn)
        while nd.IsOk():
            if self.contentsTree.GetItemText(nd) == name:
                self.contentsTree.Expand(nd)
                break
            nd, ck = self.contentsTree.GetNextChild(rn, ck)

    def ExpandCurrAsWxClass(self, anchor):
        self.navPages.SetSelection(0)
        self.contentsTree.Expand(self.contentsTree.GetSelection())
        page = self.html.GetOpenedPage()
        if anchor:
            self.controller.Display('%s#%s' % (page, string.lower(anchor)))

    def OnQuitHelp(self, event):
        self.frame.Close()

    def OnFocusHtml(self, event):
        self.html.SetFocus()

    def OnCopyPage(self, event):
        Utils.writeTextToClipboard( Utils.html2txt(
                open(self.html.GetOpenedPage()).read()))

wxHF_TOOLBAR                = 0x0001
wxHF_CONTENTS               = 0x0002
wxHF_INDEX                  = 0x0004
wxHF_SEARCH                 = 0x0008
wxHF_BOOKMARKS              = 0x0010
wxHF_OPEN_FILES             = 0x0020
wxHF_PRINT                  = 0x0040
wxHF_FLAT_TOOLBAR           = 0x0080
wxHF_MERGE_BOOKS            = 0x0100
wxHF_ICONS_BOOK             = 0x0200
wxHF_ICONS_BOOK_CHAPTER     = 0x0400
wxHF_ICONS_FOLDER           = 0x0000
wxHF_DEFAULT_STYLE          = (wxHF_TOOLBAR | wxHF_CONTENTS | wxHF_INDEX | \
                               wxHF_SEARCH | wxHF_BOOKMARKS | wxHF_PRINT)

_hc = None

def getHelpController():
    if not _hc:
        initHelp()
    return _hc

def getCacheDir():
    cacheDir = os.path.join(Preferences.rcPath, 'docs-cache')
    if not os.path.isdir(cacheDir):
        cacheDir = os.path.join(Preferences.pyPath, 'Docs', 'cache')
    return cacheDir

# needed for .htb files
wxFileSystem_AddHandler(wxZipFSHandler())

def initHelp(calledAtStartup=false):
    jn = os.path.join
    docsDir = jn(Preferences.pyPath, 'Docs')

    global _hc
    _hc = wxHtmlHelpControllerEx(wxHF_ICONS_BOOK_CHAPTER | \
        wxHF_DEFAULT_STYLE | (Preferences.flatTools and wxHF_FLAT_TOOLBAR or 0))
    cf = wxFileConfig(localFilename=os.path.normpath(jn(Preferences.rcPath,
        'helpfrm.cfg')), style=wxCONFIG_USE_LOCAL_FILE)
    _hc.UseConfig(cf)

    cacheDir = getCacheDir()
    _hc.SetTempDir(cacheDir)

    conf = Utils.createAndReadConfig('Explorer')
    books = eval(conf.get('help', 'books'), {})
    for book in books:
        if calledAtStartup:
            print 'Help: loading %s'% os.path.basename(book)
        bookPath = os.path.normpath(jn(docsDir, book))
        if os.path.exists(bookPath):
            _hc.AddBook(bookPath,
                  not os.path.exists(jn(cacheDir,
                  os.path.basename(book)+'.cached')) or not calledAtStartup)

def initWxPyDocStrs():
    docStrs = os.path.join(Preferences.pyPath, 'Docs', 'wxDocStrings.msh')
    decorateWxPythonWithDocStrs(docStrs)


def pydocWarning():
    return wxMessageBox('The pydoc server has not completely started up yet,\n '
                        'it is safer to wait for it to finish before shutting '
                        'down.\n\nDo you want to wait?', 'Pydoc server busy', 
                        wxYES_NO | wxICON_EXCLAMATION) == wxYES

def canClosePydocServer():
    if _hc:
        f = _hc.frameX
        if f and f.pydocPage and f.pydocPage.waiting:
            return False
    return True

def testPydocServerAddress(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        try:
            sock.bind((host, port))
        except socket.error, (code, msg):
            if code == 10048: # address in use
                return False
            raise
    finally:
        sock.close()
    return True

def delHelp():
    global _hc
    if _hc:
        _hc.config.Flush()
        if hasattr(_hc, 'server') and _hc.server and not _hc.server.quit:
            _hc.server.quit = 1
            _hc.server.server_close()
        
        f = _hc.GetFrame()
        if f:
            f.PopEventHandler().Destroy()
            f.Destroy()
        _hc.Destroy()
        _hc = None

def main(args):
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    initHelp()
    if args:
        showContextHelp(args[0])
    else:
        _hc.Display('')
    app.MainLoop()
    delHelp()

def _test(word):
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    initHelp()
    if word:
        showContextHelp(word)
    else:
        _hc.Display('')
    app.MainLoop()
    delHelp()
    

if __name__ == '__main__':
    #initWxPyDocStrs()
    main(sys.argv[1:])
    #_test('Window deletion overview')
