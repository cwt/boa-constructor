#----------------------------------------------------------------------
# Name:        SelectionTags.py                                        
# Purpose:     Manages the selection tags which are used to control and
#              show selection, multiple selection, sizing, moving and  
#              anchors                                                 
#                                                                      
# Author:      Riaan Booysen                                           
#                                                                      
# Created:     1999                                                    
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen                            
# Licence:     GPL                                                     
#----------------------------------------------------------------------

from wxPython.wx import *
import string, sys, time

defPos = (0, 0)
defSze = (0, 0)
tagSize = 7
frmWid = 2
screenGran = 8
anchorEnabledCol = wxBLUE
anchorDisabledCol = wxColour(40, 100, 110)

def granularise(val, oldVal = None):
    """ Snap value to grid points, including original value as grid point.
    
        Used by sizing
    """
    if oldVal is not None:
        # get prior and next grid points
        prior = (oldVal /screenGran)*screenGran
        next = prior + screenGran
        if val >= prior and val < next:
            # Delta values
            dvPrev = abs(val-prior)
            dvOld = abs(val-oldVal)
            dvNext = abs(val-next)
            if dvOld <= dvPrev <= dvNext or dvOld <= dvNext <= dvPrev:
                return oldVal

    return ((val + screenGran / 2) /screenGran)*screenGran

def granulariseMove(val, oldVal = None):
    """ Snap value to screen gran multiples of oldVal. 
    
        Used by moving
    """
    return oldVal % screenGran + (val /screenGran)*screenGran

class SelectionGroup:
    """ Group of tags and lines used to show selection, moving and sizing. 
    """
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
        self.startPos = None
        self.startSize = None
        self.colour = colour
        self.name = ''
        
        self.position = wxPoint(defPos[0], defPos[1])
        self.size = wxSize(defSze[0], defSze[1])

        self.slT = self.newLine()
        self.slR = self.newLine()
        self.slB = self.newLine()
        self.slL = self.newLine()
        
        # Create selection tags
        self.stTL = TLSelTag(parent, wxCURSOR_SIZENWSE, tagSize, self, pnlStyle)
        self.stTR = TRSelTag(parent, wxCURSOR_SIZENESW, tagSize, self, pnlStyle)
        self.stBR = BRSelTag(parent, wxCURSOR_SIZENWSE, tagSize, self, pnlStyle)
        self.stBL = BLSelTag(parent, wxCURSOR_SIZENESW, tagSize, self, pnlStyle)
        self.stT = TSelTag(parent, wxCURSOR_SIZENS, tagSize, self, pnlStyle)
        self.stB = BSelTag(parent, wxCURSOR_SIZENS, tagSize, self, pnlStyle)
        self.stL = LSelTag(parent, wxCURSOR_SIZEWE, tagSize, self, pnlStyle)
        self.stR = RSelTag(parent, wxCURSOR_SIZEWE, tagSize, self, pnlStyle)

        self.tags = [self.slT, self.slR, self.slB, self.slL,
                     self.stTL, self.stTR, self.stBR, self.stBL,
                     self.stT, self.stB, self.stR, self.stL]
        self.anchorTags = [self.stL, self.stT, self.stR, self.stB]

        for tag in self.tags:
            self.senders.addObject(tag)

    def destroy(self):
#        print 'Destroy selection group', self._cno
#        print 'group ref cnt:', sys.getrefcount(self)
        self.stT.destroy();self.stB.destroy()
        self.stR.destroy();self.stL.destroy()
        
        self.stTL.destroy();self.stTR.destroy()
        self.stBR.destroy();self.stBL.destroy()

        self.slT.Destroy();self.slR.Destroy()
        self.slB.Destroy();self.slL.Destroy()

        del self.tags

        del self.parent
        del self.inspector
        del self.designer
        del self.selection
        del self.inspSel
        
    def assign(self, group):
        self.hideTags()
        
        self.position.x, self.position.y = group.position.x, group.position.y
        self.size.x, self.size.y = group.size.x, group.size.y
        self.selection = group.selection
        self.selCompn = group.selCompn
        self.name = group.name
        self.startPos = group.startPos
        self.startSize = group.startSize
        self.setSelection()
        
        self.reparentTags(group.parent)
        self.updateAnchors()
        self.showTags()

    def showTags(self):
        self.stTL.Show(true); self.stTR.Show(true)
        self.stBR.Show(true); self.stBL.Show(true)

        self.stT.Show(true); self.stB.Show(true)
        self.stL.Show(true); self.stR.Show(true)

        self.slL.Show(false); self.slR.Show(false)
        self.slB.Show(false); self.slT.Show(false)

        map(lambda tag: tag.Refresh(), self.tags)

    def hideTags(self):
        map(lambda tag: tag.Show(false), self.tags)

    def showFramedTags(self, notHide):
        map(lambda tag: tag.Show(true), self.tags)
    
    def reparentTags(self, parent):
        map(lambda tag, newparent = parent: tag.Reparent(newparent), self.tags)

    def moveCapture(self, ctrl, compn, pos):
        # Put selection around control

        # Begin a drag
        # don't drag frame
        if ctrl.this != self.designer.this:
            self.dragging = true
            self.dragOffset = pos
            self.showFramedTags(None)

    def moving(self, ctrl, pos, multiDragCtrl = None):
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
            if ctrl.this == self.designer.this:
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

    def moveRelease(self):
        if self.dragTag:
            # XXX nasty passing a None event
            self.OnSizeEnd(None)
            self.showTags()

        if self.dragging:
            # XXX Have to hide and show to clean up artifacts, refreshing
            # XXX is not sufficient. Show/hiding seems to screw up Z order
            self.selection.Show(false)
            try:
                self.hideTags()
                self.resizeCtrl()
            finally:
                self.selection.Show(true)
                pass

            self.setSelection(finishDragging=true)

            self.initStartVals()

            self.positionUpdate()
            self.showTags()
            #self.sizeFromCtrl()

    def initStartVals(self):
        self.startPos = wxPoint(self.position.x, self.position.y)
        self.startSize = wxSize(self.size.x, self.size.y)
        
    def selectCtrl(self, ctrl, compn, selectInInspector = true):
        self.hideTags()
        if not ctrl:
            self.selection = None
            self.selCompn = None
            self.inspSel = None
        else: 
            if ctrl.this == self.designer.this:
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
            
            self.initStartVals()
                        
            self.updateAnchors()
            self.setSelection()

    def selectNone(self):
        self.hideTags()
        self.inspSel = None
        self.selection = None
        self.selCompn = None

    def resizeCtrl(self):
        """ Set the selected control's dimensions from the current selection 
            group's size & pos 
        """
        if self.selCompn: self.selCompn.beforeResize()

        try:
            self.selection.SetDimensions(self.position.x, self.position.y, 
                                         self.size.x, self.size.y)
        finally:
            if self.selCompn: self.selCompn.afterResize()

    def sizeFromCtrl(self):
        """ Called from outside the module. Set the group's size & pos from
            a control and notifies the Inspector. 
        """
        if self.selection:
            self.position = self.selection.GetPosition()
            self.size = self.selection.GetSize()
            self.sizeUpdate()
            self.positionUpdate()
        
    def setSelection(self, finishDragging=false):
        """ Show selection based on granularised position and size.
        
            While dragging only lines are updated while tags stay with original
            control position.
        """
        position = self.position
        size = self.size

        sz = self.startSize
        ps = self.startPos
        
        if not self.dragging:
            # Sizing
            if sz is None and ps is None:
                trPos = wxPoint(granularise(position.x), granularise(position.y))
                trSze = wxSize(granularise(size.x), granularise(size.y))
            else:
                trPos = wxPoint(granularise(position.x, ps.x), granularise(position.y, ps.y))
                trSze = wxSize(granularise(size.x + position.x, sz.x + ps.x) - trPos.x, 
                               granularise(size.y + position.y, sz.y + ps.y) - trPos.y)

            self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
            self.stTR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -4, tagSize, tagSize)
            self.stBR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
            self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)

            self.stT.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -4, tagSize, tagSize)
            self.stB.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -3 + trSze.y, tagSize, tagSize)
            self.stL.SetDimensions(trPos.x -4, trPos.y -4 + trSze.y/2, tagSize, tagSize)
            self.stR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4 + trSze.y/2, tagSize, tagSize)
 
        else:
            # Moving
            trPos = wxPoint(granulariseMove(position.x, ps.x), granulariseMove(position.y, ps.y))
            trSze = wxSize(sz.x, sz.y)

        self.slT.SetDimensions(trPos.x -frmWid, trPos.y -2, trSze.x +frmWid, frmWid)
        self.slR.SetDimensions(trPos.x + trSze.x, trPos.y -frmWid, frmWid, trSze.y+frmWid*2)
        self.slB.SetDimensions(trPos.x -frmWid, trPos.y + trSze.y, trSze.x +frmWid*2, frmWid)
        self.slL.SetDimensions(trPos.x -2, trPos.y-frmWid, frmWid, trSze.y +frmWid)

        if finishDragging:
            self.dragging = false
            self.startPos = trPos
            self.startSize = trSze

            self.stTL.SetDimensions(trPos.x -4, trPos.y -4, tagSize, tagSize)
            self.stTR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -4, tagSize, tagSize)
            self.stBR.SetDimensions(trPos.x -3 + trSze.x, trPos.y -3 + trSze.y, tagSize, tagSize)
            self.stBL.SetDimensions(trPos.x -4, trPos.y -3 + trSze.y, tagSize, tagSize)

            self.stT.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -4, tagSize, tagSize)
            self.stB.SetDimensions(trPos.x -4 + trSze.x/2, trPos.y -3 + trSze.y, tagSize, tagSize)
            self.stL.SetDimensions(trPos.x -4, trPos.y -4 + trSze.y/2, tagSize, tagSize)
            self.stR.SetDimensions(trPos.x -3 +trSze.x, trPos.y -4 + trSze.y/2, tagSize, tagSize)

        self.position  = trPos
        self.size = trSze

    def updateAnchors(self):
        if self.selCompn:
            for idx in range(4):
                if self.selCompn.anchorSettings:
                    self.anchorTags[idx].setAnchor(self.selCompn.anchorSettings[idx])
                else:
                    self.anchorTags[idx].setAnchor(None)
        
class SingleSelectionGroup(SelectionGroup):
    def __init__(self, parent, senders, inspector, designer):
        SelectionGroup.__init__(self, parent, senders, inspector, designer, wxBLACK, 0)

    def selectCtrl(self, ctrl, compn):
        SelectionGroup.selectCtrl(self, ctrl, compn)
        if self.selection:
            self.inspSel = ctrl	
            self.inspector.selectObject(compn)

    def positionUpdate(self):    
        self.inspector.constructorUpdate('Position')
    def sizeUpdate(self):    
        self.inspector.constructorUpdate('Size')
        self.inspector.propertyUpdate('ClientSize')

    # Events
    def OnSizeBegin(self, event):
        self.dragTag = self.senders.getObject(event)
        self.showFramedTags(self.dragTag)
        self.initStartVals()
        
    def OnSizeEnd(self, event):
        if self.dragging:
            self.moveRelease()
        else:
            self.resizeCtrl()
            self.showTags()
            self.dragTag = None
            self.setSelection()

    def OnMouseOver(self, event):
        if event.Dragging():
            pos = event.GetPosition()
            ctrl = self.senders.getObject(event)
            self.moving(ctrl, pos)
        event.Skip()

class MultiSelectionGroup(SelectionGroup): 
    def __init__(self, parent, senders, inspector, designer):
        SelectionGroup.__init__(self, parent, senders, inspector, designer, wxColour(160, 160, 160), wxSIMPLE_BORDER)#wxLIGHT_GREY)

    def selectCtrl(self, ctrl, compn):
        SelectionGroup.selectCtrl(self, ctrl, compn)
        self.inspSel = None
        self.inspector.cleanup()    
        self.inspector.multiSelectObject(None, self.designer)

    def positionUpdate(self):    
        self.inspector.directPositionUpdate(self.selCompn)
    def sizeUpdate(self):    
        self.inspector.directSizeUpdate(self.selCompn)

    # Events
    def OnSizeBegin(self, event):
        event.Skip()

    def OnSizeEnd(self, event):
        if self.dragging:
            dsgn = self.designer
            for sel in dsgn.multiSelection:
                sel.moveRelease()
            dsgn.mainMultiDrag = None
        event.Skip()

    def OnSizeEnd2(self, event):
        self.resizeCtrl()
        self.showTags()
        self.dragTag = None

    def OnMouseOver(self, event):
        if event.Dragging():
            pos = event.GetPosition()
            ctrl = self.senders.getObject(event)
            dsgn = self.designer
            for sel in dsgn.multiSelection:
                sel.moving(ctrl, pos, dsgn.mainMultiDrag)
        event.Skip()

class SelectionTag(wxPanel):
    toggleAnchors = (0, 0, 0, 0)
    def __init__(self, parent, cursor, tagSize, group, pnlStyle):# = wxSIMPLE_BORDER):
        wxPanel.__init__(self, parent, -1, size = wxSize(tagSize, tagSize), style = pnlStyle)
        self.Show(false)
        self.group = group
        self.SetCursor(wxStockCursor(cursor))
        self.selection = None
        self.position = wxSize(0, 0)
        self.setAnchor(None)
        self.menu = wxMenu()

        self.wxID_ANCHORED = wxNewId()
        self.menu.Append(self.wxID_ANCHORED, 'Anchored', checkable = true)
        EVT_MENU(self.menu, self.wxID_ANCHORED, self.OnAnchorToggle)

        EVT_LEFT_DOWN(self, group.OnSizeBegin)
        EVT_LEFT_UP(self, group.OnSizeEnd)
        EVT_MOTION(self, group.OnMouseOver)
        EVT_RIGHT_UP(self, self.OnRightClick)
    
    def doFlip(self, grpPos, grpSize, oldPos, oldSize, startPos, startSize):
        grpSize = abs(grpSize)
        # flipping from right to left
        if oldPos == grpPos: 
            grpPos = oldPos - grpSize
            startPos = startPos - startSize
        # left to right
        else: 
            grpPos = oldPos + oldSize
            startPos = startPos + startSize
        
        return grpPos, grpSize, startPos
        
    def setPos(self, position, mirrorX, mirrorY, mirrorXY, oldPos = None, oldSize = None):
        grp = self.group
        # Handle cases where the selection has flipped over
        # horizontally or vertically or both
        if grp.size.x < 0 and grp.size.y < 0:
            mirrorX = mirrorY = mirrorXY
            
        if grp.size.x < 0:
            grp.position.x, grp.size.x, grp.startPos.x  = \
                  self.doFlip(grp.position.x, grp.size.x, oldPos.x, oldSize.x, 
                              grp.startPos.x, grp.startSize.x)

            grp.dragTag = mirrorX
            
        if self.group.size.y < 0:
            grp.position.y, grp.size.y, grp.startPos.y = \
                  self.doFlip(grp.position.y, grp.size.y, oldPos.y, oldSize.y, 
                              grp.startPos.y, grp.startSize.y)

            grp.dragTag = mirrorY            
            
        grp.setSelection()
    
    def destroy(self):
        del self.group
        self.menu.Destroy()
        self.Destroy()
    
    def setAnchor(self, anchor):
        self.anchored = anchor is not None and anchor
        if anchor is None: 
            col = self.group.colour
        elif anchor:
            col = anchorEnabledCol
        else: 
            col = anchorDisabledCol
            
        self.SetBackgroundColour(col)
        self.Refresh()
    
    def updateCtrlAnchors(self, anchor):
        self.group.selCompn.updateAnchors(self.toggleAnchors, anchor)
        self.group.selCompn.applyConstraints()
        self.group.updateAnchors()
        self.group.inspector.propertyUpdate('Anchors')
        
    def OnRightClick(self, event):
        pass
            
    def OnAnchorToggle(self, event):
        pass

class CornerSelTag(SelectionTag):
    pass
    
class SideSelTag(SelectionTag):
    def OnRightClick(self, event):
        self.menu.Check(self.wxID_ANCHORED, self.anchored)
        self.PopupMenu(self.menu, event.GetPosition())
    
    def OnAnchorToggle(self, event):
        self.updateCtrlAnchors(not self.menu.IsChecked(self.wxID_ANCHORED))

class TLSelTag(CornerSelTag):
    name = 'top left'
    toggleAnchors = (1, 1, 0, 0)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.position = wxPoint(position.x, position.y)
        grp.size = wxSize((oldPos.x - position.x) + grp.size.x, 
          (oldPos.y - position.y) + grp.size.y)

        SelectionTag.setPos(self, position, grp.stTR, grp.stBL, grp.stBR, oldPos, oldSize)
        
class TRSelTag(CornerSelTag):
    name = 'top right'
    toggleAnchors = (0, 1, 1, 0)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.position = wxPoint(oldPos.x, position.y, )
        grp.size = wxSize(position.x - oldPos.x, (oldPos.y - position.y) + grp.size.y)

        SelectionTag.setPos(self, position, grp.stTL, grp.stBR, grp.stBL, oldPos, oldSize)
        
class BRSelTag(CornerSelTag):
    name = 'bottom right'
    toggleAnchors = (0, 0, 1, 1)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.position = wxPoint(grp.position.x, grp.position.y)
        grp.size = wxSize((position.x - oldPos.x), (position.y - oldPos.y))

        SelectionTag.setPos(self, position, grp.stBL, grp.stTR, grp.stTL, oldPos, oldSize)

class BLSelTag(CornerSelTag):
    name = 'bottom left'
    toggleAnchors = (1, 0, 0, 1)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.position = wxPoint(position.x, oldPos.y)
        grp.size = wxSize((oldPos.x - position.x) + grp.size.x, 
          (position.y - oldPos.y))

        SelectionTag.setPos(self, position, grp.stBR, grp.stTL, grp.stTR, oldPos, oldSize)
        
class LSelTag(SideSelTag):
    name = 'left'
    toggleAnchors = (1, 0, 0, 0)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.size = wxSize((oldPos.x - position.x) + grp.size.x, grp.size.y)
        grp.position = wxPoint(position.x, grp.position.y)

        SelectionTag.setPos(self, position, grp.stR, None, None, oldPos, oldSize)

class TSelTag(SideSelTag):
    name = 'top'
    toggleAnchors = (0, 1, 0, 0)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.size = wxSize(grp.size.x, (oldPos.y - position.y) + grp.size.y)
        grp.position = wxPoint(grp.position.x, position.y)

        SelectionTag.setPos(self, position, None, grp.stB, None, oldPos, oldSize)

class RSelTag(SideSelTag):
    name = 'right'
    toggleAnchors = (0, 0, 1, 0)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.size = wxSize((position.x - oldPos.x), grp.size.y)
        grp.position = wxPoint(grp.position.x, grp.position.y)

        SelectionTag.setPos(self, position, grp.stL, None, None, oldPos, oldSize)

class BSelTag(SideSelTag):
    name = 'bottom'
    toggleAnchors = (0, 0, 0, 1)
    def setPos(self, position):
        grp = self.group
        oldPos = grp.position
        oldSize = grp.size
        grp.size = wxSize(grp.size.x, (position.y - oldPos.y))
        grp.position = wxPoint(grp.position.x, grp.position.y)

        SelectionTag.setPos(self, position, None, grp.stT, None, oldPos, oldSize)

