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

import os

from wxPython.wx import *

def create(parent, zopepath):
    return ExtMethDlg(parent, zopepath)

class ExternalMethodFinder:
    def __init__(self, zopeDir):
        self.zopeDir = zopeDir
        if self.zopeDir:
            self.prodsDir = os.path.join(zopeDir, 'lib','python','Products')
        else:
            self.prodsDir = ''

    def getModules(self):
        mods = self._addPyMods(os.path.join(self.zopeDir, 'Extensions'))

        if self.prodsDir:
            prods = os.listdir(self.prodsDir)
            for p in prods:
                if os.path.exists(os.path.join(self.prodsDir, p)) and \
                      os.path.exists(os.path.join(self.prodsDir, p, 'Extensions')):
                    mods.extend(self._addPyMods(os.path.join(self.prodsDir, p,
                          'Extensions'), p))
        return mods

    def _addPyMods(self, pypath, prod=''):
        from Explorers import Explorer
        Explorer.listdirEx(pypath, '.zexp')
        mods = []
        fls = Explorer.listdirEx(pypath, '.py')
        for file in fls:
            mods.append(prod +(prod and '.')+os.path.splitext(file)[0])
        return mods

    def getExtPath(self, module):
        modLst = module.split('.')
        if len(modLst) == 1:
            modpath = os.path.join(self.zopeDir, 'Extensions', modLst[0] + '.py')
        else:
            modpath = os.path.join(self.prodsDir, modLst[0], 'Extensions', modLst[1]+'.py')
        return modpath.replace('<LocalFS::directory>', '<LocalFS::file>')

    def getFunctions(self, module):
        from Explorers import Explorer
        extPath = self.getExtPath(module)

        src = Explorer.openEx(extPath).load()
        sep = src.count('\r\n') < src.count('\n') and '\n' or '\r\n'
        srclines = src.split(sep)

        import moduleparse
        module = moduleparse.Module('test', srclines)

        return module.functions.keys()


[wxID_EXTMETHDLG, wxID_EXTMETHDLGBTCANCEL, wxID_EXTMETHDLGBTOK,
 wxID_EXTMETHDLGCBMODULE, wxID_EXTMETHDLGCHFUNCTION, wxID_EXTMETHDLGPANEL1,
 wxID_EXTMETHDLGSTATICTEXT1, wxID_EXTMETHDLGSTATICTEXT2,
] = map(lambda _init_ctrls: wxNewId(), range(8))

class ExtMethDlg(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_EXTMETHDLG, name='ExtMethDlg',
              parent=prnt, pos=wxPoint(363, 248), size=wxSize(267, 141),
              style=wxDEFAULT_DIALOG_STYLE, title='Add External Method')
        self._init_utils()
        self.SetClientSize(wxSize(259, 114))

        self.panel1 = wxPanel(id=wxID_EXTMETHDLGPANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(259, 114),
              style=wxTAB_TRAVERSAL)

        self.staticText1 = wxStaticText(id=wxID_EXTMETHDLGSTATICTEXT1,
              label='Module:', name='staticText1', parent=self.panel1,
              pos=wxPoint(8, 16), size=wxSize(56, 13), style=0)

        self.staticText2 = wxStaticText(id=wxID_EXTMETHDLGSTATICTEXT2,
              label='Function:', name='staticText2', parent=self.panel1,
              pos=wxPoint(8, 48), size=wxSize(56, 13), style=0)

        self.cbModule = wxComboBox(choices=[], id=wxID_EXTMETHDLGCBMODULE,
              name='cbModule', parent=self.panel1, pos=wxPoint(72, 8),
              size=wxSize(176, 21), style=0, validator=wxDefaultValidator,
              value='')
        EVT_COMBOBOX(self.cbModule, wxID_EXTMETHDLGCBMODULE,
              self.OnCbmoduleCombobox)

        self.chFunction = wxComboBox(choices=[], id=wxID_EXTMETHDLGCHFUNCTION,
              name='chFunction', parent=self.panel1, pos=wxPoint(72, 40),
              size=wxSize(176, 21), style=0, validator=wxDefaultValidator,
              value='')
        EVT_COMBOBOX(self.chFunction, wxID_EXTMETHDLGCHFUNCTION,
              self.OnChfunctionCombobox)

        self.btOK = wxButton(id=wxID_EXTMETHDLGBTOK, label='OK', name='btOK',
              parent=self.panel1, pos=wxPoint(96, 80), size=wxSize(72, 24),
              style=0)
        EVT_BUTTON(self.btOK, wxID_EXTMETHDLGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(id=wxID_EXTMETHDLGBTCANCEL, label='Cancel',
              name='btCancel', parent=self.panel1, pos=wxPoint(176, 80),
              size=wxSize(72, 24), style=0)
        EVT_BUTTON(self.btCancel, wxID_EXTMETHDLGBTCANCEL,
              self.OnBtcancelButton)

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
    app.MainLoop()
