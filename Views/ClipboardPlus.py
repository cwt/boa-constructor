#-----------------------------------------------------------------------------
# Name:        ClipboardPlus.py
# Purpose:
#
# Author:      Roman Yakovenko
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
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
