#-----------------------------------------------------------------------------
# Name:        STCPrinting.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2003/05/21
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2005
# Licence:     wxWidgets
#-----------------------------------------------------------------------------
#Boa:Dialog:STCPrintDlg

"""
"""

# XXX Currently forces stc rendering not to wrap lines, currently the page
# XXX total calculations depend on exact number of lines

# XXX

import os

from wxPython.wx import *
from wxPython.stc import *

def create(parent):
    return STCPrintDlg(parent)

[wxID_STCPRINTDLG, wxID_STCPRINTDLGBTNCANCEL, wxID_STCPRINTDLGBTNPRINT, 
 wxID_STCPRINTDLGBTNPRINTPREVIEW, wxID_STCPRINTDLGBTNPRINTSETUP, 
 wxID_STCPRINTDLGCKBFILENAME, wxID_STCPRINTDLGCKBPAGENUMBERS, 
 wxID_STCPRINTDLGRDBCOLOURMODE, 
] = map(lambda _init_ctrls: wxNewId(), range(8))

stcPrintColourModes = [0, wxSTC_PRINT_BLACKONWHITE, wxSTC_PRINT_COLOURONWHITE, 
                       wxSTC_PRINT_COLOURONWHITEDEFAULTBG]

class STCPrintDlg(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_STCPRINTDLG, name='STCPrintDlg',
              parent=prnt, pos=wxPoint(352, 204), size=wxSize(402, 189),
              style=wxDEFAULT_DIALOG_STYLE, title='Print Source')
        self._init_utils()
        self.SetClientSize(wxSize(394, 162))

        self.rdbColourMode = wxRadioBox(choices=['Normal', 'Black on white',
              'Colour on white', 'Colour on white default background'],
              id=wxID_STCPRINTDLGRDBCOLOURMODE, label='Colour Mode',
              majorDimension=1, name='rdbColourMode', parent=self,
              point=wxPoint(8, 8), size=wxSize(216, 112),
              style=wxRA_SPECIFY_COLS, validator=wxDefaultValidator)

        self.ckbFilename = wxCheckBox(id=wxID_STCPRINTDLGCKBFILENAME,
              label='Filename at top', name='ckbFilename', parent=self,
              pos=wxPoint(240, 16), size=wxSize(144, 13), style=0)
        self.ckbFilename.SetValue(True)

        self.ckbPageNumbers = wxCheckBox(id=wxID_STCPRINTDLGCKBPAGENUMBERS,
              label='Page numbers', name='ckbPageNumbers', parent=self,
              pos=wxPoint(240, 40), size=wxSize(136, 13), style=0)
        self.ckbPageNumbers.SetValue(True)

        self.btnPrintSetup = wxButton(id=wxID_STCPRINTDLGBTNPRINTSETUP,
              label='Print Setup', name='btnPrintSetup', parent=self,
              pos=wxPoint(8, 128), size=wxSize(88, 23), style=0)
        EVT_BUTTON(self.btnPrintSetup, wxID_STCPRINTDLGBTNPRINTSETUP,
              self.OnPrintSetup)

        self.btnPrintPreview = wxButton(id=wxID_STCPRINTDLGBTNPRINTPREVIEW,
              label='Print Preview', name='btnPrintPreview', parent=self,
              pos=wxPoint(104, 128), size=wxSize(88, 23), style=0)
        EVT_BUTTON(self.btnPrintPreview, wxID_STCPRINTDLGBTNPRINTPREVIEW,
              self.OnPrintPreview)

        self.btnPrint = wxButton(id=wxID_STCPRINTDLGBTNPRINT, label='Print',
              name='btnPrint', parent=self, pos=wxPoint(200, 128),
              size=wxSize(88, 23), style=0)
        EVT_BUTTON(self.btnPrint, wxID_STCPRINTDLGBTNPRINT, self.OnDoPrint)

        self.btnCancel = wxButton(id=wxID_CANCEL, label='Cancel',
              name='btnCancel', parent=self, pos=wxPoint(296, 128),
              size=wxSize(88, 23), style=0)

    colourMode = 0
    

    def __init__(self, parent, stc, filename=''):
        self._init_ctrls(parent)

        self.stc = stc
        self.filename = filename
        self.parentFrame = parent
        self.preview = None

        self.printData = wxPrintData()
        self.printData.SetPaperId(wxPAPER_LETTER)


    def OnPrintSetup(self, event):
        printerDlg = wxPrintDialog(self)
        pdd = printerDlg.GetPrintDialogData()
        pdd.SetPrintData(self.printData)
        pdd.SetSetupDialog(true)
        printerDlg.ShowModal()
        self.printData = wxPrintData(pdd.GetPrintData())
        printerDlg.Destroy()

    def createSTCPrintout(self):
        colourMode = stcPrintColourModes[self.rdbColourMode.GetSelection()]
        doPageNums = self.ckbPageNumbers.GetValue()
        if self.ckbFilename.GetValue():
            filename = self.filename
        else:
            filename = ''

        return STCPrintout(self.stc, colourMode, filename, doPageNums)
    
    def OnPrintPreview(self, event):
        printout1 = self.createSTCPrintout()
        printout2 = self.createSTCPrintout()
        self.preview = wxPrintPreview(printout1, printout2, self.printData)
        if not self.preview.Ok():
            wxLogError('An error occured while preparing preview.')
            return

        frame = wxPreviewFrame(self.preview, self.parentFrame, 'Print Preview')
        frame.Initialize()
        frame.Show(true)


    def OnDoPrint(self, event):
        pdd = wxPrintDialogData()
        pdd.SetPrintData(self.printData)
        printer = wxPrinter(pdd)
        printout = self.createSTCPrintout()
        
        if not printer.Print(self.parentFrame, printout):
            wxLogError('An error occured while printing.')
        else:
            self.printData = wxPrintData(printer.GetPrintDialogData().GetPrintData())
        printout.Destroy()
        
        self.EndModal(wxOK)


#-------------------------------------------------------------------------------

class STCPrintout(wxPrintout):
    margin = 0.1
    linesPerPage = 69
    
    def __init__(self, stc, colourMode=0, filename='', doPageNums=1):
        wxPrintout.__init__(self)
        self.stc = stc
        self.colourMode = colourMode
        self.filename = filename
        self.doPageNums = doPageNums

        self.pageTotal, m = divmod(stc.GetLineCount(), self.linesPerPage)
        if m: self.pageTotal += 1
        
##    def OnBeginDocument(self, start, end):
##        return self.base_OnBeginDocument(start, end)
##
##    def OnEndDocument(self):
##        self.base_OnEndDocument()
##
##    def OnBeginPrinting(self):
##        self.base_OnBeginPrinting()
##
##    def OnEndPrinting(self):
##        self.base_OnEndPrinting()
##
##    def OnPreparePrinting(self):
##        self.base_OnPreparePrinting()

    def HasPage(self, page):
        if page <= self.pageTotal:
            return true
        else:
            return false

    def GetPageInfo(self):
        return (1, self.pageTotal, 1, 32000)

    def OnPrintPage(self, page):
        stc = self.stc
        self.stcLineHeight = stc.TextHeight(0)

        # calculate sizes including margin and scale
        dc = self.GetDC()
        dw, dh = dc.GetSizeTuple()
        
        mw = self.margin*dw
        mh = self.margin*dh
        textAreaHeight = dh - mh*2
        textAreaWidth = dw - mw*2
        
        scale = float(textAreaHeight)/(self.stcLineHeight*self.linesPerPage)
        dc.SetUserScale(scale, scale)
        
        # render page titles and numbers
        f = dc.GetFont()
        f.SetFamily(wxROMAN)
        f.SetFaceName('Times New Roman')
        f.SetPointSize(f.GetPointSize()+3)
        dc.SetFont(f)
        
        if self.filename:
            tlw, tlh = dc.GetTextExtent(self.filename)
            dc.DrawText(self.filename, 
                  int(dw/scale/2-tlw/2), int(mh/scale-tlh*3))

        if self.doPageNums:
            pageLabel = 'Page: %d' % page
            plw, plh = dc.GetTextExtent(pageLabel)
            dc.DrawText(pageLabel, 
                  int(dw/scale/2-plw/2), int((textAreaHeight+mh)/scale+plh*2))

        # render stc into dc
        stcStartPos = stc.PositionFromLine((page-1)*self.linesPerPage)
        stcEndPos = stc.GetLineEndPosition(page*self.linesPerPage-1)

        maxWidth = 32000
        stc.SetPrintColourMode(self.colourMode)
        ep = stc.FormatRange(1, stcStartPos, stcEndPos, dc, dc, 
                        wxRect(int(mw/scale), int(mh/scale), 
                               maxWidth, int(textAreaHeight/scale)), 
                        wxRect(0, (page-1)*self.linesPerPage*self.stcLineHeight, 
                            maxWidth, self.stcLineHeight*self.linesPerPage))

        # warn when less characters than expected is rendered by the stc when 
        # printing
        if not self.IsPreview():
            if ep < stcEndPos:
                print 'warning: on page', page, \
                      ': not enough chars rendered, diff:', stcEndPos-ep

        return true


#----------------------------------------------------------------------

if __name__ == '__main__':
    testFile = 'STCPrinting.py'
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = wxFrame(None, -1, '')
    # prepare an stc
    frame.stc = wxStyledTextCtrl(frame, -1)
    frame.stc.SetText(open(testFile).read())
    config = os.path.abspath('../Config/stc-styles.rc.cfg')
    from STCStyleEditor import initSTC
    initSTC(frame.stc, config, 'python')
    # print dlg for prepared stc
    dlg = STCPrintDlg(frame, frame.stc, testFile)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    wxCallAfter(frame.Destroy)
    app.MainLoop()
