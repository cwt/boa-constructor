#-----------------------------------------------------------------------------
# Name:        ExtMethDlg.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ExtMethDlg

from wxPython.wx import *
import os
from os import path

def create(parent, zopepath):
    return ExtMethDlg(parent, zopepath)

class ExternalMethodFinder:
    def __init__(self, zopeDir):
        self.zopeDir = zopeDir
        if self.zopeDir:
            self.prodsDir = path.join(zopeDir, 'lib','python','Products')
        else:
            self.prodsDir = ''

    def getModules(self):
        mods = self._addPyMods(path.join(self.zopeDir, 'Extensions'))

        if self.prodsDir:
            prods = os.listdir(self.prodsDir)
            for p in prods:
                if path.exists(path.join(self.prodsDir, p)) and \
                      path.exists(path.join(self.prodsDir, p, 'Extensions')):
                    mods.extend(self._addPyMods(path.join(self.prodsDir, p,
                          'Extensions'), p))
        return mods

    def _addPyMods(self, pypath, prod=''):
        from Explorers import Explorer
        Explorer.listdirEx(pypath, '.zexp')
        mods = []
        fls = Explorer.listdirEx(pypath, '.py')
        for file in fls:
            mods.append(prod +(prod and '.')+path.splitext(file)[0])
        return mods

    def getExtPath(self, module):
        modLst = string.split(module, '.')
        if len(modLst) == 1:
            modpath = path.join(self.zopeDir, 'Extensions', modLst[0] + '.py')
        else:
            modpath = path.join(self.prodsDir, modLst[0], 'Extensions', modLst[1]+'.py')
        return string.replace(modpath, '<LocalFS::directory>', '<LocalFS::file>')

    def getFunctions(self, module):
        from Explorers import Explorer
        extPath = self.getExtPath(module)

        src = Explorer.openEx(extPath).load()
        sep = string.count(src, '\r\n') < string.count(src, '\n') and '\n' or '\r\n'
        srclines = string.split(src, sep)

        import moduleparse
        module = moduleparse.Module('test', srclines)

        return module.functions.keys()


[wxID_EXTMETHDLGSTATICTEXT1, wxID_EXTMETHDLGSTATICTEXT2, wxID_EXTMETHDLGCHFUNCTION, wxID_EXTMETHDLGPANEL1, wxID_EXTMETHDLGBTOK, wxID_EXTMETHDLGBTCANCEL, wxID_EXTMETHDLGCBMODULE, wxID_EXTMETHDLG] = map(lambda _init_ctrls: wxNewId(), range(8))

class ExtMethDlg(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, size = wxSize(267, 141), id = wxID_EXTMETHDLG, title = 'Add External Method', parent = prnt, name = 'ExtMethDlg', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(363, 248))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(248, 112), parent = self, id = wxID_EXTMETHDLGPANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.staticText1 = wxStaticText(label = 'Module:', id = wxID_EXTMETHDLGSTATICTEXT1, parent = self.panel1, name = 'staticText1', size = wxSize(38, 13), style = 0, pos = wxPoint(8, 16))

        self.staticText2 = wxStaticText(label = 'Function:', id = wxID_EXTMETHDLGSTATICTEXT2, parent = self.panel1, name = 'staticText2', size = wxSize(44, 13), style = 0, pos = wxPoint(8, 48))

        self.cbModule = wxComboBox(size = wxSize(184, 21), value = '', pos = wxPoint(64, 8), choices = [], parent = self.panel1, name = 'cbModule', validator = wxDefaultValidator, style = 0, id = wxID_EXTMETHDLGCBMODULE)
        EVT_COMBOBOX(self.cbModule, wxID_EXTMETHDLGCBMODULE, self.OnCbmoduleCombobox)

        self.chFunction = wxComboBox(size = wxSize(184, 21), value = '', pos = wxPoint(64, 40), choices = [], parent = self.panel1, name = 'chFunction', validator = wxDefaultValidator, style = 0, id = wxID_EXTMETHDLGCHFUNCTION)
        EVT_COMBOBOX(self.chFunction, wxID_EXTMETHDLGCHFUNCTION, self.OnChfunctionCombobox)

        self.btOK = wxButton(label = 'OK', id = wxID_EXTMETHDLGBTOK, parent = self.panel1, name = 'btOK', size = wxSize(72, 24), style = 0, pos = wxPoint(96, 80))
        EVT_BUTTON(self.btOK, wxID_EXTMETHDLGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(label = 'Cancel', id = wxID_EXTMETHDLGBTCANCEL, parent = self.panel1, name = 'btCancel', size = wxSize(72, 24), style = 0, pos = wxPoint(176, 80))
        EVT_BUTTON(self.btCancel, wxID_EXTMETHDLGBTCANCEL, self.OnBtcancelButton)

    def __init__(self, parent, zopeDir):
        self._init_ctrls(parent)

        self.emf = ExternalMethodFinder(zopeDir)

        for mod in self.emf.getModules():
            self.cbModule.Append(mod)

    def OnBtokButton(self, event):
        self.EndModal(wxID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wxID_CANCEL)

    def OnCbmoduleCombobox(self, event):
        if self.emf.zopeDir:
            self.chFunction.Clear()
            mod = self.cbModule.GetStringSelection()

            functions = self.emf.getFunctions(mod)

            for func in functions:
                self.chFunction.Append(func)

    def OnChfunctionCombobox(self, event):
        pass


if __name__ == '__main__':
    app = wxPySimpleApp()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
