#-----------------------------------------------------------------------------
# Name:        StyledTextCtrls.py                                             
# Purpose:     Mixin classes to extend wxStyledTextCtrl                       
#                                                                             
# Author:      Riaan Booysen                                                  
#                                                                             
# Created:     2000/04/26                                                     
# RCS-ID:      $Id$  
# Copyright:   (c) 1999, 2000 Riaan Booysen                                   
# Licence:     GPL                                                            
#-----------------------------------------------------------------------------

from wxPython.wx import *
from wxPython.stc import *

from Preferences import faces

def ver_tot(ma, mi, re):
    return ma*10000+mi*100+re

old_ver = ver_tot(2,2,1)
cur_ver = ver_tot(wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_NUMBER)
new_stc = cur_ver > old_ver
old_stc = not new_stc

if new_stc:
  try:
    wxStyledTextCtrl.SetKeywords        = wxStyledTextCtrl.SetKeyWords
    wxStyledTextCtrl.SetCurrentPosition = wxStyledTextCtrl.SetCurrentPos
    wxStyledTextCtrl.GetCurrentPosition = wxStyledTextCtrl.GetCurrentPos
    wxStyledTextCtrl.IndicatorSetColour = wxStyledTextCtrl.IndicatorSetForeground
    wxStyledTextCtrl.IndicatorGetColour = wxStyledTextCtrl.IndicatorGetForeground
    wxStyledTextCtrl.GetModified        = wxStyledTextCtrl.GetModify
    wxStyledTextCtrl.GetLineFromPos     = wxStyledTextCtrl.LineFromPosition
    wxStyledTextCtrl.GetLineStartPos    = wxStyledTextCtrl.PositionFromLine
    wxStyledTextCtrl.ScrollBy           = wxStyledTextCtrl.LineScroll
    wxStyledTextCtrl.GetCurrentLineText = wxStyledTextCtrl.GetCurLine
    wxStyledTextCtrl.BraceBadlight      = wxStyledTextCtrl.BraceBadLight
    wxStyledTextCtrl.SetStyleFor        = wxStyledTextCtrl.SetStyling
    wxStyledTextCtrl.MarkerGetNextLine  = wxStyledTextCtrl.MarkerNext
    wxStyledTextCtrl.MarkerGetPrevLine  = wxStyledTextCtrl.MarkerPrevious
  except:
    new_stc = 0
    old_stc = 1

# GetCharAt, GetStyleAt now returns int instead of char

word_delim  = string.letters + string.digits + '_'
object_delim = word_delim + '.'

class FoldingStyledTextCtrlMix:
    def __init__(self, wId, margin):
        self.__fold_margin = margin
        self.SetMarginType(margin, wxSTC_MARGIN_SYMBOL)
        self.SetMarginMask(margin, wxSTC_MASK_FOLDERS)
        self.SetMarginSensitive(margin, true)
        self.SetMarginWidth(margin, 13)
        self.MarkerDefine(wxSTC_MARKNUM_FOLDER, wxSTC_MARK_PLUS, "white", "black")
        self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPEN, wxSTC_MARK_MINUS, "white", "black")

        EVT_STC_MARGINCLICK(self, wId, self.OnMarginClick)

    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == self.__fold_margin:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.GetLineFromPos(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & wxSTC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, true)
                        self.Expand(lineClicked, true, true, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, false)
                            self.Expand(lineClicked, false, true, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, true)
                            self.Expand(lineClicked, true, true, 100)
                    else:
                        self.ToggleFold(lineClicked)


    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = true

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & wxSTC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break;

        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & wxSTC_FOLDLEVELHEADERFLAG and \
               (level & wxSTC_FOLDLEVELNUMBERMASK) == wxSTC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, true)
                    lineNum = self.Expand(lineNum, true)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, false)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=false, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wxSTC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, true)
                    else:
                        self.SetFoldExpanded(line, false)
                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, true, force, visLevels-1)
                    else:
                        line = self.Expand(line, false, force, visLevels-1)
            else:
                line = line + 1;

        return line
    

class PythonStyledTextCtrlMix:
    def __init__(self, wId, margin):
        self.SetEdgeMode(wxSTC_EDGE_LINE)
        self.SetEdgeColumn(80)

        self.SetLexer(wxSTC_LEX_PYTHON)
        if old_stc:
            self.SetKeywords(0,
              'and assert break class continue def del elif else except '
              'exec finally for from global if import in is lambda None '
              'not or pass print raise return try while true false')

            self.SetViewWhitespace(false)
        else:
            self.SetKeyWords(0,
              'and assert break class continue def del elif else except '
              'exec finally for from global if import in is lambda None '
              'not or pass print raise return try while true false')

            self.SetViewWhiteSpace(false)
 
        self.SetProperty("fold", "1")

        # line numbers in the margin
        if margin != -1:
            self.SetMarginType(margin, wxSTC_MARGIN_NUMBER)
            self.SetMarginWidth(margin, 25)
            self.StyleSetSpec(wxSTC_STYLE_LINENUMBER, 
              "size:%(lnsize)d,face:%(helv)s,back:#707070" % faces)

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)
        
        self.setStyles(faces)

    def setStyles(self, faces):
        # Global default styles for all languages
        # Default
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, "back:%(backcol)s,face:%(mono)s,size:%(size)d" % faces)

        self.StyleClearAll()

        # Line number
        self.StyleSetSpec(32, "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(33, "back:#C0C0C0,face:%(helv)s,size:%(lnsize)d" % faces)
        # Brace highlight
#        self.StyleSetSpec(34, "fore:#0000FF,bold")
        # Brace incomplete highlight
#        self.StyleSetSpec(35, "fore:#FF0000,bold")
        # Control characters
        self.StyleSetSpec(36, "face:%(mono)s" % faces)

        # Python styles
        # White space
        self.StyleSetSpec(0, "fore:#808080")
        # Comment
        self.StyleSetSpec(1, "fore:#007F00,back:#E8FFE8,italic,face:%(mono)s" % faces)
        # Number
        self.StyleSetSpec(2, "fore:#007F7F")
        # String
        self.StyleSetSpec(3, "fore:#7F007F,face:%(mono)s" % faces)
        # Single quoted string
        self.StyleSetSpec(4, "fore:#7F007F,face:%(mono)s" % faces)
        # Keyword
        self.StyleSetSpec(5, "fore:#00007F,bold")
        # Triple quotes
        self.StyleSetSpec(6, "fore:#7F0000")
        # Triple double quotes
        self.StyleSetSpec(7, "fore:#000033,back:#FFFFE8")
        # Class name definition
        self.StyleSetSpec(8, "fore:#0000FF,bold")
        # Function or method name definition
        self.StyleSetSpec(9, "fore:#007F7F,bold")
        # Operators
        self.StyleSetSpec(10, "bold")
        # Identifiers
        #self.StyleSetSpec(11, "bold")#,fore:#FF00FF")
        # Comment-blocks
        self.StyleSetSpec(12, "fore:#7F7F7F,italic")
        # End of line where string is not closed
        self.StyleSetSpec(13, "fore:#000000,face:%(mono)s,back:#E0C0E0,eolfilled" % faces)
        # Matched Operators
#        self.StyleSetSpec(34, "fore:#FFFFFF,back:#0000FF,bold")
#        self.StyleSetSpec(35, "fore:#000000,back:#FF0000,bold")
        self.StyleSetSpec(34, "fore:#0000FF,back:#FFFF88,bold")
        self.StyleSetSpec(35, "fore:#FF0000,back:#FFFF88,bold")
    
    def grayout(self, do):
        if do:
            from copy import copy
            f = copy(faces)
            f['backcol'] = '#EEF2FF'
        else:
            f = faces
        self.setStyles(f)
        
    def OnUpdateUI(self, evt):
#        print 'OnUpdateUI', evt
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            if old_stc:
                charBefore = self.GetCharAt(caretPos - 1)
                styleBefore = ord(self.GetStyleAt(caretPos - 1))
            else:
                try:
                    charBefore = chr(self.GetCharAt(caretPos - 1))
                except ValueError:
                    charBefore = ''
                styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and charBefore in "[]{}()" and styleBefore == 10:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            if old_stc:
                charAfter = self.GetCharAt(caretPos)
                styleAfter = ord(self.GetStyleAt(caretPos))
            else:
                try:
                    charAfter = chr(self.GetCharAt(caretPos))
                except ValueError:
                    charAfter = ''
                styleAfter = self.GetStyleAt(caretPos)

            if charAfter and charAfter in "[]{}()" and styleAfter == 10:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadlight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            # self.Refresh(false)

def idWord(line, piv, lineStart, leftDelim = word_delim, rightDelim = word_delim):
    if piv >= len(line):
        return 0, 0
    pivL = pivR = piv
    # Look left
    for pivL in range(piv, -1, -1):
        if not line[pivL] in leftDelim:
            pivL = pivL + 1
            break
    # Look right
    for pivR in range(piv + 1, len(line)):
        if not line[pivR] in rightDelim: 
            break
    
    return pivL + lineStart, pivR - pivL

class BrowseStyledTextCtrlMix:
    """ This class is to be mix-in with a wxStyledTextCtrl to add
        functionality for browsing the code.
    """

    # XXX Set red style for Debugging.
    # XXX General problem; Updating all Scintilla's settings when something
    # XXX global like this changes
    def __init__(self):
        self.handCrs = wxStockCursor(wxCURSOR_HAND)
        self.stndCrs = wxStockCursor(wxCURSOR_ARROW)
        self.IndicatorSetStyle(0, wxSTC_INDIC_PLAIN)
        self.IndicatorSetColour(0, wxBLUE)
        self.styleStart = 0
        self.styleLength = 0
        self.ctrlDown = false
        EVT_MOTION(self, self.OnBrowseMotion)
        EVT_LEFT_DOWN(self, self.OnBrowseClick)
        EVT_KEY_DOWN(self, self.OnKeyDown)
        EVT_KEY_UP(self, self.OnKeyUp)

    def doClearBrwsLn(self):
        self.styleStart, self.styleLength = \
            self.clearUnderline(self.styleStart, self.styleLength)
    
    def BrowseClick(self, word, line, lineNo, start, style):
        """Called when a link is clicked.
           Override to use, return true if click is swallowed """
        return false
    
    def StyleVeto(self, style):
        return false
        
    def underlineWord(self, start, length):
##        wxSetCursor(self.handCrs)
        self.SetCursor(self.handCrs)
        self.SetLexer(wxSTC_LEX_NULL)
        
        self.StartStyling(start, wxSTC_INDICS_MASK)
        self.SetStyleFor(length, wxSTC_INDIC0_MASK)
#        self.Refresh(false)
        return start, length
        
    def clearUnderline(self, start, length):
##        wxSetCursor(self.stndCrs)
        self.SetCursor(self.stndCrs)
        
        self.StartStyling(start, wxSTC_INDICS_MASK)
        self.SetStyleFor(length, 0)
        self.SetLexer(wxSTC_LEX_PYTHON)
        self.Refresh(false)
        return 0, 0

    def getBrowsableText(self, line, piv, lnStPs):
        return idWord(line, piv, lnStPs)

    def OnBrowseMotion(self, event):
        try:
            #check if words should be underlined
            if event.ControlDown():
                mp = event.GetPosition()
                pos = self.PositionFromPoint(wxPoint(mp.x, mp.y))
    
                if old_stc:
                    stl = ord(self.GetStyleAt(pos)) & 31
                else:
                    stl = self.GetStyleAt(pos) & 31
                    
                if self.StyleVeto(stl):
                    if self.styleLength > 0:
                        self.styleStart, self.styleLength = \
                          self.clearUnderline(self.styleStart, self.styleLength)
                    return
    
                lnNo = self.GetLineFromPos(pos)
                lnStPs = self.GetLineStartPos(lnNo)
                line = self.GetLine(lnNo)
                piv = pos - lnStPs
                start, length = self.getBrowsableText(line, piv, lnStPs)
                #mark new
                if length > 0 and self.styleStart != start:
                    if self.styleLength > 0:
                        self.clearUnderline(self.styleStart, self.styleLength)
                    self.styleStart,self.styleLength = \
                      self.underlineWord(start, length)
                #keep current
                elif self.styleStart == start: pass
                #delete previous
                elif self.styleLength > 0:
                    self.styleStart, self.styleLength = \
                      self.clearUnderline(self.styleStart, self.styleLength)
                        
            #clear any underlined words
            elif self.styleLength > 0:
                self.styleStart, self.styleLength = \
                  self.clearUnderline(self.styleStart, self.styleLength)
        finally:
            event.Skip()
    
    def getStyledWordElems(self, styleStart, styleLength):
        if styleLength > 0:
            lnNo = self.GetLineFromPos(styleStart)
            lnStPs = self.GetLineStartPos(lnNo)
            line = self.GetLine(lnNo)
            start = styleStart - lnStPs
            word = line[start:start+styleLength]
            return word, line, lnNo, start
        else: 
            return '', 0, 0, 0
        
    def OnBrowseClick(self, event):
        word, line, lnNo, start = self.getStyledWordElems(self.styleStart, self.styleLength)
        if word:
            if old_stc:
                style = ord(self.GetStyleAt(self.styleStart)) & 31
            else:                
                style = self.GetStyleAt(self.styleStart) & 31
            if self.BrowseClick(word, line, lnNo, start, style): 
                return
        event.Skip()

    def OnKeyDown(self, event):
        if event.ControlDown(): self.ctrlDown = true
        event.Skip()
        
    def OnKeyUp(self, event):
        if self.ctrlDown and (not event.ControlDown()):
            self.ctrlDown = false
            if self.styleLength > 0:
                self.styleStart, self.styleLength = \
                  self.clearUnderline(self.styleStart, self.styleLength)
        event.Skip()
        

class HTMLStyledTextCtrlMix:
    def __init__(self, wId):
        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = '\n'#wxSTC_EOL_LF #endOfLines[self.GetEOLMode()]
        
#        print self.GetSelectionBackground()
#        wxColour(wxNamedColor("BLUE"))
#        self.SetSelectionBackground(col)
#        wxColour(153, 204, 255))

        # All hypertext elements and attributes must be listed in lower case
        hypertext_elements = \
        'a abbr acronym address applet area b base basefont '\
        'bdo big blockquote body br button caption center '\
        'cite code col colgroup dd del dfn dir div dl dt em '\
        'fieldset font form frame frameset h1 h2 h3 h4 h5 h6 '\
        'head hr html i iframe img input ins isindex kbd label '\
        'legend li link map menu meta noframes noscript '\
        'object ol optgroup option p param pre q s samp '\
        'script select small span strike strong style sub sup '\
        'table tbody td textarea tfoot th thead title tr tt u ul '\
        'var xmlns '
        
        hypertext_attributes=\
        'abbr accept-charset accept accesskey action align alink '\
        'alt archive axis background bgcolor border '\
        'cellpadding cellspacing char charoff charset checked cite '\
        'class classid clear codebase codetype color cols colspan '\
        'compact content coords '\
        'data datafld dataformatas datapagesize datasrc datetime '\
        'declare defer dir disabled enctype '\
        'face for frame frameborder '\
        'headers height href hreflang hspace http-equiv '\
        'id ismap label lang language link longdesc '\
        'marginwidth marginheight maxlength media method multiple '\
        'name nohref noresize noshade nowrap '\
        'object onblur onchange onclick ondblclick onfocus '\
        'onkeydown onkeypress onkeyup onload onmousedown '\
        'onmousemove onmouseover onmouseout onmouseup '\
        'onreset onselect onsubmit onunload '\
        'profile prompt readonly rel rev rows rowspan rules '\
        'scheme scope shape size span src standby start style '\
        'summary tabindex target text title type usemap '\
        'valign value valuetype version vlink vspace width '\
        'text password checkbox radio submit reset '\
        'file hidden image '
        
        zope_elements = 'dtml-var dtml-in dtml-if dtml-with '
        
        self.SetLexer(wxSTC_LEX_HTML)
        if old_stc:
            self.SetKeywords(0, hypertext_elements + hypertext_attributes + \
              ' public !doctype '+zope_elements)
        else:
            self.SetKeyWords(0, hypertext_elements + hypertext_attributes + \
              ' public !doctype '+zope_elements)

        self.SetMargins(1, 1)
        # line numbers in the margin
        self.SetMarginType(0, wxSTC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 20)

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)

        # Default
#        style.hypertext.0=fore:#000000,font:Times New Roman,size:11
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, 
          'fore:#000000,font:%(mono)s,size:%(size)s' % faces)

        self.StyleClearAll()

        self.StyleSetSpec(wxSTC_STYLE_LINENUMBER, 
          'size:%(lnsize)d,face:%(helv)s' % faces)

        # Tags
        self.StyleSetSpec(1, 'fore:#400080,bold')
        # Unknown Tags
        self.StyleSetSpec(2, 'fore:#900050,bold')
        # Attributes
        self.StyleSetSpec(3, 'fore:#000000,bold')
        # Unknown Attributes
        self.StyleSetSpec(4, 'fore:#900050,bold')
        # Numbers
        self.StyleSetSpec(5, 'fore:#800080')
        # Double quoted strings
        self.StyleSetSpec(6, 'fore:#4040F0')
        # Single quoted strings
        self.StyleSetSpec(7, 'fore:#4040F0')
        # Other inside tag
        self.StyleSetSpec(8, 'fore:#800080')
        # Comment
        self.StyleSetSpec(9, 'fore:#808000')
        # Entities
        self.StyleSetSpec(10, 'fore:#800080,font:%(mono)s,size:%(size)s' % faces)
        # XML identifier begin '<?'
        self.StyleSetSpec(23, 'fore:#0000FF')
        # XML identifier end '?>'
        self.StyleSetSpec(24, 'fore:#0000FF')
        # Matched Operators
        self.StyleSetSpec(34, 'fore:#0000FF,back:#FFFF88,bold')
        self.StyleSetSpec(35, 'fore:#FF0000,back:#FFFF88,bold')
            
    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            if old_stc:
                charBefore = self.GetCharAt(caretPos - 1)
                styleBefore = ord(self.GetStyleAt(caretPos - 1))
            else:
                charBefore = chr(self.GetCharAt(caretPos - 1))
                styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and charBefore in "<>[]{}()" and styleBefore == 10:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            if old_stc:
                charAfter = self.GetCharAt(caretPos)
                styleAfter = ord(self.GetStyleAt(caretPos))
            else:
                charAfter = chr(self.GetCharAt(caretPos))
                styleAfter = self.GetStyleAt(caretPos)
                
            if charAfter and charAfter in "<>[]{}()" and styleAfter == 10:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadlight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            # self.Refresh(false)

class CPPStyledTextCtrlMix:
    def __init__(self, wId):
        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = '\n'
        
        keyWds = \
            'asm auto bool break case catch char class const const_cast continue '\
            'default delete do double dynamic_cast else enum explicit export '\
            'extern false float for friend goto if inline int long mutable '\
            'namespace new operator private protected public register '\
            'reinterpret_cast return short signed sizeof static static_cast '\
            'struct switch template this throw true try typedef typeid typename '\
            'union unsigned using virtual void volatile wchar_t while'

        self.SetLexer(wxSTC_LEX_CPP)
        if old_stc:
            self.SetKeywords(0, keyWds)
        else:
            self.SetKeyWords(0, keyWds)

        self.SetMargins(1, 1)
        # line numbers in the margin
        self.SetMarginType(0, wxSTC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 20)

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)

        # Default
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, 
          'fore:#000000,font:%(mono)s,size:%(size)s' % faces)

        self.StyleClearAll()

        self.StyleSetSpec(wxSTC_STYLE_LINENUMBER, 
          'size:%(lnsize)d,face:%(helv)s' % faces)

        # Comment
        self.StyleSetSpec(1, 'fore:#007F00,size:8')
        # Line Comment
        self.StyleSetSpec(2, 'fore:#007F00,size:8')
        # Doc comment
        self.StyleSetSpec(3, 'fore:#7F7F7F')
        # Number
        self.StyleSetSpec(4, 'fore:#007F7F')
        # Keyword
        self.StyleSetSpec(5, 'fore:#00007F,bold')
        # Double quoted string
        self.StyleSetSpec(6, 'fore:#7F007F')
        # Single quoted strings
        self.StyleSetSpec(7, 'fore:#7F007F')
        # Symbols 
        self.StyleSetSpec(8, 'fore:#007F7F')
        # Preprocessor
        self.StyleSetSpec(9, 'fore:#7F7F00')
        # Operators
        self.StyleSetSpec(10, 'bold')
        # Identifiers
        self.StyleSetSpec(11, '')
        # End of line where string is not closed
        self.StyleSetSpec(12, 'fore:#000000,back:#E0C0E0,eolfilled')
