#-----------------------------------------------------------------------------
# Name:        CtrlSize.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/09/11
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ControlSizeFrame

from wxPython.wx import *

def create(parent):
    return ControlSizeFrame(parent)

[wxID_CONTROLSIZEFRAME, wxID_CONTROLSIZEFRAMECANCELBTN, wxID_CONTROLSIZEFRAMEHEIGHTTC, wxID_CONTROLSIZEFRAMEOKBTN, wxID_CONTROLSIZEFRAMEPANEL1, wxID_CONTROLSIZEFRAMERADIOBOX1, wxID_CONTROLSIZEFRAMERADIOBOX2, wxID_CONTROLSIZEFRAMEWIDTHTC] = map(lambda _init_ctrls: wxNewId(), range(8))

class ControlSizeFrame(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_CONTROLSIZEFRAME, name = 'ControlSizeFrame', parent = prnt, pos = wxPoint(341, 140), size = wxSize(328, 195), style = wxDEFAULT_DIALOG_STYLE, title = 'Size')
        self._init_utils()

        self.panel1 = wxPanel(id = wxID_CONTROLSIZEFRAMEPANEL1, name = 'panel1', parent = self, pos = wxPoint(0, 0), size = wxSize(320, 168), style = wxTAB_TRAVERSAL)

        self.radioBox1 = wxRadioBox(choices = ['No change', 'Shrink to smallest', 'Grow to largest', 'Width:'], id = wxID_CONTROLSIZEFRAMERADIOBOX1, label = 'Width', majorDimension = 1, name = 'radioBox1', parent = self.panel1, point = wxPoint(8, 8), size = wxSize(144, 120), style = wxRA_SPECIFY_COLS, validator = wxDefaultValidator)

        self.radioBox2 = wxRadioBox(choices = ['No change', 'Shrink to smallest', 'Grow to largest', 'Height:'], id = wxID_CONTROLSIZEFRAMERADIOBOX2, label = 'Height', majorDimension = 1, name = 'radioBox2', parent = self.panel1, point = wxPoint(160, 8), size = wxSize(152, 120), style = wxRA_SPECIFY_COLS, validator = wxDefaultValidator)

        self.okBtn = wxButton(id = wxID_CONTROLSIZEFRAMEOKBTN, label = 'OK', name = 'okBtn', parent = self.panel1, pos = wxPoint(160, 136), size = wxSize(72, 24), style = 0)
        EVT_BUTTON(self.okBtn, wxID_CONTROLSIZEFRAMEOKBTN, self.OnOkbtnButton)

        self.cancelBtn = wxButton(id = wxID_CONTROLSIZEFRAMECANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self.panel1, pos = wxPoint(240, 136), size = wxSize(72, 24), style = 0)
        EVT_BUTTON(self.cancelBtn, wxID_CONTROLSIZEFRAMECANCELBTN, self.OnCancelbtnButton)

        self.widthTC = wxTextCtrl(id = wxID_CONTROLSIZEFRAMEWIDTHTC, name = 'widthTC', parent = self.radioBox1, pos = wxPoint(16, 88), size = wxSize(112, 24), style = 0, value = '42')

        self.heightTC = wxTextCtrl(id = wxID_CONTROLSIZEFRAMEHEIGHTTC, name = 'heightTC', parent = self.radioBox2, pos = wxPoint(16, 88), size = wxSize(120, 24), style = 0, value = '42')

    def __init__(self, parent, selection):
        self._init_ctrls(parent)
        self.choices = ('No change', 'No change')
        self.selection = selection
        self.Centre(wxBOTH)

    def OnOkbtnButton(self, event):
        hor = 0; ver = 1
        self.choices = (self.radioBox1.GetStringSelection(), self.radioBox2.GetStringSelection())

        selIdx = 0
        if len(self.selection):
            firstSel = self.selection[0]
            lastSel = self.selection[-1]
            firstSelPos = firstSel.position
            lastSelPos = lastSel.position
            selSize = len(self.selection)

        xSizes = []
        ySizes = []
        for sel in self.selection:
            xSizes.append( (sel.size.x, sel) )
            ySizes.append( (sel.size.y, sel) )
        xSizes.sort()
        ySizes.sort()

        for sel in self.selection:
            dosize = false
            newX, newY = sel.size.x, sel.size.y
            if self.choices[hor] == 'Shrink to smallest':
                if sel != xSizes[0][1]:
                    dosize = true
                    newX = xSizes[0][0]
            elif self.choices[hor] == 'Grow to largest':
                if sel != xSizes[-1][1]:
                    dosize = true
                    newX = xSizes[-1][0]
            elif self.choices[hor] == 'Width:':
                dosize = true
                newX = int(self.widthTC.GetValue())

            if self.choices[ver] == 'Shrink to smallest':
                if sel != ySizes[0][1]:
                    dosize = true
                    newY = ySizes[0][0]
            elif self.choices[ver] == 'Grow to largest':
                if sel != ySizes[-1][1]:
                    dosize = true
                    newY = ySizes[-1][0]
            elif self.choices[ver] == 'Height:':
                dosize = true
                newY = int(self.heightTC.GetValue())

            if dosize:
                sel.size  = wxPoint(newX, newY)
                sel.OnSizeEnd2(None)
                sel.setSelection()
                sel.sizeUpdate()

            selIdx = selIdx + 1

        self.EndModal(wxOK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wxCANCEL)
