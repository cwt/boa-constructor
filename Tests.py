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
    import Editor
    postCommandEvent(palette.editor, wxEVT_COMMAND_MENU_SELECTED,
                     Editor.wxID_EDITORDESIGNER)

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

[wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1] = map(lambda _init_ctrls: wxNewId(), range(2))

class wxFrame1(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(200, 200), id = wxID_WXFRAME1, title = 'wxFrame1', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(10, 10))
        self._init_utils()

        self.staticText1 = wxStaticText(label = 'staticText1', id = wxID_WXFRAME1STATICTEXT1, parent = self, name = 'staticText1', size = wxSize(192, 173), style = 0, pos = wxPoint(0, 0))

    def __init__(self, parent):
        self._init_ctrls(parent)
'''
