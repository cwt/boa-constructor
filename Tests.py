from wxPython.wx import *
from wxPython.lib.buttons import *

def postCommandEvent(ctrl, evtType, evtId = None):
    if evtId is None:
        evtId = ctrl.GetId()
    wxPostEvent(ctrl, wxCommandEvent(evtType, evtId))
    wxYield()


def test_wxFrame(palette):
    # New frame
    postCommandEvent(palette.palettePages[0].buttons['wxFrame'],
                     wxEVT_COMMAND_BUTTON_CLICKED)

    # Open designer
    from Models import EditorHelper
    postCommandEvent(palette.editor, wxEVT_COMMAND_MENU_SELECTED,
                     EditorHelper.wxID_EDITORDESIGNER)

    # Select static text
    btn = palette.palettePages[2].buttons['wxStaticText']
    btn.up = false
    evt = wxGenButtonEvent(wxEVT_COMMAND_BUTTON_CLICKED, btn.GetId())
    evt.SetButtonObj(btn)
    evt.SetIsDown(true)
    wxPostEvent(btn, evt)
    wxYield()

    # Drop component on Designer
    model = palette.editor.getActiveModulePage().model
    evt = wxMouseEvent(wxEVT_LEFT_DOWN)
#        evt.SetEventObject(model.views['Designer'])
    evt.m_x = 10
    evt.m_y = 10
    wxPostEvent(model.views['Designer'], evt)
    wxYield()

    model.views['Designer'].SetDimensions(10, 10, 200, 200)
    wxYield()

    model.views['Designer'].Close()

    if model.data == frame_answer:
        wxMessageBox('Test succeeded')
    else:
        wxMessageBox('Test failed\n'+model.data)

frame_answer = '''#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1STATICTEXT1] = map(lambda _init_ctrls: wxNewId(), range(2))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(10, 10), size = wxSize(200, 200), style = wxDEFAULT_FRAME_STYLE, title = 'wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(192, 173))

        self.staticText1 = wxStaticText(id = wxID_WXFRAME1STATICTEXT1, label = 'staticText1', name = 'staticText1', parent = self, pos = wxPoint(0, 0), size = wxSize(192, 173), style = 0)

    def __init__(self, parent):
        self._init_ctrls(parent)
'''
