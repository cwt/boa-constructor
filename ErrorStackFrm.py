#Boa:MiniFrame:ErrorStackMF

from wxPython.wx import *
import os, string
import Preferences

[wxID_ERRORSTACKMFERRORSTACKTC, wxID_ERRORSTACKMF] = map(lambda _init_ctrls: wxNewId(), range(2))

class ErrorStackMF(wxMiniFrame):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxMiniFrame.__init__(self, size = wxSize(328, 443), id = wxID_ERRORSTACKMF, title = 'Traceback browser', parent = prnt, name = 'ErrorStackMF', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(66, 66))
        self._init_utils()

        self.errorStackTC = wxTreeCtrl(size = wxSize(384, 352), id = wxID_ERRORSTACKMFERRORSTACKTC, parent = self, name = 'errorStackTC', validator = wxDefaultValidator, style = wxTR_HAS_BUTTONS, pos = wxPoint(0, 0))

    def __init__(self, parent, app, editor): 
        self._init_ctrls(parent)
        self.app = app
        self.editor = editor
        EVT_TREE_ITEM_ACTIVATED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeItemActivated)

        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth, 
          Preferences.bottomHeight)
    
    def initTree(self, errorList):
        tree = self.errorStackTC
        rtTI = tree.AddRoot('Errors')
        for err in errorList:
            errTI = tree.AppendItem(rtTI, string.strip(string.join(err.error, ' : ')))
            for si in err.stack:
                siTI = tree.AppendItem(errTI, '%d: %s: %s' % (si.lineNo, 
                      os.path.basename(si.file), string.strip(si.line)))
                tree.SetPyData(siTI, si)
            if len(err.stack):
                tree.SetItemHasChildren(errTI, true)
                tree.SetPyData(errTI, err.stack[-1])
        tree.SetItemHasChildren(rtTI, true)
        tree.Expand(rtTI)
        cookie = 0; firstErr, cookie = tree.GetFirstChild(rtTI, cookie)
        if firstErr.IsOk():
            tree.Expand(firstErr)

    def OnErrorstacktcTreeItemActivated(self, event):
        try:
            data = self.errorStackTC.GetPyData(event.GetItem())
            if data is None:
                return
            if self.app:
                fn = os.path.join(os.path.dirname(self.app.filename), data.file)
            else:
                fn = os.path.abspath(data.file)
            model = self.editor.openOrGotoModule(fn, self.app)
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].gotoLine(data.lineNo - 1)
            model.views['Source'].setStepPos(data.lineNo - 1)
#                self.editor.statusBar.setHint('%s: %s'% (err[-1].error[0], err[-1].error[0])
        finally:
            event.Skip()
            
