from wxPython.wx import *

from EditorViews import ListCtrlView, ModuleDocView, wxwAppModuleTemplate, CyclopsView, ClosableViewMix
from ProfileView import ProfileStatsView
from PrefsKeys import keyDefs
import Search
from os import path
from time import time, gmtime, strftime
try:
    from cmp import cmp
except ImportError:
    from filecmp import cmp
    
class AppFindResults(ListCtrlView, ClosableViewMix):
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    viewName = 'Application Find Results'
    def __init__(self, parent, model):
        ClosableViewMix.__init__(self, 'find results')
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT, 
          ( ('Goto match', self.OnGoto, self.gotoLineBmp, ()), ) +
            self.closingActionItems, 0)
           
        self.InsertColumn(0, 'Module', width = 100)
        self.InsertColumn(1, 'Line no', wxLIST_FORMAT_CENTRE, 40)
        self.InsertColumn(2, 'Col', wxLIST_FORMAT_CENTRE, 40)
        self.InsertColumn(3, 'Text', width = 550)

        self.results = {}
        self.listResultIdxs = []
        self.tabName = 'Results'  
        self.findPattern = ''  
        self.active = true
        self.model = model

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        i = 0
        self.listResultIdxs = []
        for mod in self.results.keys():
            for result in self.results[mod]:   
                self.listResultIdxs.append((mod, result))
                i = self.addReportItems(i, path.basename(mod), `result[1]`, 
                  `result[0]`, string.strip(result[2]))
                
##                self.InsertStringItem(i, path.basename(mod))
##                self.SetStringItem(i, 1, `result[1]`)
##                self.SetStringItem(i, 2, `result[0]`)
##                self.SetStringItem(i, 3, string.strip(result[2]))
##                i = i + 1
        self.pastelise()

    def OnGoto(self, event):
        if self.selected >= 0:
            modName = self.listResultIdxs[self.selected][0]
            model = self.model.openModule(modName)
            srcView = model.views['Source']
            srcView.focus()
            foundInfo = self.listResultIdxs[self.selected][1]
            srcView.lastSearchPattern = self.findPattern
            srcView.lastSearchResults = self.results[modName]
            try:
                srcView.lastMatchPosition = self.results[modName].index(foundInfo)
            except:
                srcView.lastMatchPosition = 0
                print 'foundInfo not found'

            srcView.selectSection(foundInfo[0], foundInfo[1], self.findPattern)

class AppView(ListCtrlView):
    openBmp = 'Images/Editor/OpenFromApp.bmp'
    openAllBmp = 'Images/Editor/OpenAll.bmp'
    saveAllBmp = 'Images/Editor/SaveAll.bmp'
    addModBmp = 'Images/Editor/AddToApp.bmp'
    remModBmp = 'Images/Editor/RemoveFromApp.bmp'
    findBmp = 'Images/Shared/Find.bmp'
    profileBmp = 'Images/Debug/Profile.bmp'
    runBmp = 'Images/Debug/RunApp.bmp'
    debugBmp = 'Images/Debug/Debug.bmp'
    cyclBmp = 'Images/Shared/Cyclops.bmp'
#    importsBmp = 'Images/Editor/Imports.bmp'

    viewName = 'Application'
    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT, 
          (('Open', self.OnOpen, self.openBmp, ()),
           ('Open all modules', self.OnOpenAll, self.openAllBmp, ()), 
           ('Save all modules', self.OnSaveAll, self.saveAllBmp, ()), 
           ('-', None, '', ()),
           ('Add', self.OnAdd, self.addModBmp, keyDefs['Insert']),
           ('Edit', self.OnEdit, '-', ()),
           ('Remove', self.OnRemove, self.remModBmp, keyDefs['Delete']),
           ('-', None, '', ()),
           ('Find', self.OnFind, self.findBmp, keyDefs['Find']),
           ('-', None, '', ()),
           ('Cyclops', self.OnCyclops, self.cyclBmp, ()),
           ('-', None, '', ()),
           ('Profile', self.OnProfile, self.profileBmp, ()),
           ('Run application', self.OnRun, self.runBmp, keyDefs['RunApp']),
           ('Debugger', self.OnDebugger, self.debugBmp, keyDefs['Debug'])), 0)

#           ('-', None, '', ()),
#           ('Imports...', self.OnImports, self.importsBmp, ())
           
        self.InsertColumn(0, 'Module', width = 150)
        self.InsertColumn(1, 'Type', width = 50)
        self.InsertColumn(2, 'Autocreate', wxLIST_FORMAT_CENTRE, 50)
        self.InsertColumn(3, 'Description', width = 150)
        self.InsertColumn(4, 'Relative path', width = 220)

        self.sortOnColumns = [0, 1, 4]
        
        EVT_LIST_BEGIN_DRAG(self, self.GetId(), self.OnDrag)

        self.SetImageList(model.editor.modelImageList, wxIMAGE_LIST_SMALL)
        
        self.lastSearchPattern = ''
        self.active = true
        self.model = model

    def OnDrag(self, event):
        print 'drag', event.GetString()
        print 'drag', dir(event.__class__.__bases__[0])

    def refreshCtrl(self):
        # XXX Add 'type' sortable column
        ListCtrlView.refreshCtrl(self)
        i = 0
        modSort = self.model.modules.keys()
        modSort.sort()
        for mod in modSort:
            # XXX Show a broken icon as default
            imgIdx = -1
            modTpe = 'Unknown'
            if self.model.moduleModels.has_key(mod):
                imgIdx = self.model.moduleModels[mod].imgIdx
                modTpe = self.model.moduleModels[mod].modelIdentifier
            else:
                self.model.idModel(mod)
                if self.model.moduleModels.has_key(mod):
                    imgIdx = self.model.moduleModels[mod].imgIdx
                    modTpe = self.model.moduleModels[mod].modelIdentifier
                    
            appMod = self.model.modules[mod]
            self.InsertImageStringItem(i, mod, imgIdx)
            self.SetStringItem(i, 1, modTpe)
            self.SetStringItem(i, 2, `appMod[0]`)
            self.SetStringItem(i, 3, appMod[1])
            self.SetStringItem(i, 4, appMod[2])
            self.SetItemData(i, i)
            i = i + 1
        
        self.pastelise()

    def OnOpen(self, event):
        if self.selected >= 0:
            self.model.openModule(self.GetItemText(self.selected))
            
    def OnAdd(self, event):
        self.model.viewAddModule()

    def OnEdit(self, event):
        pass

    def OnRemove(self, event):
        if self.selected >= 0:
            self.model.removeModule(self.GetItemText(self.selected))

    def OnRun(self, event):
        wxBeginBusyCursor()
        try:
            self.model.run()
        finally:
            wxEndBusyCursor()

    def OnDebugger(self, event):
        wxBeginBusyCursor()
        try:
            self.model.debug()  
        finally:
            wxEndBusyCursor()
    
    def OnProfile(self, event):
        stats = self.model.profile()
        resName = 'Profile stats: %s'%strftime('%H:%M:%S', gmtime(time()))
        if not self.model.views.has_key(resName):
            resultView = self.model.editor.addNewView(resName, ProfileStatsView)
        else:
            resultView = self.model.views[resName]
        resultView.tabName = resName
        resultView.stats = stats
        resultView.refresh()
        resultView.focus()
    
    def OnCyclops(self, event):
        wxBeginBusyCursor()
        try:
            report = self.model.cyclops()
        finally:
            wxEndBusyCursor()
        
        resName = 'Cyclops report: %s'%strftime('%H:%M:%S', gmtime(time()))
        if not self.model.views.has_key(resName):
            resultView = self.model.editor.addNewView(resName, CyclopsView)
        else:
            resultView = self.model.views[resName]
        resultView.tabName = resName
        resultView.report = report
        resultView.refresh()
        resultView.focus()        

    def OnImports(self, events):
        wxBeginBusyCursor()
        try:
            self.model.showImportsView()
        finally:
            wxEndBusyCursor()

        if self.model.views.has_key('Imports'):
            self.model.views['Imports'].focus()
        self.model.update()
        self.model.notify()

    def OnOpenAll(self, event):
        modules = self.model.modules.keys()
        modules.sort() 
        for mod in modules:
            try:
                self.model.editor.openOrGotoModule(\
                  self.model.modules[mod][2])
            except: pass

    def OnSaveAll(self, event):
        for modulePage in self.model.editor.modules.values():
            mod = modulePage.model
            if mod != self.model:
                if hasattr(mod, 'app') and mod.app == self.model and \
                  (mod.modified or len(mod.viewsModified)):
                    print 'saving', mod.filename  
                    if len(mod.viewsModified):
                        mod.refreshFromViews()
                    modulePage.saveOrSaveAs()
            else:
                appModPage = modulePage
        appModPage.saveOrSaveAs()
        

    def OnFind(self, event):
        dlg = wxTextEntryDialog(self.model.editor, 'Enter text:', 'Find in application', self.lastSearchPattern)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.lastSearchPattern = dlg.GetValue()
                modules = self.model.modules.keys()
                modules.sort()
                applicationResults = {}
                for mod in modules:
                    filename = self.model.moduleFilename(mod)#self.model.modules[mod][2])
                    if self.model.editor.modules.has_key(filename):
                        results = Search.findInText(self.model.editor.modules[filename].model.data, self.lastSearchPattern, false, true)
                    else:
                        results = Search.findInFile(filename, self.lastSearchPattern, false, true)
                    applicationResults[mod] = results

                resName = 'Results: '+dlg.GetValue()
                if not self.model.views.has_key(resName):
                    resultView = self.model.editor.addNewView(resName, AppFindResults)
                else:
                    resultView = self.model.views[resName]
                resultView.tabName = resName
                resultView.results = applicationResults
                resultView.findPattern = self.lastSearchPattern
                resultView.refresh()
                resultView.focus()
                        
        finally:
            dlg.Destroy()         


class AppModuleDocView(ModuleDocView):
    viewName = 'Application Documentation'

    def OnLinkClicked(self, linkinfo):
        url = linkinfo.GetHref()

        if url[0] == '#':
            self.base_OnLinkClicked(linkinfo)
        else:
            mod = path.splitext(url)[0]
#            print mod
            newMod = self.model.openModule(mod)
            newMod.views['Documentation'].focus()

    def genModuleListSect(self):
        modLst = []
        modNames = self.model.modules.keys()
        modNames.sort()
        for amod in modNames:
            desc = string.strip(self.model.modules[amod][1])
            modLst.append('<tr><td width="25%%"><a href="%s.html">%s</a></td><td>%s</td></tr>' %(amod, amod, desc))

        return '<table BORDER=0 CELLSPACING=0 CELLPADDING=0>'+string.join(modLst, '<BR>')+'</table>', modNames

    def genModuleSect(self, page):
        classList, classNames = self.genClassListSect()
        modBody = wxwAppModuleTemplate % { \
          'ModuleSynopsis': self.model.module.getModuleDoc(),
          'Module': self.model.moduleName,
          'ModuleList': self.genModuleListSect()[0],
          'ClassList': classList,
        }  

        return self.genClassesSect(page + modBody, classNames)
      
class AppCompareView(ListCtrlView, ClosableViewMix):
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    viewName = 'App. Compare'
    def __init__(self, parent, model):
        ClosableViewMix.__init__(self, 'compare results')
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT, 
          ( ('Do diff', self.OnGoto, self.gotoLineBmp, ()), ) +
           self.closingActionItems, 0)
           
        self.InsertColumn(0, 'Module', width = 100)
        self.InsertColumn(1, 'Differs from', width = 450)
        self.InsertColumn(2, 'Result', width = 75)

        self.results = {}
        self.listResultIdxs = []
        self.tabName = 'App. Compare'  
        self.active = true
        self.model = model
        self.compareTo = ''

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        from EditorModels import AppModel
        otherApp = AppModel('', self.compareTo, '', self.model.editor, true)
        otherApp.load()
        
        otherApp.readModules()
        
        i = 0

        # Compare apps
        if not cmp(self.model.filename, otherApp.filename):
            i = self.addReportItems(i, 
              path.splitext(path.basename(self.model.filename))[0], 
              otherApp.filename, 'changed')

        # Find changed modules and modules not occuring in other module
        for module in self.model.modules.keys():
            if otherApp.modules.has_key(module):
                otherFile = otherApp.moduleFilename(module)
                if not cmp(self.model.moduleFilename(module), otherFile):
                    i = self.addReportItems(i, module, otherFile, 'changed')
            else:
                i = self.addReportItems(i, module, '', 'deleted')
        
        # Find modules only occuring in other module
        for module in otherApp.modules.keys():
            if not self.model.modules.has_key(module):
                otherFile = otherApp.moduleFilename(module)
                i = self.addReportItems(i, module, '', 'added')

        self.pastelise()

    def OnGoto(self, event):
        if self.selected >= 0:
            module = self.GetItemText(self.selected)
            model = self.model.openModule(module)
            otherModule = self.GetItem(self.selected, 1).GetText()
            if otherModule:
                model.diff(otherModule)

      