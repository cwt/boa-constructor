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
frmWid = 2
screenGran = 4

def granularise(val):
    return ((val + screenGran / 2) /screenGran)*screenGran


# XXX Add 4 more sizers n, s, e, w
# XXX This module needs a bit of rework and some doc strings, interfaces are
# XXX too vauge.
class SelectionGroup:
    def newBlock(self):
        block = wxPanel(self.parent, -1)
        block.SetSize(wxSize(1, 1))
        block.SetBackgroundColour(wxBLACK)
        self.senders.addObject(block)
        EVT_MOTION(block, self.OnMouseOver)
        return block
        
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

        self.sfT = self.newBlock()
        self.sfR = self.newBlock()
        self.sfB = self.newBlock()
        self.sfL = self.newBlock()
        
        # Create selection tags
        self.stTL = TLSelTag(parent, wxPoint(defPos[0], defPos[1]), wxCURSOR_SIZENWSE, 
          (-1, -1), tagSize, self.OnSizeBegin, self.OnSizeEnd, self.OnMouseOver, self)
        self.senders.addObject(self.stTL)

        self.stTR = TRSelTag(parent, wxPoint(defPos[0] + defSze[0], defPos[1]), wxCURSOR_SIZENESW, 
          (1, -1), tagSize, self.OnSizeBegin, self.OnSizeEnd, self.OnMouseOver, self)
        self.senders.addObject(self.stTR)

        self.stBR = BRSelTag(parent, wxPoint(defPos[0] + defSze[0], defPos[1] + defSze[1]), wxCURSOR_SIZENWSE, 
          (1, 1), tagSize, self.OnSizeBegin, self.OnSizeEnd, self.OnMouseOver, self)
        self.senders.addObject(self.stBR)

        self.stBL = BLSelTag(parent, wxPoint(defPos[0], defPos[1] + defSze[1]), wxCURSOR_SIZENESW, 
          (-1, 1), tagSize, self.OnSizeBegin, self.OnSizeEnd, self.OnMouseOver, self)
        self.senders.addObject(self.stBL)
        
        self.tags = [self.sfT, self.sfR, self.sfB, self.sfL, 
        	     self.stTL, self.stTR, self.stBR, self.stBL]

    def destroy(self):
##        print 'selection tag destroy', self.tags
##        map(lambda tag: tag.destroy(), self.tags)
##        print self.stBR.__class__.__bases__[0].__dict__
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
        print 'move release', self.selection
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
              granularise(self.size.x), granularise(self.size.y))

            self.dragCtrl.Show(true)

##            self.dragCtrl.Refresh()
	    self.dragCtrl = None
	    self.showTags()
            self.inspector.constructorUpdate('Position')

    def moveCapture(self, ctrl, compn, pos):
##        print 'move capture'
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
##        print '### moving,', pos, ctrl.ClientToScreen(pos)
        # Sizing
        if self.dragTag:
     	    screenPos = ctrl.ClientToScreen(pos)
     	    parentPos = self.parent.ScreenToClient(screenPos)
    	    self.dragTag.setPos(parentPos)
    	# Moving
    	elif self.dragCtrl:
##     	    print ctrl, ctrl.ClientToScreen(pos), self.dragCtrl.ClientToScreen(pos)

            self.lastDragPos.x = pos.x
            self.lastDragPos.y = pos.y
     	    screenPos = ctrl.ClientToScreen(pos)
     	    parentPos = self.parent.ScreenToClient(screenPos)
##     	    print self.parent.ClientToScreen(parentPos)

            # Calculate an offset that is the difference between the 
            # client size and the control size. Comes into play because
            # dragging is relative to the dragging start point (dragOffset)
            dcs = self.parent.ClientToScreen(self.dragCtrl.GetPosition())
            dccs = self.dragCtrl.ClientToScreen((0, 0))
            
            offsetX = dccs.x - dcs.x
            offsetY = dccs.y - dcs.y

##     	    print 'dragOffset2:', self.dragOffset.x, self.dragOffset.y, offsetX, offsetY, pos, screenPos, parentPos
	    
            self.position = wxPoint(parentPos.x - self.dragOffset.x - offsetX, 
    	                            parentPos.y - self.dragOffset.y - offsetY)

	    self.setSelection()
  
    def selectCtrl(self, ctrl, compn):
##        print 'select ctrl'
        
        self.hideTags()
        if not ctrl:
            self.selection = None
            self.inspSel = None
        else: 
            # XXX fix!
            if ctrl == self.designer:
##                print '@@@selectCtrl designer' 
                self.parent = ctrl
                cp = wxPoint(0, 0)
                
                screenPos = ctrl.ClientToScreen(cp)
                parentPos = self.parent.ScreenToClient(screenPos)
##                print parentPos
                
            else:
                self.parent = ctrl.GetParent()
                cp = ctrl.GetPosition()
##                print '@@@selectCtrl', cp 

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
##        print 'resize ctrl'
##        self.selection.Show(false)
        self.selection.SetDimensions( \
          granularise(self.position.x), granularise(self.position.y), 
          granularise(self.size.x), granularise(self.size.y))
##        self.selection.Show(true)

    def sizeFromCtrl(self):
        """ Called from outside the module. Set the group's size & pos from
            a control and notifies the Inspector. """
##        print 'size from ctrl'
        # XXX What about granularity?
        if self.selection:
            self.position = self.selection.GetPosition()
            self.size = self.selection.GetSize()
            self.inspector.constructorUpdate('Size')
            self.inspector.propertyUpdate('ClientSize')
##        print self.position, self.size
        
    def setSelection(self):
        position = self.position
        size = self.size
##        print 'set selection', position, size

        trPos = wxPoint(granularise(position.x), granularise(position.y))
        trSze = wxSize(granularise(size.x), granularise(size.y))

        self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
        self.stTR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4, tagSize, tagSize)
        self.stBR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
        self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)
        
        self.sfT.SetDimensions(trPos.x + 3, trPos.y -2, trSze.x - 2*3, frmWid)
	self.sfR.SetDimensions(trPos.x + trSze.x, trPos.y + 3, frmWid, trSze.y - 2*3)
	self.sfB.SetDimensions(trPos.x +3, trPos.y + trSze.y, trSze.x - 2*3, frmWid)
	self.sfL.SetDimensions(trPos.x -2, trPos.y + 3, frmWid, trSze.y - 2*3)
        
    # Events
    def OnSizeBegin(self, event):
##        print 'On size begin'
        self.dragTag = self.senders.getObject(event)
        self.showFramedTags(self.dragTag)

    def OnSizeEnd(self, event):
##        print 'On size end'
        self.resizeCtrl()
#        self.selectCtrl(self.selection)
        self.showTags()
        self.dragTag = None

    def OnMouseOver(self, event):
##        print '### On move over'
        if event.Dragging():
     	    pos = event.GetPosition()
     	    ctrl = self.senders.getObject(event)
            self.moving(ctrl, pos)
	event.Skip()

# XXX Use wxSIMPLE_BORDER/wxColour(128, 128, 128) for multiple selects
class SelectionTag(wxPanel):
    def __init__(self, parent, position, cursor, offset, size, funcDown, funcUp, funcDrag, group, pnlStyle = 0):
        wxPanel.__init__(self, parent, -1, style = pnlStyle)
        self.group = group
        self.SetSize(wxSize(size, size))
        self.SetBackgroundColour(wxBLACK)
        self.SetForegroundColour(wxBLACK)
        self.SetCursor(wxStockCursor(cursor))
        self.selection = None
        self.offset = offset
	self.position = position

	EVT_LEFT_DOWN(self, funcDown)
	EVT_LEFT_UP(self, funcUp)
	EVT_MOTION(self, funcDrag)

    def setPos(self, position):
        pass
    
    def destroy(self):
        del self.group

class TLSelTag(SelectionTag):
    def setPos(self, position):
	oldPos = self.group.position
        self.group.position = position
        self.group.size = wxSize((oldPos.x - position.x) + self.group.size.x, (oldPos.y - position.y) + self.group.size.y)
        self.group.setSelection()
        
class TRSelTag(SelectionTag):
    def setPos(self, position):
	oldPos = self.group.position
        self.group.position = wxPoint(oldPos.x, position.y)
        self.group.size = wxSize((position.x - oldPos.x), (oldPos.y - position.y) + self.group.size.y)
        self.group.setSelection()
        
class BRSelTag(SelectionTag):
    def setPos(self, position):
	oldPos = self.group.position
        self.group.size = wxSize((position.x - oldPos.x), (position.y - oldPos.y))
        self.group.setSelection()

class BLSelTag(SelectionTag):
    def setPos(self, position):
	oldPos = self.group.position
        self.group.position = wxPoint(position.x, oldPos.y)
        self.group.size = wxSize((oldPos.x - position.x) + self.group.size.x, (position.y - oldPos.y))
        self.group.setSelection()
        
        
        
        
        
        
  