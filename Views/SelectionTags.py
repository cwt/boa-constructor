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
# Copyright:   (c) 1999 - 2004 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from wxPython.wx import *

import Preferences, Utils

defPos = (0, 0)
defSze = (0, 0)

dbgInfo = false

def granularise(val, oldVal = None):
    """ Snap value to grid points, including original value as grid point.

        Used by sizing
    """
    gran = Preferences.dsGridSize
    if oldVal is not None:
        # get prior and next grid points
        prior = (oldVal /gran)*gran
        next = prior + gran
        if val >= prior and val < next:
            # Delta values
            dvPrev = abs(val-prior)
            dvOld = abs(val-oldVal)
            dvNext = abs(val-next)
            if dvOld <= dvPrev <= dvNext or dvOld <= dvNext <= dvPrev:
                return oldVal

    return ((val + gran / 2) /gran)*gran

def granulariseMove(val, oldVal):
    """ Snap value to screen gran multiples of oldVal.
        Used by moving
    """
    gran = Preferences.dsGridSize
    return oldVal + int(round((val-oldVal)/float(gran))) * gran


class SelectionGroup:
    """ Group of tags and lines used to show selection, moving and sizing.
    """
    def newLine(self):
        line = wxPanel(self.parent, -1)
        line.SetSize(wxSize(1, 1))
        line.SetBackgroundColour(wxBLACK)
        EVT_MOTION(line, self.OnMouseOver)
        EVT_LEFT_UP(line, self.OnSizeEnd)
        return line

    def __init__(self, parent, inspector, designer, colour, pnlStyle):
        self.designer = designer
        self.inspSel = None
        self.inspector = inspector
        self.parent = parent
        self.selection = None
        self.selCompn = None
        self.dragTag = None
        self.dragging = false
        self.dragOffset = wxPoint()
        self.startPos = None
        self.startSize = None
        self.colour = colour
        self.name = ''

        tagSize = Preferences.dsSelectionTagSize

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

    def destroy(self):
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
        self.stTL.Show(); self.stTR.Show()
        self.stBR.Show(); self.stBL.Show()

        self.stT.Show(); self.stB.Show()
        self.stL.Show(); self.stR.Show()

        self.slL.Hide(); self.slR.Hide()
        self.slB.Hide(); self.slT.Hide()

        for tag in self.tags:
            tag.Refresh()

    def hideTags(self):
        for tag in self.tags:
            tag.Hide()

    def showFramedTags(self, notHide):
        for tag in self.tags:
            tag.Show()

    def reparentTags(self, parent):
        for tag in self.tags:
            tag.Reparent(parent)

    def moveCapture(self, ctrl, compn, pos):
        # Put selection around control

        # Begin a drag, don't drag frame
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

            self.position = wxPoint(parentPos.x - self.dragOffset.x - offsetX,
                                    parentPos.y - self.dragOffset.y - offsetY)
            self.setSelection()

    def moveRelease(self):
        if self.dragTag:
            self.OnSizeEnd()
            self.showTags()

        if self.dragging:
            # XXX Have to hide and show to clean up artifacts, refreshing
            # XXX is not sufficient. Show/hiding seems to screw up Z order
            self.hideTags()
            self.resizeCtrl()

            wxPostEvent(self.selection, wxSizeEvent( self.selection.GetSize() ))

            self.setSelection(finishDragging=true)

            self.initStartVals()

            self.positionUpdate()
            self.showTags()

    def initStartVals(self):
        self.startPos = wxPoint(self.position.x, self.position.y)
        self.startSize = wxSize(self.size.x, self.size.y)

    def selectCtrl(self, ctrl, compn, selectInInspector = true):
        self.hideTags()
        showTags = false
        if not ctrl:
            self.selection = None
            self.selCompn = None
            self.inspSel = None
        else:
            if ctrl.this == self.designer.this:
                self.name = ''
                self.parent = ctrl
                cp = (0, 0)

                screenPos = ctrl.ClientToScreen(cp)
                parentPos = self.parent.ScreenToClient(screenPos)

            else:
                self.name = ctrl.GetName()
                self.parent = ctrl.GetParent()
                cp = ctrl.GetPosition().asTuple()

                showTags = true

            if hasattr(ctrl, 'proxyContainer'):
                self.reparentTags(ctrl)
                self.position = wxPoint(0, 0)
            else:
                self.reparentTags(self.parent)
                self.position = wxPoint(cp[0], cp[1])

            self.size = ctrl.GetSize()

            self.selection = ctrl
            self.selCompn = compn

            self.initStartVals()

            self.updateAnchors()
            self.setSelection()
            
            if showTags:
                self.showTags()
                # callafter ruins dragging
                #wxCallAfter(self.showTags)

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
            currPos, currSize = self.position, self.size
            if self.isProxySelection():
                position = wxPoint(0, 0)
            else:
                position = self.selection.GetPosition()
            size = self.selection.GetSize()
            
            #if (currPos, currSize) != (position, size):
            self.position, self.size = position, size
                
            #    self.sizeUpdate()
            #    self.positionUpdate()

    def setSelection(self, finishDragging=false):
        """ Show selection based on granularised position and size.

            While dragging only lines are updated while tags stay with original
            control position.
        """
        position = self.position
        size = self.size

        sz = self.startSize
        ps = self.startPos

        frmWid = Preferences.dsSelectionFrameWidth
        tagSize = Preferences.dsSelectionTagSize

        offset, extra = divmod(tagSize, 2)
        offsetO = offset + extra
        offsetI = offset

        if not self.dragging:
            # Sizing
            if sz is None and ps is None:
                trPos = wxPoint(granularise(position.x), granularise(position.y))
                trSze = wxSize(granularise(size.x), granularise(size.y))
            else:
                trPos = wxPoint(granularise(position.x, ps.x), granularise(position.y, ps.y))
                trSze = wxSize(granularise(size.x + position.x, sz.x + ps.x) - trPos.x,
                               granularise(size.y + position.y, sz.y + ps.y) - trPos.y)

            self.stTL.SetDimensions(trPos.x -offsetO, trPos.y -offsetO, tagSize, tagSize)
            self.stTR.SetDimensions(trPos.x -offsetI + trSze.x, trPos.y -offsetO, tagSize, tagSize)
            self.stBR.SetDimensions(trPos.x -offsetI + trSze.x, trPos.y -offsetI + trSze.y, tagSize, tagSize)
            self.stBL.SetDimensions(trPos.x -offsetO, trPos.y -offsetI + trSze.y, tagSize, tagSize)

            self.stT.SetDimensions(trPos.x -offsetO + trSze.x/2, trPos.y -offsetO, tagSize, tagSize)
            self.stB.SetDimensions(trPos.x -offsetO + trSze.x/2, trPos.y -offsetI + trSze.y, tagSize, tagSize)
            self.stL.SetDimensions(trPos.x -offsetO, trPos.y -offsetO + trSze.y/2, tagSize, tagSize)
            self.stR.SetDimensions(trPos.x -offsetI +trSze.x, trPos.y -offsetO + trSze.y/2, tagSize, tagSize)

        else:
            # Moving
            if dbgInfo: InspDbgInfo(self.inspector, `position`+':'+`ps`, 1)
            trPos = wxPoint(granulariseMove(position.x, ps.x), 
                            granulariseMove(position.y, ps.y))
            if dbgInfo: InspDbgInfo(self.inspector, `trPos`, 0)
            trSze = wxSize(sz.x, sz.y)

        self.slT.SetDimensions(trPos.x -frmWid, trPos.y -frmWid, trSze.x +frmWid, frmWid)
        self.slR.SetDimensions(trPos.x + trSze.x, trPos.y -frmWid, frmWid, trSze.y+frmWid*2)
        self.slB.SetDimensions(trPos.x -frmWid, trPos.y + trSze.y, trSze.x +frmWid*2, frmWid)
        self.slL.SetDimensions(trPos.x -frmWid, trPos.y-frmWid, frmWid, trSze.y +frmWid)

        if finishDragging:
            self.dragging = false
            self.startPos = trPos
            self.startSize = trSze

            self.stTL.SetDimensions(trPos.x -offsetO, trPos.y -offsetO, tagSize, tagSize)
            self.stTR.SetDimensions(trPos.x -offsetI + trSze.x, trPos.y -offsetO, tagSize, tagSize)
            self.stBR.SetDimensions(trPos.x -offsetI + trSze.x, trPos.y -offsetI + trSze.y, tagSize, tagSize)
            self.stBL.SetDimensions(trPos.x -offsetO, trPos.y -offsetI + trSze.y, tagSize, tagSize)

            self.stT.SetDimensions(trPos.x -offsetO + trSze.x/2, trPos.y -offsetO, tagSize, tagSize)
            self.stB.SetDimensions(trPos.x -offsetO + trSze.x/2, trPos.y -offsetI + trSze.y, tagSize, tagSize)
            self.stL.SetDimensions(trPos.x -offsetO, trPos.y -offsetO + trSze.y/2, tagSize, tagSize)
            self.stR.SetDimensions(trPos.x -offsetI +trSze.x, trPos.y -offsetO + trSze.y/2, tagSize, tagSize)

        self.position  = trPos
        self.size = trSze

    def updateAnchors(self):
        if self.selCompn:
            for idx in range(4):
                if self.selCompn.anchorSettings:
                    self.anchorTags[idx].setAnchor(self.selCompn.anchorSettings[idx])
                else:
                    if not self.anchorTags[idx].setHasSizer(self.selCompn):
                        self.anchorTags[idx].setAnchor(None)

    def isProxySelection(self):
        if self.selection:
            return hasattr(self.selection, 'proxyContainer')
        else:
            return false

class SingleSelectionGroup(SelectionGroup):
    def __init__(self, parent, inspector, designer):
        SelectionGroup.__init__(self, parent, inspector, designer, wxBLACK, 0)

    def selectCtrl(self, ctrl, compn):
        SelectionGroup.selectCtrl(self, ctrl, compn)
        if self.selection:
            self.inspSel = ctrl
            self.inspector.selectObject(compn, sessionHandler=self.designer)

    def updateInspectorPageProps(self, props):
        for page, prop in props:
            if page == 'constr':
                self.inspector.constructorUpdate(prop)
            elif page == 'prop':
                self.inspector.propertyUpdate(prop)

    def positionUpdate(self):
        if self.selCompn:
            self.updateInspectorPageProps(self.selCompn.getPositionDependentProps())

    def sizeUpdate(self):
        if self.selCompn:
            self.updateInspectorPageProps(self.selCompn.getSizeDependentProps())

    # Events
    def OnSizeBegin(self, event):
        self.dragTag = event.GetEventObject()
        self.showFramedTags(self.dragTag)
        self.initStartVals()

    def OnSizeEnd(self, event=None):
        if self.dragging and not self.dragTag:
            self.moveRelease()
        else:
            self.resizeCtrl()
            self.showTags()
            self.dragTag = None
            self.setSelection()

    def OnMouseOver(self, event):
        if event.Dragging():
            pos = event.GetPosition()
            ctrl = event.GetEventObject()
            self.moving(ctrl, pos)
        event.Skip()

class MultiSelectionGroup(SelectionGroup):
    def __init__(self, parent, inspector, designer):
        SelectionGroup.__init__(self, parent, inspector, designer, wxColour(160, 160, 160), wxSIMPLE_BORDER)#wxLIGHT_GREY)

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

    def OnSizeEnd(self, event=None):
        if self.dragging:
            dsgn = self.designer
            for sel in dsgn.multiSelection:
                sel.moveRelease()
            dsgn.mainMultiDrag = None
        if event: event.Skip()

    def OnSizeEnd2(self, event=None):
        self.resizeCtrl()
        self.showTags()
        self.dragTag = None

    def OnMouseOver(self, event):
        if event.Dragging():
            pos = event.GetPosition()
            ctrl = event.GetEventObject()
            dsgn = self.designer
            for sel in dsgn.multiSelection:
                sel.moving(ctrl, pos, dsgn.mainMultiDrag)
        event.Skip()

class SelectionTag(wxPanel):
    toggleAnchors = (0, 0, 0, 0)
    def __init__(self, parent, cursor, tagSize, group, pnlStyle):# = wxSIMPLE_BORDER):
        wxPanel.__init__(self, parent, -1, size = wxSize(tagSize, tagSize), style = pnlStyle)
        self.Hide()
        self.group = group
        self.SetCursor(wxStockCursor(cursor))
        self.selection = None
        self.position = wxSize(0, 0)
        self.setAnchor(None)
        self.hasSizer = false
        self.inSizer = false

        self.wxID_ANCHORED = wxNewId()
        EVT_MENU(self, self.wxID_ANCHORED, self.OnAnchorToggle)

        self.wxID_SIZERED = wxNewId()
        EVT_MENU(self, self.wxID_SIZERED, self.OnSelectSizer)

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
        self.Destroy()

    def setAnchor(self, anchor):
        self.anchored = anchor is not None and anchor
        if anchor is None:
            col = self.group.colour
        elif anchor:
            col = Preferences.dsAnchorEnabledCol
        else:
            col = Preferences.dsAnchorDisabledCol

        self.SetBackgroundColour(col)
        self.Refresh()

    def setHasSizer(self, compn):
        sizer = compn.GetSizer(None)
        self.hasSizer = sizer is not None
        self.inSizer = hasattr(compn.control, '_in_sizer')
        if sizer is None:
            if self.inSizer:
                col = Preferences.dsInSizerCol
                self.inSizer = true
            else:
                col = self.group.colour
        else:
            col = Preferences.dsHasSizerCol

        self.SetBackgroundColour(col)
        self.Refresh()
        
        return self.hasSizer or self.inSizer

    def updateCtrlAnchors(self, anchor):
        self.group.selCompn.updateAnchors(self.toggleAnchors, anchor)
        self.group.selCompn.applyConstraints()
        self.group.updateAnchors()
        self.group.inspector.propertyUpdate('Anchors')

    def OnRightClick(self, event):
        pass

    def OnAnchorToggle(self, event):
        pass

    def OnSelectSizer(self, event):
        pass

class CornerSelTag(SelectionTag):
    pass

class SideSelTag(SelectionTag):
    def OnRightClick(self, event):
        menu = wxMenu()
        try:
            if self.hasSizer or self.inSizer:
                menu.Append(self.wxID_SIZERED, 'Select sizer')
            else:
                menu.Append(self.wxID_ANCHORED, 'Anchored', '', true)
                menu.Check(self.wxID_ANCHORED, self.anchored)
            self.PopupMenu(menu, event.GetPosition())
        finally:
            menu.Destroy()
        #self.group.showTags()

    def OnAnchorToggle(self, event):
        anchor = not event.Checked()
#        anchor = not self.menu.IsChecked(self.wxID_ANCHORED)
        # XXX Test again !!!!
        if wxPlatform == '__WXGTK__':
            anchor = not anchor
        self.updateCtrlAnchors(anchor)

    def OnSelectSizer(self, event):
        # XXX maybe move hasSizer/isSizer logic to WindowDTC ?
        if self.hasSizer:
            inspector = self.group.inspector
            companion = self.group.selCompn
            designer = companion.designer
            if designer.sizersView:
                s = companion.GetSizer(None)
                for objInfo in designer.sizersView.objects.values():
                    if objInfo[1] == s:
                        compn = objInfo[0]
                        designer.sizersView.focus()
                        inspector.selectObject(compn)
                        designer.sizersView.selectCtrls([compn.name])
                        return
                        
        elif self.inSizer:
            inspector = self.group.inspector
            companion = self.group.selCompn
            designer = companion.designer
            if designer.sizersView:
                s = companion.control.GetContainingSizer()#companion.control._in_sizer
                #print s, companion.control.GetContainingSizer()
                for objName, objInfo in designer.sizersView.objects.items():
                    if objInfo[1] == s:
                        compn = objInfo[0]
                        inspector.selectObject(compn)
                        designer.sizersView.focus()
                        nv = inspector.props.getNameValue('Items')
                        if nv: 
                            nv.propEditor.edit(None)
                            collEditor = designer.sizersView.collEditors[(objName, 'Items')]
                            for idx, crt in zip(
                                 range(len(collEditor.companion.textConstrLst)), 
                                 collEditor.companion.textConstrLst):
                                if crt.method == 'AddWindow' and \
                                      crt.params[0] != 'None':
                                    itemWin=Utils.ctrlNameFromSrcRef(crt.params[0])
                                    if itemWin == companion.name:
                                        collEditor.selectObject(idx)
                                        collEditor.frame.selectObject(idx)
                                        return
        else:
            wxLogWarning('Not part of a sizer')

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

def InspDbgInfo(insp, msg, i):
    insp.statusBar.SetStatusText(msg, i)