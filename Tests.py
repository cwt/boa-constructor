from wxPython.wx import *
from wxPython.lib.buttons import *

def postCommandEvent(ctrl, evtType, evtId = None):
    if evtId is None:
        evtId = ctrl.GetId()
    wxPostEvent(ctrl, wxCommandEvent(evtType, evtId))
    wxYield()


def test_wxFrame(palette):
    try:
        # New frame
        postCommandEvent(palette.palettePages[0].buttons['wxFrame'],
                         wxEVT_COMMAND_BUTTON_CLICKED)
    
        # Open designer
        mp = palette.editor.getActiveModulePage()
        ctrlr = palette.editor.getControllerFromModel(mp.model)
        ctrlr.OnDesigner(None)
    
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
    
        # Select Frame
        evt = wxMouseEvent(wxEVT_LEFT_DOWN)
        evt.m_x = 0
        evt.m_y = 0
        wxPostEvent(model.views['Designer'], evt)
        wxYield()
    
        constructorPage = palette.editor.inspector.constr
        for nv in constructorPage.nameValues:
            if nv.propName == 'Name':
                nv.propEditor.inspectorEdit()
                nv.propEditor.editorCtrl.editorCtrl.SetValue('TestFrame')
                nv.propEditor.inspectorPost(false)
                break
    
        # resize designer
        model.views['Designer'].SetDimensions(10, 10, 200, 200)
        model.views['Designer'].SetPosition( (0, 0) )
        wxYield()
    
        model.views['Designer'].Close()
    except:
        wxMessageBox('Test failed\n'+`sys.exc_info()`)
    else:
        #if model.data == frame_answer:
        wxMessageBox('Test succeeded')

frame_answer = '''#Boa:Frame:TestFrame

from wxPython.wx import *

def create(parent):
    return TestFrame(parent)

[wxID_TESTFRAME, wxID_TESTFRAMESTATICTEXT1,
] = map(lambda _init_ctrls: wxNewId(), range(2))

class TestFrame(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_TESTFRAME, name='TestFrame', parent=prnt,
              pos=wxPoint(0, 0), size=wxSize(200, 200),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(192, 173))

        self.staticText1 = wxStaticText(id=wxID_TESTFRAMESTATICTEXT1,
              label='staticText1', name='staticText1', parent=self,
              pos=wxPoint(0, 0), size=wxSize(192, 173), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
'''
