#----------------------------------------------------------------------
# Name:        SelectionTags.py
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
import string
import sender

defPos = (0, 0)
defSze = (0, 0)
tagSize = 7
frmWid = 1
screenGran = 8

def granularise(val):
    return ((val + screenGran / 2) /screenGran)*screenGran

##def granularise2(val):
##    if val % (screenGran/2) or not val % screenGran:
##        return granularise(val)
##    else:
##        return granularise(val - 1)

class SelectionGroup:
    def newLine(self):
        line = wxPanel(self.parent, -1)
        line.SetSize(wxSize(1, 1))
        line.SetBackgroundColour(wxBLACK)
        self.senders.addObject(line)
        EVT_MOTION(line, self.OnMouseOver)
        EVT_LEFT_UP(line, self.OnSizeEnd)
        return line
        
    def __init__(self, parent, senders, inspector, designer):
#        print 'init selection!'
        self.designer = designer
        self.inspSel = None
        self.inspector = inspector
        self.parent = parent
        self.senders = senders
        self.selection = None
        self.dragTag = None
        self.dragCtrl = None
        self.dragOffset = wxPoint()
        self.dragSize = wxSize()
        self.lastDragPos = wxPoint()
        
        self.position = wxPoint(defPos[0], defPos[1])
        self.size = wxSize(defSze[0], defSze[1])

        self.sfT = self.newLine()
        self.sfR = self.newLine()
        self.sfB = self.newLine()
        self.sfL = self.newLine()
        
        # Create selection tags
        self.stTL = TLSelTag(parent, wxCURSOR_SIZENWSE, tagSize, self)
        self.stTR = TRSelTag(parent, wxCURSOR_SIZENESW, tagSize, self)
        self.stBR = BRSelTag(parent, wxCURSOR_SIZENWSE, tagSize, self)
        self.stBL = BLSelTag(parent, wxCURSOR_SIZENESW, tagSize, self)
        self.stT = TSelTag(parent, wxCURSOR_SIZENS, tagSize, self)
        self.stB = BSelTag(parent, wxCURSOR_SIZENS, tagSize, self)
        self.stL = LSelTag(parent, wxCURSOR_SIZEWE, tagSize, self)
        self.stR = RSelTag(parent, wxCURSOR_SIZEWE, tagSize, self)

        self.tags = [self.sfT, self.sfR, self.sfB, self.sfL,
        	     self.stTL, self.stTR, self.stBR, self.stBL,
        	     self.stT, self.stB, self.stR, self.stL]

        for tag in self.tags:
            self.senders.addObject(tag)

    def destroy(self):
        self.stT.destroy()
        self.stB.destroy()
        self.stR.destroy()
        self.stL.destroy()
        
        self.stTL.destroy()
        self.stTR.destroy()
        self.stBR.destroy()
        self.stBL.destroy()

        del self.tags

        del self.parent
        del self.inspector
        del self.designer
        del self.selection
        del self.inspSel
        
    def __del__(self):
        print '__del__ selection group'

    def showTags(self):
        self.stTL.Show(true)
        self.stTR.Show(true)
        self.stBR.Show(true)
        self.stBL.Show(true)
        self.stT.Show(true)
        self.stB.Show(true)
        self.stL.Show(true)
        self.stR.Show(true)
        self.sfL.Show(false)
        self.sfR.Show(false)
        self.sfB.Show(false)
        self.sfT.Show(false)

    def hideTags(self):
        map(lambda tag: tag.Show(false), self.tags)

    def showFramedTags(self, notHide):
        map(lambda tag: tag.Show(true), self.tags)
    
    def reparentTags(self, parent):
        map(lambda tag, newparent = parent: tag.Reparent(newparent), self.tags)

    def moveRelease(self):
        if self.dragTag:
            # XXX nasty passing a None event
            self.OnSizeEnd(None)
	    self.showTags()
        if self.dragCtrl:
            # XXX Have to hide and show to clean up artifacts, refreshing
            # XXX is not sufficient. Show/hiding seems to screw up Z order
	    self.dragCtrl.Show(false)

            self.dragCtrl.SetDimensions( \
              granularise(self.position.x), granularise(self.position.y), 
              granularise(self.size.x -1), granularise(self.size.y -1))

            self.dragCtrl.Show(true)

##            self.dragCtrl.Refresh()
	    self.dragCtrl = None
	    self.showTags()
            self.inspector.constructorUpdate('Position')

    def moveCapture(self, ctrl, compn, pos):
        # Put selection around control

        self.lastDragPos.x = pos.x
        self.lastDragPos.y = pos.y

        # Begin a drag
        # don't drag frame
        if ctrl != self.designer:
            self.dragCtrl = ctrl
	    self.dragOffset = pos
	    self.showFramedTags(None)
	    self.dragSize = ctrl.GetSize()
	
    def moving(self, ctrl, pos):
        # Sizing
        if self.dragTag:
     	    screenPos = ctrl.ClientToScreen(pos)
     	    parentPos = self.parent.ScreenToClient(screenPos)
            if ctrl == self.designer:
                tb = self.designer.GetToolBar()
                if tb:
                    parentPos.y = parentPos.y - tb.GetSize().y
    	    self.dragTag.setPos(parentPos)
    	# Moving
    	elif self.dragCtrl:
            self.lastDragPos.x = pos.x
            self.lastDragPos.y = pos.y
     	    screenPos = ctrl.ClientToScreen(pos)
     	    parentPos = self.parent.ScreenToClient(screenPos)

            # Calculate an offset that is the difference between the 
            # client size and the control size. Comes into play because
            # dragging is relative to the dragging start point (dragOffset)
            dcs = self.parent.ClientToScreen(self.dragCtrl.GetPosition())
            dccs = self.dragCtrl.ClientToScreen((0, 0))
            
            offsetX = dccs.x - dcs.x
            offsetY = dccs.y - dcs.y

            if ctrl == self.designer:
                tb = self.designer.GetToolBar()
                if tb:
                    offsetY = offsetY + tb.GetSize().y
                    
            self.position = wxPoint(parentPos.x - self.dragOffset.x - offsetX, 
    	                            parentPos.y - self.dragOffset.y - offsetY)

	    self.setSelection()
  
    def selectCtrl(self, ctrl, compn):
        
        self.hideTags()
        if not ctrl:
            self.selection = None
            self.inspSel = None
        else: 
            # XXX fix!
            if ctrl == self.designer:
                self.parent = ctrl
                cp = wxPoint(0, 0)
                
                screenPos = ctrl.ClientToScreen(cp)
                parentPos = self.parent.ScreenToClient(screenPos)
                
            else:
                self.parent = ctrl.GetParent()
                cp = ctrl.GetPosition()

                self.showTags()

            self.reparentTags(self.parent)

            self.position = wxPoint(cp.x, cp.y)
            self.size = ctrl.GetSize()
          
            self.selection = ctrl
            self.lastDragPos = wxPoint(self.position.x, self.position.y)

            self.setSelection()

            self.inspSel = ctrl	
            self.inspector.selectObject(ctrl, compn)

    def selectNone(self):
        self.hideTags()
        self.inspSel = None
        self.selection = None

    def resizeCtrl(self):
        """ Set the selected control's dimensions by granulising
            the current selection group's size & pos """
##        self.selection.Show(false)
        self.selection.SetDimensions( \
          granularise(self.position.x), granularise(self.position.y), 
          granularise(self.size.x - 1), granularise(self.size.y - 1))
##        self.selection.Show(true)

    def sizeFromCtrl(self):
        """ Called from outside the module. Set the group's size & pos from
            a control and notifies the Inspector. """
        # XXX What about granularity?
        if self.selection:
            self.position = self.selection.GetPosition()
            self.size = self.selection.GetSize()
            self.inspector.constructorUpdate('Size')
            self.inspector.propertyUpdate('ClientSize')
            self.inspector.constructorUpdate('Position')
        
    def setSelection(self):
        position = self.position
        size = self.size

        trPos = wxPoint(granularise(position.x), granularise(position.y))
        trSze = wxSize(granularise(size.x -1), granularise(size.y -1))

        self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
        self.stTR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -4, tagSize, tagSize)
        self.stBR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)

        self.stT.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -4, tagSize, tagSize)
        self.stB.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stL.SetDimensions(trPos.x -4, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        self.stR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        
        self.sfT.SetDimensions(trPos.x +3, trPos.y -2, trSze.x - 2*3, frmWid)
	self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y +3, frmWid, trSze.y - 2*3)
	self.sfB.SetDimensions(trPos.x +3, trPos.y + trSze.y, trSze.x - 2*3, frmWid)
	self.sfL.SetDimensions(trPos.x -2, trPos.y +3, frmWid, trSze.y - 2*3)
	
	self.position  = trPos
	self.size = trSze
        
    # Events
    def OnSizeBegin(self, event):
        self.dragTag = self.senders.getObject(event)
        self.showFramedTags(self.dragTag)

    def OnSizeEnd(self, event):
        self.resizeCtrl()
#        self.selectCtrl(self.selection)
        self.showTags()
        self.dragTag = None

    def OnMouseOver(self, event):
        if event.Dragging():
     	    pos = event.GetPosition()
     	    ctrl = self.senders.getObject(event)
            self.moving(ctrl, pos)
	event.Skip()

# XXX Use wxSIMPLE_BORDER/wxColour(128, 128, 128) for multiple selects
class SelectionTag(wxPanel):
    def __init__(self, parent, cursor, size, group, pnlStyle = 0):
        wxPanel.__init__(self, parent, -1, style = pnlStyle)
        self.group = group
        self.SetSize(wxSize(size, size))
        self.SetBackgroundColour(wxBLACK)
        self.SetForegroundColour(wxBLACK)
        self.SetCursor(wxStockCursor(cursor))
        self.selection = None
	self.position = wxSize(0, 0)

        EVT_LEFT_DOWN(self, group.OnSizeBegin)
        EVT_LEFT_UP(self, group.OnSizeEnd)
        EVT_MOTION(self, group.OnMouseOver)

    def setPos(self, position, mirrorX, mirrorY, mirrorXY, oldPos = None, oldSize = None):
        grp = self.group
        if grp.size.x < 0 and grp.size.y < 0:
            grp.size.x = 0
            if oldPos and oldSize: grp.position.x = oldPos.x + oldSize.x
            grp.size.y = 0
            if oldPos and oldSize: grp.position.y = oldPos.y + oldSize.y
            grp.dragTag = mirrorXY
        elif grp.size.x < 0:
            grp.size.x = 0
            if oldPos and oldSize: grp.position.x = oldPos.x + oldSize.x
            grp.dragTag = mirrorX
        elif self.group.size.y < 0:
            grp.size.y = 0
            if oldPos and oldSize: grp.position.y = oldPos.y + oldSize.y
            grp.dragTag = mirrorY
            
        grp.setSelection()
    
    def destroy(self):
        del self.group

class TLSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.position = wxPoint(position.x, position.y)
        grp.size = wxSize((oldPos.x - position.x) + grp.size.x, 
          (oldPos.y - position.y) + grp.size.y)

        SelectionTag.setPos(self, position, grp.stTR, grp.stBL, grp.stBR, oldPos, oldSize)
        
class TRSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.position = wxPoint(oldPos.x, position.y, )
        grp.size = wxSize(position.x - oldPos.x, (oldPos.y - position.y) + grp.size.y)

        SelectionTag.setPos(self, position, grp.stTL, grp.stBR, grp.stBL, oldPos, oldSize)
        
class BRSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.position = wxPoint(grp.position.x, grp.position.y)
        grp.size = wxSize((position.x - oldPos.x), (position.y - oldPos.y))

        SelectionTag.setPos(self, position, grp.stBL, grp.stTR, grp.stTL, oldPos, oldSize)

class BLSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.position = wxPoint(position.x, oldPos.y)
        grp.size = wxSize((oldPos.x - position.x) + grp.size.x, 
          (position.y - oldPos.y))

        SelectionTag.setPos(self, position, grp.stBR, grp.stTL, grp.stTR, oldPos, oldSize)
        

class TSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.size = wxSize(grp.size.x, (oldPos.y - position.y) + grp.size.y)
        grp.position = wxPoint(grp.position.x, position.y)

        SelectionTag.setPos(self, position, None, grp.stB, None, oldPos, oldSize)

class BSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.size = wxSize(grp.size.x, (position.y - oldPos.y))
        grp.position = wxPoint(grp.position.x, grp.position.y)

        SelectionTag.setPos(self, position, None, grp.stT, None)

class LSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.size = wxSize((oldPos.x - position.x) + grp.size.x, grp.size.y)
        grp.position = wxPoint(position.x, grp.position.y)

        SelectionTag.setPos(self, position, grp.stR, None, None, oldPos, oldSize)

class RSelTag(SelectionTag):
    def setPos(self, position):
        grp = self.group
	oldPos = grp.position
	oldSize = grp.size
        grp.size = wxSize((position.x - oldPos.x), grp.size.y)
        grp.position = wxPoint(grp.position.x, grp.position.y)

        SelectionTag.setPos(self, position, grp.stL, None, None)
        
        
        
        
        
  