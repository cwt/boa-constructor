#Boa:Dialog:ExtMethDlg

from wxPython.wx import *
import moduleparse
import os
from os import path

##def create(parent):
##    return ExtMethDlg(parent, 'd:\\program files\\zope\\armalyte1')

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

        self.zopeDir = zopeDir#'d:\\program files\\zope\\armalyte1'
        if zopeDir:
            self.prodsDir = path.join(zopeDir, 'lib','python','Products')

            self.addPyMods(path.join(zopeDir, 'extensions'))

            prods = os.listdir(self.prodsDir)
            for p in prods:
                if path.exists(path.join(self.prodsDir, p)) and \
                      path.exists(path.join(self.prodsDir, p, 'extensions')):
                    self.addPyMods(path.join(self.prodsDir, p, 'extensions'), p)
        else:
            self.prodsDir = ''

    def addPyMods(self, pypath, prod = ''):
        fls = filter(lambda f: path.splitext(f)[1] == '.py', os.listdir(pypath))
        for file in fls:
            self.cbModule.Append(prod +(prod and '.')+path.splitext(file)[0])

    def OnBtokButton(self, event):
        self.EndModal(wxID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wxID_CANCEL)

    def OnCbmoduleCombobox(self, event):
        if self.zopeDir:
            self.chFunction.Clear()
            mod = self.cbModule.GetStringSelection()
            modLst = string.split(mod, '.')
            if len(modLst) == 1:
                pypath = path.join(self.zopeDir, 'extensions', modLst[0] + '.py')
            else:
                pypath = path.join(self.prodsDir, modLst[0], 'extensions', modLst[1]+'.py')

            module = moduleparse.Module('test', open(pypath).readlines())

            for func in module.functions.keys():
                self.chFunction.Append(func)

    def OnChfunctionCombobox(self, event):
        pass
