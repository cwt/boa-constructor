#-----------------------------------------------------------------------------
# Name:        ClipboardPlus.py
# Purpose:
#
# Author:      Roman Yakovenko, plug-in by Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2004
# Licence:
#-----------------------------------------------------------------------------

from wxPython.wx import *
from types import *

class ClipboardPlus:
    def __init__(self, buffer = [], buffer_size = 10):
        self._buffer = buffer
        self._buffer_size = buffer_size

    def _read(self):
        doData = wxTextDataObject()
        wxTheClipboard.Open()
        success = wxTheClipboard.GetData(doData)
        wxTheClipboard.Close()
        if success:
            return doData.GetText()
        else:
            wxBell()
            return ''

    def _write(self, what):
        doWhat = wxTextDataObject()
        doWhat.SetText(what)
        wxTheClipboard.Open()
        wxTheClipboard.SetData(doWhat)
        wxTheClipboard.Close()

    def _smart_insert(self, text):
        try:
            self._buffer.remove(text)
        except ValueError:
            pass
        self._buffer.insert(0, text)

    def update(self, param = None):
        if param is None:
            self._smart_insert(self._read() )
        elif isinstance(param, ListType):
            self._buffer = param
        elif isinstance(param, StringType):
            self._smart_insert(param)

        # Limit growth
        self._buffer = self._buffer[:self._buffer_size]

    def updateClipboard(self, text):
        self._write(text)
        self.update(text)

    def getClipboardList(self):
        return self._buffer

#-------------------------------------------------------------------------------

class ClipboardPlusViewPlugin:

    clipboardPlus = ClipboardPlus()

    def __init__(self, model, view, actions):
        self.model = model
        self.view = view
        actions.extend( (
              ('-', None, '-', ''),
              ('Copy+', self.OnEditCopyPlus, '-', 'CopyPlus'),
              ('Paste+', self.OnEditPastePlus, '-', 'PastePlus'),
        ) )

    
    def OnEditCopyPlus(self, event):
        self.clipboardPlus.updateClipboard(self.view.GetSelectedText())

    def OnEditPastePlus(self, event):
        buffer = self.clipboardPlus.getClipboardList()
        if len(buffer) == 1:
            self.view.Paste()
        else:
            dlg = wxSingleChoiceDialog(self.view, 'Context', 'Smart clipboard', buffer)
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.clipboardPlus.updateClipboard( dlg.GetStringSelection() )
                    self.view.Paste()
            finally:
                dlg.Destroy()

from Views import SourceViews
SourceViews.EditorStyledTextCtrl.plugins += (ClipboardPlusViewPlugin,)

Preferences.keyDefs['CopyPlus'] = (wxACCEL_CTRL|wxACCEL_SHIFT, ord('C') , 'Ctrl-Shift-C')
Preferences.keyDefs['PastePlus'] = (wxACCEL_CTRL|wxACCEL_SHIFT, ord('V'), 'Ctrl-Shift-V')
