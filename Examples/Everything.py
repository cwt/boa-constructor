#Boa:Frame:wxFrame1

""" Frame containing all controls available on the Palette. """

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors
from wxPython.grid import *
from wxPython.help import *
from wxPython.lib.buttons import *
from wxPython.html import *
from wxPython.gizmos import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BITMAPBUTTON1, wxID_WXFRAME1BUTTON1,
 wxID_WXFRAME1CHECKBOX1, wxID_WXFRAME1CHECKLISTBOX1, wxID_WXFRAME1CHOICE1,
 wxID_WXFRAME1COMBOBOX1, wxID_WXFRAME1CONTEXTHELPBUTTON1,
 wxID_WXFRAME1DYNAMICSASHWINDOW1, wxID_WXFRAME1EDITABLELISTBOX1,
 wxID_WXFRAME1GAUGE1, wxID_WXFRAME1GENBITMAPBUTTON1,
 wxID_WXFRAME1GENBITMAPTEXTTOGGLEBUTTON1, wxID_WXFRAME1GENBITMAPTOGGLEBUTTON1,
 wxID_WXFRAME1GENBUTTON1, wxID_WXFRAME1GENTOGGLEBUTTON1, wxID_WXFRAME1GRID1,
 wxID_WXFRAME1HTMLWINDOW1, wxID_WXFRAME1LEDNUMBERCTRL1, wxID_WXFRAME1LISTBOX1,
 wxID_WXFRAME1LISTCTRL1, wxID_WXFRAME1NOTEBOOK1, wxID_WXFRAME1PANEL1,
 wxID_WXFRAME1PANEL2, wxID_WXFRAME1PANEL3, wxID_WXFRAME1PANEL4,
 wxID_WXFRAME1PANEL5, wxID_WXFRAME1PANEL6, wxID_WXFRAME1RADIOBOX1,
 wxID_WXFRAME1RADIOBUTTON1, wxID_WXFRAME1SASHLAYOUTWINDOW1,
 wxID_WXFRAME1SASHWINDOW1, wxID_WXFRAME1SCROLLBAR1,
 wxID_WXFRAME1SCROLLEDWINDOW1, wxID_WXFRAME1SLIDER1, wxID_WXFRAME1SPINBUTTON1,
 wxID_WXFRAME1SPLITTERWINDOW1, wxID_WXFRAME1STATICBITMAP1,
 wxID_WXFRAME1STATICBOX1, wxID_WXFRAME1STATICLINE1, wxID_WXFRAME1STATICTEXT1,
 wxID_WXFRAME1STATUSBAR1, wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1TOGGLEBUTTON1,
 wxID_WXFRAME1TOOLBAR1, wxID_WXFRAME1TREECTRL1, wxID_WXFRAME1WINDOW1,
 wxID_WXFRAME1WINDOW10, wxID_WXFRAME1WINDOW2, wxID_WXFRAME1WINDOW3,
 wxID_WXFRAME1WINDOW4, wxID_WXFRAME1WINDOW5, wxID_WXFRAME1WINDOW6,
 wxID_WXFRAME1WINDOW7, wxID_WXFRAME1WINDOW8, wxID_WXFRAME1WINDOW9,
] = map(lambda _init_ctrls: wxNewId(), range(56))

[wxID_WXFRAME1TOOLBAR1TOOLS0] = map(lambda _init_coll_toolBar1_Tools: wxNewId(), range(1))

[wxID_WXFRAME1MENU1ITEMS0] = map(lambda _init_coll_menu1_Items: wxNewId(), range(1))

[wxID_WXFRAME1TIMER1] = map(lambda _init_utils: wxNewId(), range(1))

class wxFrame1(wxFrame):
    def _init_coll_menu1_Items(self, parent):
        # generated method, don't edit

        parent.Append(helpString='', id=wxID_WXFRAME1MENU1ITEMS0, item='Items0')
        EVT_MENU(self, wxID_WXFRAME1MENU1ITEMS0, self.OnMenu1items0Menu)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menu1, title='Menus0')

    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(select=true, imageId=-1, page=self.panel1,
              text='Containers/Layout')
        parent.AddPage(select=false, imageId=-1, page=self.panel2,
              text='Basic Controls')
        parent.AddPage(select=false, imageId=-1, page=self.panel3,
              text='Buttons')
        parent.AddPage(select=false, imageId=-1, page=self.panel4,
              text='List Controls')
        parent.AddPage(select=false, imageId=-1, page=self.panel5,
              text='Anchors')
        parent.AddPage(select=false, imageId=-1, page=self.panel6,
              text='Misc')

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(2)

        parent.SetStatusText(i=0, text='Fields0')
        parent.SetStatusText(i=1, text='Fields1')

        parent.SetStatusWidths([-1, -1])

    def _init_coll_toolBar1_Tools(self, parent):
        # generated method, don't edit

        parent.AddTool(bitmap=wxNullBitmap, id=wxID_WXFRAME1TOOLBAR1TOOLS0,
              isToggle=false, longHelpString='', pushedBitmap=wxNullBitmap,
              shortHelpString='Tools0')
        EVT_TOOL(self, wxID_WXFRAME1TOOLBAR1TOOLS0, self.OnToolbar1tools0Tool)

        parent.Realize()

    def _init_utils(self):
        # generated method, don't edit
        self.menuBar1 = wxMenuBar()

        self.menu1 = wxMenu(title='')
        self._init_coll_menu1_Items(self.menu1)

        self.imageList1 = wxImageList(height=16, width=16)

        self.stockCursor1 = wxStockCursor(id=wxCURSOR_PENCIL)

        self.timer1 = wxTimer(evtHandler=self, id=wxID_WXFRAME1TIMER1)
        EVT_TIMER(self, wxID_WXFRAME1TIMER1, self.OnTimer1Timer)

        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(555, 294), size=wxSize(516, 476),
              style=wxDEFAULT_FRAME_STYLE, title='Everything')
        self._init_utils()
        self.SetClientSize(wxSize(508, 449))
        self.SetMenuBar(self.menuBar1)
        self.Center(wxBOTH)

        self.toolBar1 = wxToolBar(id=wxID_WXFRAME1TOOLBAR1, name='toolBar1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(508, 27),
              style=wxTB_HORIZONTAL | wxNO_BORDER)
        self._init_coll_toolBar1_Tools(self.toolBar1)
        self.SetToolBar(self.toolBar1)

        self.statusBar1 = wxStatusBar(id=wxID_WXFRAME1STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self.statusBar1.SetPosition(wxPoint(0, 308))
        self.statusBar1.SetSize(wxSize(422, 20))
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.notebook1 = wxNotebook(id=wxID_WXFRAME1NOTEBOOK1, name='notebook1',
              parent=self, pos=wxPoint(0, 27), size=wxSize(508, 383), style=0)

        self.panel1 = wxPanel(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(500, 357),
              style=wxTAB_TRAVERSAL)

        self.splitterWindow1 = wxSplitterWindow(id=wxID_WXFRAME1SPLITTERWINDOW1,
              name='splitterWindow1', parent=self.panel1, point=wxPoint(8, 8),
              size=wxSize(200, 100), style=wxSP_3D)

        self.scrolledWindow1 = wxScrolledWindow(id=wxID_WXFRAME1SCROLLEDWINDOW1,
              name='scrolledWindow1', parent=self.splitterWindow1,
              pos=wxPoint(2, 2), size=wxSize(98, 96),
              style=wxSUNKEN_BORDER | wxTAB_TRAVERSAL)
        self.scrolledWindow1.SetToolTipString('wxScrolledWindow')

        self.sashWindow1 = wxSashWindow(id=wxID_WXFRAME1SASHWINDOW1,
              name='sashWindow1', parent=self.splitterWindow1, pos=wxPoint(107,
              2), size=wxSize(91, 96), style=wxCLIP_CHILDREN | wxSW_3D)
        self.splitterWindow1.SplitVertically(self.scrolledWindow1,
              self.sashWindow1, 100)

        self.sashLayoutWindow1 = wxSashLayoutWindow(id=wxID_WXFRAME1SASHLAYOUTWINDOW1,
              name='sashLayoutWindow1', parent=self.panel1, pos=wxPoint(8, 120),
              size=wxSize(200, 80), style=wxCLIP_CHILDREN | wxSW_3D)

        self.window1 = wxWindow(id=wxID_WXFRAME1WINDOW1, name='window1',
              parent=self.panel1, pos=wxPoint(216, 120), size=wxSize(96, 80),
              style=wxSIMPLE_BORDER)
        self.window1.SetCursor(self.stockCursor1)

        self.dynamicSashWindow1 = wxDynamicSashWindow(id=wxID_WXFRAME1DYNAMICSASHWINDOW1,
              name='dynamicSashWindow1', parent=self.panel1, pos=wxPoint(216,
              8), size=wxSize(100, 100), style=wxCLIP_CHILDREN)

        self.panel2 = wxPanel(id=wxID_WXFRAME1PANEL2, name='panel2',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(500, 357),
              style=wxTAB_TRAVERSAL)

        self.staticText1 = wxStaticText(id=wxID_WXFRAME1STATICTEXT1,
              label='staticText1', name='staticText1', parent=self.panel2,
              pos=wxPoint(16, 16), size=wxSize(52, 13), style=0)

        self.textCtrl1 = wxTextCtrl(id=wxID_WXFRAME1TEXTCTRL1, name='textCtrl1',
              parent=self.panel2, pos=wxPoint(16, 40), size=wxSize(100, 21),
              style=0, value='textCtrl1')

        self.comboBox1 = wxComboBox(choices=[], id=wxID_WXFRAME1COMBOBOX1,
              name='comboBox1', parent=self.panel2, pos=wxPoint(16, 72),
              size=wxSize(125, 21), style=0, validator=wxDefaultValidator,
              value='comboBox1')

        self.choice1 = wxChoice(choices=[], id=wxID_WXFRAME1CHOICE1,
              name='choice1', parent=self.panel2, pos=wxPoint(16, 104),
              size=wxSize(125, 21), style=0, validator=wxDefaultValidator)

        self.checkBox1 = wxCheckBox(id=wxID_WXFRAME1CHECKBOX1,
              label='checkBox1', name='checkBox1', parent=self.panel2,
              pos=wxPoint(16, 136), size=wxSize(73, 13), style=0)

        self.radioButton1 = wxRadioButton(id=wxID_WXFRAME1RADIOBUTTON1,
              label='radioButton1', name='radioButton1', parent=self.panel2,
              pos=wxPoint(16, 160), size=wxSize(80, 20), style=0)

        self.slider1 = wxSlider(id=wxID_WXFRAME1SLIDER1, maxValue=100,
              minValue=0, name='slider1', parent=self.panel2, point=wxPoint(152,
              16), size=wxSize(136, 20), style=wxSL_HORIZONTAL,
              validator=wxDefaultValidator, value=0)
        EVT_SCROLL(self.slider1, self.OnSlider1Slider)

        self.scrollBar1 = wxScrollBar(id=wxID_WXFRAME1SCROLLBAR1,
              name='scrollBar1', parent=self.panel2, pos=wxPoint(16, 192),
              size=wxSize(120, 14), style=wxSB_HORIZONTAL)
        self.scrollBar1.SetThumbPosition(0)

        self.staticBitmap1 = wxStaticBitmap(bitmap=wxNullBitmap,
              id=wxID_WXFRAME1STATICBITMAP1, name='staticBitmap1',
              parent=self.panel2, pos=wxPoint(160, 136), size=wxSize(128, 16),
              style=0)

        self.staticLine1 = wxStaticLine(id=wxID_WXFRAME1STATICLINE1,
              name='staticLine1', parent=self.panel2, pos=wxPoint(15, 216),
              size=wxSize(121, 2), style=0)

        self.staticBox1 = wxStaticBox(id=wxID_WXFRAME1STATICBOX1,
              label='staticBox1', name='staticBox1', parent=self.panel2,
              pos=wxPoint(152, 120), size=wxSize(144, 40), style=0)

        self.htmlWindow1 = wxHtmlWindow(id=wxID_WXFRAME1HTMLWINDOW1,
              name='htmlWindow1', parent=self.panel2, pos=wxPoint(152, 168),
              size=wxSize(144, 80))

        self.lEDNumberCtrl1 = wxLEDNumberCtrl(id=wxID_WXFRAME1LEDNUMBERCTRL1,
              parent=self.panel2, pos=wxPoint(152, 40), size=wxSize(136, 40),
              style=wxLED_ALIGN_CENTER)
        self.lEDNumberCtrl1.SetValue('123')

        self.panel3 = wxPanel(id=wxID_WXFRAME1PANEL3, name='panel3',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(500, 357),
              style=wxTAB_TRAVERSAL)

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label='button1',
              name='button1', parent=self.panel3, pos=wxPoint(16, 16),
              size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.button1, wxID_WXFRAME1BUTTON1, self.OnButton1Button)
        EVT_LEFT_UP(self.button1, self.OnButton1LeftUp)

        self.bitmapButton1 = wxBitmapButton(bitmap=wxNullBitmap,
              id=wxID_WXFRAME1BITMAPBUTTON1, name='bitmapButton1',
              parent=self.panel3, pos=wxPoint(16, 56), size=wxSize(72, 24),
              style=wxBU_AUTODRAW, validator=wxDefaultValidator)
        EVT_BUTTON(self.bitmapButton1, wxID_WXFRAME1BITMAPBUTTON1,
              self.OnBitmapbutton1Button)

        self.spinButton1 = wxSpinButton(id=wxID_WXFRAME1SPINBUTTON1,
              name='spinButton1', parent=self.panel3, pos=wxPoint(136, 96),
              size=wxSize(32, 16), style=wxSP_HORIZONTAL)
        EVT_COMMAND_SCROLL(self.spinButton1, wxID_WXFRAME1SPINBUTTON1,
              self.OnSpinbutton1CommandScroll)

        self.toggleButton1 = wxToggleButton(id=wxID_WXFRAME1TOGGLEBUTTON1,
              label='toggleButton1', name='toggleButton1', parent=self.panel3,
              pos=wxPoint(104, 16), size=wxSize(81, 23), style=0)
        EVT_BUTTON(self.toggleButton1, wxID_WXFRAME1TOGGLEBUTTON1,
              self.OnTogglebutton1Button)

        self.genButton1 = wxGenButton(ID=wxID_WXFRAME1GENBUTTON1,
              label='genButton1', name='genButton1', parent=self.panel3,
              pos=wxPoint(16, 160), size=wxSize(88, 37), style=0)

        self.genBitmapButton1 = wxGenBitmapButton(ID=wxID_WXFRAME1GENBITMAPBUTTON1,
              bitmap=wxNullBitmap, name='genBitmapButton1', parent=self.panel3,
              pos=wxPoint(16, 192), size=wxSize(59, 58), style=0)

        self.genToggleButton1 = wxGenToggleButton(ID=wxID_WXFRAME1GENTOGGLEBUTTON1,
              label='genToggleButton1', name='genToggleButton1',
              parent=self.panel3, pos=wxPoint(104, 160), size=wxSize(113, 37),
              style=0)

        self.genBitmapToggleButton1 = wxGenBitmapToggleButton(ID=wxID_WXFRAME1GENBITMAPTOGGLEBUTTON1,
              bitmap=wxNullBitmap, name='genBitmapToggleButton1',
              parent=self.panel3, pos=wxPoint(72, 192), size=wxSize(59, 58),
              style=0)

        self.genBitmapTextToggleButton1 = wxGenBitmapTextToggleButton(ID=wxID_WXFRAME1GENBITMAPTEXTTOGGLEBUTTON1,
              bitmap=wxNullBitmap, label='genBitmapTextToggleButton1',
              name='genBitmapTextToggleButton1', parent=self.panel3,
              pos=wxPoint(128, 192), size=wxSize(88, 58), style=0)

        self.contextHelpButton1 = wxContextHelpButton(parent=self.panel3,
              pos=wxPoint(136, 64), size=wxSize(20, 19), style=wxBU_AUTODRAW)

        self.panel4 = wxPanel(id=wxID_WXFRAME1PANEL4, name='panel4',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(500, 357),
              style=wxTAB_TRAVERSAL)

        self.radioBox1 = wxRadioBox(choices=['asd'], id=wxID_WXFRAME1RADIOBOX1,
              label='radioBox1', majorDimension=1, name='radioBox1',
              parent=self.panel4, point=wxPoint(16, 16), size=wxDefaultSize,
              style=wxRA_SPECIFY_COLS, validator=wxDefaultValidator)

        self.listBox1 = wxListBox(choices=[], id=wxID_WXFRAME1LISTBOX1,
              name='listBox1', parent=self.panel4, pos=wxPoint(16, 64),
              size=wxSize(115, 63), style=0, validator=wxDefaultValidator)

        self.checkListBox1 = wxCheckListBox(choices=[],
              id=wxID_WXFRAME1CHECKLISTBOX1, name='checkListBox1',
              parent=self.panel4, pos=wxPoint(16, 136), size=wxSize(115, 63),
              style=0, validator=wxDefaultValidator)

        self.grid1 = wxGrid(id=wxID_WXFRAME1GRID1, name='grid1',
              parent=self.panel4, pos=wxPoint(144, 16), size=wxSize(128, 112),
              style=0)

        self.listCtrl1 = wxListCtrl(id=wxID_WXFRAME1LISTCTRL1, name='listCtrl1',
              parent=self.panel4, pos=wxPoint(280, 16), size=wxSize(100, 30),
              style=wxLC_ICON, validator=wxDefaultValidator)

        self.treeCtrl1 = wxTreeCtrl(id=wxID_WXFRAME1TREECTRL1, name='treeCtrl1',
              parent=self.panel4, pos=wxPoint(280, 56), size=wxSize(100, 80),
              style=wxTR_HAS_BUTTONS, validator=wxDefaultValidator)

        self.editableListBox1 = wxEditableListBox(id=wxID_WXFRAME1EDITABLELISTBOX1,
              label='editableListBox1', name='editableListBox1',
              parent=self.panel4, pos=wxPoint(152, 152), size=wxSize(200, 100))

        self.panel5 = wxPanel(id=wxID_WXFRAME1PANEL5, name='panel5',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(500, 357),
              style=wxTAB_TRAVERSAL)
        self.panel5.SetAutoLayout(true)

        self.window2 = wxWindow(id=wxID_WXFRAME1WINDOW2, name='window2',
              parent=self.panel5, pos=wxPoint(446, 16), size=wxSize(40, 40),
              style=0)
        self.window2.SetBackgroundColour(wxColour(128, 255, 0))
        self.window2.SetConstraints(LayoutAnchors(self.window2, false, true,
              true, false))

        self.window3 = wxWindow(id=wxID_WXFRAME1WINDOW3, name='window3',
              parent=self.panel5, pos=wxPoint(16, 299), size=wxSize(40, 40),
              style=0)
        self.window3.SetBackgroundColour(wxColour(128, 255, 0))
        self.window3.SetConstraints(LayoutAnchors(self.window3, true, false,
              false, true))

        self.window4 = wxWindow(id=wxID_WXFRAME1WINDOW4, name='window4',
              parent=self.panel5, pos=wxPoint(446, 299), size=wxSize(40, 40),
              style=0)
        self.window4.SetBackgroundColour(wxColour(128, 255, 0))
        self.window4.SetConstraints(LayoutAnchors(self.window4, false, false,
              true, true))

        self.window5 = wxWindow(id=wxID_WXFRAME1WINDOW5, name='window5',
              parent=self.panel5, pos=wxPoint(16, 16), size=wxSize(40, 40),
              style=0)
        self.window5.SetBackgroundColour(wxColour(128, 255, 0))
        self.window5.SetConstraints(LayoutAnchors(self.window5, true, true,
              false, false))

        self.window6 = wxWindow(id=wxID_WXFRAME1WINDOW6, name='window6',
              parent=self.panel5, pos=wxPoint(192, 16), size=wxSize(126, 40),
              style=0)
        self.window6.SetBackgroundColour(wxColour(128, 255, 0))
        self.window6.SetConstraints(LayoutAnchors(self.window6, true, true,
              true, false))

        self.window7 = wxWindow(id=wxID_WXFRAME1WINDOW7, name='window7',
              parent=self.panel5, pos=wxPoint(446, 120), size=wxSize(40, 115),
              style=0)
        self.window7.SetBackgroundColour(wxColour(128, 255, 0))
        self.window7.SetConstraints(LayoutAnchors(self.window7, false, true,
              true, true))

        self.window8 = wxWindow(id=wxID_WXFRAME1WINDOW8, name='window8',
              parent=self.panel5, pos=wxPoint(192, 299), size=wxSize(126, 40),
              style=0)
        self.window8.SetBackgroundColour(wxColour(128, 255, 0))
        self.window8.SetConstraints(LayoutAnchors(self.window8, true, false,
              true, true))

        self.window9 = wxWindow(id=wxID_WXFRAME1WINDOW9, name='window9',
              parent=self.panel5, pos=wxPoint(16, 120), size=wxSize(40, 115),
              style=0)
        self.window9.SetBackgroundColour(wxColour(128, 255, 0))
        self.window9.SetConstraints(LayoutAnchors(self.window9, true, true,
              false, true))

        self.window10 = wxWindow(id=wxID_WXFRAME1WINDOW10, name='window10',
              parent=self.panel5, pos=wxPoint(225, 147), size=wxSize(40, 40),
              style=0)
        self.window10.SetBackgroundColour(wxColour(128, 255, 0))
        self.window10.SetConstraints(LayoutAnchors(self.window10, false, false,
              false, false))

        self.panel6 = wxPanel(id=wxID_WXFRAME1PANEL6, name='panel6',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(500, 357),
              style=wxTAB_TRAVERSAL)

        self.gauge1 = wxGauge(id=wxID_WXFRAME1GAUGE1, name='gauge1',
              parent=self.panel2, pos=wxPoint(152, 88), range=100,
              size=wxSize(136, 16), style=wxGA_SMOOTH | wxGA_HORIZONTAL,
              validator=wxDefaultValidator)
        self.gauge1.SetValue(50)

        self._init_coll_notebook1_Pages(self.notebook1)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnMenu1items0Menu(self, event):
        print 'Menu0'

    def OnToolbar1tools0Tool(self, event):
        raise 'Tool0'

    def OnButton1Button(self, event):
        self.timer1.Start(1000, false)

    def OnBitmapbutton1Button(self, event):
        event.Skip()

    def OnSpinbutton1CommandScroll(self, event):
        event.Skip()

    def OnTogglebutton1Button(self, event):
        event.Skip()

    def OnButton1Help(self, event):
        event.Skip()

    def OnButton1LeftUp(self, event):
        event.Skip()

    def OnTimer1Timer(self, event):
        import time
        self.staticText1.SetLabel(time.asctime())

    def OnSlider1Slider(self, event):
        self.lEDNumberCtrl1.SetValue(`event.GetPosition()`)
        self.gauge1.SetValue(event.GetPosition())

if __name__ == '__main__':
    app = wxPySimpleApp()
    app.SetAssertMode(wxPYAPP_ASSERT_SUPPRESS) # suppress invalid tool bmp assert
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()
