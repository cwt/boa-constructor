#-----------------------------------------------------------------------------
# Name:        HelpBook.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:HelpBookItemDlg

from wxPython.wx import *

def createIndexDlg(parent, keyword, location, anchors):
    return HelpBookItemDlg(parent, 'Help Book - Index', keyword, 'Keyword(s)', '',
                     location, 'Location', anchors)

def createContentsDlg(parent, title, htmlTitle, location, anchors):
    return HelpBookItemDlg(parent, 'Help Book - Contents', title, 'Title', htmlTitle,
                     location, 'Location', anchors)

[wxID_HELPBOOKITEMDLG, wxID_HELPBOOKITEMDLGBTNREADTITLE,
 wxID_HELPBOOKITEMDLGBUTTON2, wxID_HELPBOOKITEMDLGBUTTON3,
 wxID_HELPBOOKITEMDLGCBBANCHORS, wxID_HELPBOOKITEMDLGSTATICTEXT1,
 wxID_HELPBOOKITEMDLGSTATICTEXT2, wxID_HELPBOOKITEMDLGTXTPAGE,
 wxID_HELPBOOKITEMDLGTXTTITLE,
] = map(lambda _init_ctrls: wxNewId(), range(9))

class HelpBookItemDlg(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_HELPBOOKITEMDLG, name='HelpBookItemDlg',
              parent=prnt, pos=wxPoint(452, 359), size=wxSize(446, 136),
              style=wxDEFAULT_DIALOG_STYLE, title=self.caption)
        self._init_utils()
        self.SetClientSize(wxSize(438, 109))

        self.staticText1 = wxStaticText(id=wxID_HELPBOOKITEMDLGSTATICTEXT1,
              label=self.nameLabel, name='staticText1', parent=self,
              pos=wxPoint(8, 16), size=wxSize(56, 13), style=0)

        self.txtTitle = wxTextCtrl(id=wxID_HELPBOOKITEMDLGTXTTITLE,
              name='txtTitle', parent=self, pos=wxPoint(72, 8), size=wxSize(232,
              21), style=0, value=self.name)

        self.staticText2 = wxStaticText(id=wxID_HELPBOOKITEMDLGSTATICTEXT2,
              label=self.valueLabel, name='staticText2', parent=self,
              pos=wxPoint(8, 48), size=wxSize(64, 13), style=0)

        self.txtPage = wxTextCtrl(id=wxID_HELPBOOKITEMDLGTXTPAGE,
              name='txtPage', parent=self, pos=wxPoint(72, 40), size=wxSize(232,
              21), style=0, value=self.value)

        self.cbbAnchors = wxComboBox(choices=self.valueAnchors,
              id=wxID_HELPBOOKITEMDLGCBBANCHORS, name='cbbAnchors', parent=self,
              pos=wxPoint(304, 40), size=wxSize(125, 21), style=0,
              validator=wxDefaultValidator, value=self.valueAnchorsValue)

        self.btnReadTitle = wxButton(id=wxID_HELPBOOKITEMDLGBTNREADTITLE,
              label='Title from HTML', name='btnReadTitle', parent=self,
              pos=wxPoint(304, 8), size=wxSize(123, 23), style=0)
        EVT_BUTTON(self.btnReadTitle, wxID_HELPBOOKITEMDLGBTNREADTITLE,
              self.OnBtnreadtitleButton)

        self.button2 = wxButton(id=wxID_OK, label='OK', name='button2',
              parent=self, pos=wxPoint(272, 72), size=wxSize(75, 23), style=0)

        self.button3 = wxButton(id=wxID_CANCEL, label='Cancel', name='button3',
              parent=self, pos=wxPoint(353, 72), size=wxSize(75, 23), style=0)

    def __init__(self, parent, caption, name, nameLabel, nameDefault,
                 value, valueLabel, valueAnchors):

        self.caption = 'Help Book'
        self.caption = caption
        self.name = ''
        self.name = name
        self.nameLabel = 'Name'
        self.nameLabel = nameLabel
        self.nameDefault = ''
        self.nameDefault = nameDefault
        self.value = ''
        self.value = self.getFilenameValue(value)
        self.valueLabel = 'Value'
        self.valueLabel = valueLabel
        self.valueAnchors = []
        self.valueAnchors = valueAnchors
        self.valueAnchorsValue = ''
        self.valueAnchorsValue = self.getAnchorValue(value)

        self._init_ctrls(parent)

        self.titleFromHtml = ''

        if not self.nameDefault:
            self.btnReadTitle.Disable()

        self.button2.SetDefault()

    def GetResult(self):
        name = self.txtTitle.GetValue()

        anch = self.cbbAnchors.GetValue().strip()
        value = self.txtPage.GetValue()
        if anch:
            value = value + '#' + anch

        return name, value


    def OnBtnreadtitleButton(self, event):
        self.txtTitle.SetValue(self.titleFromHtml)


#-------------------------------------------------------------------------------

    def getAnchorValue(self, value):
        if value.find('#') != -1:
            return value.split('#', 1)[1]
        else:
            return ''

    def getFilenameValue(self, value):
        if value.find('#') != -1:
            return value.split('#')[0]
        else:
            return value

import os, sys, htmllib, formatter

if __name__ == '__main__':
    sys.path.append('..')

from wxPython.wx import *
from wxPython.stc import *

class HelpConfigParser:
    def __init__(self, lines, defaultName='helpbook'):
        self.options = {'Compatibility': '1.1',
                        'Full-text search': 'Yes',
                        'Default Window': 'wxHelp',
                        'Default topic': 'index.html',
                        'Title': defaultName,
        }
        self.updateFilenameOptions(defaultName)
        self.windows = []
        self.files = []

        self._section = ''

        for line in [l.strip() for l in lines if l.strip()]:
            if line in ('[OPTIONS]', '[WINDOWS]', '[FILES]'):
                self._section = line
            else:
                if self._section == '[OPTIONS]':
                    k, v = line.split('=')
                    self.options[k] = v
                elif self._section == '[WINDOWS]':
                    k, v = line.split('=')
                    self.windows = v.split(',')
                elif self._section == '[FILES]':
                    self.files.append(line)

    def generateConfigData(self):
        res = ['[OPTIONS]']
        res.extend(['%s=%s'%(key, val) for key, val in self.options.items()])
        res.append('')
        res.append('[WINDOWS]')
        # I have no idea what the magic numbers mean
        res.append('wxHelp=,"%(Contents file)s","%(Index file)s",'
              '"%(Default topic)s",,,,,,0x2420,,0x380e,,,,,0,,,'%self.options)
        res.append('')
        res.append('[FILES]')
        res.extend(self.files)

        return '\n'.join(res)


    def updateFilenameOptions(self, name):
        self.options.update({'Contents file': name+'.hhc',
                             'Compiled file': name+'.chm',
                             'Index file': name+'.hhk'})

class HelpBookParser(htmllib.HTMLParser):
    def __init__(self, formatter, verbose=0):
        htmllib.HTMLParser.__init__(self, formatter, verbose)

        self.indexes = None
        self.index = None

        self.workstack = []
        self.result = []

    def start_ul(self, attrs):
        indexes = []

        if self.indexes is not None:
            self.workstack.append(self.indexes)

        if self.indexes:
            self.indexes[-1] = self.indexes[-1][:2]+(indexes,)

        self.indexes = indexes
        self.index = None

    def end_ul(self):
        if not self.workstack:
            self.result = self.indexes
        else:
            self.indexes = self.workstack.pop()

    def do_param(self, attrs):
        if self.indexes is not None and self.index:
            name, value = attrs[0][1], attrs[1][1]
            self.index[name == 'Local'] = value

    def start_object(self, attrs):
        if self.indexes is not None and self.index is None:
            self.index = [None, None, None]

    def end_object(self):
        if self.indexes is not None:
            self.indexes.append(tuple(self.index))
            self.index = None

def writeHelpBook(items):
    res = ['<UL>']
    for name, value, children in items:
        res.append('<LI><OBJECT type="text/sitemap">')
        res.append('<PARAM name="Local" value="%s">'%value)
        res.append('<PARAM name="Name" value="%s">'%name)
        res.append('</OBJECT>')

        if children:
            res.append(writeHelpBook(children))

    res.append('</UL>')

    return '\n'.join(res)

def parseHelpFile(data, Parser=HelpBookParser):
    w = formatter.NullWriter()
    f = formatter.NullFormatter(w)
    p = Parser(f)
    p.feed(data)
    return p


class BreakOnTitle(Exception): pass

class HtmlDocDetailParser(htmllib.HTMLParser):
    def __init__(self, formatter, verbose=0, breakOnTitle=False):
        htmllib.HTMLParser.__init__(self, formatter, verbose)
        self.anchors = []
        self.title = ''
        self.breakOnTitle = breakOnTitle
        self.result = [self.title, self.anchors]

    _in_title = False
    def start_title(self, attrs):
        self._in_title = True
    def end_title(self):
        self._in_title = False

    def start_a(self, attrs):
        if attrs and attrs[0] and attrs[0][0].lower() == 'name':
            self.anchors.append(attrs[0][1])
    def end_a(self):
        pass

    def handle_data(self, data):
        if self._in_title:
            self.title = self.result[0] = data.strip()

            if self.breakOnTitle:
                raise BreakOnTitle, self.title


    def do_param(self, attrs):
        pass#print 'do_param', attrs


def _testHPP():
    from pprint import pprint
    #pprint(parseHelpFile(open('../Docs/python/python.hhc').read()))
    #i = parseHelpFile(open('../Docs/boa/apphelp/apphelp.hhc').read())
    #print i
    ##writeHelpBook(i)
    print parseHelpFile(open('../Docs/boa/apphelp/debugger.html').read(), Parser=HtmlDocDetailParser).result

def _testHCP():
    h = HelpConfigParser(open('../Docs/wxpython/wx/wx.hhp').readlines())
    print h.options, h.windows, h.files


if __name__ == '__main__':
    _testHPP()
    #_testHCP()

#-------------------------------------------------------------------------------

import Preferences, Utils, Plugins
import PaletteStore

from Models import Controllers, EditorHelper, EditorModels
from Views import EditorViews, SourceViews, StyledTextCtrls
from Explorers import Explorer, ExplorerNodes

import ProcessProgressDlg

import glob, zipfile
from cStringIO import StringIO

Plugins.registerPreference('HelpBook', 'hbShowDocumentTitles', 'True', 
                           ['Should the document title be parsed from HTML and '
                            'displayed under "Files".'])


class HelpBookModel(EditorModels.SourceModel):
    modelIdentifier = 'HelpBook'
    defaultName = 'helpbook'
    bitmap = 'HelpBook.png'
    ext = '.hhp'
    imgIdx = EditorHelper.imgHelpBook

    def __init__(self, data, name, editor, saved):
        EditorModels.SourceModel.__init__(self, data, name, editor, saved)

        contents = os.path.splitext(name)[0]+'.hhc'
        try:
            transport = Explorer.openEx(contents)
            data = transport.load()
        except ExplorerNodes.TransportError:
            transport = None
            data = ''
        self.contentsModel = EditorModels.SourceModel(data, contents, editor, saved)
        self.contentsModel.transport = transport

        indexes = os.path.splitext(name)[0]+'.hhk'
        try:
            transport = Explorer.openEx(indexes)
            data = transport.load()
        except ExplorerNodes.TransportError:
            transport = None
            data = ''
        self.indexesModel = EditorModels.SourceModel(data, indexes, editor, saved)
        self.indexesModel.transport = transport

        self.update()

    def update(self):
        self.config = HelpConfigParser(StringIO(self.data).readlines())
        self.contentsModel.update()
        self.contents = parseHelpFile(self.contentsModel.data).result
        self.indexesModel.update()
        self.indexes = parseHelpFile(self.indexesModel.data).result

    def load(self, notify=True):
        try: self.contentsModel.load(False)
        except ExplorerNodes.TransportError: pass

        try: self.indexesModel.load(False)
        except ExplorerNodes.TransportError: pass

        EditorModels.SourceModel.load(self, notify)

    def save(self, overwriteNewer=False):
        if self.modified:
            gen = '<META name="GENERATOR" content="Boa Constructor - HelpBook">\n'
            if self.contentsModel.modified:
                self.contentsModel.data = gen + writeHelpBook(self.contents)
                self.contentsModel.save(overwriteNewer)
            if self.indexesModel.modified:
                self.indexesModel.data = gen + writeHelpBook(self.indexes)
                self.indexesModel.save(overwriteNewer)

            self.data = self.config.generateConfigData()
            EditorModels.SourceModel.save(self, overwriteNewer)

    def saveAs(self, filename):
        newDir, newName = os.path.split(filename)
        oldDir, oldName = os.path.split(self.filename)
        if self.savedAs and newDir != oldDir:
            raise ExplorerNodes.TransportSaveError, \
                  'Once saved, help books files cannot be moved, only renamed.\n'\
                  'Please move the entrire directory.'

        if newName != oldName:
            self.config.updateFilenameOptions(os.path.splitext(newName)[0])
            self.modified = True

        noExtFilename = os.path.splitext(filename)[0]
        self.contentsModel.saveAs(noExtFilename+'.hhc')
        self.indexesModel.saveAs(noExtFilename+'.hhk')

        EditorModels.SourceModel.saveAs(self, filename)

    def setModified(self, section='config'):
        if section == 'contents':
            self.contentsModel.modified = True
        elif section == 'indexes':
            self.indexesModel.modified = True

        self.modified = True

    def makeHTB(self):
        pass

# XXX Experimental, should just load and save from zip
class HTBHelpBookModel(HelpBookModel):
    modelIdentifier = 'BTBHelpBook'
    defaultName = 'htbhelpbook'
    ext = '.htb'

    def __init__(self, data, name, editor, saved):
        HelpBookModel.__init__(self, data, name, editor, saved)

    def load(self, notify=True):
        pass

    def save(self, overwriteNewer=False):
        pass

##        if self.GetItemCount():
##            itemFrom = self.GetTopItem()
##            itemTo   = self.GetTopItem()+1 + self.GetCountPerPage()
##            itemTo   = min(itemTo, self.GetItemCount()-1)
##            self.RefreshItems(itemFrom, itemTo)


class HelpBookFilesView(EditorViews.VirtualListCtrlView):
    viewName = 'Files'

    addBmp = 'Images/Shared/NewItem.png'
    delBmp = 'Images/Shared/DeleteItem.png'
    def __init__(self, parent, model, provideActions=True):
        if provideActions:
            actions = (('Add file', self.OnAddFile, self.addBmp, ''),
                       ('Add files', self.OnAddFiles, '-', ''), 
                       ('Remove file', self.OnRemoveFile, self.delBmp, ''),
                       ('Open file', self.OnOpenFile, '-', ''),
                       ('-', None, '-', ''),
                       ('Normalise paths', self.OnNormalisePaths, '-', ''),)
        else:
            actions = ()
        EditorViews.VirtualListCtrlView.__init__(self, parent, model,
              wxLC_REPORT, actions, -1)

        EVT_LEFT_DOWN(self, self.OnFilesLeftDown)

        #self.sortOnColumns = [0, 1, 2]

        self.InsertColumn(0, 'No')
        self.InsertColumn(1, 'Name')
        self.InsertColumn(2, 'Path')
        self.SetColumnWidth(0, 30)
        self.SetColumnWidth(1, 150)
        self.SetColumnWidth(2, 300)

        if Preferences.hbShowDocumentTitles:
            self.InsertColumn(3, 'Title')
            self.SetColumnWidth(3, 300)

        self.active = true

        self.resetCache()

        #EVT_LIST_CACHE_HINT(self, self.GetId(), self.OnCacheHint)

    def refreshCtrl(self):
        self.resetCache()
        self.SetItemCount(len(self.model.config.files))

    def OnGetItemText(self, item, col):
        f = self.model.config.files[item]
        if col == 0:
            return `item`
        elif col == 1:
            return os.path.basename(f)
        elif col == 2:
            return f
        elif Preferences.hbShowDocumentTitles and col == 3:
            if not self.cached[item]:
                title = ''
                try:
                    if os.path.splitext(f)[1].lower() not in ('.htm', '.html'):
                        return ''
                    docsDir = os.path.dirname(self.model.filename)
                    try: data = Explorer.openEx(os.path.join(docsDir, f)).load()
                    except ExplorerNodes.TransportError: return ''
                    fmtr = formatter.NullFormatter(formatter.NullWriter())
                    try: HtmlDocDetailParser(fmtr, breakOnTitle=True).feed(data)
                    except BreakOnTitle, title: return str(title)
                    except: return ''
                    else: return ''
                finally:
                    self.cached[item] = title
            else:
                return self.cached[item]

    def doStartDrag(self):
        sel = self.GetSelections()
        if sel:
            filenames = [self.model.config.files[idx] for idx in sel]
            filelist = wxCustomDataObject(wxCustomDataFormat('FileList'))
            filelist.SetData(`filenames`)
            #tdo = wxTextDataObject(filename)
            ds = wxDropSource(self)
            ds.SetData(filelist)
            ds.DoDragDrop(wxDrag_DefaultMove)

    def OnFilesLeftDown(self, event):
        event.Skip()
        Utils.wxCallAfter(self.doStartDrag)

    helpBookDirMsg = 'Help documents must be in the same directory as the help '\
                     'book, or a sub-directory. Not allowed outside the tree.'
    def OnAddFile(self, event):
        if not self.model.savedAs:
            wxLogError('Please save the help book before adding files\n'+self.helpBookDirMsg)
            return

        filename = self.model.editor.openFileDlg()
        if filename:
            helpProjDir = os.path.dirname(self.model.filename)
            if not filename.startswith(helpProjDir):
                wxLogError(self.helpBookDirMsg)
                return

            self.model.config.files.append(filename[len(helpProjDir)+1:])

            self.refreshCtrl()
            self.updateOtherViews()

            self.model.setModified()
            self.updateEditor()

    def OnRemoveFile(self, event):
        sel = self.GetSelections()
        if sel:
            sel.sort()
            sel.reverse()
            for idx in sel:
                del self.model.config.files[idx]

            self.refreshCtrl()
            self.updateOtherViews()

            self.model.setModified()
            self.updateEditor()

    def updateOtherViews(self):
        views = self.model.views
        if views.has_key('Contents'):
            views['Contents'].files.refreshCtrl()
        if views.has_key('Index'):
            views['Index'].files.refreshCtrl()

    def OnOpenFile(self, event):
        idx = self.selected
        if idx != -1:
            helpBookDir = os.path.dirname(self.model.filename)
            self.model.editor.openOrGotoModule(
                  helpBookDir+'/'+self.model.config.files[idx])

    #def OnCacheHint(self, event):
    #    print 'From', event.GetCacheFrom()
    #    print 'To', event.GetCacheTo()

    def resetCache(self, ):
        self.cached = [False]*len(self.model.config.files)

    def OnNormalisePaths(self, event):
        helpBookDir = os.path.dirname(self.model.localFilename())
        delidxs = []
        for idx, filename in zip(range(len(self.model.config.files)), 
                                 self.model.config.files):
            absfn = os.path.normpath(os.path.join(helpBookDir, filename))
            if absfn[:len(helpBookDir)] != helpBookDir:
                if wxMessageBox('Filename "%s" not inside help book directory.'
                      '\n\nRemove?'%absfn, 'Invalid file', 
                      wxICON_QUESTION | wxYES_NO) == wxYES:
                    delidxs.append(idx)
            else:
                self.model.config.files[idx] = absfn[len(helpBookDir)+1:]
        
        if delidxs:
            delidxs.reverse()
            for idx in delidxs:
                del self.model.config.files[idx]

        self.refreshCtrl()
        self.updateOtherViews()

        self.model.setModified()
        self.updateEditor()

    def OnAddFiles(self, event):
        helpBookDir = os.path.dirname(self.model.localFilename())
        dlg = wxDirDialog(self)
        try:
            dlg.SetPath(helpBookDir)
            if dlg.ShowModal() != wxID_OK:
                return
            dir = dlg.GetPath()
        finally:
            dlg.Destroy()

        if not dir.startswith(helpBookDir):
            wxLogError(self.helpBookDirMsg)
            return
            
        dlg = wxTextEntryDialog(self, 'Enter wildcard', 'Add Files', '*.*')
        try:
            if dlg.ShowModal() != wxID_OK:
                return
            globStr = dlg.GetValue()
        finally:
            dlg.Destroy()

        files = glob.glob(os.path.join(dir, globStr))

        for filename in files:
            self.model.config.files.append(filename[len(helpBookDir)+1:])

        self.refreshCtrl()
        self.updateOtherViews()

        self.model.setModified()
        self.updateEditor()

class FileListDropTarget(wxPyDropTarget):
    def __init__(self):
        wxPyDropTarget.__init__(self)
        self.fmt = wxCustomDataFormat('FileList')
        self.data = wxCustomDataObject(self.fmt)
        self.SetDataObject(self.data)

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, d):
        if self.GetData():
            filelist = eval(self.data.GetData())
            self.OnDropFiles(x, y, filelist)
        return d

class HelpBookIndexDropTarget(FileListDropTarget):
    def __init__(self, indexList):
        FileListDropTarget.__init__(self)
        self.list = indexList

    def OnDropFiles(self, x, y, files):
        docsDir = os.path.dirname(self.list.model.filename)

        for filename in files:
            data = Explorer.openEx(os.path.join(docsDir, filename)).load()
            prs = parseHelpFile(data, HtmlDocDetailParser)
            dlg = createIndexDlg(None, '', filename, prs.anchors)
            try:
                if dlg.ShowModal() != wxID_OK:
                    return

                keyword, location = dlg.GetResult()
            finally:
                dlg.Destroy()

            #item, flags = self.list.HitTest( (x, y) )
            self.list.model.indexes.append((keyword, location, None))

        self.list.model.setModified('indexes')
        self.list.updateEditor()

        self.list.refreshCtrl()


class HelpBookIndexView(wxSplitterWindow, EditorViews.EditorView):
    viewName = 'Index'
    
    addBmp = 'Images/Shared/NewItem.png'
    delBmp = 'Images/Shared/DeleteItem.png'
    def __init__(self, parent, model):
        wxSplitterWindow.__init__(self, parent, -1,
              style=wxCLIP_CHILDREN | wxNO_3D | wxSP_3DSASH)

        self.indexes = HelpBookIndexListView(self, model, self)
        self.files = HelpBookFilesView(self, model, False)

        self.SplitVertically(self.indexes, self.files, 350)

        EditorViews.EditorView.__init__(self, model, (
            ('Add index', self.indexes.OnAddIndex, self.addBmp, ''),
            ('Edit index', self.indexes.OnEditIndex, '-', ''),
            ('Delete index', self.indexes.OnDeleteIndex, self.delBmp, ''),
        ), 0)

        self.active = true

    def refreshCtrl(self):
        self.indexes.refreshCtrl()
        self.files.refreshCtrl()


class HelpBookIndexListView(EditorViews.VirtualListCtrlView):
    def __init__(self, parent, model, parentView=None):
        EditorViews.VirtualListCtrlView.__init__(self, parent, model, wxLC_REPORT,
          (), -1)
        self.parentView = parentView

        self.SetDropTarget(HelpBookIndexDropTarget(self))

        #self.sortOnColumns = [0, 1]

        self.InsertColumn(0, 'Keyword')
        self.InsertColumn(1, 'Location')
        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 400)

        self.active = true

    def refreshCtrl(self):
        self.SetItemCount(len(self.model.indexes))

    def OnGetItemText(self, item, col):
        return self.model.indexes[item][col]

    def OnRightClick(self, event):
        if self.parentView:
            menu = self.parentView.generateMenu()
            event.GetEventObject().PopupMenuXY(menu, event.GetX(), event.GetY())
            menu.Destroy()

    def OnAddIndex(self, event):
        dlg = createIndexDlg(None, '', '', [])
        try:
            if dlg.ShowModal() != wxID_OK:
                return

            keyword, location = dlg.GetResult()
        finally:
            dlg.Destroy()

        self.model.indexes.append((keyword, location, None))

        self.model.setModified('indexes')
        self.updateEditor()

        self.refreshCtrl()

    def OnEditIndex(self, event):
        if self.selected != -1:
            keyword, location, c = self.model.indexes[self.selected]

            docsDir = os.path.dirname(self.model.filename)
            try:
                data = Explorer.openEx(
                      os.path.join(docsDir, location.split('#')[0])).load()
            except ExplorerNodes.TransportLoadError:
                data = ''
            prs = parseHelpFile(data, HtmlDocDetailParser)
            dlg = createIndexDlg(None, keyword, location, prs.anchors)
            try:
                if dlg.ShowModal() != wxID_OK:
                    return

                res = dlg.GetResult()
            finally:
                dlg.Destroy()

            if res != (keyword, location):
                keyword, location = res
                self.model.indexes[self.selected] = (keyword, location, None)

                self.model.setModified('indexes')
                self.updateEditor()

                self.refreshCtrl()

    def OnDeleteIndex(self, event):
        if self.selected != -1:
            del self.model.indexes[self.selected]

            self.model.setModified('indexes')
            self.updateEditor()

            self.refreshCtrl()

class HelpBookContentsDropTarget(FileListDropTarget):
    def __init__(self, contentsTree):
        FileListDropTarget.__init__(self)
        self.tree = contentsTree

    def OnDropFiles(self, x, y, files):
        item, flags = self.tree.HitTest( (x, y) )
        if not item.Ok(): return
        
        name = self.tree.GetItemText(item)
        value, items, children = self.tree.GetPyData(item)

        docsDir = os.path.dirname(self.tree.model.filename)

        for filename in files:
            title, page = doContentsDlg(None, filename, docsDir)

            if (title, page) == (None, None):
                continue
            
            entry = (title, page, None)

            if children is None:
                idx = items.index( (name, value, children) )
                items[idx] = (name, value, [entry])
                children = [entry]
            else:
                children.append(entry)

        self.tree.model.setModified('contents')
        self.tree.updateEditor()

        self.tree.SetItemHasChildren(item, True)
        self.tree.SetItemData(item, wxTreeItemData((value, items, children)))
        #if self.tree.GetItemImage(item) != 0:
        #    self.tree.SetItemImage(item, 1, 1) # XXX Doesn't work
        self.tree.SelectItem(item)
        self.tree.Collapse(item)
        self.tree.Expand(item)

        #self.tree.refreshCtrl()


def doContentsDlg(title, text, docsDir):
    #text, anchor = (text.split('#')+[''])[:2]
    data = Explorer.openEx(os.path.join(docsDir, text.split('#')[0])).load()
    prs = parseHelpFile(data, HtmlDocDetailParser)
    if title is None:
        title = prs.title
    dlg = createContentsDlg(None, title, prs.title, text, prs.anchors)
    try:
        if dlg.ShowModal() != wxID_OK:
            return None, None

        title, location = dlg.GetResult()
    finally:
        dlg.Destroy()
    return title, location

class HelpBookContentsView(wxSplitterWindow, EditorViews.EditorView):
    viewName = 'Contents'

    addBmp = 'Images/Shared/NewItem.png'
    delBmp = 'Images/Shared/DeleteItem.png'
    def __init__(self, parent, model):
        wxSplitterWindow.__init__(self, parent, -1,
              style=wxCLIP_CHILDREN|wxNO_3D|wxSP_3DSASH)

        self.contents = HelpBookContentsTreeView(self, model, self)
        self.files = HelpBookFilesView(self, model, False)

        self.SplitVertically(self.contents, self.files, 350)

        actions = (('Edit entry', self.contents.OnEditEntry, '-', ''),
                   ('Delete entry', self.contents.OnDeleteEntry, self.delBmp, ''),
                   ('Import...', self.OnImportContents, '-', ''), )
        EditorViews.EditorView.__init__(self, model, actions, -1)

        self.active = true

    def refreshCtrl(self):
        self.contents.refreshCtrl()
        self.files.refreshCtrl()


    def OnImportContents(self, event):
        pass

class HelpBookContentsTreeView(wxTreeCtrl, EditorViews.EditorView):
    viewName = 'Contents'

    def __init__(self, parent, model, parentView=None):
        wxTreeCtrl.__init__(self, parent, -1,
         style=wxTR_HAS_BUTTONS|wxSUNKEN_BORDER|wxTR_DEFAULT_STYLE)
        EditorViews.EditorView.__init__(self, model, (), -1)
        self.parentView = parentView
        #(('Edit entry', self.OnEditEntry, '-', ''),)

        self.SetDropTarget(HelpBookContentsDropTarget(self))

        self.helpImgLst = wxImageList(16, 16)
        for artId in (wxART_HELP_BOOK, wxART_HELP_FOLDER, wxART_HELP_PAGE):
            bmp = wxArtProvider_GetBitmap(artId, wxART_TOOLBAR, (16, 16))
            self.helpImgLst.Add(bmp)
        self.AssignImageList(self.helpImgLst)

        EVT_TREE_ITEM_EXPANDING(self, self.GetId(), self.OnTreeExpand)
        EVT_TREE_SEL_CHANGED(self, self.GetId(), self.OnTreeSelChanged)

        self.active = true

    def refreshCtrl(self):
        self.DeleteAllItems()
        title = self.model.config.options['Title']
        rootItem = self.AddRoot(title, 0,
              data=wxTreeItemData((title, None, self.model.contents)))

        self.SetItemHasChildren(rootItem, True)
        self.Expand(rootItem)


    def recurseAddItems(self, items, treeItem):
        # XXX no longer used, build entire tree recursively
        for name, value, children in items:
            item = self.AppendItem(treeItem, name, children and 1 or 2, -1,
                                   wxTreeItemData((value, items, children)))
            if children:
                self.recurseAddItems(children, item)
                self.SetItemHasChildren(item, True)

    def addTreeItems(self, items, treeItem):
        self.DeleteChildren(treeItem)
        for name, value, children in items:
            item = self.AppendItem(treeItem, name, children and 1 or 2, -1,
                                   wxTreeItemData((value, items, children)))
            if children:
                self.SetItemHasChildren(item, True)

    def OnRightClick(self, event):
        if self.parentView:
            menu = self.parentView.generateMenu()
            event.GetEventObject().PopupMenuXY(menu, event.GetX(), event.GetY())
            menu.Destroy()

    def OnTreeExpand(self, event):
        item = event.GetItem()
        self.addTreeItems(self.GetPyData(item)[-1], item)

    def OnTreeSelChanged(self, event):
        item = event.GetItem()
        if item.Ok():
            location = self.GetPyData(item)[0]
            self.model.editor.setStatus(location)

    def OnEditEntry(self, event):
        tree = self
        item = tree.GetSelection()
        name = tree.GetItemText(item)
        value, items, children = tree.GetPyData(item)

        if item == tree.GetRootItem():
            options = self.model.config.options
            dlg =  HelpBookItemDlg(self.model.editor, 'Help Book - Contents properties',
                   options['Title'], 'Title', '',
                   options['Default topic'], 'Default topic', [])
            try:
                if dlg.ShowModal() != wxID_OK:
                    return

                title, defTopic = dlg.GetResult()
            finally:
                dlg.Destroy()

            if options['Title'] != title or options['Default topic'] != defTopic:
                self.model.setModified('config')
                self.updateEditor()

                options['Title'] = title
                options['Default topic'] = defTopic

                tree.SetItemData(item, wxTreeItemData((title, defTopic, children)))
                tree.SetItemText(item, title)

            # XXX mark hhp modified
            return


        docsDir = os.path.dirname(self.model.filename)
        title, page = doContentsDlg(name, value, docsDir)

        if (title, page) == (None, None):
            return


        if (name, value, children) != (title, page, children):
            idx = items.index( (name, value, children) )
            items[idx] = (title, page, children)

            self.model.setModified('contents')
            self.updateEditor()

            tree.SetItemData(item, wxTreeItemData((page, items, children)))
            tree.SetItemText(item, title)

    def OnDeleteEntry(self, event):
        item = self.GetSelection()

        if item == self.GetRootItem():
            wxLogError('Cannot delete root node.')
            return

        name = self.GetItemText(item)
        value, items, children = self.GetPyData(item)

        idx = items.index( (name, value, children) )

        if wxMessageBox('Delete %s'%name, 'Delete node and children',
              wxICON_WARNING | wxYES_NO) == wxYES:
            del items[idx]
            self.model.modified = True
            self.updateEditor()

            self.Collapse(item)
            self.Delete(item)


def visitDir((files, excludes), dirname, names):
    for name in names:
        if name not in excludes:
            filename = os.path.join(dirname, name)
            if os.path.isfile(filename):
                files.append(filename)

wxID_HP_X = wxNewId()
class HelpBookController(Controllers.SourceController):
    Model = HelpBookModel
    DefaultViews = [HelpBookFilesView, HelpBookContentsView, HelpBookIndexView]

    def actions(self, model):
        actions = [
              ('-', None, '', ''),
              ('Make HTB', self.OnMakeHTB, '', ''),
              ]
        if wxPlatform == '__WXMSW__':
            actions.append( ('Make CHM', self.OnMakeCHM, '', '') )

        return Controllers.SourceController.actions(self, model) + actions

    def OnMakeHTB(self, event):
        model = self.getModel()
        dlg = wxSingleChoiceDialog(model.editor, 'Choose source files', 
              'Make HTB', ['Files list', 'Entire help book directory'])
        try:
            if dlg.ShowModal() != wxID_OK:
                return
            selected = dlg.GetSelection()
        finally:
            dlg.Destroy()
        
        modelFile = model.localFilename()
        zipfilename = os.path.splitext(modelFile)[0]+'.htb'

        docsDir = os.path.dirname(modelFile)
        if selected == 0:
            files = [os.path.join(docsDir, f) for f in model.config.files]
        elif selected == 1:
            files = []
            os.path.walk(docsDir, visitDir, 
                         (files, [os.path.basename(zipfilename)]))
        
        wxBeginBusyCursor()
        zf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
        try:
            for filename in files:
                zf.write(filename, filename[len(docsDir)+1:])
        finally:
            wxEndBusyCursor()
            zf.close()

        wxLogMessage('Written %s.'%zipfilename)
            
    def OnMakeCHM(self, event):
        modelFile = model.localFilename()
        dir, name = os.path.split(modelFile)
        cmd = 'hhc %s'%name
        cwd = os.getcwd()
        try:
            os.chdir(runDir)
            dlg = ProcessProgressDlg.ProcessProgressDlg(self.editor, cmd, 'Make CHM')
            try:
                if dlg.ShowModal() == wxOK:
                    outls = dlg.output
                    errls = dlg.errors
                else:
                    return
            finally:
                dlg.Destroy()
        finally:
            os.chdir(cwd)

        #err = ''.join(errls).strip()
            
#-------------------------------------------------------------------------------


EditorHelper.modelReg[HelpBookModel.modelIdentifier] = HelpBookModel
EditorHelper.extMap[HelpBookModel.ext] = HelpBookModel
Controllers.modelControllerReg[HelpBookModel] = HelpBookController
PaletteStore.paletteLists['New'].append(HelpBookModel.modelIdentifier)
PaletteStore.newControllers[HelpBookModel.modelIdentifier] = HelpBookController
