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

eols = {  wxSTC_EOL_CRLF : '\r\n',
          wxSTC_EOL_CR : '\r',
          wxSTC_EOL_LF : '\n'}

from Preferences import faces
import Preferences
import methodparse

indentLevel = 4

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

#---Utility mixins--------------------------------------------------------------

class FoldingStyledTextCtrlMix:
    def __init__(self, wId, margin):
        self.__fold_margin = margin
        self.SetProperty('fold', '1')
        self.SetMarginType(margin, wxSTC_MARGIN_SYMBOL)
        self.SetMarginMask(margin, wxSTC_MASK_FOLDERS)
        self.SetMarginSensitive(margin, true)
        self.SetMarginWidth(margin, 13)
        self.MarkerDefine(wxSTC_MARKNUM_FOLDER, wxSTC_MARK_PLUS, 'white', 'black')
        self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPEN, wxSTC_MARK_MINUS, 'white', 'black')


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
                break

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
    else:
        pivR = pivR+1

    return pivL + lineStart, pivR - pivL

class BrowseStyledTextCtrlMix:
    """ This class is to be mix-in with a wxStyledTextCtrl to add
        functionality for browsing the code.
    """
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

class CodeHelpStyledTextCtrlMix:
    def getCurrLineInfo(self):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        return (pos, lnNo, lnStPs, 
                self.GetCurrentLineText()[0], pos - lnStPs - 1)

    def getFirstContinousBlock(self, docs):
        res = []
        for line in string.split(docs, '\n'):
            if string.strip(line):
                res.append(line)
            else:
                break
        return string.join(res, '\n')
        

class AutoCompleteCodeHelpSTCMix(CodeHelpStyledTextCtrlMix):

##    def getCodeCompOptions(self, word, rootWord, matchWord, lnNo):
##        return []

    def codeCompCheck(self):
        pos, lnNo, lnStPs, line, piv = self.getCurrLineInfo()

        start, length = idWord(line, piv, lnStPs, object_delim, object_delim)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        pivword = piv - startLine
        
        dot = string.rfind(word, '.', 0, pivword+1)
        matchWord = word
        if dot != -1:
            rdot = string.find(word, '.', pivword)
            if rdot != -1:
                matchWord = word[dot+1:rdot]
            else:
                matchWord = word[dot+1:]
                
            offset = pivword - dot
            rootWord = word[:dot]
        else:
            offset = pivword + 1
            rootWord = ''

        if not matchWord:
            offset = 0

        names = self.getCodeCompOptions(word, rootWord, matchWord, lnNo)
        
        # remove duplicates
        unqNms = {}
        for name in names: unqNms[name] = None
        names = unqNms.keys()

        self.AutoCompShow(offset, string.join(names, ' '))
        self.AutoCompSelect(matchWord)
        
class CallTipCodeHelpSTCMix(CodeHelpStyledTextCtrlMix):
    def __init__(self):
        self.lastCallTip = ''
        self.lastTipHilite = (0, 0)

    def getTipValue(self, word, lnNo):
        return ''
        
    def callTipCheck(self):
        pos, lnNo, lnStPs, line, piv = self.getCurrLineInfo()

        bracket = methodparse.matchbracket(line[:piv+1], '(')
        if bracket == -1 and self.CallTipActive():
            self.CallTipCancel()
            return
        
        cursBrktOffset = piv - bracket
        
        start, length = idWord(line, bracket-1, lnStPs, object_delim, object_delim)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        if word:
            tip = self.getTipValue(word, lnNo)
            if tip:
                # Minus offset of 1st bracket in the tip
                tipBrkt = string.find(tip, '(')
                if tipBrkt != -1:
                    pos = pos - tipBrkt - 1
                else:
                    tipBrkt = 0
                    
                # get the current parameter from source
                paramNo = len(methodparse.safesplitfields(\
                      line[bracket+1:piv+1]+'X', ','))
                if paramNo:
                    paramNo = paramNo - 1
                
                # get hilight & corresponding parameter from tip
                tipBrktEnd = string.rfind(tip, ')')
                tip_param_str = tip[tipBrkt+1:tipBrktEnd]
                tip_params = methodparse.safesplitfields(\
                    tip_param_str, ',', ('(', '{'), (')', '}') )
                try: 
                    hiliteStart = tipBrkt+1 + string.find(tip_param_str, tip_params[paramNo])
                except IndexError: 
                    hilite = (0, 0)
                else:
                    hilite = (hiliteStart, 
                              hiliteStart+len(tip_params[paramNo]))

                # don't update if active and unchanged
                if self.CallTipActive() and tip == self.lastCallTip and \
                      hilite == self.lastTipHilite:
                    return

                # close if active and changed
                if self.CallTipActive() and (tip != self.lastCallTip or \
                      hilite != self.lastTipHilite):
                    self.CallTipCancel()

                self.CallTipShow(pos - cursBrktOffset, tip)

                self.CallTipSetHighlight(hilite[0], hilite[1])
                self.lastCallTip = tip
                self.lastTipHilite = hilite



#---Language mixins-------------------------------------------------------------

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

        # line numbers in the margin
        if margin != -1:
            self.SetMarginType(margin, wxSTC_MARGIN_NUMBER)
            self.SetMarginWidth(margin, 25)
##            self.StyleSetSpec(wxSTC_STYLE_LINENUMBER,
##              "size:%(lnsize)d,face:%(helv)s,back:#707070" % faces)

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)

        self.setStyles(faces)

    def setStyles(self, faces):
        # Global default styles for all languages
        # Default
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, "back:%(backcol)s,face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()

        self.StyleSetSpec(wxSTC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(lnsize)d" % faces)
        self.StyleSetSpec(wxSTC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        self.StyleSetSpec(wxSTC_STYLE_BRACELIGHT, "fore:#0000FF,back:#FFFF88,bold")
        self.StyleSetSpec(wxSTC_STYLE_BRACEBAD, "fore:#FF0000,back:#FFFF88,bold")

        # Python styles
        self.StyleSetSpec(wxSTC_P_DEFAULT, "fore:#808080")
        self.StyleSetSpec(wxSTC_P_COMMENTLINE, "fore:#007F00,back:#E8FFE8,italic,face:%(mono)s" % faces)
        self.StyleSetSpec(wxSTC_P_NUMBER, "fore:#007F7F")
        self.StyleSetSpec(wxSTC_P_STRING, "fore:#7F007F,face:%(mono)s" % faces)
        self.StyleSetSpec(wxSTC_P_CHARACTER, "fore:#7F007F,face:%(mono)s" % faces)
        self.StyleSetSpec(wxSTC_P_WORD, "fore:#00007F,bold")
        self.StyleSetSpec(wxSTC_P_TRIPLE, "fore:#7F0000")
        self.StyleSetSpec(wxSTC_P_TRIPLEDOUBLE, "fore:#000033,back:#FFFFE8")
        self.StyleSetSpec(wxSTC_P_CLASSNAME, "fore:#0000FF,bold")
        self.StyleSetSpec(wxSTC_P_DEFNAME, "fore:#007F7F,bold")
        self.StyleSetSpec(wxSTC_P_OPERATOR, "bold")
        self.StyleSetSpec(wxSTC_P_IDENTIFIER, "")
        self.StyleSetSpec(wxSTC_P_COMMENTBLOCK, "fore:#7F7F7F,italic")
        self.StyleSetSpec(wxSTC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eolfilled" % faces)

    def grayout(self, do):
        if not Preferences.grayoutSource:
            return
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
    
    def doAutoIndent(self, prevline, pos):
#        prevline = self.GetLine(lineNo -1)[:-1]
        stripprevline = string.strip(prevline)
        if stripprevline:
            indent = prevline[:string.find(prevline, stripprevline)]
        else:
            indent = prevline[:-1]
        if string.rstrip(prevline)[-1:] == ':':
            indent = indent + (indentLevel*' ')
        self.BeginUndoAction()
        try:
            self.InsertText(pos, indent)
            self.GotoPos(pos + len(indent))
        finally:
            self.EndUndoAction()    

    keymap={'euro': {81: chr(64), 56: chr(91), 57: chr(93), 55: chr(123), 
                     48: chr(125), 219: chr(92), 337: chr(126), 226: chr(124)},
            'france': {48: chr(64), 53: chr(91), 219: chr(93), 52: chr(123),
                       337: chr(125), 56: chr(92), 50: chr(126), 226: chr(54),
                       55: chr(96), 51: chr(35), 54: chr(124)},
           } 
    def handleSpecialEuropeanKeys(self, event, countryKeymap='euro'):
        key = event.KeyCode()
        keymap = self.keymap[countryKeymap]
        if event.AltDown() and event.ControlDown() and keymap.has_key(key):
            currPos = self.GetCurrentPos()
            self.InsertText(currPos, keymap[key])
            self.SetCurrentPos(self.GetCurrentPos()+1)
            self.SetSelectionStart(self.GetCurrentPos())


class HTMLStyledTextCtrlMix:
    def __init__(self, wId):
        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = '\n'#wxSTC_EOL_LF #endOfLines[self.GetEOLMode()]

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

        zope_elements = 'dtml-var dtml-in dtml-if dtml-elif dtml-else dtml-unless '\
        'dtml-with dtml-let dtml-call dtml-comment dtml-tree dtml-try dtml-except '

        zope_attributes=\
        'sequence-key sequence-item sequence-start sequence-end sequence-odd '

        self.SetLexer(wxSTC_LEX_HTML)
        if old_stc:
            self.SetKeywords(0, hypertext_elements + hypertext_attributes + \
              ' public !doctype '+zope_elements + zope_attributes)
        else:
            self.SetKeyWords(0, hypertext_elements + hypertext_attributes + \
              ' public !doctype '+zope_elements + zope_attributes)

        self.SetMargins(1, 1)
        # line numbers in the margin
        self.SetMarginType(0, wxSTC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 20)

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)

        # Default
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, "back:%(backcol)s,face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()

        self.StyleSetSpec(wxSTC_STYLE_LINENUMBER,
          'size:%(lnsize)d,face:%(helv)s' % faces)

# XXX Add these
##wxSTC_H_TAGEND
##wxSTC_H_XMLSTART
##wxSTC_H_XMLEND
##wxSTC_H_SCRIPT
##wxSTC_H_ASP
##wxSTC_H_ASPAT
##wxSTC_H_CDATA
##wxSTC_H_QUESTION
##wxSTC_H_VALUE

        self.StyleSetSpec(wxSTC_H_DEFAULT, 'fore:#000000,font:%(mono)s'%faces)
        self.StyleSetSpec(wxSTC_H_TAG, 'fore:#400080,bold')
        self.StyleSetSpec(wxSTC_H_TAGUNKNOWN, 'fore:#900050,bold')
        self.StyleSetSpec(wxSTC_H_ATTRIBUTE, 'fore:#000000,bold')
        self.StyleSetSpec(wxSTC_H_ATTRIBUTEUNKNOWN, 'fore:#900050,bold')
        self.StyleSetSpec(wxSTC_H_NUMBER, 'fore:#800080')
        self.StyleSetSpec(wxSTC_H_DOUBLESTRING, 'fore:#4040F0')
        self.StyleSetSpec(wxSTC_H_SINGLESTRING, 'fore:#4040F0')
        self.StyleSetSpec(wxSTC_H_OTHER, 'fore:#800080')
        self.StyleSetSpec(wxSTC_H_COMMENT, 'fore:#808000')
        self.StyleSetSpec(wxSTC_H_ENTITY, 'fore:#800080,font:%(mono)s,size:%(size)s' % faces)
        # XML identifier begin '<?'
        self.StyleSetSpec(23, 'fore:#0000FF')
        # XML identifier end '?>'
        self.StyleSetSpec(24, 'fore:#0000FF')
        # Matched Operators
        self.StyleSetSpec(34, 'fore:#0000FF,back:#FFFF88,bold')
        self.StyleSetSpec(35, 'fore:#FF0000,back:#FFFF88,bold')

    def OnUpdateUI(self, event):
        pass

# Currently almost a direct copy of the html mixin
class XMLStyledTextCtrlMix:
    def __init__(self, wId):
        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = '\n'#wxSTC_EOL_LF #endOfLines[self.GetEOLMode()]

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

        self.SetLexer(wxSTC_LEX_XML)
        if old_stc:
            self.SetKeywords(0, hypertext_elements + hypertext_attributes + \
              ' public !doctype ')
        else:
            self.SetKeyWords(0, hypertext_elements + hypertext_attributes + \
              ' public !doctype ')

        self.SetMargins(1, 1)
        # line numbers in the margin
        self.SetMarginType(0, wxSTC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 20)

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)

        # Default
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, "back:%(backcol)s,face:%(mono)s,size:%(size)d" % faces)
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

    def OnUpdateUI(self, event):
        pass


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
        self.StyleSetSpec(wxSTC_STYLE_DEFAULT, "back:%(backcol)s,face:%(mono)s,size:%(size)d" % faces)
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

    def OnUpdateUI(self, event):
        pass

from types import IntType, SliceType, StringType
class STCLinesList:
    def __init__(self, STC):
        self.__STC = STC

    def __getitem__(self, key):
        if type(key) is IntType:
            # XXX last char is garbage
            if key < len(self):
                return self.__STC.GetLine(key)[:-1]
            else:
                raise IndexError
        elif type(key) is SliceType:
            res = []
            for idx in range(key.start, key.stop):
                res.append(self[idx])
            return res
        else:
            raise TypeError, '%s not supported' % `type(key)`

    def __setitem__(self, key, value):
        stc = self.__STC
        if type(key) is IntType:
            assert type(value) is StringType
            if key < len(self):
                stc.SetSelection(stc.PositionFromLine(key), stc.GetLineEndPosition(key))
                stc.ReplaceSelection(value)
            else:
                raise IndexError
        elif type(key) is SliceType:
            lines = string.join(value, eols[stc.GetEOLMode()])
            stc.SetSelection(stc.PositionFromLine(key.start),
                  stc.GetLineEndPosition(key.stop))
            stc.ReplaceSelection(lines)
        else:
            raise TypeError, '%s not supported' % `type(key)`

    def __delitem__(self, key):
        stc = self.__STC
        if type(key) is IntType:
            stc.SetSelection(stc.PositionFromLine(key), stc.GetLineEndPosition(key)+1)
            stc.ReplaceSelection('')
        elif type(key) is SliceType:
            stc.SetSelection(stc.PositionFromLine(key.start),
                  stc.GetLineEndPosition(key.stop)+1)
            stc.ReplaceSelection('')
        else:
            raise TypeError, '%s not supported' % `type(key)`

    def __len__(self):
        return self.__STC.GetLineCount()
