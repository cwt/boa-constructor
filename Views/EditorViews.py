#----------------------------------------------------------------------
# Name:        EditorViews.py                                          
# Purpose:     Base view classes that are the visual plugins for models
#                                                                      
# Author:      Riaan Booysen                                           
#                                                                      
# Created:     1999                                                    
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen                            
# Licence:     GPL                                                     
#----------------------------------------------------------------------

# So many views
# on the same thing
# facets, aspects, perspectives

from wxPython.wx import *
from wxPython.html import *
import PaletteMapping, Search
import string, os
import Preferences
from os import path
from Utils import AddToolButtonBmpObject
from moduleparse import CodeBlock
from Preferences import IS, staticInfoPrefs
from Utils import BoaFileDropTarget
from PrefsKeys import keyDefs
from Debugger import Debugger
from thread import start_new_thread

wxwHeaderTemplate ='''<html>
<head>
   <title>%(Title)s</title>
</head>
<body bgcolor="#FFFFFF">'''

wxwModuleTemplate = '''
<h1>%(Module)s</h1>
%(ModuleSynopsis)s
<p><b><font color="#FF0000">Classes</font></b><br>
<p>%(ClassList)s
<hr>
'''

wxwAppModuleTemplate = '''
<h1>%(Module)s</h1>
%(ModuleSynopsis)s
<p><b><font color="#FF0000">Modules</font></b><br>
<p>%(ModuleList)s
<br>
<p><b><font color="#FF0000">Classes</font></b><br>
<p>%(ClassList)s
<hr>
'''

wxwClassTemplate = '''
<a NAME="%(Class)s"></a>
<h2>%(Class)s</h2>
%(ClassSynopsis)s
<p><b><font color="#FF0000">Derived from</font></b>
<p>%(ClassSuper)s
<p><b><font color="#FF0000">Methods</font></b>
<p>
%(MethodList)s
<p>
%(MethodDetails)s
<hr>
<center>
*</center>
'''

wxwMethodTemplate = '''
<hr><a NAME="%(Class)s%(Method)s"></a>
<h3>
%(Class)s.%(Method)s</h3>
<b>%(Method)s</b>(<i>%(Params)s</i>)
<p>&nbsp;%(MethodSynopsis)s
<p>
'''

wxwFooterTemplate = '</body></html>'

class ViewBrowser:
    def __init__(self, model, current):
        self.prevList = []
        self.nextList = []
        self.current = current
        self.pagers = {}
    
    def registerPage(self, name, pageFunc):
        self.pagers[name] = pageFunc
        
    
    def browseTo(self, place):
        self.prevList.append(place)
       
    def previous(self):
        pass
    
    def next(self):
        pass
    
    def canPrev(self):
        return len(self.prevList)
    
    def canNext(self):
        return len(self.nextList)

class EditorView:
    def __init__(self, model, actions = [], dclickActionIdx = -1, editorIsWindow = true):
        self.actions = actions
        self.active = false
        self.model = model
        self.modified = false
        if editorIsWindow: 
            EVT_RIGHT_DOWN(self, self.OnRightDown)
            # for wxMSW
#            EVT_COMMAND_RIGHT_CLICK(self, -1, self.OnRightClick)
            # for wxGTK
            EVT_RIGHT_UP(self, self.OnRightClick)

            dt = BoaFileDropTarget(model.editor)
            self.SetDropTarget(dt)
            
        self.menu = wxMenu()
        self.editorMenu = wxMenu()
        self.popx = self.popy = 0

        self.defaultActionIdx = dclickActionIdx
        self.ids = []
        self.accelLst = []

        # Build Edit/popup menu and accelerator list
        for name, meth, bmp, accl in actions:
            if name == '-': wId = -1
            else: wId = wxNewId()
            
            if name[0] == '+':
                canCheck = true
                name = name[1:]
            else:
                canCheck = false
            
            if accl: 
                name = name + (accl[2] and '     <'+accl[2]+'>' or '')

            self.menu.Append(wId, name, checkable = canCheck)
            EVT_MENU(self, wId, meth)
            self.editorMenu.Append(wId, name, checkable = canCheck)
            EVT_MENU(self.model.editor, wId, meth)
            self.ids.append(wId)
            if accl: self.accelLst.append( (accl[0], accl[1], wId) )
    
        # Connect default action of the view to doubleclick on view 
        if dclickActionIdx < len(actions) and dclickActionIdx > -1:
            EVT_LEFT_DCLICK(self, actions[dclickActionIdx][1])
    
    def destroy(self):
        print 'destroy', self.__class__.__name__, sys.getrefcount(self)
        for wId in self.ids:
            if wId != -1:
                self.model.editor.Disconnect(wId)
        self.menu.Destroy()
        self.editorMenu.Destroy()
        del self.model
        del self.actions

##    def __del__(self):
##        print '__del__', self.__class__.__name__
        
    def addViewTools(self, toolbar):
        for name, meth, bmp, accls in self.actions:
            if name == '-' and not bmp:
                toolbar.AddSeparator()
            elif bmp != '-':
                if name[0] == '+':
                    # XXX Add toggle button
                    name = name [1:]
                AddToolButtonBmpObject(self.model.editor, toolbar, IS.load(bmp), name, meth)

    docked = true
    def addToNotebook(self, notebook, viewName = '', panel = None):
        self.notebook = notebook
        if not viewName: viewName = self.viewName
        if panel:
            notebook.AddPage(panel, viewName)
        else:
            notebook.AddPage(self, viewName)

        wxYield()
        self.pageIdx = notebook.GetPageCount() -1
        self.modified =  false
        self.readOnly = false

    def deleteFromNotebook(self, focusView, tabName):
        # set selection to source view
        self.model.reorderFollowingViewIdxs(self.pageIdx) 
        self.model.views[focusView].focus()
        del self.model.views[tabName]
        self.destroy()
        self.notebook.DeletePage(self.pageIdx)

    def activate(self):
        self.active = true
        if self.modified: self.refresh()
        
    def deactivate(self):
        self.active = false
            
    def update(self):
        self.modified = true
        if self.active:
            self.refresh()

    def refresh(self):
        self.refreshCtrl()
        self.modified = false

    def refreshModel(self):
        """ Override this to apply changes in your view to the model """
        self.model.update()
        self.model.notify()
    
    def focus(self, refresh = true):
        self.notebook.SetSelection(self.pageIdx)
        if refresh:
##            self.notebook.Refresh()
            self.SetFocus()
    
    def setReadOnly(self, val):
        self.readOnly = val
    
    def close(self):
        print 'EditorView close'
        self.destroy()
    
##    def viewMenu(self):
##        return self.menu, self.
##        menu = wxMenu()
##        accelLst = []
##        for name, meth, bmp, accels in self.actions:
##            if name == '-':
##                menu.AppendSeparator()
##            else:
##                newId = NewId()
##                menu.Append(newId, name)
##                EVT_MENU(self, newId, meth)#
##                if accels: accelLst.append((accels[0], accels[1], newId))
##        return menu, accelLst

    def isModified(self):
        return self.modified 
    
    def goto(self, marker):
        print 'GOTO MARKER', marker
    
    def OnRightDown(self, event):
        self.popx = event.GetX()
        self.popy = event.GetY()

    def OnRightClick(self, event):
        self.PopupMenu(self.menu, wxPoint(self.popx, self.popy))
            
class TestView(wxTextCtrl, EditorView):
    viewName = 'Test'
    def __init__(self, parent, model):
        wxTextCtrl.__init__(self, parent, -1, '', style = wxTE_MULTILINE | wxTE_RICH | wxHSCROLL)
        EditorView.__init__(self, model, (), 5)
        self.active = true
        
    def refreshCtrl(self):
        self.SetValue('')
                
class HTMLView(wxHtmlWindow, EditorView):
    prevBmp = 'Images/Shared/Previous.bmp'
    nextBmp = 'Images/Shared/Next.bmp'

    viewName = 'HTML'
    def __init__(self, parent, model, actions = ()):
        wxHtmlWindow.__init__(self, parent)
        EditorView.__init__(self, model, (('Back', self.OnPrev, self.prevBmp, ()),
                                   ('Forward', self.OnNext, self.nextBmp, ()) )+ actions, -1)
        self.SetRelatedFrame(model.editor, 'Editor')
        self.SetRelatedStatusBar(2)

        model.editor.statusBar.setHint('')

        self.title = 'HTML'
        self.data = ''
        self.active = true

    def generatePage(self):
        return ''

    def refreshCtrl(self):
        self.data = self.generatePage()
        self.SetPage(self.data)

    def OnPrev(self, event):
        self.HistoryBack()

    def OnNext(self, event):
        self.HistoryForward()

class HTMLFileView(HTMLView):
    viewName = 'View'    
    def generatePage(self):
        return self.model.data

# XXX This is expensive and will really need to delay generatePage until View
# XXX is focused (like ExploreView)
# XXX The HTML control does not interact well with Zope.

class ZopeHTMLView(HTMLView):
    viewName = 'View'    
    def generatePage(self):
##        if hasattr(self, 'lastpage'):
##            if len(self.model.viewsModified):
##                return self.lastpage
        import urllib
        url = 'http://%s:%d/%s'%(self.model.zopeConn.host, 
              self.model.zopeConn.http_port, self.model.zopeObj.whole_name())
        f = urllib.urlopen(url)
        s = f.read()
        print url, s
        return s#f.read()


# XXX Add structured text/wiki option for doc strings
# XXX Option to only list documented methods
class HTMLDocView(HTMLView):
    viewName = 'Documentation'
    def __init__(self, parent, model, actions = ()):
        HTMLView.__init__(self, parent, model, ( ('Save HTML', self.OnSaveHTML, '-', ()), )+ actions)
        self.title = 'Boa docs'

    def generatePage(self):
        page = wxwHeaderTemplate % {'Title': self.title}
        page = self.genCustomPage(page) + wxwFooterTemplate
        return page

    def genCustomPage(self, page):
        """ Override to make the page a little more interesting """
        return page

    def OnSaveHTML(self, event):
        # XXX Replace with Boa file selector
        filename = wxFileSelector('Choose a file', '.', '', 
          'HTML files (*.html)|*.html', '.html', wxSAVE)
        if filename:
            open(filename, 'w').write(self.data)

class ModuleDocView(HTMLDocView):

    def genCustomPage(self, page):
        return self.genModuleSect(page)

    def genModuleSect(self, page):
        classList, classNames = self.genClassListSect()
        module = self.model.getModule()
        modBody = wxwModuleTemplate % { \
          'ModuleSynopsis': module.getModuleDoc(),
          'Module': self.model.moduleName,
          'ClassList': classList,
        }

        return self.genClassesSect(page + modBody, classNames)

    def genClassListSect(self):
        clssLst = []
        classNames = self.model.getModule().classes.keys()
        classNames.sort()
        for aclass in classNames:
            clssLst.append('<a href="#%s">%s</a>' %(aclass, aclass))

        return string.join(clssLst, '<BR>'), classNames
                
    def genClassesSect(self, page, classNames):
        clsBody = ''
        classes = []
        module = self.model.getModule()
        for aclass in classNames:
            supers = []
            for super in module.classes[aclass].super:
                try:
                    supers.append('<a href="#%s">%s</a>'%(super.name, super.name))
                except:
                    supers.append(super)
            if len(supers) > 0:
                supers = string.join(supers, ', ')
            else:
                supers = ''

            methlist, meths = self.genMethodSect(aclass)

            clsBody = wxwClassTemplate % { \
              'Class': aclass,
              'ClassSuper': supers,
              'ClassSynopsis': module.getClassDoc(aclass),
              'MethodList': methlist,
              'MethodDetails': meths,
            }
            classes.append(clsBody)
 
        return page + string.join(classes)

    def genMethodSect(self, aclass):
        methlist = []
        meths = []
        module = self.model.getModule()
        methods = module.classes[aclass].methods.keys()
        methods.sort()
        for ameth in methods:
            methlist.append('<a href="#%(Class)s%(Method)s">%(Method)s</a><br>' % {\
              'Class': aclass,
              'Method': ameth})
            methBody = wxwMethodTemplate % { \
              'Class': aclass,
              'Method': ameth,
              'MethodSynopsis': module.getClassMethDoc(aclass, ameth),
              'Params': module.classes[aclass].methods[ameth].signature,
            }
            meths.append(methBody)

        return string.join(methlist), string.join(meths)

class ClosableViewMix:
    closeBmp = 'Images/Editor/Close.bmp'
    
    def __init__(self, hint = 'results'):
        self.closingActionItems = ( ('Close '+ hint, self.OnClose, 
                                     self.closeBmp, keyDefs['Close']), )

    def OnClose(self, event):
        del self.closingActionItems
        self.deleteFromNotebook('Source', self.tabName)

class CyclopsView(HTMLView, ClosableViewMix):
    viewName = 'Cyclops report'
    def __init__(self, parent, model):
        ClosableViewMix.__init__(self)
        HTMLView.__init__(self, parent, model, ( ('-', -1, '', ()), ) + 
          self.closingActionItems)

    def OnLinkClicked(self, linkinfo):
        """ classlink, attriblink """
        url = linkinfo.GetHref()

        if url[0] == '#':
            self.base_OnLinkClicked(linkinfo)
        else:
            jumpType, jumpPath = string.split(url, '://')
            segs = string.split(jumpPath, '.')
            if jumpType == 'classlink':
                mod, clss = segs[-2:]
                if len(segs) > 2:
                    pack = segs[:-2]
                else:
                    pack = []
            elif jumpType == 'attrlink':
                mod, clss, attr = segs[-3:]
                if len(segs) > 3:
                    pack = segs[:-3]
                else:
                    pack = []
    
            for dirname in sys.path:
                fullname = path.abspath(os.path.join(dirname, mod+'.py'))
                if path.exists(fullname):
                    found = fullname
                    break
                else:
                    pckPth = string.join(pack, '/')
                    fullname = path.abspath(path.join(dirname, pckPth, mod+'.py'))
                    if os.path.exists(fullname):
                        found = fullname
                        break
                                
            else: return
            
            model = self.model.editor.openOrGotoModule(fullname)
            module = model.getModule()
            if jumpType == 'classlink':
                lineno = module.classes[clss].block.start
            elif jumpType == 'attrlink':
                if module.classes[clss].attributes.has_key(attr):
                    lineno = module.classes[clss].attributes[attr][0].start
                elif module.classes[clss].methods.has_key(attr):
                    lineno = module.classes[clss].methods[attr].start
                else:
                    lineno = module.classes[clss].block.start

                mod, clss, attr = segs[-3:]
                if len(segs) > 3:
                    pack = segs[:-3]
                else:
                    pack = []
    
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].gotoLine(lineno - 1)
            
    def generatePage(self):
        return self.report
        
    def OnSaveReport(self, event):        
        fn, suc = self.model.editor.saveAsDlg(\
          path.splitext(self.model.filename)[0]+'.cycles', '*.cycles')
        if suc and self.stats:
            pass
 
class ListCtrlView(wxListCtrl, EditorView):
    viewName = 'List (abstract)'
    def __init__(self, parent, model, listStyle, actions, dclickActionIdx = -1):
        wxListCtrl.__init__(self, parent, -1, style = listStyle)
        EditorView.__init__(self, model, actions, dclickActionIdx)

        EVT_LIST_ITEM_SELECTED(self, -1, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, -1, self.OnItemDeselect)
        EVT_KEY_UP(self, self.OnKeyPressed)
        EVT_LIST_COL_CLICK(self, -1, self.OnColClick)
        
        self.selected = -1

        self.sortOnColumns = []
        self.sortCol = -1
        self.active = true
    
    def pastelPicker(self, idx):
        return idx % 2

    def pastelise(self):
        if Preferences.pastels:
            for idx in range(self.GetItemCount()):
                item = self.GetItem(idx)
                if self.pastelPicker(idx):
                    item.SetBackgroundColour(Preferences.pastelMedium)
                else:
                    item.SetBackgroundColour(Preferences.pastelLight)
                self.SetItem(item)

    def refreshCtrl(self):
        self.DeleteAllItems()
    
    def addReportItems(self, index, *list):
        if list:
            self.InsertStringItem(index, list[0])
            self.SetItemData(index, index)
            col = 1
            if len(list) > 1:
                for text in list[1:]:
                    self.SetStringItem(index, col, text)
                    col = col + 1
        return index + 1

    def sortColumn(self, itemIdx1, itemIdx2):
        item1 = self.GetItem(itemIdx1, self.sortCol)
        item2 = self.GetItem(itemIdx2, self.sortCol)
        txt1, txt2 = item1.GetText(), item2.GetText()
        if txt1 < txt2: return -1
        if txt1 > txt2: return 1
        return 0
    
    def OnKeyPressed(self, event):
        key = event.KeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1
    
    def OnColClick(self, event):
        if event.m_col in self.sortOnColumns:
            self.sortCol = event.m_col
            self.SortItems(self.sortColumn)
        # reset idx
        for idx in range(self.GetItemCount()):
            self.SetItemData(idx, idx)
 
idGotoLine = NewId()    
class ToDoView(ListCtrlView):
    viewName = 'Todo'
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT, 
          (('Goto line', self.OnGoto, self.gotoLineBmp, ()),), 0)
        self.InsertColumn(0, 'Line#')
        self.InsertColumn(1, 'Urgency')
        self.InsertColumn(2, 'Entry')
        self.SetColumnWidth(0, 40)
        self.SetColumnWidth(1, 75)
        self.SetColumnWidth(2, 350)

        self.active = true
        self.distinctTodos = []
        self.blockReentrant = false
    
    def pastelPicker(self, idx):
        return ListCtrlView.pastelPicker(self, self.distinctTodos[idx])

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        i = 0
        lastLine = -1
        todoCnt = 0
        self.distinctTodos = []
        module = self.model.getModule()
        for todo in module.todos:
            if todo[0] - 1 == lastLine:
                self.InsertStringItem(i, '')
                self.SetStringItem(i, 1, '')
            else:
                self.InsertStringItem(i, `todo[0]`)
                self.SetStringItem(i, 1, 'Unknown')
                todoCnt = todoCnt + 1
            lastLine = todo[0]
            
            self.distinctTodos.append(todoCnt)
            self.SetStringItem(i, 2, todo[1])
            i = i + 1

        self.pastelise()

##    def OnItemSelect(self, event):
##        ListCtrlView.OnItemSelect(self, event)
##        if not self.blockReentrant:
##            self.blockReentrant = true
##            try:
##                selectedIdx = self.distinctTodos[self.selected]
##                for idx in range(self.GetItemCount()):
##                    item = self.GetItem(idx)
##                    focusState = item.GetState() & wxLIST_STATE_FOCUSED
##                    if self.distinctTodos[idx] == selectedIdx:
##                        selectState = wxLIST_STATE_SELECTED
##                    else:
##                        selectState = 0
##                    item.SetState(selectState | focusState)
##                    self.SetItem(item)
##            finally:
##                self.blockReentrant = false
##
##    def OnItemDeselect(self, event):
##        return
###        ListCtrlView.OnItemDeselect(self, event)
##        if not self.blockReentrant:
##            self.blockReentrant = true
##            try:
##                selectedIdx = self.distinctTodos[self.selected]
##                for idx in range(self.GetItemCount()):
##                    item = self.GetItem(idx)
##                    focusState = item.GetState() & wxLIST_STATE_FOCUSED
##                    if self.distinctTodos[idx] == selectedIdx:
##                        selectState = wxLIST_STATE_SELECTED
##                    else:
##                        selectState = 0
##                    item.SetState(selectState | focusState)
##                    self.SetItem(item)
##            finally:
##                self.blockReentrant = false

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            # XXX Implement an interface for views to talk
            srcView.focus()
            module = self.model.getModule()
            srcView.gotoLine(int(module.todos[self.selected][0]) -1)

tPopupIDPackageOpen = 300

class PackageView(ListCtrlView):
    viewName = 'Package'
    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_LIST, 
          (('Open', self.OnOpen, '-', ()),), 0)

        self.SetImageList(model.editor.modelImageList, wxIMAGE_LIST_SMALL)
               
    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        self.filenames = {}
        self.packageFiles = self.model.generateFileList()
        self.packageFiles.reverse()
        for file in self.packageFiles:
            self.filenames[file[0]] = file[1]
            self.InsertImageStringItem(0, file[0], file[1].imgIdx)

    def OnOpen(self, event):
        if self.selected >= 0:
            name = self.GetItemText(self.selected)
            modCls = self.filenames[name]
            if modCls.defaultName == 'package':
                self.model.openPackage(name)
            else:
                self.model.openFile(name)

class InfoView(wxTextCtrl, EditorView):
    viewName = 'Info'

    def __init__(self, parent, model):
        wxTextCtrl.__init__(self, parent, -1, '', style = wxTE_MULTILINE | wxTE_RICH | wxHSCROLL)
        EditorView.__init__(self, ('Add comment block to code', self.OnAddInfo, ()), 5)
        self.active = true
        self.model = model
        self.SetFont(wxFont(9, wxMODERN, wxNORMAL, wxNORMAL, false))

    def setReadOnly(self, val):
        EditorView.readOnly(self, val)
        self.SetEditable(val)
    
    def refreshCtrl(self):
        pass
        self.SetValue('')
        module = self.model.getModule()
        info = module.getInfoBlock()
        self.WriteText(`info`)
    
    def OnAddInfo(self, event):
        self.model.addInfoBlock()

class ExploreView(wxTreeCtrl, EditorView):
    viewName = 'Explore'
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    def __init__(self, parent, model):
        wxTreeCtrl.__init__(self, parent, -1)
        EditorView.__init__(self, model, (('Goto line', self.OnGoto, self.gotoLineBmp, ()),), 0)

        self.tokenImgLst = wxImageList(16, 16)
        self.tokenImgLst.Add(IS.load('Images/Views/Explore/class.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Views/Explore/method.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Views/Explore/event.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Views/Explore/function.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Views/Explore/attribute.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Modules/'+self.model.bitmap))
        self.SetImageList(self.tokenImgLst)

        self.active = true

        EVT_KEY_UP(self, self.OnKeyPressed)

    _populated_tree = 0

    def OnPageActivated(self, evt):
        if not self._populated_tree:
            self._populated_tree = 1
            # XXX Threading should go...
            if wxPlatform == '__WXGTK__':
                self.refreshCtrl(1)
            else:
                start_new_thread(self.refreshCtrl, (1,))
        
    def refreshCtrl(self, load_now=0):
        self.DeleteAllItems()
        if not load_now:
            self._populated_tree = 0
            return
        self.AddRoot('Loading...')
        module = self.model.getModule()
        self.DeleteAllItems()
        rootItem = self.AddRoot(self.model.moduleName, 5, -1, wxTreeItemData(CodeBlock('', 0, 0)))
        for className in module.class_order:
            classItem = self.AppendItem(rootItem, className, 0, -1, wxTreeItemData(module.classes[className].block))
            for attrib in module.classes[className].attributes.keys():
                attribItem = self.AppendItem(classItem, attrib, 4, -1, #+ ' '+module.classes[className].attributes[attrib][0].signature
                  wxTreeItemData(module.classes[className].attributes[attrib]))
            for method in module.classes[className].method_order:
                if (len(method) >= 3) and (method[:2] == 'On') and \
                  (method[2] in string.uppercase):
                    methodsItem = self.AppendItem(classItem, method, 2, -1, 
                      wxTreeItemData(module.classes[className].methods[method]))
                else:
                    methodsItem = self.AppendItem(classItem, method, 1, -1, 
                      wxTreeItemData(module.classes[className].methods[method]))

        functionList = module.functions.keys()
        functionList.sort()               
        for func in functionList:
            funcItem = self.AppendItem(rootItem, func, 3, -1,
              wxTreeItemData(module.functions[func]))

        self.Expand(rootItem)

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            idx = self.GetSelection()
            if idx.IsOk():
                srcView.focus()
                self.model.editor.addBrowseMarker(srcView.GetCurrentLine())
                dat = self.GetPyData(idx)
                if type(dat) == type([]):   
                    srcView.gotoLine(dat[0].start -1)
                else: 
                    srcView.gotoLine(dat.start -1)

    def OnKeyPressed(self, event):
        key = event.KeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)

class HierarchyView(wxTreeCtrl, EditorView):
    viewName = 'Hierarchy'
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    def __init__(self, parent, model):
        id = NewId()
        wxTreeCtrl.__init__(self, parent, id)
        EditorView.__init__(self, model, 
          (('Goto line', self.OnGoto, self.gotoLineBmp, ()),), 0)

        self.tokenImgLst = wxImageList(16, 16)
        self.tokenImgLst.Add(IS.load('Images/Views/Hierarchy/inherit.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Views/Hierarchy/inherit_base.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Views/Hierarchy/inherit_outside.bmp'))
        self.tokenImgLst.Add(IS.load('Images/Modules/'+self.model.bitmap))

        self.SetImageList(self.tokenImgLst)

        EVT_KEY_UP(self, self.OnKeyPressed)

        self.active = true

    def buildTree(self, parent, dict):
        for item in dict.keys():
            child = self.AppendItem(parent, item, 0)
            if len(dict[item].keys()):
                self.buildTree(child, dict[item])
            self.Expand(child)

    def refreshCtrl(self):
        self.AddRoot('Loading...')
        module = self.model.getModule()
        self.DeleteAllItems()
        hierc = module.createHierarchy()
        
        root = self.AddRoot(self.model.moduleName, 3)#, 0, wxTreeItemData(CodeBlock('', 0, 0)))
        for top in hierc.keys():
            if module.classes.has_key(top): imgIdx = 1
            else: imgIdx = 2
            
            item = self.AppendItem(root, top, imgIdx)
            self.buildTree(item, hierc[top])
            self.Expand(item)
        
        self.Expand(root)


    def OnGoto(self, event):
        idx  = self.GetSelection()
        if idx.IsOk():
            name = self.GetItemText(idx)
            if self.model.views.has_key('Source') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Source']
                srcView.focus()
                module = self.model.getModule()
                srcView.gotoLine(int(module.classes[name].block.start) -1)

    def OnKeyPressed(self, event):
        key = event.KeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)

class DistUtilView(wxPanel, EditorView):
    viewName = 'DistUtils'

    def __init__(self, parent, model):
        wxPanel.__init__(self, parent, -1)
        EditorView.__init__(self, ())#('Add comment block to code', self.OnAddInfo, ()), 5)
        self.active = true
        self.model = model

    
    def refreshCtrl(self):
        pass
    
#class CVSView : Shows conflicts after merging CVS    

#class ImportView(wxOGL, EditorView) -> AppModel: implimented in UMLView.py

#class ContainmentView(wxTreeCtrl, EditorView) -> FrameModel: 
#      parent/child relationship tree hosted in inspector

#class XMLView(wxTextCtrl, EditorView) -> FrameM
