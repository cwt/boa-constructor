#----------------------------------------------------------------------
# Name:        ClassBrowser.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:ClassBrowserFrame

from os import path
import pyclbr, string

from wxPython.wx import *

import Preferences, Utils
from Preferences import IS

[wxID_CLASSBROWSERFRAME, wxID_CLASSBROWSERFRAMEHIERARCHY, wxID_CLASSBROWSERFRAMEPAGES, wxID_CLASSBROWSERFRAMESTATUSBAR, wxID_CLASSBROWSERFRAMETREE] = map(lambda _init_ctrls: wxNewId(), range(5))

class ClassBrowserFrame(wxFrame, Utils.FrameRestorerMixin):
    def _init_coll_pages_Pages(self, parent):

        parent.AddPage(bSelect = true, imageId = -1, pPage = self.hierarchy, strText = 'Hierarchy')
        parent.AddPage(bSelect = false, imageId = -1, pPage = self.tree, strText = 'Modules')

    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_CLASSBROWSERFRAME, name = '', parent = prnt, pos = wxPoint(475, 238), size = wxSize(299, 497), style = wxDEFAULT_FRAME_STYLE | Preferences.childFrameStyle, title = 'wxPython Class Browser')
        self._init_utils()
        self.SetClientSize(wxSize(291, 470))
        EVT_CLOSE(self, self.OnCloseWindow)

        self.statusBar = wxStatusBar(id = wxID_CLASSBROWSERFRAMESTATUSBAR, name = 'statusBar', parent = self, style = wxST_SIZEGRIP)
        self.SetStatusBar(self.statusBar)

        self.pages = wxNotebook(id = wxID_CLASSBROWSERFRAMEPAGES, name = 'pages', parent = self, pos = wxPoint(0, 0), size = wxSize(291, 450), style = 0)

        self.hierarchy = wxTreeCtrl(id = wxID_CLASSBROWSERFRAMEHIERARCHY, name = 'hierarchy', parent = self.pages, pos = wxPoint(0, 0), size = wxSize(283, 424), style = wxTR_HAS_BUTTONS, validator = wxDefaultValidator)

        self.tree = wxTreeCtrl(id = wxID_CLASSBROWSERFRAMETREE, name = 'tree', parent = self.pages, pos = wxPoint(0, 0), size = wxSize(283, 424), style = wxTR_HAS_BUTTONS, validator = wxDefaultValidator)

        self._init_coll_pages_Pages(self.pages)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.winConfOption = 'classbrowser'
        self.loadDims()

        self.SetIcon(IS.load('Images/Icons/ClassBrowser.ico'))

        self.classes = pyclbr.readmodule('wxPython.wx')

#        self.pages = wxNotebook(self, -1)
#        self.statusBar = self.CreateStatusBar()

        tID = wxNewId()
#        self.hierarchy = wxTreeCtrl(self.pages, tID)
#        self.pages.AddPage(self.hierarchy, 'Hierarchy')
#        wxYield()
        root = self.hierarchy.AddRoot('wxObject')

        clsDict = {}

        for i in self.classes.keys():
            travTilBase(i, self.classes, clsDict)

        buildTree(self.hierarchy, root, clsDict)
        self.hierarchy.Expand(root)

        tID = wxNewId()

#        self.tree = wxTreeCtrl(self.pages, tID)
#        self.pages.AddPage(self.tree, 'Modules')
#        wxYield()

        root = self.tree.AddRoot('Modules')
        modules = {}
        moduleName = ''
        for className in self.classes.keys():
            moduleName = path.basename(self.classes[className].file)
            if not modules.has_key(moduleName):
                modules[moduleName] = {}
            modules[moduleName][className] = {}
            modules[moduleName][className]['Properties'] = {}
            modules[moduleName][className]['Methods'] = {}
            modules[moduleName][className]['Built-in'] = {}
            for method in self.classes[className].methods.keys():
                if (method[:2] == '__'):
                    modules[moduleName][className]['Built-in'][method] = self.classes[className].lineno
                elif (method[:3] == 'Get'):
                    if self.classes[className].methods.has_key('Set'+method[3:]):
                        modules[moduleName][className]['Properties'][method[3:]] = self.classes[className].lineno
                    else:
                        modules[moduleName][className]['Methods'][method] = self.classes[className].lineno
                elif (method[:3] == 'Set'):
                    if self.classes[className].methods.has_key('Get'+method[3:]):
                        modules[moduleName][className]['Properties'][method[3:]] = self.classes[className].lineno
                    else:
                        modules[moduleName][className]['Methods'][method] = self.classes[className].lineno
                else:
                    modules[moduleName][className]['Methods'][method] = self.classes[className].lineno
        moduleLst = modules.keys()
        moduleLst.sort()
        for module in moduleLst:
            roots = self.tree.AppendItem(root, module)
            classLst = modules[module].keys()
            classLst.sort()
            for classes in classLst:
                aClass = self.tree.AppendItem(roots, classes)
                methItem = self.tree.AppendItem(aClass, 'Methods')
                for methods in modules[module][classes]['Methods'].keys():
                    methodsItem = self.tree.AppendItem(methItem, methods)
                propItem = self.tree.AppendItem(aClass, 'Properties')
                for properties in modules[module][classes]['Properties'].keys():
                    propertyItem = self.tree.AppendItem(propItem, properties)
                bInItem = self.tree.AppendItem(aClass, 'Built-in')
                for builtIns in modules[module][classes]['Built-in'].keys():
                    builtInItem = self.tree.AppendItem(bInItem, builtIns)
                suprItem = self.tree.AppendItem(aClass, 'Super')
                for supers in self.classes[classes].super:
                    superItem = self.tree.AppendItem(suprItem, supers.name)

#                supers = self.tree.AppendItem(roots, 'Super')
#                for super in self.classes[className].super:
#                    aMethod = self.tree.AppendItem(supers, super.name)
        self.tree.Expand(root)

    def setDefaultDimensions(self):
        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth,
          Preferences.bottomHeight)

    def OnCloseWindow(self, event):
        self.Show(true)
        self.Show(false)
        if __name__ == '__main__':
            self.Destroy()


def findInsertModules(name, tree):
    ri = tree.GetRootItem()
    item = ri
    found = false
    while item:
        item = tree.GetNextSibling(item)
        if tree.GetItemText(item) == name:
            found = true
            return item

    return tree.AddRoot(name)

def travTilBase(name, classes, root):
    if len(classes[name].super) == 0:
        if not root.has_key(name):
            root[name] = {}
        return root[name]
    else:
        c = travTilBase(classes[name].super[0].name, classes, root)
        if not c.has_key(name):
            c[name] = {}
        return c[name]

def buildTree(tree, parent, dict):
    items = dict.keys()
    items.sort()
    for item in items:
        child = tree.AppendItem(parent, item)
        if len(dict[item].keys()):
            buildTree(tree, child, dict[item])


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = ClassBrowserFrame(None)
    frame.Show(true)
    app.MainLoop()
