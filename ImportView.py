#----------------------------------------------------------------------
# Name:        ImportView.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from wxPython.wx import *
from wxPython.ogl import *
import EditorViews

wxOGLInitialize()


class RoundedRectangleShape(wxRectangleShape):
    def __init__(self, w=0.0, h=0.0):
        wxRectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)

class MyEvtHandler(wxShapeEvtHandler):
    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(false, dc)
            canvas.Redraw(dc)
        else:
            redraw = false
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []
            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(true, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(false, dc)
                canvas.Redraw(dc)

#        self.UpdateStatusBar(shape)


    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        self.base_OnEndDragLeft(x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
#        self.UpdateStatusBar(shape)


    def OnSize(self, x, y):
        self.base_OnSize(x, y)


#    def OnMovePost(self, dc, x, y, oldX, oldY, display):
#        self.base_OnMovePost(dc, x, y, oldX, oldY, display)
#        self.UpdateStatusBar(self.GetShape())


    def OnRightClick(self, *dontcare):
        pass


#----------------------------------------------------------------------

incy = 45

class UMLView(wxShapeCanvas, EditorViews.EditorView):
    viewName = 'UML'
##    def buildTree(self, parent, dict):
##        for item in dict.keys():
##            child = self.AppendItem(parent, item)
##	    if len(dict[item].keys()):
##	        self.buildTree(child, dict[item])

    def __init__(self, parent, model):
        wxShapeCanvas.__init__(self, parent)

        self.SetBackgroundColour(wxWHITE)
        self.diagram = wxDiagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []

        rRectBrush = wxBrush(wxNamedColour("MEDIUM TURQUOISE"), wxSOLID)

##    def refreshCtrl(self):
##        roots = self.AddRoot(self.model.moduleName)
##        hierc = self.model.module.createHierarchy()
##        print hierc
##        
##        self.buildTree(roots, hierc)

        

        self.active = true
        self.model = model

     
    def addClass(self, size, pos, className, classMeths):
        idx = self.MyAddShape(wxDividedShape(size[0], size[1]), pos[0], pos[1], wxBLACK_PEN, wxLIGHT_GREY_BRUSH, 'UMLC')

        region = wxShapeRegion()
#        print dir(region.__class__.__bases__[0])
        region.SetText(className)
        region.SetProportions(0.0, 0.25)
        self.shapes[idx].AddRegion(region)
        region = wxShapeRegion()
        region.SetProportions(0.0, 0.05)
        self.shapes[idx].AddRegion(region)
        region = wxShapeRegion()
        region.SetText(string.join(classMeths, '\012'))
        region.SetProportions(0.0, 0.7)
        self.shapes[idx].AddRegion(region)
        
        return self.shapes[idx] 


    def MyAddShape(self, shape, x, y, pen, brush, text):
#        shape.SetDraggable(false)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        shape.SetPen(pen)
        shape.SetBrush(brush)
        shape.AddText(text)
        shape.SetShadowMode(SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(true)

        evthandler = MyEvtHandler()
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        
        return len(self.shapes) -1

    def addLine(self, dc, fromShape, toShape):
        line = wxLineShape()
        line.SetCanvas(self)
        line.SetPen(wxBLACK_PEN)
        line.SetBrush(wxBLACK_BRUSH)
        line.AddArrow(ARROW_ARROW)
        line.MakeLineControlPoints(2)
        fromShape.AddLine(line, toShape)
        self.diagram.AddShape(line)
        line.Show(true)

        # for some reason, the shapes have to be moved for the line to show up...
        fromShape.Move(dc, fromShape.GetX(), fromShape.GetY())

    def processLevel(self, dc, hierc, pos, incx, fromShape = None):
        for clss in hierc.keys():
            if self.model.module.classes.has_key(clss):
                toShape = self.addClass((20, 30), (pos[0], pos[1]), clss, self.model.module.classes[clss].methods.keys())
                if fromShape:
                    self.addLine(dc, toShape, fromShape)
                k = hierc[clss].keys()
                if len(k):
                    px, py, incx = self.processLevel(dc, hierc[clss], [pos[0], pos[1]+incy], incx, toShape)
                else: px, py = pos[0], pos[1] 
                pos[0] = px + incx
#                pos[1] = p
                if pos[0] > 700:
                    pos[1] = py + incy
                    pos[0] = 40
                    incx = incx *-1
                elif pos[0] < 40:
                    pos[1] = py + incy
                    pos[0] = 700
                    incx = incx *-1
        
        return pos[0], pos[1], incx
        

    def refreshCtrl(self):
        dc = wxClientDC(self)
        self.PrepareDC(dc)

        hierc = self.model.module.createHierarchy()

        pos = [40, 40]
        
        incx = 40
        self.processLevel(dc, hierc, pos, incx)
##        for topCls in hierc.keys():
##            dummy, pos[1] = self.processLevel(dc, hierc[topCls], pos)
##            pos[0] = 20
##            print pos


    def __del__(self):
        for shape in self.diagram.GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)
                shape.Destroy()

class __Cleanup:
    cleanup = wxOGLCleanUp
    def __del__(self):
        self.cleanup()

# when this module gets cleaned up then wxOGLCleanUp() will get called
__cu = __Cleanup()








overview = """\
The Object Graphics Library is a library supporting the creation and
manipulation of simple and complex graphic images on a canvas.

"""


