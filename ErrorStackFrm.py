#-----------------------------------------------------------------------------
# Name:        ErrorStackFrm.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
##Boa:Frame:ErrorStackMF
# remove between #-- comments before editing visually

from wxPython.wx import *
import os, string
import Preferences, Utils

[wxID_ERRORSTACKMFSTATUSBAR, wxID_ERRORSTACKMFERRORSTACKTC, wxID_ERRORSTACKMF, wxID_ERRORSTACKMFNOTEBOOK1, wxID_ERRORSTACKMFOUTPUTTC] = map(lambda _init_ctrls: wxNewId(), range(5))

class ErrorStackMF(wxFrame):
    def _init_coll_notebook1_Pages(self, parent):

        parent.AddPage(strText = 'Errors', bSelect = true, pPage = self.errorStackTC, imageId = -1)
        parent.AddPage(strText = 'Output', bSelect = false, pPage = self.outputTC, imageId = -1)

    def _init_coll_statusBar_Fields(self, parent):
        parent.SetFieldsCount(1)

        parent.SetStatusText(text = '', i = 0)

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(330, 443), id = wxID_ERRORSTACKMF, title = 'Traceback and Output browser', parent = prnt, name = 'ErrorStackMF', style = wxDEFAULT_FRAME_STYLE | Preferences.childFrameStyle, pos = wxPoint(464, 228))
        self._init_utils()
        EVT_CLOSE(self, self.OnErrorstackmfClose)

        self.notebook1 = wxNotebook(size = wxSize(330, 418), id = wxID_ERRORSTACKMFNOTEBOOK1, parent = self, name = 'notebook1', style = 0, pos = wxPoint(0, 0))

        self.statusBar = wxStatusBar(size = wxSize(330, 25), id = wxID_ERRORSTACKMFSTATUSBAR, pos = wxPoint(0, 418), parent = self, name = 'statusBar', style = 0)
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.outputTC = wxTextCtrl(size = wxSize(326, 384), value = '', pos = wxPoint(0, 0), parent = self.notebook1, name = 'outputTC', style = wxTE_MULTILINE, id = wxID_ERRORSTACKMFOUTPUTTC)

        #--
        # Special case to fix GTK redraw problem
        if wxPlatform == '__WXGTK__':
            prxy, errorStackTC = Utils.wxProxyPanel(self.notebook1, wxTreeCtrl, size = wxSize(312, 390), id = wxID_ERRORSTACKMFERRORSTACKTC, name = 'errorStackTC', validator = wxDefaultValidator, style = wxTR_HAS_BUTTONS | wxSUNKEN_BORDER, pos = wxPoint(0, 0))
            self.errorStackTC = prxy
            self._init_coll_notebook1_Pages(self.notebook1)
            self.errorStackTC = errorStackTC
        else:
            self.errorStackTC = wxTreeCtrl(size = wxSize(312, 390), id = wxID_ERRORSTACKMFERRORSTACKTC, parent = self.notebook1, name = 'errorStackTC', validator = wxDefaultValidator, pos = wxPoint(4, 22))
            self._init_coll_notebook1_Pages(self.notebook1)
        #--

    def __init__(self, parent, editor):
        self._init_ctrls(parent)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(Preferences.IS.load('Images/Icons/OutputError.ico'))

        self.app = None
        self.editor = editor
        self.vetoEvents = false
        EVT_TREE_ITEM_ACTIVATED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeItemActivated)
        EVT_TREE_SEL_CHANGED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeSelChanged)
        EVT_LEFT_DOWN(self.errorStackTC, self.OnErrorstacktcLeftDown)

        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth,
          Preferences.bottomHeight)

        self.lastClick = (0, 0)

    def updateCtrls(self, errorList, outputList = None, rootName = 'Error', runningDir = ''):
        self.runningDir = runningDir
        self.tracebackType = rootName
        tree = self.errorStackTC
        tree.DeleteAllItems()
        rtTI = tree.AddRoot(rootName+'s')
        for err in errorList:
            if err.error and err.stack:
                errTI = tree.AppendItem(rtTI, string.strip(string.join(err.error, ' : ')))
                for si in err.stack:
                    siTI = tree.AppendItem(errTI, '%d: %s: %s' % (si.lineNo,
                          os.path.basename(si.file), string.strip(si.line)))
                    tree.SetPyData(siTI, si)
                if err.stack:
                    tree.SetItemHasChildren(errTI, true)
                    tree.SetPyData(errTI, err.stack[-1])
        tree.SetItemHasChildren(rtTI, true)
        tree.Expand(rtTI)
        cookie = 0; firstErr, cookie = tree.GetFirstChild(rtTI, cookie)
        if firstErr.IsOk():
            tree.Expand(firstErr)

        if outputList:
            self.outputTC.SetValue(string.join(outputList, ''))

            if not errorList:
                self.notebook1.SetSelection(1)

    def Destroy(self):
        self.vetoEvents = true
        wxFrame.Destroy(self)

    def OnErrorstacktcTreeItemActivated(self, event):
        try:
            data = self.errorStackTC.GetPyData(event.GetItem())
            if data is None:
                return
            if self.app:
                fn = os.path.join(os.path.dirname(self.app.filename), data.file)
            elif self.runningDir:
                fn = os.path.join(self.runningDir, data.file)
            else:
                fn = os.path.abspath(data.file)
            model = self.editor.openOrGotoModule(fn, self.app)
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].gotoLine(data.lineNo - 1)
            model.views['Source'].setStepPos(data.lineNo - 1)
            self.editor.statusBar.setHint(string.join(data.error, ' : '),
                self.tracebackType)
#            self.Lower()
#            self.editor.Raise()
#            self.editor.Focus()
#                self.editor.statusBar.setHint('%s: %s'% (err[-1].error[0], err[-1].error[0])
        finally:
#            pass
            event.Skip()

    def OnErrorstackmfClose(self, event):
        self.Show(true)
        self.Show(false)

    def OnErrorstacktcTreeSelChanged(self, event):
        if self.vetoEvents: return
        selLine = self.errorStackTC.GetItemText(event.GetItem())
        if wxPlatform == '__WXGTK__':
            self.errorStackTC.SetToolTipString(selLine)
        self.statusBar.SetStatusText(selLine)


    def OnErrorstacktcLeftDown(self, event):
        self.lastClick = event.GetPosition().asTuple()
        event.Skip()
