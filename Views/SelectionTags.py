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
import string, sys
import sender

# XXX Fix granularise to not use a grid in screen coordinated but rather a 
# XXX grid in client coordinates

defPos = (0, 0)
defSze = (0, 0)
tagSize = 7
frmWid = 2
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
        
    def __init__(self, parent, senders, inspector, designer, colour, pnlStyle):
        self.designer = designer
        self.inspSel = None
        self.inspector = inspector
        self.parent = parent
        self.senders = senders
        self.selection = None
        self.selCompn = None
        self.dragTag = None
        self.dragging = false
        self.dragOffset = wxPoint()
        self.colour = colour
        self.name = ''
#        self.pnlStyle = pnlStyle
        
        self.position = wxPoint(defPos[0], defPos[1])
        self.size = wxSize(defSze[0], defSze[1])

##        self.lastPosAndSize = self.position, self.size

        self.sfT = self.newLine()
        self.sfR = self.newLine()
        self.sfB = self.newLine()
        self.sfL = self.newLine()
        
        # Create selection tags
        self.stTL = TLSelTag(parent, wxCURSOR_SIZENWSE, tagSize, self, pnlStyle)
        self.stTR = TRSelTag(parent, wxCURSOR_SIZENESW, tagSize, self, pnlStyle)
        self.stBR = BRSelTag(parent, wxCURSOR_SIZENWSE, tagSize, self, pnlStyle)
        self.stBL = BLSelTag(parent, wxCURSOR_SIZENESW, tagSize, self, pnlStyle)
        self.stT = TSelTag(parent, wxCURSOR_SIZENS, tagSize, self, pnlStyle)
        self.stB = BSelTag(parent, wxCURSOR_SIZENS, tagSize, self, pnlStyle)
        self.stL = LSelTag(parent, wxCURSOR_SIZEWE, tagSize, self, pnlStyle)
        self.stR = RSelTag(parent, wxCURSOR_SIZEWE, tagSize, self, pnlStyle)

        self.tags = [self.sfT, self.sfR, self.sfB, self.sfL,
        	     self.stTL, self.stTR, self.stBR, self.stBL,
        	     self.stT, self.stB, self.stR, self.stL]

        for tag in self.tags:
            self.senders.addObject(tag)

    def destroy(self):
#        print 'group ref cnt:', sys.getrefcount(self)
        self.stT.destroy()
        self.stB.destroy()
        self.stR.destroy()
        self.stL.destroy()
        
        self.stTL.destroy()
        self.stTR.destroy()
        self.stBR.destroy()
        self.stBL.destroy()

        self.sfT.Destroy()
        self.sfR.Destroy()
        self.sfB.Destroy()
        self.sfL.Destroy()

        del self.tags

        del self.parent
        del self.inspector
        del self.designer
        del self.selection
        del self.inspSel
        
    def __del__(self):
        print '__del__ selection group'
        
    def assign(self, group):
        self.hideTags()
        
        self.position.x, self.position.y = group.position.x, group.position.y
        self.size.x, self.size.y = group.size.x, group.size.y
        self.selection = group.selection
        self.selCompn = group.selCompn
        self.name = group.name
        self.setSelection()
        
        self.reparentTags(group.parent)
        self.showTags()

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

        if self.dragging:
            # XXX Have to hide and show to clean up artifacts, refreshing
            # XXX is not sufficient. Show/hiding seems to screw up Z order
	    self.selection.Show(false)
	    self.hideTags()

            self.selection.SetDimensions( \
              granularise(self.position.x), granularise(self.position.y), 
              granularise(self.size.x -1), granularise(self.size.y -1))

            self.selection.Show(true)
#	    self.showTags()

            self.dragging = false
            self.setSelection()
	    self.showTags()
	    self.positionUpdate()

    def moveCapture(self, ctrl, compn, pos):
        # Put selection around control

        # Begin a drag
        # don't drag frame
        if ctrl != self.designer:
	    self.dragging = true
            self.dragOffset = pos
            self.showFramedTags(None)
	
    def moving(self, ctrl, pos, multiDragCtrl = None):#, relCtrl = None):
        # Calculate relative position if it is a multiple selection drag
        if multiDragCtrl:
            dragCtrlPos = multiDragCtrl.GetPosition()
            movingCtrlPos = self.selection.GetPosition()
            pos = wxPoint(pos.x - dragCtrlPos.x + movingCtrlPos.x, 
                          pos.y - dragCtrlPos.y + movingCtrlPos.y)

        screenPos = ctrl.ClientToScreen(pos)
        parentPos = self.parent.ScreenToClient(screenPos)
        # Sizing
        if self.dragTag:
            if ctrl == self.designer:
                tb = self.designer.GetToolBar()
                if tb:
                    parentPos.y = parentPos.y - tb.GetSize().y
    	    self.dragTag.setPos(parentPos)
    	# Moving
    	elif self.dragging:
            # Calculate an offset that is the difference between the 
            # client size and the control size. Comes into play because
            # dragging is relative to the dragging start point (dragOffset)
            dcs = self.parent.ClientToScreen(self.selection.GetPosition())
            dccs = self.selection.ClientToScreen((0, 0))
            
            offsetX = dccs.x - dcs.x
            offsetY = dccs.y - dcs.y

            # Check if toolbar is connected to frame
            if ctrl == self.designer:
                tb = self.designer.GetToolBar()
                if tb:
                    offsetY = offsetY + tb.GetSize().y
                    
            self.position = wxPoint(parentPos.x - self.dragOffset.x - offsetX, 
    	                            parentPos.y - self.dragOffset.y - offsetY)
            self.setSelection()

    def selectCtrl(self, ctrl, compn, selectInInspector = true):
        self.hideTags()
        if not ctrl:
            self.selection = None
            self.selCompn = None
            self.inspSel = None
        else: 
            # XXX fix!
            if ctrl == self.designer:
                self.name = ''
                self.parent = ctrl
                cp = wxPoint(0, 0)
                
                screenPos = ctrl.ClientToScreen(cp)
                parentPos = self.parent.ScreenToClient(screenPos)
                
            else:
                self.name = ctrl.GetName()
                self.parent = ctrl.GetParent()
                cp = ctrl.GetPosition()

                self.showTags()

            self.reparentTags(self.parent)

            self.position = wxPoint(cp.x, cp.y)
            self.size = ctrl.GetSize()
          
            self.selection = ctrl
            self.selCompn = compn

            self.setSelection()

    def selectNone(self):
        self.hideTags()
        self.inspSel = None
        self.selection = None
        self.selCompn = None

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
            self.sizeUpdate()
            self.positionUpdate()
        
    def setSelection(self):
        position = self.position
        size = self.size

        trPos = wxPoint(granularise(position.x), granularise(position.y))
        trSze = wxSize(granularise(size.x -1), granularise(size.y -1))
        
##        lps = self.lastPosAndSize
##        change = (trPos.x, trPos.y, trSze.x, trSze.y) == \
##                 (lps[0].x, lps[0].y, lps[1].x, lps[1].y)
##
##        if change:
##            self.hideTags()

        self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
        self.stTR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -4, tagSize, tagSize)
        self.stBR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)

        self.stT.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -4, tagSize, tagSize)
        self.stB.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stL.SetDimensions(trPos.x -4, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        self.stR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        
##        self.sfT.SetDimensions(trPos.x +3, trPos.y -2, trSze.x - 2*3, frmWid)
##        self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y +3, frmWid, trSze.y - 2*3)
##        self.sfB.SetDimensions(trPos.x +3, trPos.y + trSze.y, trSze.x - 2*3, frmWid)
##        self.sfL.SetDimensions(trPos.x -2, trPos.y +3, frmWid, trSze.y - 2*3)

        self.sfT.SetDimensions(trPos.x -frmWid, trPos.y -2, trSze.x +frmWid, frmWid)
        self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y -frmWid, frmWid, trSze.y+frmWid)
        self.sfB.SetDimensions(trPos.x -frmWid, trPos.y + trSze.y, trSze.x +frmWid, frmWid)
        self.sfL.SetDimensions(trPos.x -2, trPos.y-frmWid, frmWid, trSze.y +frmWid)
	
        self.position  = trPos
        self.size = trSze

##        if change:
##            self.showTags()
##
##        self.lastPosAndSize = trPos, trSze
        
    def OnMouseOver(self, event):
        if event.Dragging():
     	    pos = event.GetPosition()
     	    ctrl = self.senders.getObject(event)
            self.moving(ctrl, pos)
        event.Skip()

class SingleSelectionGroup(SelectionGroup):
    def __init__(self, parent, senders, inspector, designer):
        SelectionGroup.__init__(self, parent, senders, inspector, designer, wxBLACK, 0)

    def selectCtrl(self, ctrl, compn):
        SelectionGroup.selectCtrl(self, ctrl, compn)
        if self.selection:
            self.inspSel = ctrl	
            self.inspector.selectObject(compn)

    def setSelection(self):
        position = self.position
        size = self.size

        trPos = wxPoint(granularise(position.x), granularise(position.y))
        trSze = wxSize(granularise(size.x -1), granularise(size.y -1))
        
##        lps = self.lastPosAndSize
##        change = (trPos.x, trPos.y, trSze.x, trSze.y) == \
##                 (lps[0].x, lps[0].y, lps[1].x, lps[1].y)
##
##        if change:
##            self.hideTags()

        self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
        self.stTR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -4, tagSize, tagSize)
        self.stBR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)

        self.stT.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -4, tagSize, tagSize)
        self.stB.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stL.SetDimensions(trPos.x -4, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        self.stR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        
##        self.sfT.SetDimensions(trPos.x +3, trPos.y -2, trSze.x - 2*3, frmWid)
##        self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y +3, frmWid, trSze.y - 2*3)
##        self.sfB.SetDimensions(trPos.x +3, trPos.y + trSze.y, trSze.x - 2*3, frmWid)
##        self.sfL.SetDimensions(trPos.x -2, trPos.y +3, frmWid, trSze.y - 2*3)

        self.sfT.SetDimensions(trPos.x -frmWid, trPos.y -2, trSze.x +frmWid, frmWid)
        self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y -frmWid, frmWid, trSze.y+frmWid*2)
        self.sfB.SetDimensions(trPos.x -frmWid, trPos.y + trSze.y, trSze.x +frmWid*2, frmWid)
        self.sfL.SetDimensions(trPos.x -2, trPos.y-frmWid, frmWid, trSze.y +frmWid)
	
        self.position  = trPos
        self.size = trSze
    
    def positionUpdate(self):    
        self.inspector.constructorUpdate('Position')
    def sizeUpdate(self):    
        self.inspector.constructorUpdate('Size')
        self.inspector.propertyUpdate('ClientSize')

    # Events
    def OnSizeBegin(self, event):
        self.dragTag = self.senders.getObject(event)
        self.showFramedTags(self.dragTag)

    def OnSizeEnd(self, event):
        self.resizeCtrl()
        self.showTags()
        self.dragTag = None

class MultiSelectionGroup(SelectionGroup): 
    def __init__(self, parent, senders, inspector, designer):
        SelectionGroup.__init__(self, parent, senders, inspector, designer, wxColour(160, 160, 160), wxSIMPLE_BORDER)#wxLIGHT_GREY)

    def selectCtrl(self, ctrl, compn):
        print 'MultiSelectionGroup.selectCtrl'
        SelectionGroup.selectCtrl(self, ctrl, compn)
        self.inspSel = None
        self.inspector.cleanup()    
        self.inspector.multiSelectObject(None, self.designer)

    def setSelection(self):
        position = self.position
        size = self.size

        trPos = wxPoint(granularise(position.x), granularise(position.y))
        trSze = wxSize(granularise(size.x -1), granularise(size.y -1))
        
##        lps = self.lastPosAndSize
##        change = (trPos.x, trPos.y, trSze.x, trSze.y) == \
##                 (lps[0].x, lps[0].y, lps[1].x, lps[1].y)
##
##        if change:
##            self.hideTags()

        if not self.dragging:
            self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
            self.stTR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -4, tagSize, tagSize)
            self.stBR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
            self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)
    
            self.stT.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -4, tagSize, tagSize)
            self.stB.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -3 + trSze.y, tagSize, tagSize)
            self.stL.SetDimensions(trPos.x -4, trPos.y -4 + trSze.y/2, tagSize, tagSize)
            self.stR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4 + trSze.y/2, tagSize, tagSize)
        
##        self.sfT.SetDimensions(trPos.x +3, trPos.y -2, trSze.x - 2*3, frmWid)
##        self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y +3, frmWid, trSze.y - 2*3)
##        self.sfB.SetDimensions(trPos.x +3, trPos.y + trSze.y, trSze.x - 2*3, frmWid)
##        self.sfL.SetDimensions(trPos.x -2, trPos.y +3, frmWid, trSze.y - 2*3)

        self.sfT.SetDimensions(trPos.x -frmWid, trPos.y -2, trSze.x +frmWid, frmWid)
        self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y -frmWid, frmWid, trSze.y+frmWid*2)
        self.sfB.SetDimensions(trPos.x -frmWid, trPos.y + trSze.y, trSze.x +frmWid*2, frmWid)
        self.sfL.SetDimensions(trPos.x -2, trPos.y-frmWid, frmWid, trSze.y +frmWid)
	
        self.position  = trPos
        self.size = trSze

    def positionUpdate(self):    
        self.inspector.directPositionUpdate(self.selCompn)
    def sizeUpdate(self):    
        self.inspector.directSizeUpdate(self.selCompn)

    # Events
    def OnSizeBegin(self, event):
        event.Skip()

    def OnSizeEnd(self, event):
        event.Skip()

    def OnSizeEnd2(self, event):
        self.resizeCtrl()
        self.showTags()
        self.dragTag = None

class SelectionTag(wxPanel):
    def __init__(self, parent, cursor, tagSize, group, pnlStyle):# = wxSIMPLE_BORDER):
        wxPanel.__init__(self, parent, -1, size = wxSize(tagSize, tagSize), style = pnlStyle)
        self.Show(false)
        self.group = group
        self.SetBackgroundColour(group.colour)
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
            grp.size.x, grp.size.y = 0
            if oldPos and oldSize: 
                grp.position.x = oldPos.x + oldSize.x
                grp.position.y = oldPos.y + oldSize.y
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
        self.Destroy()

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
        
        
        
        
        
  