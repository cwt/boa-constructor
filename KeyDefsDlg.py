#Boa:Dialog:KeyDefsDialog

# XXX fix accel names/ key codes when 2.5 is used for resource config values

import string

import wx, wxPython.wx

import Preferences, Utils

class InvalidValueError(Exception): pass

[wxID_KEYDEFSDIALOG, wxID_KEYDEFSDIALOGALTFLAGCHB, 
 wxID_KEYDEFSDIALOGCANCELBTN, wxID_KEYDEFSDIALOGCTRLFLAGCHB, 
 wxID_KEYDEFSDIALOGKEYCODECBB, wxID_KEYDEFSDIALOGOKBTN, 
 wxID_KEYDEFSDIALOGSHIFTFLAGCHB, wxID_KEYDEFSDIALOGSHORTCUTTC, 
 wxID_KEYDEFSDIALOGSTATICBOX1, wxID_KEYDEFSDIALOGSTATICTEXT1, 
 wxID_KEYDEFSDIALOGSTATICTEXT2, 
] = [wx.NewId() for _init_ctrls in range(11)]

class KeyDefsDialog(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_KEYDEFSDIALOG, name='KeyDefsDialog',
              parent=prnt, pos=wx.Point(430, 271), size=wx.Size(298, 184),
              style=wx.DEFAULT_DIALOG_STYLE, title=self.entryTitle)
        self.SetClientSize(wx.Size(290, 157))

        self.staticBox1 = wx.StaticBox(id=wxID_KEYDEFSDIALOGSTATICBOX1,
              label='Flags', name='staticBox1', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(136, 96), style=0)

        self.ctrlFlagChb = wx.CheckBox(id=wxID_KEYDEFSDIALOGCTRLFLAGCHB,
              label='wxACCEL_CTRL', name='ctrlFlagChb', parent=self,
              pos=wx.Point(16, 24), size=wx.Size(120, 19), style=0)
        self.ctrlFlagChb.Bind(wx.EVT_CHECKBOX, self.OnUpdateShortcut,
              id=wxID_KEYDEFSDIALOGCTRLFLAGCHB)

        self.altFlagChb = wx.CheckBox(id=wxID_KEYDEFSDIALOGALTFLAGCHB,
              label='wxACCEL_ALT', name='altFlagChb', parent=self,
              pos=wx.Point(16, 48), size=wx.Size(120, 19), style=0)
        self.altFlagChb.Bind(wx.EVT_CHECKBOX, self.OnUpdateShortcut,
              id=wxID_KEYDEFSDIALOGALTFLAGCHB)

        self.shiftFlagChb = wx.CheckBox(id=wxID_KEYDEFSDIALOGSHIFTFLAGCHB,
              label='wxACCEL_SHIFT', name='shiftFlagChb', parent=self,
              pos=wx.Point(16, 72), size=wx.Size(120, 19), style=0)
        self.shiftFlagChb.Bind(wx.EVT_CHECKBOX, self.OnUpdateShortcut,
              id=wxID_KEYDEFSDIALOGSHIFTFLAGCHB)

        self.keyCodeCbb = wx.ComboBox(choices=self.preDefKeys,
              id=wxID_KEYDEFSDIALOGKEYCODECBB, name='keyCodeCbb', parent=self,
              pos=wx.Point(152, 32), size=wx.Size(125, 21), style=0, value='')
        self.keyCodeCbb.Bind(wx.EVT_COMBOBOX, self.OnUpdateShortcutKeyCodeCbb,
              id=wxID_KEYDEFSDIALOGKEYCODECBB)
        self.keyCodeCbb.Bind(wx.EVT_TEXT, self.OnUpdateShortcutKeyCodeCbb,
              id=wxID_KEYDEFSDIALOGKEYCODECBB)

        self.staticText1 = wx.StaticText(id=wxID_KEYDEFSDIALOGSTATICTEXT1,
              label='Key code:', name='staticText1', parent=self,
              pos=wx.Point(152, 16), size=wx.Size(120, 13), style=0)

        self.staticText2 = wx.StaticText(id=wxID_KEYDEFSDIALOGSTATICTEXT2,
              label='Shortcut text:', name='staticText2', parent=self,
              pos=wx.Point(152, 64), size=wx.Size(120, 13), style=0)

        self.shortcutTc = wx.TextCtrl(id=wxID_KEYDEFSDIALOGSHORTCUTTC,
              name='shortcutTc', parent=self, pos=wx.Point(152, 80),
              size=wx.Size(124, 21), style=0, value='')

        self.okBtn = wx.Button(id=wxID_KEYDEFSDIALOGOKBTN, label='OK',
              name='okBtn', parent=self, pos=wx.Point(120, 120),
              size=wx.Size(75, 23), style=0)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkbtnButton,
              id=wxID_KEYDEFSDIALOGOKBTN)

        self.cancelBtn = wx.Button(id=wxID_KEYDEFSDIALOGCANCELBTN,
              label='Cancel', name='cancelBtn', parent=self, pos=wx.Point(200,
              120), size=wx.Size(75, 23), style=0)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancelbtnButton,
              id=wxID_KEYDEFSDIALOGCANCELBTN)

    def __init__(self, parent, entryName, accelEntry):
        #possibly raise exception for invalid format before creating the dialog
        # XXX fix when 2.5 is used for resource config values
        flags, keyCode, shortcut = eval(accelEntry, wxPython.wx.__dict__)[0]

        self.preDefKeys = []
        self.preDefKeys = specialKeys.keys() + otherKeys1 + otherKeys2
        self.entryTitle = 'Key binding definition:'
        self.entryTitle = 'Key binding definition: %s' % entryName

        self._init_ctrls(parent)

        self.SetAcceleratorTable(
              wx.AcceleratorTable([ Utils.setupCloseWindowOnEscape(self) ]))

        self.flagCtrls = ((self.ctrlFlagChb, wx.ACCEL_CTRL),
                          (self.altFlagChb, wx.ACCEL_ALT),
                          (self.shiftFlagChb, wx.ACCEL_SHIFT))

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
            flags = ' | '.join(flags)
        else:
            flags = 'wxACCEL_NORMAL'

        keyCode = self.keyCodeCbb.GetValue()
        if not keyCode:
            raise InvalidValueError('Key code may not be blank')
        if keyCode not in specialKeys.keys() + otherKeys1 + otherKeys2:
            if len(keyCode) != 1 or keyCode not in string.letters+string.digits:
                raise InvalidValueError('Key code must either be a single character (letter or digit) or an identifier selected from the combobox')
            keyCode = "ord('%s')" % keyCode.upper()

        shortcut = self.shortcutTc.GetValue()
        if not shortcut:
            raise InvalidValueError('Shortcut may not be blank, enter a concise description, e.g. Ctrl-Shift-S')

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

        self.shortcutTc.SetValue('-'.join(segs))

    def OnOkbtnButton(self, event):
        try:
            self.result = self.validateCtrls()
        except InvalidValueError, err:
            wx.MessageBox(str(err), 'Invalid value error', wx.OK | wx.ICON_ERROR, self)
        else:
            self.EndModal(wx.ID_OK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnUpdateShortcut(self, event):
        self.deriveShortcut()

    def OnUpdateShortcutKeyCodeCbb(self, event):
        self.deriveShortcut(event.GetString())


def printableKeyCode(keyCode):
    if len(keyCode) >=5 and keyCode[:4] == 'WXK_':
        return keyCode[4:].capitalize()
    else:
        return keyCode.upper()

flagValNames = {wx.ACCEL_CTRL:  ('wxACCEL_CTRL', 'Ctrl'),
                wx.ACCEL_ALT:   ('wxACCEL_ALT', 'Alt'),
                wx.ACCEL_SHIFT: ('wxACCEL_SHIFT', 'Shift')}

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
    app =wx.PySimpleApp()
    dlg = KeyDefsDialog(None, 'ContextHelp', "(wxACCEL_NORMAL, WXK_F1, 'F1'),")
    try:
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.result
    finally:
        dlg.Destroy()
    app.MainLoop()
