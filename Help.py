#----------------------------------------------------------------------
# Name:        Help.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import os, marshal
from os import path

from wxPython.wx import *
from wxPython.html import *
from wxPython.htmlhelp import *

import Preferences, Utils
from Preferences import IS, flatTools, keyDefs

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
    _hc.Display(bookname).ExpandBook(bookname)

def showCtrlHelp(wxClass, method=''):
    _hc.Display(wxClass).ExpandCurrAsWxClass(method)
    
def showHelp(filename):
    _hc.Display(filename)

def showContextHelp(parent, toolbar, word):
    if word in sys.builtin_module_names:
        word = '%s (built-in module)'%word
    else:
        try:
            libPath = os.path.dirname(os.__file__)
        except AttributeError, error:
            pass
        else:
            if os.path.isfile('%s/%s.py'%(libPath, word)):
                word = '%s (standard module)'%word
    _hc.Display(word).IndexFind(word)

def decorateWxPythonWithDocStrs(dbfile):
    namespace = Utils.getEntireWxNamespace()
    
    try:
        db = marshal.load(open(dbfile, 'rb'))
    except IOError:
        pass
    else:
        for name, doc in db['classes'].items():
            try:
                wxClass = eval(name, namespace)
                wxClass.__doc__ = doc
    
                wxClass = eval(name+'Ptr', namespace)
                wxClass.__doc__ = doc
            except:
                pass
    
        for name, doc in db['methods'].items():
            try:
                wxMeth = eval(name, namespace)
                wxMeth.im_func.__doc__ = doc
    
                cls, mth = string.split(name, '.')
                wxMeth = eval(string.join((cls+'Ptr', mth), '.'), namespace)
                wxMeth.im_func.__doc__ = doc
            except:
                pass

class wxHtmlHelpControllerEx(wxHtmlHelpController):
    def Display(self, text):
        wxHtmlHelpController.Display(self, text)
        frameX = wxHelpFrameEx(self)
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
        
# Note, I think this works nicely because of OOR
class wxHelpFrameEx:
    def __init__(self, helpctrlr):
        self.controller = helpctrlr
        self.frame = helpctrlr.GetFrame()
        
        wxID_QUITHELP = wxNewId()
        EVT_MENU(self.frame, wxID_QUITHELP, self.OnQuitHelp)
        
        self.frame.PushEventHandler(_CloseEvtHandler(self.frame))
        
        # helpfrm.cpp defines no accelerators so this is ok
        self.frame.SetAcceleratorTable(
              wxAcceleratorTable([(0, WXK_ESCAPE, wxID_QUITHELP)]))
        
        if wxPlatform == '__WXMSW__':
            _none, self.toolbar, self.splitter = self.frame.GetChildren()
        else:
            self.toolbar, self.splitter = self.frame.GetChildren()
        self.html, self.navPages = self.splitter.GetChildren()

        assert self.navPages.GetPageText(0) == 'Contents'
        self.contentsPanel = self.navPages.GetPage(0)
        self.contentsAddBookmark, self.contentsDelBookmark, \
              self.contentsChooseBookmark, self.contentsTree = \
              self.contentsPanel.GetChildren()
        
        assert self.navPages.GetPageText(1) == 'Index'
        self.indexPanel = self.navPages.GetPage(1)

        self.indexTextCtrl, self.indexShowAllBtn, self.indexFindBtn = \
              self.indexPanel.GetChildren()[:3]
    
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

def initHelp():
    jn = os.path.join
    global _hc
    docsDir = jn(Preferences.pyPath, 'Docs')
    
    _hc = wxHtmlHelpControllerEx(wxHF_ICONS_BOOK_CHAPTER | \
        wxHF_DEFAULT_STYLE | (Preferences.flatTools and wxHF_FLAT_TOOLBAR or 0))
    cf = wxFileConfig(localFilename=os.path.normpath(jn(Preferences.rcPath, 
        'helpfrm.cfg')), style=wxCONFIG_USE_LOCAL_FILE)
    _hc.UseConfig(cf)
        
    docStrs = jn(docsDir, 'wxDocStrings.msh')
    # Early abort if documentation not installed
    if not os.path.isfile(docStrs):
        wxLogWarning('Documentation not installed, please download from '
                     'http://boa-constructor.sourceforge.net/Help/Docs.zip\n'
                     'or http://boa-constructor.sourceforge.net/Help/Docs.tar.gz\n'
                     'Unzip into the Boa root directory.')
        return
    
    _hc.SetTempDir(jn(docsDir, 'cache'))

    conf = Utils.createAndReadConfig('Explorer')
    books = eval(conf.get('help', 'books'), {})
    for book in books:
        print 'Help: loading %s'% os.path.basename(book)
        _hc.AddBook(os.path.normpath(jn(docsDir, book+'.hhp')), 
         not os.path.exists(jn(docsDir, 'cache', 
         os.path.basename(book)+'.hhp.cached')))

    decorateWxPythonWithDocStrs(docStrs)
    

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    initHelp()
    ##_hc.Display('Boa').IndexFind('reduce')
    _hc.Display('Python Documentation').ExpandBook('Python Documentation')
    app.MainLoop()
    _hc.config.Flush()
 