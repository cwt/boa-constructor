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

[wxID_CONTROLSIZEFRAMERADIOBOX2, wxID_CONTROLSIZEFRAMEWIDTHTC, wxID_CONTROLSIZEFRAMERADIOBOX1, wxID_CONTROLSIZEFRAMEPANEL1, wxID_CONTROLSIZEFRAMEOKBTN, wxID_CONTROLSIZEFRAMEHEIGHTTC, wxID_CONTROLSIZEFRAMECANCELBTN, wxID_CONTROLSIZEFRAME] = map(lambda _init_ctrls: wxNewId(), range(8))

class ControlSizeFrame(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(328, 195), id = wxID_CONTROLSIZEFRAME, title = 'Size', parent = prnt, name = 'ControlSizeFrame', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(341, 140))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(320, 168), parent = self, id = wxID_CONTROLSIZEFRAMEPANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.radioBox1 = wxRadioBox(label = 'Width', id = wxID_CONTROLSIZEFRAMERADIOBOX1, choices = ['No change', 'Shrink to smallest', 'Grow to largest', 'Width:'], majorDimension = 1, point = wxPoint(8, 8), parent = self.panel1, name = 'radioBox1', size = wxSize(144, 120), validator = wxDefaultValidator, style = wxRA_SPECIFY_COLS)

        self.radioBox2 = wxRadioBox(label = 'Height', id = wxID_CONTROLSIZEFRAMERADIOBOX2, choices = ['No change', 'Shrink to smallest', 'Grow to largest', 'Height:'], majorDimension = 1, point = wxPoint(160, 8), parent = self.panel1, name = 'radioBox2', size = wxSize(152, 120), validator = wxDefaultValidator, style = wxRA_SPECIFY_COLS)

        self.okBtn = wxButton(label = 'OK', id = wxID_CONTROLSIZEFRAMEOKBTN, parent = self.panel1, name = 'okBtn', size = wxSize(72, 24), style = 0, pos = wxPoint(160, 136))
        EVT_BUTTON(self.okBtn, wxID_CONTROLSIZEFRAMEOKBTN, self.OnOkbtnButton)

        self.cancelBtn = wxButton(label = 'Cancel', id = wxID_CONTROLSIZEFRAMECANCELBTN, parent = self.panel1, name = 'cancelBtn', size = wxSize(72, 24), style = 0, pos = wxPoint(240, 136))
        EVT_BUTTON(self.cancelBtn, wxID_CONTROLSIZEFRAMECANCELBTN, self.OnCancelbtnButton)

        self.widthTC = wxTextCtrl(size = wxSize(112, 24), value = '42', pos = wxPoint(16, 88), parent = self.radioBox1, name = 'widthTC', style = 0, id = wxID_CONTROLSIZEFRAMEWIDTHTC)

        self.heightTC = wxTextCtrl(size = wxSize(120, 24), value = '42', pos = wxPoint(16, 88), parent = self.radioBox2, name = 'heightTC', style = 0, id = wxID_CONTROLSIZEFRAMEHEIGHTTC)

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


