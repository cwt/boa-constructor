#-----------------------------------------------------------------------------
# Name:        ProcessProgressDlg.py
# Purpose:     Dialog that shows errors and output of a process executed with
#              wxProcess. Operation can be canceled.
#
# Author:      Riaan Booysen
#
# Created:     2001/02/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ProcessProgressDlg

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

import string, os, time

[wxID_PROCESSPROGRESSDLGERRORTCTRL, wxID_PROCESSPROGRESSDLGSPLITTERWINDOW1, wxID_PROCESSPROGRESSDLGSTATUSSTXT, wxID_PROCESSPROGRESSDLGCMDSTXT, wxID_PROCESSPROGRESSDLGOUTPUTTCTRL, wxID_PROCESSPROGRESSDLGSTATUSGGE, wxID_PROCESSPROGRESSDLGCANCELBTN, wxID_PROCESSPROGRESSDLG] = map(lambda _init_ctrls: wxNewId(), range(8))

class ProcessProgressDlg(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, size = wxSize(384, 363), id = wxID_PROCESSPROGRESSDLG, title = 'Progress', parent = prnt, name = 'ProcessProgressDlg', style = wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE, pos = wxPoint(313, 215))
        self._init_utils()
        self.SetAutoLayout(true)
        EVT_CLOSE(self, self.OnProcessprogressdlgClose)

        self.cancelBtn = wxButton(label = 'Cancel', id = wxID_PROCESSPROGRESSDLGCANCELBTN, parent = self, name = 'cancelBtn', size = wxSize(80, 24), style = 0, pos = wxPoint(288, 304))
        self.cancelBtn.SetConstraints(LayoutAnchors(self.cancelBtn, false, false, true, true))
        EVT_BUTTON(self.cancelBtn, wxID_PROCESSPROGRESSDLGCANCELBTN, self.OnCancelbtnButton)

        self.cmdStxt = wxStaticText(label = 'staticText1', id = wxID_PROCESSPROGRESSDLGCMDSTXT, parent = self, name = 'cmdStxt', size = wxSize(360, 64), style = wxST_NO_AUTORESIZE, pos = wxPoint(8, 8))
        self.cmdStxt.SetConstraints(LayoutAnchors(self.cmdStxt, true, true, true, false))

        self.splitterWindow1 = wxSplitterWindow(size = wxSize(360, 192), parent = self, id = wxID_PROCESSPROGRESSDLGSPLITTERWINDOW1, name = 'splitterWindow1', style = wxSP_3D, point = wxPoint(8, 80))
        self.splitterWindow1.SetConstraints(LayoutAnchors(self.splitterWindow1, true, true, true, true))

        self.errorTctrl = wxTextCtrl(size = wxSize(356, 78), value = '', pos = wxPoint(2, 2), parent = self.splitterWindow1, name = 'errorTctrl', style = wxTE_MULTILINE, id = wxID_PROCESSPROGRESSDLGERRORTCTRL)
        self.errorTctrl.SetForegroundColour(wxColour(128, 0, 0))

        self.outputTctrl = wxTextCtrl(size = wxSize(356, 103), value = '', pos = wxPoint(2, 87), parent = self.splitterWindow1, name = 'outputTctrl', style = wxTE_MULTILINE, id = wxID_PROCESSPROGRESSDLGOUTPUTTCTRL)
        self.splitterWindow1.SplitHorizontally(self.errorTctrl, self.outputTctrl, 80)

        self.statusStxt = wxStaticText(label = 'staticText1', id = wxID_PROCESSPROGRESSDLGSTATUSSTXT, parent = self, name = 'statusStxt', size = wxSize(248, 16), style = 0, pos = wxPoint(8, 288))
        self.statusStxt.SetConstraints(LayoutAnchors(self.statusStxt, true, false, true, true))

        self.statusGge = wxGauge(size = wxSize(184, 16), id = wxID_PROCESSPROGRESSDLGSTATUSGGE, style = wxGA_HORIZONTAL, parent = self, name = 'statusGge', validator = wxDefaultValidator, range = 100, pos = wxPoint(8, 312))
        self.statusGge.SetConstraints(LayoutAnchors(self.statusGge, true, false, true, true))

    def __init__(self, parent, command, caption, modally = true, linesep = os.linesep, autoClose = true):
        self._init_ctrls(parent)
        self.SetTitle(caption)
        self.Center(wxBOTH)

        self.process = None
        self.output = []
        self.errors = []
        self.modally = true
        self.finished = false
        self.responded = false
        self.linesep = linesep
        self.autoClose = autoClose

        EVT_IDLE(self, self.OnIdle)
        EVT_END_PROCESS(self, -1, self.OnProcessEnded)

        self.cmdStxt.SetLabel(command)
        self.execute(command, modally)
        if not modally:
            while not self.finished: wxYield()

    def execute(self, cmd, modally = true):
        self.cancelBtn.SetLabel('Cancel')
        self.statusStxt.SetLabel('Waiting for response...')
        self.responded = false
        self.modally = modally

        self.process = wxProcess(self)
        self.process.Redirect();
        wxExecute(cmd, false, self.process)
        self.errorStream = self.process.GetErrorStream()
        self.outputStream = self.process.GetInputStream()
        self.OnIdle(None)

    def prepareResult(self):
        self.output = string.split(string.join(self.output, ''), self.linesep)[:-1]
        for idx in range(len(self.output)):
            self.output[idx] = self.output[idx] + os.linesep
        self.errors = string.split(string.join(self.errors, ''), self.linesep)[:-1]
        for idx in range(len(self.errors)):
            self.errors[idx] = self.errors[idx] + os.linesep

    def updateStream(self, stream, data, tCtrl):
        if stream and not stream.eof():
            if not self.responded:
                self.statusStxt.SetLabel('Receiving response...')
                self.responded = true
            text = stream.read()
            print text
            data.append(text)
            tCtrl.SetFocus()
            tCtrl.AppendText(text)

    def OnIdle(self, event):
        if not self.finished:
            v = self.statusGge.GetValue()
            if v > 100:
                v = 0
            else:
                v = v + 1
            self.statusGge.SetValue(v)

        if self.process is not None:
            self.updateStream(self.errorStream, self.errors, self.errorTctrl)
            self.updateStream(self.outputStream, self.output, self.outputTctrl)

        wxWakeUpIdle()
        time.sleep(0.01)

    def OnProcessEnded(self, event):
        self.OnIdle(None)
        self.statusStxt.SetLabel('Response received.')

        self.process.Destroy()
        self.process = None

        self.prepareResult()
        self.statusGge.SetValue(0)

        self.finished = true
        self.cancelBtn.SetLabel('OK')

        if self.modally and self.autoClose:
            self.EndModal(wxOK)

    def OnProcessprogressdlgClose(self, event):
        try:
            if self.process is not None:
                self.process.Detach()
                self.process.CloseOutput()
                self.process = None
        finally:
            event.Skip()

    def OnCancelbtnButton(self, event):
        if not self.finished:
            self.process.CloseOutput()
            self.process.Detach()
            self.process = None
            self.prepareResult()
            if self.modally:
                self.EndModal(wxCANCEL)
        else:
            self.EndModal(wxOK)


if __name__ == '__main__':
    app = wxPySimpleApp()
    modal = 1
    dlg = ProcessProgressDlg(None, 'cvs -H status', 'Test', modal, autoClose=false)
    if modal:
        dlg.ShowModal()
    print dlg.errors, dlg.output
    dlg.Destroy()
    app.MainLoop()
