#Boa:Frame:wxFrame1

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors
import pyTree, sys

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1CHECKBOX7, wxID_WXFRAME1CHECKBOX6, wxID_WXFRAME1CHECKBOX5, wxID_WXFRAME1CHECKBOX4, wxID_WXFRAME1CHECKBOX3, wxID_WXFRAME1PANEL2, wxID_WXFRAME1PANEL1, wxID_WXFRAME1BUTTON4, wxID_WXFRAME1BUTTON5, wxID_WXFRAME1BUTTON2, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1CHECKBOX9, wxID_WXFRAME1BUTTON3, wxID_WXFRAME1CHECKBOX10, wxID_WXFRAME1NOTEBOOK1, wxID_WXFRAME1TREECTRL1, wxID_WXFRAME1CHECKBOX2, wxID_WXFRAME1PANEL3, wxID_WXFRAME1STATICBOX2, wxID_WXFRAME1CHECKBOX1, wxID_WXFRAME1STATICBOX1, wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1TEXTCTRL2, wxID_WXFRAME1TEXTCTRL3, wxID_WXFRAME1TEXTCTRL4, wxID_WXFRAME1PANEL4, wxID_WXFRAME1] = map(lambda _init_ctrls: wxNewId(), range(28))

class wxFrame1(wxFrame):
    def _init_coll_notebook1_Pages(self, parent):

        parent.AddPage(strText = 'Options', bSelect = false, pPage = self.panel2, imageId = -1)
        parent.AddPage(strText = 'Collect', bSelect = false, pPage = self.panel3, imageId = -1)
        parent.AddPage(strText = 'gc.garbage', bSelect = false, pPage = self.panel4, imageId = -1)

    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(368, 339), id = wxID_WXFRAME1, title = 'Garbage Collection Interface', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(400, 284))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(360, 312), parent = self, id = wxID_WXFRAME1PANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))
        self.panel1.SetAutoLayout(true)

        self.notebook1 = wxNotebook(size = wxSize(344, 264), parent = self.panel1, id = wxID_WXFRAME1NOTEBOOK1, name = 'notebook1', style = 0, pos = wxPoint(8, 8))
        self.notebook1.SetSelection(2)
        self.notebook1.SetConstraints(LayoutAnchors(self.notebook1, true, true, true, true))

        self.panel2 = wxPanel(size = wxSize(336, 240), parent = self.notebook1, id = wxID_WXFRAME1PANEL2, name = 'panel2', style = wxTAB_TRAVERSAL, pos = wxPoint(8, 24))
        self.panel2.SetAutoLayout(true)

        self.checkBox1 = wxCheckBox(label = 'Garbage collection enabled', parent = self.panel2, id = wxID_WXFRAME1CHECKBOX1, size = wxSize(168, 16), style = 0, pos = wxPoint(8, 8))

        self.staticBox1 = wxStaticBox(label = 'Debug flags', id = wxID_WXFRAME1STATICBOX1, parent = self.panel2, name = 'staticBox1', size = wxSize(320, 104), style = 0, pos = wxPoint(8, 32))
        self.staticBox1.SetConstraints(LayoutAnchors(self.staticBox1, true, true, true, false))

        self.staticBox2 = wxStaticBox(label = 'Threshold', id = wxID_WXFRAME1STATICBOX2, parent = self.panel2, name = 'staticBox2', size = wxSize(320, 96), style = 0, pos = wxPoint(8, 136))
        self.staticBox2.SetConstraints(LayoutAnchors(self.staticBox2, true, true, true, false))

        self.checkBox7 = wxCheckBox(name = 'checkBox7', label = 'DEBUG_OBJECTS', parent = self.staticBox1, id = wxID_WXFRAME1CHECKBOX7, size = wxSize(128, 16), style = 0, pos = wxPoint(176, 32))
        self.checkBox7.SetConstraints(LayoutAnchors(self.checkBox7, false, true, false, false))

        self.checkBox6 = wxCheckBox(name = 'checkBox6', label = 'DEBUG_STATS', parent = self.staticBox1, id = wxID_WXFRAME1CHECKBOX6, size = wxSize(160, 16), style = 0, pos = wxPoint(8, 16))
        self.checkBox6.SetConstraints(LayoutAnchors(self.checkBox6, false, true, false, false))

        self.checkBox5 = wxCheckBox(name = 'checkBox5', label = 'DEBUG_COLLECTABLE', parent = self.staticBox1, id = wxID_WXFRAME1CHECKBOX5, size = wxSize(160, 16), style = 0, pos = wxPoint(8, 32))
        self.checkBox5.SetConstraints(LayoutAnchors(self.checkBox5, false, true, false, false))

        self.checkBox4 = wxCheckBox(name = 'checkBox4', label = 'DEBUG_UNCOLLECTABLE', parent = self.staticBox1, id = wxID_WXFRAME1CHECKBOX4, size = wxSize(160, 16), style = 0, pos = wxPoint(8, 48))
        self.checkBox4.SetConstraints(LayoutAnchors(self.checkBox4, false, true, false, false))

        self.checkBox3 = wxCheckBox(name = 'checkBox3', label = 'DEBUG_SAVEALL', parent = self.staticBox1, id = wxID_WXFRAME1CHECKBOX3, size = wxSize(128, 16), style = 0, pos = wxPoint(176, 48))
        self.checkBox3.SetConstraints(LayoutAnchors(self.checkBox3, false, true, false, false))

        self.checkBox2 = wxCheckBox(name = 'checkBox2', label = 'DEBUG_INSTANCES', parent = self.staticBox1, id = wxID_WXFRAME1CHECKBOX2, size = wxSize(128, 16), style = 0, pos = wxPoint(176, 16))
        self.checkBox2.SetConstraints(LayoutAnchors(self.checkBox2, false, true, false, false))

        self.staticText1 = wxStaticText(label = 'threshold0', id = wxID_WXFRAME1STATICTEXT1, parent = self.staticBox2, name = 'staticText1', size = wxSize(56, 16), style = 0, pos = wxPoint(8, 16))

        self.textCtrl1 = wxTextCtrl(size = wxSize(96, 24), value = '', pos = wxPoint(8, 32), parent = self.staticBox2, name = 'textCtrl1', style = 0, id = wxID_WXFRAME1TEXTCTRL1)

        self.textCtrl2 = wxTextCtrl(size = wxSize(96, 24), value = '', pos = wxPoint(112, 32), parent = self.staticBox2, name = 'textCtrl2', style = 0, id = wxID_WXFRAME1TEXTCTRL2)
        self.textCtrl2.SetConstraints(LayoutAnchors(self.textCtrl2, false, true, false, false))

        self.textCtrl3 = wxTextCtrl(size = wxSize(96, 24), value = '', pos = wxPoint(216, 32), parent = self.staticBox2, name = 'textCtrl3', style = 0, id = wxID_WXFRAME1TEXTCTRL3)
        self.textCtrl3.SetConstraints(LayoutAnchors(self.textCtrl3, false, true, true, false))

        self.checkBox10 = wxCheckBox(label = 'threshold2', id = wxID_WXFRAME1CHECKBOX10, parent = self.staticBox2, size = wxSize(96, 16), style = 0, pos = wxPoint(216, 16))
        self.checkBox10.SetConstraints(LayoutAnchors(self.checkBox10, false, true, true, false))

        self.checkBox9 = wxCheckBox(name = 'checkBox9', label = 'threshold1', id = wxID_WXFRAME1CHECKBOX9, parent = self.staticBox2, size = wxSize(96, 16), style = 0, pos = wxPoint(112, 16))
        self.checkBox9.SetConstraints(LayoutAnchors(self.checkBox9, false, true, false, false))

        self.panel3 = wxPanel(size = wxSize(336, 240), parent = self.notebook1, id = wxID_WXFRAME1PANEL3, name = 'panel3', style = wxTAB_TRAVERSAL, pos = wxPoint(8, 24))
        self.panel3.SetAutoLayout(true)

        self.panel4 = wxPanel(size = wxSize(336, 240), parent = self.notebook1, id = wxID_WXFRAME1PANEL4, name = 'panel4', style = wxTAB_TRAVERSAL, pos = wxPoint(8, 24))
        self.panel4.SetAutoLayout(true)

        self.button1 = wxButton(label = 'DEBUG_LEAK', id = wxID_WXFRAME1BUTTON1, parent = self.staticBox1, name = 'button1', size = wxSize(88, 24), style = 0, pos = wxPoint(224, 72))
        self.button1.SetConstraints(LayoutAnchors(self.button1, false, true, true, false))

        self.button2 = wxButton(label = 'Set threshold', id = wxID_WXFRAME1BUTTON2, parent = self.staticBox2, name = 'button2', size = wxSize(88, 24), style = 0, pos = wxPoint(224, 64))
        self.button2.SetConstraints(LayoutAnchors(self.button2, false, true, true, false))

        self.button3 = wxButton(label = 'OK', id = wxID_WXFRAME1BUTTON3, parent = self.panel1, name = 'button3', size = wxSize(72, 24), style = 0, pos = wxPoint(144, 280))
        self.button3.SetConstraints(LayoutAnchors(self.button3, false, false, false, true))

        self.button4 = wxButton(label = 'Refresh', id = wxID_WXFRAME1BUTTON4, parent = self.panel4, name = 'button4', size = wxSize(72, 24), style = 0, pos = wxPoint(256, 208))
        self.button4.SetConstraints(LayoutAnchors(self.button4, false, false, true, true))

        self.textCtrl4 = wxTextCtrl(size = wxSize(320, 192), value = '', pos = wxPoint(8, 8), parent = self.panel3, name = 'textCtrl4', style = wxTE_MULTILINE, id = wxID_WXFRAME1TEXTCTRL4)
        self.textCtrl4.SetConstraints(LayoutAnchors(self.textCtrl4, true, true, true, true))

        self.treeCtrl1 = wxTreeCtrl(size = wxSize(320, 192), id = wxID_WXFRAME1TREECTRL1, parent = self.panel4, name = 'treeCtrl1', validator = wxDefaultValidator, style = wxTR_HAS_BUTTONS, pos = wxPoint(8, 8))
        self.treeCtrl1.SetConstraints(LayoutAnchors(self.treeCtrl1, true, true, true, true))

        self.button5 = wxButton(label = 'Collect', id = wxID_WXFRAME1BUTTON5, parent = self.panel3, name = 'button5', size = wxSize(72, 24), style = 0, pos = wxPoint(256, 208))
        self.button5.SetConstraints(LayoutAnchors(self.button5, false, false, true, true))

        self._init_coll_notebook1_Pages(self.notebook1)

    def __init__(self, parent): 
        self._init_ctrls(parent)

        self.treeCtrl1 = wxTreeCtrl(size = wxSize(320, 192), id = wxID_WXFRAME1TREECTRL1, parent = self.panel4, name = 'treeCtrl1', validator = wxDefaultValidator, style = wxTR_HAS_BUTTONS, pos = wxPoint(8, 8))
        self.treeCtrl1.SetConstraints(LayoutAnchors(self.treeCtrl1, true, true, true, true))

        self.Layout()


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()