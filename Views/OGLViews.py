#----------------------------------------------------------------------
# Name:        OGLViews.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import pickle
from os import path

from wxPython.wx import *
from wxPython.ogl import *

from Preferences import IS

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
                try:
                    if s and s.Selected():
                        # If we unselect it now then some of the objects in
                        # shapeList will become invalid (the control points are
                        # shapes too!) and bad things will happen...
                        toUnselect.append(s)
                except Exception, message: pass#print Exception, message

            shape.Select(true, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(false, dc)
                canvas.Redraw(dc)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        self.base_OnEndDragLeft(x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

    def OnSize(self, x, y):
        self.base_OnSize(x, y)

    def OnRightClick(self, x, y, a, b):
        print 'rightclick', x, y, a, b
#        self.PopupMenu(self.menu, wxPoint(self.x, self.y))

    def OnRightDown(self, event):
        print "OnRightDown", event

#----------------------------------------------------------------------

incy = 45

class PersistentShapeCanvas(wxShapeCanvas):
    ext = '.lay'
    def __init__(self, parent):
        wxShapeCanvas.__init__(self, parent)
        self.shapes = []

    def saveSizes(self, filename):
        '''Build a picklable dictionary of sizes/positions and save.'''
        persProps = {}

        for shape in self.shapes:
            try:
                if hasattr(shape, 'unqPclName'):
                    persProps[shape.unqPclName] = shape.getPos()
            except:
                print 'error:', shape
                raise


        f = open(filename, 'w')
        pickle.dump(persProps, f)
        f.close()

    def loadSizes(self, filename):
        # construct list of non matching

        f = open(filename, 'r')
        persProps = pickle.load(f)
        f.close()

        unmatchedPcls = persProps.keys()
        matchedShapes = []

        for shape in self.shapes:
            if persProps.has_key(shape.unqPclName):
                unmatchedPcls.remove(shape.unqPclName)
            else:
                unmatchedPcls.append(shape.unqPclName)

        for shape in self.shapes:
#            if shape.unqPclName in matchedShapes:
            if persProps.has_key(shape.unqPclName):
#                size, pos = persProps[shape.unqPclName]
#                shape.setSize(size)
                pos = persProps[shape.unqPclName]
                shape.setPos(pos)

        diagram = self.GetDiagram()
        canvas = diagram.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.shapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
#            shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)


class PerstShape:
    def __init__(self, unqPclName):
        self.unqPclName = unqPclName

    def setPos(self, pos):
        """Must be implemented for any class deriving from it, called
         after reading positions from pickle."""

    def getPos(self, pos):
        """Must be implemented for any class deriving from it, called
         before reading sizes into pickle."""


class PerstDividedShape(wxDividedShape, PerstShape):
    def __init__(self, unqPclName, width, height):
        wxDividedShape.__init__(self, width, height)
        PerstShape.__init__(self, unqPclName)

    def setPos(self, pos):
        '''Pos for divide shape, format:
         (width, height)'''

        self.SetX(pos[0])
        self.SetY(pos[1])


    def getPos(self):
        """Pos for divide shape, format:
         (width, height)"""

        return (self.GetX(), self.GetY())

    def FlushText(self):
        """This method retrieves the text from the shape
        regions and draws it. There seems to be a problem that
        the text is not normally drawn. """
        canvas = self.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)
        count = 0
        for region in self.GetRegions():
            region.SetFormatMode(4)
            self.FormatText(dc, region.GetText(), count)
            count = count + 1

class PersistentOGLView(PersistentShapeCanvas, EditorViews.EditorView):
    viewName = 'OGL'
    loadBmp = 'Images/Editor/Open.bmp'
    saveBmp = 'Images/Editor/Save.bmp'

    def __init__(self, parent, model, actions = ()):
        PersistentShapeCanvas.__init__(self, parent)
        EditorViews.EditorView.__init__(self, model,
          (('(Re)load diagram', self.OnLoad, self.loadBmp, ()),
#           ('tst', self.OnTst, self.loadBmp, ()),
           ('Save diagram', self.OnSave, self.saveBmp, ()))+actions)

        self.SetBackgroundColour(wxWHITE)
        self.diagram = wxDiagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []

        self.active = true

    def destroy(self):
        self.destroyShapes()
        EditorViews.EditorView.destroy(self)

    def destroyShapes(self):
        self.shapes = []
        self.diagram.DeleteAllShapes()

    def refreshCtrl(self):
        layoutFile = path.splitext(self.model.filename)[0]+self.ext
        if path.exists(layoutFile):
            self.loadSizes(layoutFile)


    def newLine(self, dc, fromShape, toShape):
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

    def newRegion(self, font, name, textLst, maxWidth, totHeight = 10):
        region = wxShapeRegion()
        dc = wxClientDC(self)
        dc.SetFont(font)

        for text in textLst:
            w, h = dc.GetTextExtent(text)
            if w > maxWidth: maxWidth = w
            totHeight = totHeight + h + 0 # interline padding

        region.SetFont(font)
        region.SetText(string.join(textLst, '\n'))
        region.SetName(name)

        return region, maxWidth, totHeight

    def addShape(self, shape, x, y, pen, brush, text):
#        shape.SetDraggable(false)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        shape.SetPen(pen)
        shape.SetBrush(brush)
#        shape.SetFont(wxFont(6, wxMODERN, wxNORMAL, wxNORMAL, false))
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

    def OnLoad(self, event):
        self.loadSizes(path.splitext(self.model.filename)[0]+self.ext)

    def OnSave(self, event):
        self.saveSizes(path.splitext(self.model.filename)[0]+self.ext)

    def OnTst(self, event):
        dc = wxClientDC(self)
        self.diagram.RecentreAll(dc)

if wxPlatform == '__WXGTK__':
    boldFont = wxFont(12, wxDEFAULT, wxNORMAL, wxBOLD, false)
    font = wxFont(10, wxDEFAULT, wxNORMAL, wxNORMAL, false)
else:
    boldFont = wxFont(7, wxDEFAULT, wxNORMAL, wxBOLD, false)
    font = wxFont(7, wxDEFAULT, wxNORMAL, wxNORMAL, false)

class UMLView(PersistentOGLView):
    ext = '.umllay'
    viewName = 'UML'
    showAttributes = 1
    showMethods = 1
    AllClasses = {}
    toggleAttrBmp = 'Images/Views/UML/attribute.bmp'
    toggleMethBmp = 'Images/Views/UML/method.bmp'

    def __init__(self, parent, model):
        PersistentOGLView.__init__(self, parent, model, (
            ('Toggle Attributes', self.OnToggleAttributes, self.toggleAttrBmp, ()),
            ('Toggle Methods', self.OnToggleMethods, self.toggleMethBmp, ())))
        self.menuStdClass = wxMenu()
        id = wxNewId()
        self.menuStdClass.Append(id, "Goto Source", checkable = 0)
        EVT_MENU(self, id, self.OnGotoSource)
        id = wxNewId()
        self.menuStdClass.Append(id, "Goto Documentation", checkable = 0)
        EVT_MENU(self, id, self.OnGotoDoc)

    def newClass(self, size, pos, className, classMeths, classAttrs):
        shape = PerstDividedShape(className, size[0], size[1])

        maxWidth = 10 #padding
        if not self.showAttributes: classAttrs = [' ']
        if not self.showMethods: classMeths = [' ']

        regionName, maxWidth, nameHeight = self.newRegion(boldFont, 'class_name', [className], maxWidth)
        regionAttribs, maxWidth, attribsHeight = self.newRegion(font, 'attributes', classAttrs, maxWidth)
        regionMeths, maxWidth, methsHeight = self.newRegion(font, 'methods', classMeths, maxWidth)

        totHeight = nameHeight + attribsHeight + methsHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionAttribs.SetProportions(0.0, 1.0*(attribsHeight/float(totHeight)))
        regionMeths.SetProportions(0.0, 1.0*(methsHeight/float(totHeight)))

        shape.AddRegion(regionName)
        shape.AddRegion(regionAttribs)
        shape.AddRegion(regionMeths)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()

        idx = self.addShape(shape, pos[0], pos[1], wxBLACK_PEN,
          wxLIGHT_GREY_BRUSH, '')

        shape.FlushText()

        return self.shapes[idx]

    def newExternalClass(self, size, pos, className):
        shape = PerstDividedShape(className, size[0], size[1])

        maxWidth = 10 #padding

        regionName, maxWidth, nameHeight = self.newRegion(boldFont, 'class_name', [className], maxWidth)

        totHeight = nameHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))

        shape.AddRegion(regionName)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()

        idx = self.addShape(shape, pos[0], pos[1], wxBLACK_PEN,
          wxGREY_BRUSH, '')

        shape.FlushText()

        return self.shapes[idx]

    def processLevel(self, dc, hierc, pos, incx, fromShape = None):
        module = self.model.getModule()
        for clss in hierc.keys():
            if self.AllClasses.has_key(clss):
                toShape = self.AllClasses[clss]
                px, py = pos[0], pos[1]
            else:
                if module.classes.has_key(clss):
                    toShape = self.newClass((20, 30), (pos[0], pos[1]),
                      clss, module.classes[clss].methods.keys(),
                       module.classes[clss].attributes.keys())
                    self.AllClasses[clss] = toShape
                else:
                    toShape = self.newExternalClass((20, 30), (pos[0], pos[1]), clss)
                    self.AllClasses[clss] = toShape
                toShape.SetId(1000 + len(self.AllClasses))
                k = hierc[clss].keys()
                if len(k):
                    px, py, incx = self.processLevel(dc, hierc[clss],
                        [pos[0], pos[1]+incy], incx, toShape)
                else: px, py = pos[0], pos[1]
            if fromShape:
                self.newLine(dc, toShape, fromShape)

            pos[0] = px + incx
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

        self.destroyShapes()
        self.AllClasses = {}

        module = self.model.getModule()
        hierc = module.createHierarchy()

        pos = [40, 40]

        incx = 40
        self.processLevel(dc, hierc, pos, incx)

        PersistentOGLView.refreshCtrl(self)

    def OnToggleMethods(self, event):
        if self.showMethods == 1: self.showMethods = 0
        else: self.showMethods = 1
        return self.refreshCtrl()

    def OnToggleAttributes(self, event):
        if self.showAttributes == 1: self.showAttributes = 0
        else: self.showAttributes = 1
        return self.refreshCtrl()

    def OnGotoDoc(self, event):
        if self.menuClass:
            name = self.menuClass
            if self.model.views.has_key('Documentation') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Documentation']
                srcView.focus()
                module = self.model.getModule()
                #srcView.gotoLine(int(module.classes[name].block.start) -1)
            else:
                print "Documentation View is not open"
        else:
            print "No shape selected"

    def OnGotoSource(self, event):
        if self.menuClass:
            name = self.menuClass
            if self.model.views.has_key('Source') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Source']
                srcView.focus()
                module = self.model.getModule()
                srcView.gotoLine(int(module.classes[name].block.start) -1)
            else:
                print "No source for selection"
        else:
            print "No shape selected"

    ## This allows me to pop-up a menu for the shape. However it loses the
    ## main menu position (x, y) go to 0,0 after the skip
    def OnRightDown(self, event):
        """If the event occurs on one of our shapes, I want to pop-up a shape"""
        (x, y) = (event.m_x, event.m_y)
        for (name, shape) in self.AllClasses.items():
            (hit, attach_point, distance) = shape.HitTest(x, y)
            if hit: break
        if not hit:
            self.PopupMenu(self.menu, wxPoint(x, y))
            return
        # If we reach this point, then we have a selected shape.
        # However, it may be a class or external
        if self.model.getModule().classes.has_key(name):
            (self.menuShape, self.menuClass) = (shape, name)
            self.PopupMenu(self.menuStdClass, wxPoint(x, y))
            (self.menuShape, self.menuClass) = (None, None)

class ImportsView(PersistentOGLView):
    ext = '.implay'
    refreshBmp = 'Images/Editor/Refresh.bmp'
    viewName = 'Imports'

    def __init__(self, parent, model):
        PersistentOGLView.__init__(self, parent, model,
          (('-', None, '', ()),
           ('Refresh', self.OnRefresh, self.refreshBmp, ()))
        )
        self.relationships = None
        self.showImports = 1

    def newModule(self, size, pos, moduleName, importList):
        idx = self.addShape(PerstDividedShape(moduleName, size[0], size[1]),
          pos[0], pos[1], wxBLACK_PEN, wxLIGHT_GREY_BRUSH, '')

        if not self.showImports: importList = [' ']

        maxWidth = 10 #padding

        regionName, maxWidth, nameHeight = self.newRegion(boldFont,
          'module_name', [moduleName], maxWidth)
        regionClss, maxWidth, clssHeight = self.newRegion(font,
          'methods', importList, maxWidth)

        totHeight = nameHeight + clssHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionClss.SetProportions(0.0, 1.0*(clssHeight/float(totHeight)))

        shape = self.shapes[idx]
        shape.AddRegion(regionName)
        shape.AddRegion(regionClss)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()
        shape.FlushText()

        return shape, maxWidth + 10

    def refreshCtrl(self):
        dc = wxClientDC(self)
        self.PrepareDC(dc)

        # Because of slow building process, cache after first time
        if not self.relationships:
            relations = self.model.buildImportRelationshipDict()
            self.relationships = relations
            self.destroyShapes()
        else:
            return
            #relations = self.relationships

        shapes = {}
        p = 10
        y = 20
        # Add shapes
        for rel in relations.keys():
            impLst = []
            for i in relations[rel].imports.keys():
                if relations.has_key(i): impLst.append(i)

            shape, width = self.newModule((20, 30), (p, y), rel, relations[rel].classes.keys())
            shapes[rel] = (shape, impLst)
            p = p + width + 10
            if p > self.GetSize().x:
                p = 10
                y = y + 120

        # Add lines
        for module in shapes.keys():
            for line in shapes[module][1]:
                self.newLine(dc, shapes[module][0], shapes[line][0])

        PersistentOGLView.refreshCtrl(self)

    def OnRefresh(self, event):
        self.relationships = None
        self.refreshCtrl()


class AppPackageView(PersistentOGLView):
    ext = '.apklay'
    refreshBmp = 'Images/Editor/Refresh.bmp'
    viewName = 'Application packages'

    def __init__(self, parent, model):
        PersistentOGLView.__init__(self, parent, model,
          (('-', None, '', ()),
           ('Refresh', self.OnRefresh, self.refreshBmp, ()))
        )
        self.relationships = None

    def newModule(self, size, pos, moduleName, importList):
        idx = self.addShape(PerstDividedShape(moduleName, size[0], size[1]),
          pos[0], pos[1], wxBLACK_PEN, wxLIGHT_GREY_BRUSH, '')

        maxWidth = 10 #padding

        regionName, maxWidth, nameHeight = self.newRegion(boldFont,
          'module_name', [moduleName], maxWidth)
        regionClss, maxWidth, clssHeight = self.newRegion(font,
          'methods', importList, maxWidth)

        totHeight = nameHeight + clssHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionClss.SetProportions(0.0, 1.0*(clssHeight/float(totHeight)))

        shape = self.shapes[idx]
        shape.AddRegion(regionName)
        shape.AddRegion(regionClss)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()
        shape.FlushText()

        return shape, maxWidth + 10

    def refreshCtrl(self):
        dc = wxClientDC(self)
        self.PrepareDC(dc)

        # Because of slow building process, cache after first time
        if not self.relationships:
            relations = self.model.buildImportRelationshipDict()
            self.relationships = relations
            self.destroyShapes()
        else:
            return
            #relations = self.relationships

        shapes = {}
        p = 10
        y = 20
        # Add shapes
        for rel in relations.keys():
            impLst = []
            for i in relations[rel].imports.keys():
                if relations.has_key(i): impLst.append(i)

            shape, width = self.newModule((20, 30), (p, y), rel, relations[rel].classes.keys())
            shapes[rel] = (shape, impLst)
            p = p + width + 10
            if p > self.GetSize().x:
                p = 10
                y = y + 120

        # Add lines
        for module in shapes.keys():
            for line in shapes[module][1]:
                self.newLine(dc, shapes[module][0], shapes[line][0])

        PersistentOGLView.refreshCtrl(self)

    def OnRefresh(self, event):
        self.relationships = None
        self.refreshCtrl()

class __Cleanup:
    cleanup = wxOGLCleanUp
    def __del__(self):
        self.cleanup()

# when this module gets cleaned up then wxOGLCleanUp() will get called
__cu = __Cleanup()
