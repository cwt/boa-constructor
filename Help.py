#----------------------------------------------------------------------
# Name:        Help.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999, rewritten 2001
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import os, marshal

from wxPython.wx import *
from wxPython.html import *
from wxPython.htmlhelp import *

import Preferences, Utils

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
    if Utils.startswith(word, 'EVT_'):
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
    def Display(self, text):
        wxHtmlHelpController.Display(self, text)
        frameX = wxHelpFrameEx(self)
        #frameX.restore()
        if frameX.frame.IsIconized():
            frameX.frame.Iconize(false)
        frameX.frame.Raise()
        return frameX

    def UseConfig(self, config):
        # Fix config file if stored as minimised
        if config.ReadInt('hcX') == -32000:
            map(config.DeleteEntry, ('hcX', 'hcY', 'hcW', 'hcH'))

        wxHtmlHelpController.UseConfig(self, config)
        self.config = config

class _CloseEvtHandler(wxEvtHandler):
    def __init__(self, frame):
        wxEvtHandler.__init__(self)
        EVT_CLOSE(frame, self.OnClose)
        self.frame = frame

    def OnClose(self, event):
        self.frame.Hide()
        event.Skip()
        self.frame.PopEventHandler().Destroy()

wxID_COPYTOCLIP = wxNewId()

# Note, this works nicely because of OOR
class wxHelpFrameEx:
    def __init__(self, helpctrlr):
        self.controller = helpctrlr
        self.frame = helpctrlr.GetFrame()

        wxID_QUITHELP, wxID_FOCUSHTML = wxNewId(), wxNewId()
        EVT_MENU(self.frame, wxID_QUITHELP, self.OnQuitHelp)
        EVT_MENU(self.frame, wxID_FOCUSHTML, self.OnFocusHtml)

        self.frame.PushEventHandler(_CloseEvtHandler(self.frame))

        # helpfrm.cpp defines no accelerators so this is ok
        self.frame.SetAcceleratorTable(
              wxAcceleratorTable([(0, WXK_ESCAPE, wxID_QUITHELP),
                                  (wxACCEL_CTRL, ord('H'), wxID_FOCUSHTML),]))

        if wxPlatform == '__WXMSW__':
            _none, self.toolbar, self.splitter = self.frame.GetChildren()
        else:
            self.toolbar, self.splitter = self.frame.GetChildren()
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
        ck = 0; nd, ck = self.contentsTree.GetFirstChild(rn, ck)
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

def initHelp(calledAtStartup=false):
    jn = os.path.join
    global _hc
    docsDir = jn(Preferences.pyPath, 'Docs')

    _hc = wxHtmlHelpControllerEx(wxHF_ICONS_BOOK_CHAPTER | \
        wxHF_DEFAULT_STYLE | (Preferences.flatTools and wxHF_FLAT_TOOLBAR or 0))
    cf = wxFileConfig(localFilename=os.path.normpath(jn(Preferences.rcPath,
        'helpfrm.cfg')), style=wxCONFIG_USE_LOCAL_FILE)
    _hc.UseConfig(cf)

    cacheDir = jn(Preferences.rcPath, 'docs-cache')
    if not os.path.isdir(cacheDir):
        cacheDir = jn(docsDir, 'cache')
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

def delHelp():
    global _hc
    if _hc:
        _hc.config.Flush()
        f = _hc.GetFrame()
        if f:
            f.Close()
            del f
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
    #main(sys.argv[1:])
    _test('Keycodes')
