#Boa:Dialog:KeyDefsDialog

from wxPython.wx import *

import Preferences, Utils

class InvalidValueError(Exception): pass

[wxID_KEYDEFSDIALOG, wxID_KEYDEFSDIALOGALTFLAGCHB, wxID_KEYDEFSDIALOGCANCELBTN, wxID_KEYDEFSDIALOGCTRLFLAGCHB, wxID_KEYDEFSDIALOGKEYCODECBB, wxID_KEYDEFSDIALOGOKBTN, wxID_KEYDEFSDIALOGSHIFTFLAGCHB, wxID_KEYDEFSDIALOGSHORTCUTTC, wxID_KEYDEFSDIALOGSTATICBOX1, wxID_KEYDEFSDIALOGSTATICTEXT1, wxID_KEYDEFSDIALOGSTATICTEXT2] = map(lambda _init_ctrls: wxNewId(), range(11))

class KeyDefsDialog(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_KEYDEFSDIALOG, name = 'KeyDefsDialog', parent = prnt, pos = wxPoint(430, 271), size = wxSize(298, 184), style = wxDEFAULT_DIALOG_STYLE, title = self.entryTitle)
        self._init_utils()
        self.SetClientSize(wxSize(290, 157))

        self.staticBox1 = wxStaticBox(id = wxID_KEYDEFSDIALOGSTATICBOX1, label = 'Flags', name = 'staticBox1', parent = self, pos = wxPoint(8, 8), size = wxSize(136, 96), style = 0)

        self.ctrlFlagChb = wxCheckBox(id = wxID_KEYDEFSDIALOGCTRLFLAGCHB, label = 'wxACCEL_CTRL', name = 'ctrlFlagChb', parent = self, pos = wxPoint(16, 24), size = wxSize(112, 19), style = 0)
        EVT_CHECKBOX(self.ctrlFlagChb, wxID_KEYDEFSDIALOGCTRLFLAGCHB, self.OnUpdateShortcut)

        self.altFlagChb = wxCheckBox(id = wxID_KEYDEFSDIALOGALTFLAGCHB, label = 'wxACCEL_ALT', name = 'altFlagChb', parent = self, pos = wxPoint(16, 48), size = wxSize(112, 19), style = 0)
        EVT_CHECKBOX(self.altFlagChb, wxID_KEYDEFSDIALOGALTFLAGCHB, self.OnUpdateShortcut)

        self.shiftFlagChb = wxCheckBox(id = wxID_KEYDEFSDIALOGSHIFTFLAGCHB, label = 'wxACCEL_SHIFT', name = 'shiftFlagChb', parent = self, pos = wxPoint(16, 72), size = wxSize(112, 19), style = 0)
        EVT_CHECKBOX(self.shiftFlagChb, wxID_KEYDEFSDIALOGSHIFTFLAGCHB, self.OnUpdateShortcut)

        self.keyCodeCbb = wxComboBox(choices = self.preDefKeys, id = wxID_KEYDEFSDIALOGKEYCODECBB, name = 'keyCodeCbb', parent = self, pos = wxPoint(152, 32), size = wxSize(125, 21), style = 0, validator = wxDefaultValidator, value = '')
        EVT_COMBOBOX(self.keyCodeCbb, wxID_KEYDEFSDIALOGKEYCODECBB, self.OnUpdateShortcutKeyCodeCbb)
        EVT_TEXT(self.keyCodeCbb, wxID_KEYDEFSDIALOGKEYCODECBB, self.OnUpdateShortcutKeyCodeCbb)

        self.staticText1 = wxStaticText(id = wxID_KEYDEFSDIALOGSTATICTEXT1, label = 'Key code:', name = 'staticText1', parent = self, pos = wxPoint(152, 16), size = wxSize(48, 13), style = 0)

        self.staticText2 = wxStaticText(id = wxID_KEYDEFSDIALOGSTATICTEXT2, label = 'Shortcut text:', name = 'staticText2', parent = self, pos = wxPoint(152, 64), size = wxSize(63, 13), style = 0)

        self.shortcutTc = wxTextCtrl(id = wxID_KEYDEFSDIALOGSHORTCUTTC, name = 'shortcutTc', parent = self, pos = wxPoint(152, 80), size = wxSize(124, 21), style = 0, value = '')

        self.okBtn = wxButton(id = wxID_KEYDEFSDIALOGOKBTN, label = 'OK', name = 'okBtn', parent = self, pos = wxPoint(120, 120), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.okBtn, wxID_KEYDEFSDIALOGOKBTN, self.OnOkbtnButton)

        self.cancelBtn = wxButton(id = wxID_KEYDEFSDIALOGCANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self, pos = wxPoint(200, 120), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.cancelBtn, wxID_KEYDEFSDIALOGCANCELBTN, self.OnCancelbtnButton)

    def __init__(self, parent, entryName, accelEntry):
        #possibly raise exception for invalid format before creating the dialog
        flags, keyCode, shortcut = eval(accelEntry)[0]

        self.preDefKeys = []
        self.preDefKeys = specialKeys.keys() + otherKeys1 + otherKeys2
        self.entryTitle = 'Key binding definition:'
        self.entryTitle = 'Key binding definition: %s' % entryName

        self._init_ctrls(parent)

        self.SetAcceleratorTable(
              wxAcceleratorTable([ Utils.setupCloseWindowOnEscape(self) ]))

        self.flagCtrls = ((self.ctrlFlagChb, wxACCEL_CTRL),
                          (self.altFlagChb, wxACCEL_ALT),
                          (self.shiftFlagChb, wxACCEL_SHIFT))

        for ctrl, flag in self.flagCtrls:
            ctrl.SetValue((flags & flag) == flag)

        if valNameMap.has_key(keyCode):
            self.keyCodeCbb.SetValue(valNameMap[keyCode])
        else:
            self.keyCodeCbb.SetValue(chr(keyCode))

        self.shortcutTc.SetValue(shortcut)

    def validateCtrls(self):
        flags = []
        for ctrl, flag in self.flagCtrls:
            if ctrl.GetValue():
                flags.append(flagValNames[flag][0])
        if flags:
            flags = string.join(flags, ' | ')
        else:
            flags = 'wxACCEL_NORMAL'

        keyCode = self.keyCodeCbb.GetValue()
        if not keyCode:
            raise InvalidValueError('Key code may not be blank')
        if keyCode not in specialKeys.keys() + otherKeys1 + otherKeys2:
            if len(keyCode) != 1 or keyCode not in string.letters+string.digits:
                raise InvalidValueError('Key code must either be a single character (letter or digit) or an identifier selected from the combobox')
            keyCode = "ord('%s')" % string.upper(keyCode)

        shortcut = self.shortcutTc.GetValue()
        if not shortcut:
            raise InvalidValueError('Shortcut may not be blank, enter a concise description, e.g. Ctrl-Shft-S')

        return "(%s, %s, '%s')," % (flags, keyCode, shortcut)

    def deriveShortcut(self, keyCode=None):
        segs = []
        for ctrl, flag in self.flagCtrls:
            if ctrl.GetValue():
                segs.append(flagValNames[flag][1])
        if keyCode is None:
            keyCode = self.keyCodeCbb.GetValue()
        if keyCode:
            segs.append(printableKeyCode(keyCode))

        self.shortcutTc.SetValue(string.join(segs, '-'))

    def OnOkbtnButton(self, event):
        try:
            self.result = self.validateCtrls()
        except InvalidValueError, err:
            wxMessageBox(str(err), 'Invalid value error', wxOK | wxICON_ERROR, self)
        else:
            self.EndModal(wxID_OK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wxID_CANCEL)

    def OnUpdateShortcut(self, event):
        self.deriveShortcut()

    def OnUpdateShortcutKeyCodeCbb(self, event):
        self.deriveShortcut(event.GetString())


def printableKeyCode(keyCode):
    if len(keyCode) >=5 and keyCode[:4] == 'WXK_':
        return string.capitalize(keyCode[4:])
    else:
        return string.upper(keyCode)

flagValNames = {wxACCEL_CTRL:  ('wxACCEL_CTRL', 'Ctrl'),
                wxACCEL_ALT:   ('wxACCEL_ALT', 'Alt'),
                wxACCEL_SHIFT: ('wxACCEL_SHIFT', 'Shft')}

specialKeys = {'WXK_BACK': 8, 'WXK_TAB': 9, 'WXK_RETURN': 13, 'WXK_ESCAPE': 27,
               'WXK_SPACE': 32, 'WXK_DELETE': 127}
# values 300+
otherKeys1 = ['WXK_START', 'WXK_LBUTTON', 'WXK_RBUTTON', 'WXK_CANCEL', 'WXK_MBUTTON',
 'WXK_CLEAR', 'WXK_SHIFT']
# values 308+
otherKeys2 = ['WXK_CONTROL', 'WXK_MENU', 'WXK_PAUSE', 'WXK_CAPITAL',
 'WXK_PRIOR', 'WXK_NEXT', 'WXK_END', 'WXK_HOME', 'WXK_LEFT', 'WXK_UP', 'WXK_RIGHT',
 'WXK_DOWN', 'WXK_SELECT', 'WXK_PRINT', 'WXK_EXECUTE', 'WXK_SNAPSHOT', 'WXK_INSERT',
 'WXK_HELP', 'WXK_NUMPAD0', 'WXK_NUMPAD1', 'WXK_NUMPAD2', 'WXK_NUMPAD3', 'WXK_NUMPAD4',
 'WXK_NUMPAD5', 'WXK_NUMPAD6', 'WXK_NUMPAD7', 'WXK_NUMPAD8', 'WXK_NUMPAD9',
 'WXK_MULTIPLY', 'WXK_ADD', 'WXK_SEPARATOR', 'WXK_SUBTRACT', 'WXK_DECIMAL',
 'WXK_DIVIDE', 'WXK_F1', 'WXK_F2', 'WXK_F3', 'WXK_F4', 'WXK_F5', 'WXK_F6',
 'WXK_F7', 'WXK_F8', 'WXK_F9', 'WXK_F10', 'WXK_F11', 'WXK_F12', 'WXK_F13',
 'WXK_F14', 'WXK_F15', 'WXK_F16', 'WXK_F17', 'WXK_F18', 'WXK_F19', 'WXK_F20',
 'WXK_F21', 'WXK_F22', 'WXK_F23', 'WXK_F24', 'WXK_NUMLOCK', 'WXK_SCROLL',
 'WXK_PAGEUP', 'WXK_PAGEDOWN', ]

# build reverse mapping
valNameMap = {}
for name, val in specialKeys.items():
    valNameMap[val] = name
val = 300
for name in otherKeys1:
    valNameMap[val] = name
    val = val + 1
val = 308
for name in otherKeys2:
    valNameMap[val] = name
    val = val + 1

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    app = wxPySimpleApp()
    dlg = KeyDefsDialog(None, 'ContextHelp', "(wxACCEL_NORMAL, WXK_F1, 'F1'),")
    try:
        if dlg.ShowModal() == wxID_OK:
            print dlg.result
    finally:
        dlg.Destroy()
