#----------------------------------------------------------------------
# Name:        InspectorEditorControls.py
# Purpose:     Controls that are hosted by the inspector to edit props
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from wxPython.wx import *
import Preferences
from os import path
import Utils

# XXX Refactor all the position offsets into class attribs and move logic
# XXX to the base class

class InspectorEditorControl:
    """ Interface for controls that edit values in the Inspector
        values are stored in the native type of the control       """

    def __init__(self, propEditor, value):
        self.propEditor = propEditor
        self.editorCtrl = None
        self.wID = wxNewId()
        self.value = value

    def createControl(self):
        if self.editorCtrl: self.editorCtrl.SetFocus()

    def destroyControl(self):
        """ Close an open editor control """
        if self.editorCtrl:
            self.editorCtrl.Destroy()
            self.editorCtrl = None

    def getValue(self):
        """ Read value from editor control """
        return self.value

    def setValue(self, value):
        """ Write value to editor control """
        self.value = value

    # default sizing for controls that span the entire value width
    def setWidth(self, width):
        if self.editorCtrl:
            height = self.editorCtrl.GetSize().y
            self.editorCtrl.SetSize(wxSize(width -1, height))

    def setIdx(self, idx):
        """ Move the to the given index """
        if self.editorCtrl:
            self.editorCtrl.SetPosition( (-2, idx*Preferences.oiLineHeight -2) )

    def OnSelect(self, event):
        """ Post the value.

            Bind the event of the control that 'sets' the value to this method
        """
        self.propEditor.inspectorPost(false)
        event.Skip()

class BevelIEC(InspectorEditorControl):
    def destroyControl(self):
        if self.bevelTop:
            self.bevelTop.Destroy()
            self.bevelTop = None
            self.bevelBottom.Destroy()
        InspectorEditorControl.destroyControl(self)

    def createControl(self, parent, idx, sizeX):
        self.bevelTop = wxPanel(parent, -1,
            (0, idx*Preferences.oiLineHeight -1), (sizeX, 1))
        self.bevelTop.SetBackgroundColour(wxBLACK)
        self.bevelBottom = wxPanel(parent, -1,
            (0, (idx + 1)*Preferences.oiLineHeight -1), (sizeX, 1))
        self.bevelBottom.SetBackgroundColour(wxWHITE)

    def setWidth(self, width):
        if self.bevelTop:
            self.bevelTop.SetSize(wxSize(width, 1))
            self.bevelBottom.SetSize(wxSize(width, 1))

    def setIdx(self, idx):
        if self.bevelTop:
            self.bevelTop.SetPosition(wxPoint(-2, idx*Preferences.oiLineHeight -1))
            self.bevelBottom.SetPosition(wxPoint(-2, (idx +1)*Preferences.oiLineHeight -1))
#        InspectorEditorControl.setIdx(self, idx)

class BeveledLabelIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX):
        BevelIEC.createControl(self, parent, idx, sizeX)
        self.editorCtrl = wxStaticText(parent, -1, self.value,
            (2, idx*Preferences.oiLineHeight+2),
            (sizeX, Preferences.oiLineHeight-3))
        self.editorCtrl.SetForegroundColour(Preferences.propValueColour)

class TextCtrlIEC(InspectorEditorControl):
    def createControl(self, parent, value, idx, sizeX, style = 0):
        value = self.propEditor.valueToIECValue()
        self.editorCtrl = wxTextCtrl(parent, self.wID, value,
              (-2, idx*Preferences.oiLineHeight -2),
              (sizeX, Preferences.oiLineHeight+3), style = style)
        InspectorEditorControl.createControl(self)

        if value:
            self.editorCtrl.SetSelection(0, len(value))

        # XXX Ideally the text ctrl should catch the 'enter' keystroke
        # XXX and post the inspector, but I cant seem to catch it
        # XXX This is currently handled by the Inspector with an
        # XXX accelerator table binding on Enter
    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.GetValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.SetValue(value)

class ChoiceIEC(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wxChoice(parent, self.wID,
         wxPoint(-2, idx*Preferences.oiLineHeight -1), wxSize(sizeX, Preferences.oiLineHeight+3),
         self.propEditor.getValues())
        EVT_CHOICE(self.editorCtrl, self.wID, self.OnSelect)
        InspectorEditorControl.createControl(self);
    def getValue(self):
        if self.editorCtrl:
            return self.editorCtrl.GetStringSelection()
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetStringSelection(value)
    def repopulate(self):
        self.editorCtrl.Clear()
        for val in self.propEditor.getValues():
            self.editorCtrl.Append(val)


class ComboIEC(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wxComboBox(parent, self.wID, self.value,
         wxPoint(-2, idx*Preferences.oiLineHeight -1), wxSize(sizeX, Preferences.oiLineHeight+3),
         self.propEditor.getValues())
        InspectorEditorControl.createControl(self);
    def getValue(self):
        if self.editorCtrl:
            return self.editorCtrl.GetStringSelection()
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetSelection(self.editorCtrl.FindString(value))

class ButtonIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX, editMeth):
       # XXX use image store
        bmp = Preferences.IS.load('Images/Shared/ellipsis.png')
#        wxBitmap(path.join(Preferences.pyPath, 'Images', 'Shared', 'ellipsis.png'), wxBITMAP_TYPE_BMP)
        self.editorCtrl = wxBitmapButton(parent, self.wID, bmp,
          wxPoint(sizeX -18 - 3, idx*Preferences.oiLineHeight +1),
          wxSize(18, Preferences.oiLineHeight-2))
        EVT_BUTTON(self.editorCtrl, self.wID, editMeth)
        BevelIEC.createControl(self, parent, idx, sizeX)

    def setWidth(self, width):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(width - 18 - 3, self.editorCtrl.GetPosition().y,
              18, Preferences.oiLineHeight-2)

        BevelIEC.setWidth(self, width)

    def setIdx(self, idx):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(self.editorCtrl.GetPosition().x,
              idx*Preferences.oiLineHeight +1, 18, Preferences.oiLineHeight-2)
        BevelIEC.setIdx(self, idx)

class TextCtrlButtonIEC(BevelIEC):

    def createControl(self, parent, idx, sizeX, editMeth):
        bmp = Preferences.IS.load('Images/Shared/ellipsis.png')
        value = self.propEditor.valueToIECValue()
        self.wID2 = wxNewId()
        self.editorCtrl = [
              wxTextCtrl(parent, self.wID, value,
               (-2, idx*Preferences.oiLineHeight -2),
               (sizeX - 18, Preferences.oiLineHeight+3)),#, style = style),
              wxBitmapButton(parent, self.wID2, bmp,
               (sizeX - 18 -3, idx*Preferences.oiLineHeight +1),
               (18, Preferences.oiLineHeight-2))]
        EVT_BUTTON(self.editorCtrl[1], self.wID2, editMeth)

        if value:
            self.editorCtrl[0].SetSelection(0, len(value))

        BevelIEC.createControl(self, parent, idx, sizeX)

    def destroyControl(self):
        """ Close an open editor control """
        if self.editorCtrl:
            #self.editorCtrl.GetParent().SetFocus()
            for ec in self.editorCtrl:
                ec.Destroy()
            self.editorCtrl = None
        if self.bevelTop:
            self.bevelTop.Destroy()
            self.bevelTop = None
            self.bevelBottom.Destroy()
            self.bevelBottom = None

    # default sizing for controls that span the entire value width
    def setWidth(self, width):
        if self.editorCtrl:
            self.editorCtrl[0].SetSize(wxSize(width -18,
                  self.editorCtrl[0].GetSize().y))
            self.editorCtrl[1].SetDimensions(width - 18 -3,
                  self.editorCtrl[1].GetPosition().y, 18,
                  Preferences.oiLineHeight-2)

        BevelIEC.setWidth(self, width)

    def setIdx(self, idx):
        """ Move the to the given index """
        if self.editorCtrl:
            for ec in self.editorCtrl:
                ec.SetPosition(ec.GetPosition().x, idx*Preferences.oiLineHeight -2)
        BevelIEC.setIdx(self, idx)

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl[0].GetValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl[0].SetValue(value)

class CheckBoxIEC2(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wxWindow(parent, wxNewId(),
         style = wxTAB_TRAVERSAL | wxSUNKEN_BORDER)
        self.editorCtrl.SetDimensions(-2, idx*Preferences.oiLineHeight-2,
         sizeX, Preferences.oiLineHeight+3)

        self.checkBox = wxCheckBox(self.editorCtrl, self.wID, 'false', (2, 1))
        EVT_CHECKBOX(self.editorCtrl, self.wID, self.OnSelect)
        def OnWinSize(evt, win=self.checkBox):
            win.SetSize(evt.GetSize())
        EVT_SIZE(self.editorCtrl, OnWinSize)

        InspectorEditorControl.createControl(self)

    truefalseMap = {true: 'true', false: 'false'}
    def getValue(self):
        if self.editorCtrl:
            return self.truefalseMap[self.editorCtrl.GetValue()]
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(self.truefalseMap[true] == value)

    def OnSelect(self, event):
        if event.IsChecked():
            self.setValue(self.truefalseMap[event.IsChecked()])

        InspectorEditorControl.OnSelect(self, event)

class CheckBoxIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wxCheckBox(parent, self.wID, 'false',
            (2, idx*Preferences.oiLineHeight+1),
            (sizeX, Preferences.oiLineHeight-2) )
        EVT_CHECKBOX(self.editorCtrl, self.wID, self.OnSelect)

        BevelIEC.createControl(self, parent, idx, sizeX)

    truefalseMap = {true: 'true', false: 'false'}
    def getValue(self):
        if self.editorCtrl:
            return self.truefalseMap[self.editorCtrl.GetValue()]
        else:
            return self.value
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(self.truefalseMap[true] == value)

    def setIdx(self, idx):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(2, idx*Preferences.oiLineHeight +1,
            self.editorCtrl.GetSize().x, Preferences.oiLineHeight-2)
        BevelIEC.setIdx(self, idx)
#        InspectorEditorControl.setIdx(self, idx)
    def OnSelect(self, event):
        self.setValue(self.truefalseMap[event.IsChecked()])

        BevelIEC.OnSelect(self, event)
