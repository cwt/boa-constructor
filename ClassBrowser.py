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

from wxPython.wx import *
import pyclbr
import string
import Preferences
from os import path

[wxID_CLASSBROWSERFRAME] = map(lambda _init_ctrls: NewId(), range(1))

class ClassBrowserFrame(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = (-1, -1), id = wxID_CLASSBROWSERFRAME, title = 'wxPython Class Browser', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = (-1, -1))

    def __init__(self, parent, id, title):
        self._init_ctrls(parent)
        self._init_utils()
        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth,
          Preferences.bottomHeight)
        EVT_CLOSE(self, self.OnCloseWindow)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/ClassBrowser.ico'))

        self.classes = pyclbr.readmodule('wxPython.wx')

        self.pages = wxNotebook(self, -1)
        self.statusBar = self.CreateStatusBar()

        tID = NewId()
        self.hierarchy = wxTreeCtrl(self.pages, tID)
        self.pages.AddPage(self.hierarchy, 'Hierarchy')
        wxYield()
        root = self.hierarchy.AddRoot('wxObject')

        clsDict = {}

        for i in self.classes.keys():
            travTilBase(i, self.classes, clsDict)

        buildTree(self.hierarchy, root, clsDict)
        self.hierarchy.Expand(root)

        tID = NewId()

        self.tree = wxTreeCtrl(self.pages, tID)
        self.pages.AddPage(self.tree, 'Modules')
        wxYield()

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

    def OnCloseWindow(self, event):
        self.Show(false)

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
    for item in dict.keys():
        child = tree.AppendItem(parent, item)
        if len(dict[item].keys()):
            buildTree(tree, child, dict[item])
