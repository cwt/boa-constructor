#Boa:FramePanel:ImageEditorPanel

import os, math, tempfile, StringIO, string

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

import Utils

if wxVERSION < (2,3,3):
    raise Utils.SkipPlugin, 'This plugin requires wxPython 2.3.3 or higher'

# draw destination consts
ddCanvas = 1
ddGrid = 2

[wxID_IMAGEEDITORPANEL, wxID_IMAGEEDITORPANELBGCOLBTN,
 wxID_IMAGEEDITORPANELBRUSHCOLBTN, wxID_IMAGEEDITORPANELEDITWINDOW,
 wxID_IMAGEEDITORPANELFGCOLBTN, wxID_IMAGEEDITORPANELMODECHOICE,
 wxID_IMAGEEDITORPANELPENBRUSHWINDOW, wxID_IMAGEEDITORPANELSLIDER1,
 wxID_IMAGEEDITORPANELSPINBUTTON1, wxID_IMAGEEDITORPANELSPINBUTTON2,
 wxID_IMAGEEDITORPANELSPINBUTTON3, wxID_IMAGEEDITORPANELSTATICTEXT1,
] = map(lambda _init_ctrls: wxNewId(), range(12))

class ImageEditorPanel(wxPanel):
    def _init_utils(self):
        # generated method, don't edit
        self.cursorCross = wxStockCursor(id=wxCURSOR_CROSS)

        self.cursorMove = wxStockCursor(id=wxCURSOR_SIZING)

        self.cursorDraw = wxStockCursor(id=wxCURSOR_PENCIL)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPanel.__init__(self, id=wxID_IMAGEEDITORPANEL,
              name='ImageEditorPanel', parent=prnt, pos=wxPoint(466, 318),
              size=wxSize(586, 356), style=wxSUNKEN_BORDER | wxTAB_TRAVERSAL)
        self._init_utils()
        self.SetAutoLayout(true)
        self.SetClientSize(wxSize(578, 329))

        self.modeChoice = wxChoice(choices=self.drawingModes,
              id=wxID_IMAGEEDITORPANELMODECHOICE, name='modeChoice',
              parent=self, pos=wxPoint(8, 7), size=wxSize(64, 21), style=0,
              validator=wxDefaultValidator)
        self.modeChoice.SetColumns(2)
        self.modeChoice.SetToolTipString('Current drawing mode')
        EVT_CHOICE(self.modeChoice, wxID_IMAGEEDITORPANELMODECHOICE,
              self.OnModeChoiceChoice)

        self.FGColBtn = wxButton(id=wxID_IMAGEEDITORPANELFGCOLBTN, label='',
              name='FGColBtn', parent=self, pos=wxPoint(78, 5), size=wxSize(24,
              24), style=0)
        self.FGColBtn.SetBackgroundColour(wxColour(0, 0, 0))
        self.FGColBtn.SetToolTipString('Pen colour')
        EVT_BUTTON(self.FGColBtn, wxID_IMAGEEDITORPANELFGCOLBTN,
              self.OnFgcolbtnButton)

        self.spinButton3 = wxSpinButton(id=wxID_IMAGEEDITORPANELSPINBUTTON3,
              name='spinButton3', parent=self, pos=wxPoint(106, 5),
              size=wxSize(16, 24), style=wxSP_VERTICAL)
        self.spinButton3.SetRange(0, 32)
        self.spinButton3.SetToolTipString('Pen width')
        EVT_COMMAND_SCROLL(self.spinButton3, wxID_IMAGEEDITORPANELSPINBUTTON3,
              self.OnSpinbutton3CommandScroll)

        self.spinButton2 = wxSpinButton(id=wxID_IMAGEEDITORPANELSPINBUTTON2,
              name='spinButton2', parent=self, pos=wxPoint(122, 5),
              size=wxSize(16, 24), style=wxSP_VERTICAL)
        self.spinButton2.SetRange(0, 11)
        self.spinButton2.SetToolTipString('Pen style')
        EVT_COMMAND_SCROLL(self.spinButton2, wxID_IMAGEEDITORPANELSPINBUTTON2,
              self.OnSpinbutton2CommandScroll)

        self.penBrushWindow = wxWindow(id=wxID_IMAGEEDITORPANELPENBRUSHWINDOW,
              name='penBrushWindow', parent=self, pos=wxPoint(137, 5),
              size=wxSize(32, 24), style=wxSUNKEN_BORDER)
        self.penBrushWindow.SetToolTipString('Pen / Brush preview')
        EVT_PAINT(self.penBrushWindow, self.OnPenBrushWindowPaint)

        self.spinButton1 = wxSpinButton(id=wxID_IMAGEEDITORPANELSPINBUTTON1,
              name='spinButton1', parent=self, pos=wxPoint(168, 5),
              size=wxSize(16, 24), style=wxSP_VERTICAL)
        self.spinButton1.SetRange(0, 7)
        self.spinButton1.SetToolTipString('Brush style')
        EVT_COMMAND_SCROLL(self.spinButton1, wxID_IMAGEEDITORPANELSPINBUTTON1,
              self.OnSpinbutton1CommandScroll)

        self.brushColBtn = wxButton(id=wxID_IMAGEEDITORPANELBRUSHCOLBTN,
              label='', name='brushColBtn', parent=self, pos=wxPoint(189, 5),
              size=wxSize(24, 24), style=0)
        self.brushColBtn.SetBackgroundColour(wxColour(255, 255, 255))
        self.brushColBtn.SetToolTipString('Brush colour')
        EVT_BUTTON(self.brushColBtn, wxID_IMAGEEDITORPANELBRUSHCOLBTN,
              self.OnBrushcolbtnButton)

        self.BGColBtn = wxButton(id=wxID_IMAGEEDITORPANELBGCOLBTN, label='',
              name='BGColBtn', parent=self, pos=wxPoint(213, 5), size=wxSize(24,
              24), style=0)
        self.BGColBtn.SetBackgroundColour(wxColour(192, 192, 192))
        self.BGColBtn.SetToolTipString('Background brush colour')
        EVT_BUTTON(self.BGColBtn, wxID_IMAGEEDITORPANELBGCOLBTN,
              self.OnBgcolbtnButton)

        self.slider1 = wxSlider(id=wxID_IMAGEEDITORPANELSLIDER1, maxValue=25,
              minValue=1, name='slider1', parent=self, point=wxPoint(244, 5),
              size=wxSize(108, 24), style=wxSL_HORIZONTAL,
              validator=wxDefaultValidator, value=16)
        self.slider1.SetToolTipString('Zoom factor')
        EVT_SCROLL(self.slider1, self.OnSlider1ScrollThumbtrack)

        self.editWindow = wxScrolledWindow(id=wxID_IMAGEEDITORPANELEDITWINDOW,
              name='editWindow', parent=self, pos=wxPoint(8, 34),
              size=wxSize(561, 288), style=wxSUNKEN_BORDER)
        self.editWindow.SetBackgroundColour(wxColour(255, 255, 255))
        self.editWindow.SetConstraints(LayoutAnchors(self.editWindow, true,
              true, true, true))
        EVT_PAINT(self.editWindow, self.OnEditWindowPaint)
        EVT_LEFT_DOWN(self.editWindow, self.OnEditWindowLeftDown)
        EVT_LEFT_UP(self.editWindow, self.OnEditWindowLeftUp)
        EVT_MOTION(self.editWindow, self.OnEditWindowMotion)
        EVT_SCROLLWIN(self.editWindow, self.OnEditWindowScroll)

        self.staticText1 = wxStaticText(id=wxID_IMAGEEDITORPANELSTATICTEXT1,
              label='Image info', name='staticText1', parent=self,
              pos=wxPoint(360, 2), size=wxSize(208, 27),
              style=wxST_NO_AUTORESIZE)

    def __init__(self, parent):
        self.drawingModes = ['Select', 'Draw', 'Line', 'Circle', 'Box', 'Fill', 'Colour']
        self._init_ctrls(parent)

        self.currentCursor = None

        self.drawingMethMap = {'Select': (ddCanvas|ddGrid, self.drawSelection),
                               'Draw'  : (ddCanvas,        self.drawPoint),
                               'Line'  : (ddCanvas|ddGrid, self.drawLine),
                               'Circle': (ddCanvas|ddGrid, self.drawCircle),
                               'Box'   : (ddCanvas|ddGrid, self.drawBox),
                               'Fill'  : (ddCanvas,        self.drawFill),
                               'Move'  : (ddCanvas|ddGrid, self.drawMove),
                               'Colour': (ddCanvas,        self.drawPickColour),
                              }

        self.mode = ''
        self.setMode('Draw')

        self.mDC = self.bmp = None

        self.fgcol = wxBLACK
        self.fgpen = wxPen(self.fgcol, 1, wxSOLID)
        self.bgcol = wxLIGHT_GREY
        self.bgbsh = wxBrush(self.bgcol)
        self.brush = wxBrush(wxWHITE, wxTRANSPARENT)
        self.invpen = wxPen(wxBLUE, 0, wxTRANSPARENT)
        self.selpen = wxPen(wxWHITE, 2, wxSOLID)

        self.x = self.y = 0

        self.modeChoice.SetSelection(1)

        self.offset = 0, 0

        self.prevSelRect = ()
        self.prevLineSeg = ()
        self.prevPointCol = ()


    brushStyles = [wxTRANSPARENT, wxSOLID, wxBDIAGONAL_HATCH, wxCROSSDIAG_HATCH,
                   wxFDIAGONAL_HATCH, wxCROSS_HATCH, wxHORIZONTAL_HATCH,
                   wxVERTICAL_HATCH]

    penStyles = [wxSOLID, wxTRANSPARENT, wxDOT, wxLONG_DASH, wxSHORT_DASH, wxDOT_DASH,
                 wxBDIAGONAL_HATCH, wxCROSSDIAG_HATCH, wxFDIAGONAL_HATCH, wxCROSS_HATCH,
                 wxHORIZONTAL_HATCH, wxVERTICAL_HATCH]

    extTypeMap = {'.bmp': wxBITMAP_TYPE_BMP,
                  '.gif': wxBITMAP_TYPE_GIF,
                  '.jpg': wxBITMAP_TYPE_JPEG,
                  '.png': wxBITMAP_TYPE_PNG,
                  }

#---Public methods--------------------------------------------------------------

    def initImageData(self, ext, data):
        """ Initialise editor with data """
        if data:
            self.mDC = wxMemoryDC()
            self.bmp = wxBitmapFromImage(wxImageFromStream(StringIO.StringIO(data)))
            self.mDC.SelectObject(self.bmp)
        else:
            self.mDC, self.bmp = self.getTempMemDC(16, 16)
            brush = wxBrush(self.bgcol)
            self.mDC.SetBackground(brush)
            self.mDC.Clear()

        self.imgExt = ext

        self.editWindow.Refresh()

        self.mDCundo, self.bmpundo = self.getTempMemDC(self.bmp.GetWidth(),
                                     self.bmp.GetHeight())
        self.selundo = None
        self.snapshot()

        self.updateScrollbars()
        self.updateImageInfo()

    def getImageData(self, ext=None):
        """ Returns the current bitmap data """
        if not ext: ext = self.imgExt

        fn = tempfile.mktemp(ext)
        tpe = self.extTypeMap[string.lower(ext)]
        self.bmp.SaveFile(fn, tpe)
        try:
            return open(fn, 'rb').read()
        finally:
            os.remove(fn)

    def imageModified(self):
        """ Called whenever image is modified, override to catch """
        pass

#---Utils-----------------------------------------------------------------------

    def setMode(self, mode, updateGUI=false):
        if self.mode != mode:
            if mode in ('Draw', 'Line', 'Circle', 'Box', 'Fill'):
                self.currentCursor = self.cursorDraw
            else:
                self.currentCursor = self.cursorCross
            self.editWindow.SetCursor(self.currentCursor)

            self.clearState()

            self.mode = mode
            self.drawDest, self.drawMeth = self.drawingMethMap[self.mode]

            if updateGUI:
                self.modeChoice.SetStringSelection(mode)

    def clearState(self):
        self.dragoffset = self.dragpos = self.dragbmp = self.dragsrcrect = None
        self.sel = self.line = self.circle = self.box = None
        self.editWindow.SetCursor(self.currentCursor)

    def snapshot(self):
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDCundo.Blit(0, 0, self.bmp.GetWidth(), self.bmp.GetHeight(),
              self.mDC, 0, 0)
        if self.sel: self.selundo = self.sel[:]
        else: self.selundo = None

    def getImgPos(self, event):
        x, y = event.GetPositionTuple()
        x, y = self.editWindow.CalcUnscrolledPosition(x, y)
        scale = self.slider1.GetValue()
        return ((x-self.offset[0]) / scale, (y-self.offset[1]) / scale)

    def getTempMemDC(self, width, height):
        bmp = wxEmptyBitmap(width, height)
        memDC = wxMemoryDC()
        memDC.SelectObject(bmp)
        return memDC, bmp

    def getSelBmp(self):
        if self.sel:
            x1, y1, x2, y2 = self.sel
            mDC, bmp = self.getTempMemDC(x2-x1+1, y2-y1+1)
            self.mDC.SetUserScale(1.0, 1.0)
            mDC.Blit(0, 0, x2-x1+1, y2-y1+1, self.mDC, x1, y1)
            mDC.SelectObject(wxNullBitmap)
            return bmp
        return None

    def setMemDCBmp(self, bmp):
        if not bmp or not bmp.Ok():
            raise 'Invalid bitmap'
        self.mDC.SelectObject(wxNullBitmap)
        self.bmp = bmp
        self.mDC.SelectObject(self.bmp)

    def updateScrollbars(self):
        scale = self.slider1.GetValue()
        xPos, yPos = self.editWindow.GetViewStart()
        self.editWindow.SetScrollbars(scale, scale,
              self.bmp.GetWidth(), self.bmp.GetHeight(), xPos, yPos)

    def updateImageInfo(self):
        if self.imgExt: ext = string.upper(self.imgExt[1:])
        else:           ext = 'UNKNOWN'

        w, h, d = self.bmp.GetWidth(), self.bmp.GetHeight(), self.bmp.GetDepth()

        msk = self.bmp.GetMask()
        if msk: m = 'Image is masked'
        else:   m = 'Image is not masked'

        if self.bmp.Ok(): x = ''
        else:             x = 'The bitmap is not valid!'

        text = '%s: (%s, %s), depth: %s\n%s. %s'%(ext, w, h, d, m, x)
        self.staticText1.SetLabel(text)

#---Drawing methods-------------------------------------------------------------

    def undo(self):
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDC.Blit(0, 0, self.bmp.GetWidth(), self.bmp.GetHeight(),
              self.mDCundo, 0, 0)

    def drawSelection(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.sel = self.getImgPos(event) * 2
            elif state in ('drag', 'end'):
                self.sel = self.sel[:2] + self.getImgPos(event)
                if state == 'end':
                    x1, y1, x2, y2 = self.sel
                    self.sel = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

            if self.sel != self.prevSelRect:
                if state == 'end':
                    self.prevSelRect = ()
                else:
                    self.prevSelRect = self.sel
                self.editWindow.Refresh()

        if dc and self.sel:
            x1, y1, x2, y2 = self.sel
            x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wxXOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wxTRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset + x1 * scale - 1, yoffset + y1 * scale - 1,
                   (x2 - x1 + 1) * scale + 4, (y2 - y1 + 1) * scale + 4)

    def drawPoint(self, event, state):
        if state == 'start':
            self.snapshot()

        imgx, imgy = self.getImgPos(event)
        self.mDC.SetPen(self.fgpen)
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDC.DrawPoint(imgx, imgy)
        self.editWindow.Refresh()

        if imgx >=0 and imgx < self.bmp.GetWidth() and \
           imgy >=0 and imgy < self.bmp.GetHeight():
            self.imageModified()

    def drawLine(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.line = self.getImgPos(event) * 2
            elif self.line:
                self.line = self.line[:2] + self.getImgPos(event)
                if state == 'end':
                    self.snapshot()
                    self.mDC.SetLogicalFunction(wxCOPY)
                    self.mDC.SetPen(self.fgpen)
                    self.mDC.SetUserScale(1.0, 1.0)
                    apply(self.mDC.DrawLine, self.line)
                    self.mDC.DrawPoint(self.line[2], self.line[3])

                    x1, y1, x2, y2 = self.line
                    w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
                    if not ((x1 < 0 and x2 < 0) or (x1 >= w and x2 >= w) or \
                            (y1 < 0 and y2 < 0) or (y1 >= h and y2 >= h)):
                        self.imageModified()

                    self.line = None

            if self.prevLineSeg != self.line:
                if state == 'end':
                    self.prevLineSeg = ()
                else:
                    self.prevLineSeg = self.line

                self.editWindow.Refresh()

        if dc and self.line:
            x1, y1, x2, y2 = self.line
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wxXOR)
            dc.SetPen(self.selpen)
            dc.DrawLine(xoffset + x1 * scale + scale/2, yoffset + y1 * scale + scale/2,
                        xoffset + x2 * scale + scale/2, yoffset + y2 * scale + scale/2)

    def drawBox(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.box = self.getImgPos(event) * 2
            else:
                self.box = self.box[:2] + self.getImgPos(event)
                if state == 'end':
                    self.snapshot()
                    self.mDC.SetLogicalFunction(wxCOPY)
                    self.mDC.SetPen(self.fgpen)
                    self.mDC.SetUserScale(1.0, 1.0)
                    self.mDC.SetBrush(self.brush)
                    x1, y1, x2, y2 = self.box
                    self.mDC.DrawRectangle(x1, y1, x2-x1+1, y2-y1+1)
                    self.editWindow.Refresh()

                    x1, y1, x2, y2 = self.box
                    w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
                    if not ((x1 < 0 and x2 < 0) or (x1 >= w and x2 >= w) or \
                            (y1 < 0 and y2 < 0) or (y1 >= h and y2 >= h)):
                        self.imageModified()

                    self.box = None

            self.editWindow.Refresh()

        if dc and self.box:
            x1, y1, x2, y2 = self.box
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wxXOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wxTRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset + x1 * scale - 1, yoffset + y1 * scale - 1,
                       (x2 - x1 + 1) * scale + 4, (y2 - y1 + 1) * scale + 4)

    def drawCircle(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.circle = self.getImgPos(event) + (0,)
            elif state in ('drag', 'end'):
                x1, y1, x2, y2 = self.circle[:2] + self.getImgPos(event)
                rad = math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2)) + 0.5
                self.circle = (x1, y1, rad)
                if state == 'end':
                    self.snapshot()
                    self.mDC.SetLogicalFunction(wxCOPY)
                    self.mDC.SetPen(self.fgpen)
                    self.mDC.SetUserScale(1.0, 1.0)
                    self.mDC.SetBrush(self.brush)
                    self.mDC.DrawEllipse(x1-rad+0.5, y1-rad+0.5, rad*2, rad*2)

                    x, y, rad = self.circle
                    x1, y1 = x-rad+0.5, y-rad+0.5
                    x2, y2 = x1 +rad*2, y1 +rad*2
                    w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
                    if not ((x1 < 0 and x2 < 0) or (x1 >= w and x2 >= w) or \
                            (y1 < 0 and y2 < 0) or (y1 >= h and y2 >= h)):
                        self.imageModified()

                    self.circle = None

            self.editWindow.Refresh()

        if dc and self.circle:
            x, y, rad = self.circle
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wxXOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wxTRANSPARENT_BRUSH)
            dc.DrawEllipse(xoffset + (x-rad+0.5) * scale,
                           yoffset + (y-rad+0.5) * scale,
                           rad*scale*2, rad*scale*2)

    def drawFill(self, event, state):
        self.snapshot()
        x, y = self.getImgPos(event)
        brush = wxBrush(self.fgcol)
        self.mDC.SetBrush(brush)
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDC.FloodFill(x, y, self.mDC.GetPixel(x, y))
        self.editWindow.Refresh()

        if x >=0 and x < self.bmp.GetWidth() and \
           y >=0 and y < self.bmp.GetHeight():
            self.imageModified()

    def drawMove(self, event, state, dc=None):
        x1, y1, x2, y2 = self.sel
        if not dc:
            x, y = self.getImgPos(event)
            if state == 'start':
                self.dragoffset = (x1 - x, y1 - y)
                if not self.dragbmp:
                    self.snapshot()
                    self.dragbmp = self.getSelBmp()
                    self.dragsrcrect = x1, y1, x2-x1+1, y2-y1+1
            elif state in ('drag', 'end'):
                # better to only do this once
                self.undo()

                dox, doy = self.dragoffset
                dx, dy = self.dragpos = dox + x, doy + y

                self.mDC.SetUserScale(1.0, 1.0)
                self.mDC.SetLogicalFunction(wxCOPY)
                self.mDC.SetPen(self.invpen)
                self.mDC.SetBrush(self.bgbsh)
                apply(self.mDC.DrawRectangle, self.dragsrcrect)

                self.mDC.DrawBitmap(self.dragbmp, dx, dy)

                if state == 'end':
                    self.sel = dx, dy, dx + x2-x1, dy + y2-y1

                self.editWindow.Refresh()

                self.imageModified()

        if dc and self.sel and self.dragpos:
            xoffset, yoffset = self.offset
            dx, dy = self.dragpos
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wxXOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wxTRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset + dx * scale - 1, yoffset + dy * scale - 1,
                       (x2 - x1 + 1) * scale + 4, (y2 - y1 + 1) * scale + 4)

    def drawPickColour(self, event, state):
        if state == 'end':
            x, y = self.getImgPos(event)
            newcol = self.mDC.GetPixel(x, y)

            self.fgcol = newcol
            self.fgpen.SetColour(newcol)
            self.FGColBtn.SetBackgroundColour(self.fgcol)

            self.setMode('Draw', updateGUI=true)

    def drawGrid(self, dc):
        pen = wxPen(wxWHITE)
        dc.SetPen(pen)
        dc.SetLogicalFunction(wxXOR)
        scale = self.slider1.GetValue()
        lines = []
        height = self.bmp.GetHeight()
        width = self.bmp.GetWidth()
        xoffset, yoffset = self.offset
        for y in range(height):
            lines.append( (xoffset, y * scale + yoffset,
                           width * scale + xoffset, y * scale + yoffset) )
        for x in range(width):
            lines.append( (x * scale + xoffset, yoffset,
                           x * scale + xoffset, height * scale + yoffset) )

        dc.DrawLineList(lines)

#---View control events---------------------------------------------------------

    def OnEditWindowPaint(self, event):
        dc = wxPaintDC(self.editWindow)
        self.editWindow.PrepareDC(dc)

        if not self.mDC or not self.bmp:
            return

        dc.BeginDrawing()
        try:
            scale = self.slider1.GetValue()
            self.mDC.SetUserScale(1.0/scale, 1.0/scale)
            width = self.bmp.GetWidth()*scale
            height = self.bmp.GetHeight()*scale
            xoffset = max((self.editWindow.GetSize().x - width) / 2, 0)
            yoffset = max((self.editWindow.GetSize().y - height) / 2, 0)
            dc.Blit(xoffset, yoffset, width, height, self.mDC, 0, 0)
            self.mDC.SetUserScale(1.0, 1.0)
            self.offset = xoffset, yoffset
            if scale > 5:
                self.drawGrid(dc)
                framesize = 3
            else:
                framesize = 1

            dc.SetLogicalFunction(wxCOPY)
            pen = wxPen(wxBLACK, framesize, wxSOLID)
            dc.SetPen(pen)
            dc.SetBrush(wxTRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset-1 , yoffset-1, width+2, height+2)

            if (self.drawDest & ddGrid) and self.drawMeth:
                self.drawMeth(None, '', dc)
        finally:
            dc.EndDrawing()

    def OnPenBrushWindowPaint(self, event):
        dc = wxPaintDC(self.penBrushWindow)
        dc.SetBrush(self.brush)
        dc.SetBackground(self.bgbsh)
        dc.SetPen(self.invpen)
        dc.BeginDrawing()
        try:
            cs = self.penBrushWindow.GetClientSize()
            dc.DrawRectangle(0, 0, cs.x, cs.y)
            dc.SetPen(self.fgpen)
            dc.DrawRectangle(cs.x/3-3, cs.y/3-3, cs.x/3+8, cs.y/3+6)
            #dc.Clear()
        finally:
            dc.EndDrawing()

    def OnEditWindowLeftDown(self, event):
        self.editWindow.CaptureMouse()

        if self.mode == 'Select' and self.sel:
            x1, y1, x2, y2 = self.sel
            x, y = self.getImgPos(event)
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                self.setMode('Move')
                self.sel = x1, y1, x2, y2
        elif self.mode == 'Move' and self.sel:
            x1, y1, x2, y2 = self.sel
            x, y = self.getImgPos(event)
            if not (x >= x1 and x <= x2 and y >= y1 and y <= y2):
                self.setMode('Select')
                self.sel = x1, y1, x2, y2

        if (self.drawDest & ddCanvas) and self.drawMeth:
            self.drawMeth(event, 'start')

    def OnEditWindowLeftUp(self, event):
        if self.editWindow.HasCapture():
            self.editWindow.ReleaseMouse()
            if (self.drawDest & ddCanvas) and self.drawMeth:
                self.drawMeth(event, 'end')

    def OnEditWindowMotion(self, event):
        if event.Dragging() and event.LeftIsDown():
            if (self.drawDest & ddCanvas) and self.drawMeth:
                self.drawMeth(event, 'drag')

        if self.sel and not event.Dragging() and not event.LeftIsDown():
            x1, y1, x2, y2 = self.sel
            x, y = self.getImgPos(event)
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                self.editWindow.SetCursor(self.cursorMove)
            else:
                self.editWindow.SetCursor(self.currentCursor)

    def OnSlider1ScrollThumbtrack(self, event):
        self.updateScrollbars()
        self.editWindow.Refresh()

    def showColDlg(self, col):
        data = wxStdColourData(col)
        dlg = wxColourDialog(self, data)
        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetColourData().GetColour()
            return None
        finally:
            dlg.Destroy()

    def OnFgcolbtnButton(self, event):
        newcol = self.showColDlg(self.fgcol)

        if newcol:
            self.fgcol = newcol
            self.fgpen.SetColour(newcol)
            self.FGColBtn.SetBackgroundColour(self.fgcol)
            self.penBrushWindow.Refresh()

    def OnBgcolbtnButton(self, event):
        newcol = self.showColDlg(self.bgcol)

        if newcol:
            self.bgcol = newcol
            self.bgbsh.SetColour(newcol)
            self.BGColBtn.SetBackgroundColour(self.bgcol)
            self.penBrushWindow.Refresh()

    def OnBrushcolbtnButton(self, event):
        newcol = self.showColDlg(self.brush.GetColour())

        if newcol:
            self.brush.SetColour(newcol)
            self.brushColBtn.SetBackgroundColour(newcol)
            self.penBrushWindow.Refresh()

    def OnModeChoiceChoice(self, event):
        self.setMode(self.modeChoice.GetStringSelection())
        self.editWindow.Refresh()

    def OnEditWindowScroll(self, event):
        event.Skip()
        self.editWindow.Refresh()

    def OnSpinbutton1CommandScroll(self, event):
        self.brush.SetStyle(self.brushStyles[self.spinButton1.GetValue()])
        self.penBrushWindow.Refresh()

    def OnSpinbutton2CommandScroll(self, event):
        self.fgpen.SetStyle(self.penStyles[self.spinButton2.GetValue()])
        self.penBrushWindow.Refresh()

    def OnSpinbutton3CommandScroll(self, event):
        self.fgpen.SetWidth(self.spinButton3.GetValue())
        self.penBrushWindow.Refresh()

#---View action events----------------------------------------------------------

    def OnCopy(self, event):
        clip = wxTheClipboard
        clip.Open()
        try:
            bmp = self.getSelBmp()
            clip.SetData(wxBitmapDataObject(bmp))
        finally:
            clip.Close()

    def OnPaste(self, event):
        clip = wxTheClipboard
        clip.Open()
        try:
            data = wxBitmapDataObject()
            try:
                clip.GetData(data)
            except:
                wxLogError('Not a picture')
            else:
                self.modeChoice.SetSelection(0)
                self.setMode('Move')
                self.snapshot()
                self.dragbmp = data.GetBitmap()
                self.dragsrcrect = -1, -1, 0, 0
                self.dragpos = 0, 0
                self.sel = 0, 0, self.dragbmp.GetWidth()-1, self.dragbmp.GetHeight()-1
                self.mDC.DrawBitmap(self.dragbmp, 0, 0)
                self.editWindow.Refresh()

                self.imageModified()
        finally:
            clip.Close()

    def OnUndo(self, event):
        self.undo()

        self.editWindow.Refresh()
        self.updateImageInfo()

    def OnClear(self, event):
        self.snapshot()
        if self.sel:
            x1, y1, x2, y2 = self.sel
            self.mDC.SetClippingRegion(x1, y1, x2-x1, y2-y1)
            self.mDC.Clear()
            self.mDC.DestroyClippingRegion()
        else:
            self.mDC.Clear()

        self.editWindow.Refresh()
        self.imageModified()

    def OnSetTransparentMask(self, event):
        self.mDC.SelectObject(wxNullBitmap)
        self.bmp.SetMask(wxMaskColour(self.bmp, self.fgcol))
        self.mDC.SelectObject(self.bmp)

        self.updateImageInfo()

    def OnClearTransparentMask(self, event):
        self.mDC.SelectObject(wxNullBitmap)
        self.bmp.SetMask(None)
        self.mDC.SelectObject(self.bmp)

        self.updateImageInfo()

    def OnResize(self, event):
        dlg = wxTextEntryDialog(self, 'Enter a tuple for the new size',
              'Resize', '%s, %s'%(self.bmp.GetWidth(), self.bmp.GetHeight()))
        try:
            if dlg.ShowModal() != wxID_OK:
                return
            width, height = eval(dlg.GetValue())
        finally:
            dlg.Destroy()

        # Create new bitmap of required size and copy current one to it
        mDC, bmp = self.getTempMemDC(width, height)
        mDC.Blit(0, 0, self.bmp.GetWidth(), self.bmp.GetHeight(),
                 self.mDC, 0, 0)
        mDC.SelectObject(wxNullBitmap)

        self.setMemDCBmp(bmp)

        self.editWindow.Refresh()
        self.updateImageInfo()
        self.imageModified()

    def OnScale(self, event):
        dlg = wxTextEntryDialog(self, 'Enter a tuple for the new size',
              'Scale', '%s, %s'%(self.bmp.GetWidth(), self.bmp.GetHeight()))
        try:
            if dlg.ShowModal() != wxID_OK:
                return
            width1, height1 = self.bmp.GetWidth(), self.bmp.GetHeight()
            width2, height2 = eval(dlg.GetValue())
        finally:
            dlg.Destroy()

        # draw a new version of the current bmp scaled to the user requested size
        xScale, yScale = float(width2)/width1, float(height2)/height1
        self.mDC.SetUserScale(1/xScale, 1/yScale)
        width, height = self.bmp.GetWidth()*xScale, self.bmp.GetHeight()*yScale
        mDC, bmp = self.getTempMemDC(width, height)
        mDC.Blit(0, 0, width, height, self.mDC, 0, 0)
        mDC.SelectObject(wxNullBitmap)

        self.mDC.SetUserScale(1.0, 1.0)
        self.setMemDCBmp(bmp)

        self.editWindow.Refresh()
        self.updateImageInfo()
        self.imageModified()

    def OnCrop(self, event):
        self.setMemDCBmp(self.getSelBmp())

        self.clearState()

        self.editWindow.Refresh()
        self.updateImageInfo()
        self.imageModified()


class wxStdColourData(wxColourData):
    stdcolours = [(0, 0, 0), (128, 128, 128), (128, 0, 0), (128, 128, 0),
                  (0, 128, 0), (0, 128, 128), (0, 0, 128), (128, 0, 128),
                  (255, 255, 255), (192, 192, 192), (255, 0, 0), (255, 255, 0),
                  (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]

    def __init__(self, col=None):
        wxColourData.__init__(self)
        if col: self.SetColour(col)

        i = 0
        for r, g, b in self.stdcolours:
            self.SetCustomColour(i, wxColour(r, g, b))
            i = i + 1

#-Tester------------------------------------------------------------------------

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = wxFrame(None, -1, 'Image Edit Test')
    panel = ImageEditorPanel(frame)
    frame.Show(true)
    panel.initImageData('.png', open('Images/Modules/Pyrex_s.png', 'rb').read())
    app.MainLoop()
    import sys
    sys.exit()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

import Preferences

from Models import EditorModels, Controllers, EditorHelper
from Views import EditorViews

class ImageView(wxPanel, EditorViews.EditorView):
    viewName = 'View'
    def __init__(self, parent, model):
        wxPanel.__init__(self, parent, -1, style=wxSUNKEN_BORDER)
        self.staticBitmapSmall = wxStaticBitmap(self, -1, wxNullBitmap)
        self.staticBitmapBig = wxStaticBitmap(self, -1, wxNullBitmap)
        EditorViews.EditorView.__init__(self, model, (), -1)
        self.active = true

    imgsep = 32
    def refreshCtrl(self):
        if self.model.data:
            bmp = wxBitmapFromImage(wxImageFromStream(
                                    StringIO.StringIO(self.model.data)))
            self.staticBitmapSmall.SetBitmap(bmp)
            self.staticBitmapSmall.SetDimensions(self.imgsep, self.imgsep,
                                                 bmp.GetWidth(), bmp.GetHeight())
            self.staticBitmapBig.SetBitmap(bmp)
            self.staticBitmapBig.SetDimensions(bmp.GetWidth()+self.imgsep*2,
                  self.imgsep, bmp.GetWidth()*2, bmp.GetHeight()*2)

class ImageEditorView(ImageEditorPanel, EditorViews.EditorView):
    viewName = 'Edit'

    refreshBmp = 'Images/Editor/Refresh.png'
    #cutBmp = 'Images/Shared/Cut.png'
    copyBmp = 'Images/Shared/Copy.png'
    pasteBmp = 'Images/Shared/Paste.png'
    undoBmp = 'Images/Shared/Undo.png'
    def __init__(self, parent, model):
        ImageEditorPanel.__init__(self, parent)
        EditorViews.EditorView.__init__(self, model, (
          ('Refresh', self.OnRefresh, self.refreshBmp, ''),
          ('-', None, '-', ''),
          ('Copy', self.OnCopy, self.copyBmp, ''),
          ('Paste', self.OnPaste, self.pasteBmp, ''),
          ('Undo last change', self.OnUndo, self.undoBmp, ''),
          ('Undo view changes', self.OnUndoViewChanges, '-', ''),
          ('Clear', self.OnClear, '-', ''),
          ('-', None, '-', ''),
          ('Crop', self.OnCrop, '-', ''),
          ('Resize...', self.OnResize, '-', ''),
          ('Scale...', self.OnScale, '-', ''),
          ('-', None, '-', ''),
          ('Use current colour to set transparent mask', self.OnSetTransparentMask, '-', ''),
          ('Clear current transparent mask', self.OnClearTransparentMask, '-', ''),
        ), -1)

        EVT_RIGHT_DOWN(self.editWindow, self.OnRightDown)
        EVT_RIGHT_UP(self.editWindow, self.OnRightClick)

        self.active = true

    def refreshCtrl(self):
        ext = os.path.splitext(self.model.filename)[-1]
        self.initImageData(ext, self.model.data)
        self.editWindow.Refresh()

        self.modified = false
        self.updateViewState()

    def refreshModel(self):
        ext = os.path.splitext(self.model.filename)[-1]
        data = self.getImageData(ext)
        if self.model.data != data:
            self.model.data = data
            self.model.modified = true

        if self.model.viewsModified.count(self.viewName):
            self.model.viewsModified.remove(self.viewName)
        self.modified = false
        EditorViews.EditorView.refreshModel(self)

        self.updateEditor()
        self.updateViewState()

    def imageModified(self):
        self.modified = true
        self.updateViewState()

    def OnRefresh(self, event):
        self.refreshModel()

    def OnUndoViewChanges(self, event):
        self.refreshCtrl()


class BitmapEditorFileController(Controllers.PersistentController):
    Model = EditorModels.BitmapFileModel
    DefaultViews    = [ImageView]
    AdditionalViews = [ImageEditorView]

    editBmpBmp = 'Images/EditBitmap.png'

    def actions(self, model):
        return Controllers.PersistentController.actions(self, model) + [
              ('-', None, '-', ''),
              ('Edit image', self.OnGotoEditView, self.editBmpBmp, '')]

    def OnGotoEditView(self, event):
        model = self.getModel()
        if not model.views.has_key('Edit'):
            modPge = self.editor.getActiveModulePage()
            for View, wid in modPge.adtViews:
                if View == ImageEditorView:
                    self.editor.mainMenu.Check(wid, true)
                    break
            view = modPge.addView(ImageEditorView)
            view.refreshCtrl()
        else:
            view = model.views['Edit']
        view.focus()


Controllers.modelControllerReg[EditorModels.BitmapFileModel] = BitmapEditorFileController

import PaletteStore
PaletteStore.newControllers['Bitmap'] = BitmapEditorFileController
PaletteStore.paletteLists['New'].append('Bitmap')
