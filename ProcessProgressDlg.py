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

import string, os, time, sys

# XXX Change to be non-modal, minimizable and run CVS operation in thread !!

# XXX remove when 2.3.3 is minimum version
from Utils import canReadStream

class ProcessRunnerMix:
    def __init__(self):
        EVT_IDLE(self, self.OnIdle)
        EVT_END_PROCESS(self, -1, self.OnProcessEnded)

        self.reset()

    def reset(self):
        self.process = None
        self.output = []
        self.errors = []
        self.errorStream = None
        self.outputStream = None
        self.finished = false
        self.responded = false

    def execute(self, cmd):
        self.process = wxProcess(self)
        self.process.Redirect()

        wxExecute(cmd, false, self.process)

        self.errorStream = self.process.GetErrorStream()
        self.outputStream = self.process.GetInputStream()

        self.OnIdle()

    def detach(self):
        if self.process is not None:
            self.process.CloseOutput()
            self.process.Detach()
            self.process = None

    def updateStream(self, stream, data):
        if stream and canReadStream(stream):
            if not self.responded:
                self.responded = true
            text = stream.read()
            data.append(text)
            return text
        else:
            return None

    def updateErrStream(self, stream, data):
        return self.updateStream(stream, data)

    def updateOutStream(self, stream, data):
        return self.updateStream(stream, data)

    def OnIdle(self, event=None):
        if self.process is not None:
            self.updateErrStream(self.errorStream, self.errors)
            self.updateOutStream(self.outputStream, self.output)

        wxWakeUpIdle()
        time.sleep(0.001)

    def OnProcessEnded(self, event):
        self.OnIdle()

        self.process.Destroy()
        self.process = None

        self.finished = true

class ProcessRunner(wxEvtHandler, ProcessRunnerMix):
    def __init__(self):
        wxEvtHandler.__init__(self)
        ProcessRunnerMix.__init__(self)

[wxID_PROCESSPROGRESSDLG, wxID_PROCESSPROGRESSDLGCANCELBTN,
 wxID_PROCESSPROGRESSDLGCMDSTXT, wxID_PROCESSPROGRESSDLGERRORTCTRL,
 wxID_PROCESSPROGRESSDLGOUTPUTTCTRL, wxID_PROCESSPROGRESSDLGSPLITTERWINDOW1,
 wxID_PROCESSPROGRESSDLGSTATUSGGE, wxID_PROCESSPROGRESSDLGSTATUSSTXT,
] = map(lambda _init_ctrls: wxNewId(), range(8))

class ProcessProgressDlg(wxDialog, ProcessRunnerMix):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_PROCESSPROGRESSDLG,
              name='ProcessProgressDlg', parent=prnt, pos=wxPoint(313, 215),
              size=wxSize(384, 363),
              style=wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE,
              title=self.dlg_caption)
        self._init_utils()
        self.SetAutoLayout(true)
        self.SetClientSize(wxSize(376, 336))
        EVT_CLOSE(self, self.OnProcessprogressdlgClose)

        self.cancelBtn = wxButton(id=wxID_PROCESSPROGRESSDLGCANCELBTN,
              label='Cancel', name='cancelBtn', parent=self, pos=wxPoint(288,
              304), size=wxSize(80, 24), style=0)
        self.cancelBtn.SetConstraints(LayoutAnchors(self.cancelBtn, false,
              false, true, true))
        EVT_BUTTON(self.cancelBtn, wxID_PROCESSPROGRESSDLGCANCELBTN,
              self.OnCancelbtnButton)

        self.cmdStxt = wxStaticText(id=wxID_PROCESSPROGRESSDLGCMDSTXT,
              label='staticText1', name='cmdStxt', parent=self, pos=wxPoint(8,
              8), size=wxSize(360, 64), style=wxST_NO_AUTORESIZE)
        self.cmdStxt.SetConstraints(LayoutAnchors(self.cmdStxt, true, true,
              true, false))

        self.splitterWindow1 = wxSplitterWindow(id=wxID_PROCESSPROGRESSDLGSPLITTERWINDOW1,
              name='splitterWindow1', parent=self, point=wxPoint(8, 80),
              size=wxSize(360, 192), style=wxSP_3DSASH | wxSP_FULLSASH)
        self.splitterWindow1.SetConstraints(LayoutAnchors(self.splitterWindow1,
              true, true, true, true))

        self.errorTctrl = wxTextCtrl(id=wxID_PROCESSPROGRESSDLGERRORTCTRL,
              name='errorTctrl', parent=self.splitterWindow1, pos=wxPoint(0, 0),
              size=wxSize(360, 80), style=wxTE_MULTILINE | wxTE_RICH, value='')
        self.errorTctrl.SetForegroundColour(wxColour(128, 0, 0))

        self.outputTctrl = wxTextCtrl(id=wxID_PROCESSPROGRESSDLGOUTPUTTCTRL,
              name='outputTctrl', parent=self.splitterWindow1, pos=wxPoint(0,
              87), size=wxSize(360, 105), style=wxTE_MULTILINE | wxTE_RICH,
              value='')
        self.splitterWindow1.SplitHorizontally(self.errorTctrl,
              self.outputTctrl, 80)

        self.statusStxt = wxStaticText(id=wxID_PROCESSPROGRESSDLGSTATUSSTXT,
              label='staticText1', name='statusStxt', parent=self,
              pos=wxPoint(8, 288), size=wxSize(248, 16), style=0)
        self.statusStxt.SetConstraints(LayoutAnchors(self.statusStxt, true,
              false, true, true))

        self.statusGge = wxGauge(id=wxID_PROCESSPROGRESSDLGSTATUSGGE,
              name='statusGge', parent=self, pos=wxPoint(8, 312), range=100,
              size=wxSize(184, 16), style=wxGA_HORIZONTAL,
              validator=wxDefaultValidator)
        self.statusGge.SetConstraints(LayoutAnchors(self.statusGge, true, false,
              true, true))

    def __init__(self, parent, command, caption, modally = true, linesep = os.linesep, autoClose = true, overrideDisplay = ''):
        self.dlg_caption = 'Progress'
        self.dlg_caption = caption
        self._init_ctrls(parent)

        self.splitterWindow1.SetMinimumPaneSize(20)

        ProcessRunnerMix.__init__(self)

        self.Center(wxBOTH)

        self.modally = true
        self.linesep = linesep
        self.autoClose = autoClose

        if overrideDisplay:
            self.cmdStxt.SetLabel(overrideDisplay)
        else:
            self.cmdStxt.SetLabel(command)

        self.execute(command, modally)

        if not modally:
            while not self.finished:
                wxYield()

    def execute(self, cmd, modally = true):
        self.cancelBtn.SetLabel('Cancel')
        self.statusStxt.SetLabel('Waiting for response...')
        self.responded = false
        self.modally = modally

        ProcessRunnerMix.execute(self, cmd)

    def updateStream(self, stream, data):
        resp = self.responded
        try:
            return ProcessRunnerMix.updateStream(self, stream, data)
        finally:
            if self.responded == (not resp):
                self.statusStxt.SetLabel('Receiving response...')

    def updateErrStream(self, stream, data):
        txt = ProcessRunnerMix.updateErrStream(self, stream, data)
        if txt is not None:
            self.errorTctrl.SetFocus()
            self.errorTctrl.AppendText(txt)

    def updateOutStream(self, stream, data):
        txt = ProcessRunnerMix.updateOutStream(self, stream, data)
        if txt is not None:
            self.outputTctrl.SetFocus()
            self.outputTctrl.AppendText(txt)

    def OnIdle(self, event=None):
        # step the gauge to indicate activity
        if not self.finished:
            v = self.statusGge.GetValue()
            if v >= 100:
                v = 0
            else:
                v = v + 1
            self.statusGge.SetValue(v)

        ProcessRunnerMix.OnIdle(self, event)

    def OnProcessEnded(self, event):
        ProcessRunnerMix.OnProcessEnded(self, event)

        self.statusStxt.SetLabel('Response received.')

        self.prepareResult()
        self.statusGge.SetValue(0)

        self.cancelBtn.SetLabel('OK')

        if self.modally and self.autoClose:
            self.EndModal(wxOK)

    def OnProcessprogressdlgClose(self, event):
        try:
            self.detach()
        finally:
            event.Skip()

    def prepareResult(self):
        self.output = string.split(string.join(self.output, ''), self.linesep)[:-1]
        for idx in range(len(self.output)):
            self.output[idx] = self.output[idx] + os.linesep
        self.errors = string.split(string.join(self.errors, ''), self.linesep)[:-1]
        for idx in range(len(self.errors)):
            self.errors[idx] = self.errors[idx] + os.linesep

    def OnCancelbtnButton(self, event):
        if not self.finished:
            self.detach()
            self.prepareResult()
            if self.modally:
                self.EndModal(wxCANCEL)
        else:
            self.EndModal(wxOK)

if __name__ == '__main__':
    app = wxPySimpleApp()
    if 1:
        modal = 1
        dlg = ProcessProgressDlg(None, 'cvs -H status', 'Test', modal, autoClose=false)
        if modal:
            dlg.ShowModal()
        #print dlg.errors, dlg.output
        dlg.Destroy()
        dlg.MainLoop()
    else:
        class TestProcessRunner(ProcessRunner):
            def updateErrStream(self, stream, data):
                txt = ProcessRunner.updateErrStream(self, stream, data)
                if txt is not None: print 'error: %s'%txt

            def updateOutStream(self, stream, data):
                txt = ProcessRunner.updateOutStream(self, stream, data)
                if txt is not None: print 'output: %s'%txt

            def OnProcessEnded(self, event):
                ProcessRunnerMix.OnProcessEnded(self, event)
                # Test doesn't terminate, don't know why :(
                app.ExitMainLoop()

        tpr = TestProcessRunner()
        tpr.execute('cvs -H status')
        app.MainLoop()
