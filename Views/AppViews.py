#-----------------------------------------------------------------------------
# Name:        AppViews.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

""" View classes for the AppModel """

from os import path
import time
#from time import time, gmtime, strftime
try:
    from cmp import cmp
except ImportError:
    from filecmp import cmp

from wxPython.wx import *

from EditorViews import ListCtrlView, ModuleDocView, wxwAppModuleTemplate, CyclopsView, ClosableViewMix
import ProfileView
import PySourceView
from Preferences import keyDefs
import Search, Utils

class AppFindResults(ListCtrlView, ClosableViewMix):
    gotoLineBmp = 'Images/Editor/GotoLine.bmp'

    viewName = 'Application Find Results'
    def __init__(self, parent, model):
        ClosableViewMix.__init__(self, 'find results')
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT,
          ( ('Goto match', self.OnGoto, self.gotoLineBmp, ()), 
            ('Rerun query', self.OnRerun, '-', ()),
          ) +
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
                i = self.addReportItems(i, (path.basename(mod), `result[0]`,
                  `result[1]`, string.strip(result[2])) )

        self.model.editor.statusBar.setHint('%d matches of "%s".'%(i, self.findPattern))

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

    def OnRerun(self, event):
        pass

class AppView(ListCtrlView):
    openBmp = 'Images/Editor/OpenFromApp.bmp'
    addModBmp = 'Images/Editor/AddToApp.bmp'
    remModBmp = 'Images/Editor/RemoveFromApp.bmp'
    findBmp = 'Images/Shared/Find.bmp'

    viewName = 'Application'
    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT,
          (('Open', self.OnOpen, self.openBmp, ()),
           ('-', None, '', ()),
           ('Add', self.OnAdd, self.addModBmp, keyDefs['Insert']),
           ('Edit', self.OnEdit, '-', ()),
           ('Remove', self.OnRemove, self.remModBmp, keyDefs['Delete']),
           ('-', None, '', ()),
           ('Find', self.OnFind, self.findBmp, keyDefs['Find']),
           ('-', None, '-', ()),
           ('Make module main module', self.OnMakeMain, '-', ()),
           ), 0)

        self.InsertColumn(0, 'Module', width = 150)
        self.InsertColumn(1, 'Type', width = 50)
#        self.InsertColumn(2, 'Autocreate', wxLIST_FORMAT_CENTRE, 50)
        self.InsertColumn(2, 'Description', width = 150)
        self.InsertColumn(3, 'Relative path', width = 220)

        self.sortOnColumns = [0, 1, 3]

#        EVT_LIST_BEGIN_DRAG(self, self.GetId(), self.OnDrag)

        self.SetImageList(model.editor.modelImageList, wxIMAGE_LIST_SMALL)

        self.lastSearchPattern = ''
        self.active = true
        self.canExplore = true
        self.model = model

    def OnDrag(self, event):
        print 'drag', event.GetString()
        print 'drag', dir(event.__class__.__bases__[0])

    def explore(self):
        modSort = self.model.modules.keys()
        modSort.sort()
        return modSort

    def refreshCtrl(self):
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

            if appMod[0]:
                modTpe = '*%s*'%modTpe

            i = self.addReportItems(i, (mod, modTpe, appMod[1], appMod[2]), imgIdx)

        self.pastelise()

    def OnOpen(self, event):
        if self.selected >= 0:
            self.model.openModule(self.GetItemText(self.selected))

    def OnAdd(self, event):
        self.model.viewAddModule()

    def OnEdit(self, event):
        name = self.GetItemText(self.selected)
        dlg = wxTextEntryDialog(self, 'Set the description of the module',
            'Edit item', self.model.modules[name][1])
        try:
            if dlg.ShowModal() == wxID_OK:
                answer = dlg.GetValue()
                self.model.editModule(name, name, self.model.modules[name][0],
                      answer)
                self.model.update()
                self.model.notify()
        finally:
            dlg.Destroy()

    def OnRemove(self, event):
        if self.selected >= 0:
            if not self.model.modules[self.GetItemText(self.selected)][0]:
                self.model.removeModule(self.GetItemText(self.selected))
            else:
                wxMessageBox('Cannot remove the main frame of an application',
                    'Module remove error')

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

    def OnFind(self, event):
        dlg = wxTextEntryDialog(self.model.editor, 'Enter text:', 'Find in application', self.lastSearchPattern)
        try:
            te = Utils.getCtrlsFromDialog(dlg, 'wxTextCtrlPtr')[0]
            te.SetSelection(0, len(self.lastSearchPattern))
            if dlg.ShowModal() == wxID_OK:
                self.lastSearchPattern = dlg.GetValue()
                modules = self.model.modules.keys()
                modules.sort()
                applicationResults = {}
                for mod in modules:
                    filename = self.model.moduleFilename(mod)
                    if self.model.editor.modules.has_key(filename):
                        results = Search.findInText(string.split(\
                          self.model.editor.modules[filename].model.data, '\n'),
                          self.lastSearchPattern, false, true)
                    else:
                        results = Search.findInFile(filename,
                          self.lastSearchPattern, false, true)
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
            event.Skip()

    def OnMakeMain(self, event):
        if self.selected >= 0:
            self.model.changeMainFrameModule(self.GetItemText(self.selected))


class AppModuleDocView(ModuleDocView):
    viewName = 'Application Documentation'

    def OnLinkClicked(self, linkinfo):
        url = linkinfo.GetHref()

        if url[0] == '#':
            self.base_OnLinkClicked(linkinfo)
        else:
            mod = path.splitext(url)[0]
            newMod = self.model.openModule(mod)
            view  = newMod.editor.addNewView(ModuleDocView.viewName, ModuleDocView)
            view.refreshCtrl()
            view.focus()

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
        funcList, funcNames = self.genFuncListSect()
        module = self.model.getModule()
        modBody = wxwAppModuleTemplate % { \
          'ModuleSynopsis': module.getModuleDoc(),
          'Module': self.model.moduleName,
          'ModuleList': self.genModuleListSect()[0],
          'ClassList': classList,
          'FunctionList': funcList,
       }

        return self.genFunctionsSect(\
            self.genClassesSect(page + modBody, classNames), funcNames)

#        return self.genClassesSect(page + modBody, classNames)

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
        otherApp = AppModel('', self.compareTo, '', self.model.editor, true, {})
        otherApp.load()

        otherApp.readModules()

        i = 0

        # Compare apps
        if not cmp(self.model.filename, otherApp.filename):
            i = self.addReportItems(i,
              (path.splitext(path.basename(self.model.filename))[0],
              otherApp.filename, 'changed'))

        # Find changed modules and modules not occuring in other module
        for module in self.model.modules.keys():
            if otherApp.modules.has_key(module):
                otherFile = otherApp.moduleFilename(module)
                try:
                    if not cmp(self.model.moduleFilename(module), otherFile):
                        i = self.addReportItems(i, (module, otherFile, 'changed') )
                except OSError:
                    pass
            else:
                i = self.addReportItems(i, (module, '', 'deleted') )

        # Find modules only occuring in other module
        for module in otherApp.modules.keys():
            if not self.model.modules.has_key(module):
                otherFile = otherApp.moduleFilename(module)
                i = self.addReportItems(i, (module, '', 'added') )

        self.pastelise()

    def OnGoto(self, event):
        if self.selected >= 0:
            module = self.GetItemText(self.selected)
            model = self.model.openModule(module)
            otherModule = self.GetItem(self.selected, 1).GetText()
            if otherModule:
                model.diff(otherModule)

class TextInfoFileView(PySourceView.EditorStyledTextCtrl):
    viewName = 'TextInfo'
    def __init__(self, parent, model):
        PySourceView.EditorStyledTextCtrl.__init__(self, parent, -1,
          model, (), 0)
        self.active = true
        PySourceView.EVT_STC_UPDATEUI(self, self.GetId(), self.OnUpdateUI)
        self.model.loadTextInfo(self.viewName)

    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

    def getModelData(self):
        return self.model.textInfos[self.viewName]

    def setModelData(self, data):
        self.model.textInfos[self.viewName] = data
        if self.viewName not in self.model.unsavedTextInfos:
            self.model.unsavedTextInfos.append(self.viewName)

class AppREADME_TIFView(TextInfoFileView):
    viewName = 'Readme.txt'

class AppTODO_TIFView(TextInfoFileView):
    viewName = 'Todo.txt'

class AppBUGS_TIFView(TextInfoFileView):
    viewName = 'Bugs.txt'

class AppCHANGES_TIFView(TextInfoFileView):
    viewName = 'Changes.txt'

class AppTimeTrackView(ListCtrlView):
    viewName = 'Time Tracking'
    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT,
          (('Start', self.OnStart, '-', ()),
           ('End', self.OnEnd, '-', ()),
           ('Delete', self.OnDelete, '-', ()),
          ), 1 )

        self.InsertColumn(0, 'Start', width = 150)
        self.InsertColumn(1, 'End', width = 150)
        self.InsertColumn(2, 'Description', width = 350)

        self.sortOnColumns = [0, 1]

        self.times = []

        self.active = true
        self.model = model

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        try:
            self.times = self.readTimes()
        except IOError:
            self.times = []
            #fn = self.getTTVFilename()
            #if not path.exists(fn): open(fn, 'w')

        i = 0
        modSort = self.model.modules.keys()
        modSort.sort()
        for start, end, desc in self.times:
            i = self.addReportItems(i,
                  (self.getTimeStr(start),
                   end and self.getTimeStr(end) or '',
                   desc) )

        self.pastelise()

    def getTimeStr(self, thetime):
        return time.strftime('%Y/%m/%d : %H:%M:%S', time.gmtime(thetime))

    def getTTVFilename(self):
        return path.splitext(self.model.filename)[0]+'.ttv'

    def writeTimeEntry(self, file, start, end, desc):
        file.write("(%s, %s, %s)\n" % (`start`, `end`, `desc`))

    def readTimes(self):
        return map(lambda line: eval(line), open(self.getTTVFilename()).readlines())

    def writeTimes(self):
        timesFile = open(self.getTTVFilename(), 'w')
        for start, end, desc in self.times:
            self.writeTimeEntry(timesFile, start, end, desc)

    def OnStart(self, event):
        self.writeTimeEntry(open(self.getTTVFilename(), 'a'), time.time(), 0, '')

        self.refreshCtrl()

    def OnEnd(self, event):
        selIdx = self.getSelectedIndex()
        start, end, desc = self.times[selIdx]

        if not end:
            end = time.time()

        dlg = wxTextEntryDialog(self, 'Start time :%s\nEnd time :%s\n\n'\
            'Enter a description for the time spent' % (self.getTimeStr(start),
              self.getTimeStr(end)), 'Time tracking', desc)
        try:
            if dlg.ShowModal() == wxID_OK:
                answer = dlg.GetValue()
                self.times[selIdx] = (start, end, answer)
                self.writeTimes()
                self.refreshCtrl()
        finally:
            dlg.Destroy()

    def OnDelete(self, event):
        selIdx = self.getSelectedIndex()

        if selIdx == -1:
            return

        dlg = wxMessageDialog(self, 'Are you sure?',
          'Delete', wxOK | wxCANCEL | wxICON_QUESTION)
        try:
            if dlg.ShowModal() == wxID_OK:
                del self.times[selIdx]
                self.writeTimes()
                self.refreshCtrl()

        finally:
            dlg.Destroy()
