import wx

class CaptionedCtrlMixin:
    """ Mixin to attach a caption to a control
    
    The caption can be aligned to the top or left of the text control
    """
    def __init__(self, parent, caption):
        self.StaticText = wx.StaticText(parent, -1, caption)
        self._captionAlignment = wx.TOP
        self._captionOffset = wx.Point(0, 0)
        self.updateStaticTextPos()

        self.PushEventHandler(_PosEvtHandler(self))
        
    
    def updateStaticTextPos(self):
        pos = self.GetPosition()
        offset = self._captionOffset
        if self.StaticText:
            if self._captionAlignment == wx.TOP:
                self.StaticText.SetPosition(\
                      (pos.x + offset.x, 
                       offset.y + pos.y - self.StaticText.GetSize().y-5) )
            elif self._captionAlignment == wx.LEFT:
                self.StaticText.SetPosition(\
                      (offset.x + pos.x - self.StaticText.GetSize().x -5, 
                       offset.y + pos.y) )
        self.StaticText.Refresh(1)
    
    def Destroy(self):
        self.PopEventHandler(1)

        self.StaticText.Destroy()
        self.StaticText = None
    
#---Properties------------------------------------------------------------------
    def GetCaption(self):
        return self.StaticText.GetLabel()
    
    def SetCaption(self, caption):
        self.StaticText.SetLabel(caption)
        self.updateStaticTextPos()
    
    def GetCaptionAlignment(self):
        return self._captionAlignment
        
    def SetCaptionAlignment(self, align):
        if align not in (wx.LEFT, wx.TOP):
            raise 'Unsupported alignment'
        self._captionAlignment = align
        self.updateStaticTextPos()

    def GetCaptionOffset(self):
        return self._captionOffset

    def SetCaptionOffset(self, offset):
        self._captionOffset = offset
        self.updateStaticTextPos()

class StaticTextCtrl(wx.TextCtrl, CaptionedCtrlMixin):
    """ Text Control with attached Static Text caption
    
    The caption can be aligned to the top or left of the text control
    """
    def __init__(self, parent, id, value = '', caption = '', 
              pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0, 
              validator = wx.DefaultValidator, name = 'text'):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style, 
              validator, name)
        CaptionedCtrlMixin.__init__(self, parent, caption)

    def Destroy(self):
        CaptionedCtrlMixin.Destroy(self)
        wx.TextCtrl.Destroy(self)


##class wxStaticTextCtrl(wx.wxTextCtrl):
##    """ Text Control with attached Static Text caption
##    
##    The caption can be aligned to the top or left of the text control
##    """
##    def __init__(self, parent, id, value = '', caption = '', 
##              pos = wx.wxDefaultPosition, size = wx.wxDefaultSize, style = 0, 
##              validator = wx.wxDefaultValidator, name = 'text'):
##        wx.wxTextCtrl.__init__(self, parent, id, value, pos, size, style, 
##              validator, name)
##
##        self.StaticText = wx.wxStaticText(parent, -1, caption)
##        self._captionAlignment = wx.wxTOP
##        self._captionOffset = wx.wxPoint(0, 0)
##        self.updateStaticTextPos()
##
##        self.PushEventHandler(_PosEvtHandler(self))
##        
##    
##    def updateStaticTextPos(self):
##        pos = self.GetPosition()
##        offset = self._captionOffset
##        if self.StaticText:
##            if self._captionAlignment == wx.wxTOP:
##                self.StaticText.SetPosition(\
##                      (pos.x + offset.x, 
##                       offset.y + pos.y - self.StaticText.GetSize().y-5) )
##            elif self._captionAlignment == wx.wxLEFT:
##                self.StaticText.SetPosition(\
##                      (offset.x + pos.x - self.StaticText.GetSize().x -5, 
##                       offset.y + pos.y) )
##        self.StaticText.Refresh(1)
##    
##    def Destroy(self):
##        self.PopEventHandler(1)
##
##        self.StaticText.Destroy()
##        self.StaticText = None
##        wx.wxTextCtrl.Destroy(self)
##    
###---Properties------------------------------------------------------------------
##    def GetCaption(self):
##        return self.StaticText.GetLabel()
##    
##    def SetCaption(self, caption):
##        self.StaticText.SetLabel(caption)
##        self.updateStaticTextPos()
##    
##    def GetCaptionAlignment(self):
##        return self._captionAlignment
##        
##    def SetCaptionAlignment(self, align):
##        if align not in (wx.wxLEFT, wx.wxTOP):
##            raise 'Unsupported alignment'
##        self._captionAlignment = align
##        self.updateStaticTextPos()
##
##    def GetCaptionOffset(self):
##        return self._captionOffset
##
##    def SetCaptionOffset(self, offset):
##        self._captionOffset = offset
##        self.updateStaticTextPos()


class _PosEvtHandler(wx.EvtHandler):
    """ Custom position event handler that moves the caption with the text ctrl

    An wxEventHandler is used so that user can still use the OnMove event 
    """
    def __init__(self, ctrl):
        wx.EvtHandler.__init__(self)
        wx.EVT_MOVE(ctrl, self.OnMove)
        self.ctrl = ctrl
        
    def OnMove(self, event):
        event.Skip()
        self.ctrl.updateStaticTextPos()
              