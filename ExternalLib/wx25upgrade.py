#-----------------------------------------------------------------------------
# Name:        wx25upgrade.py
# Purpose:     Upgrade code from 2.4 style to 2.5
#
# Author:      Paul Sorensen
# Contrib.:    Werner F. Bruhin
#              Riaan Booysen
#
# Created:     Feb 2005
# RCS-ID:      $Id$
#-----------------------------------------------------------------------------
#
# WARNING - changes files, take care!
#
# requires: pyparsing
# usage: python wx25upgrade myFrame.py > myNewFrame.py
#
# There are three dictionaries which allow for easy conversion for addtional
# converstions, update the key section with the 2.4 name and the value with the
# 2.5 name.
#
# self.importNames, for import statements
# self.specialNames, for classes, e.g. 'GenButton': 'wx.lib.buttons.GenButton'
# self.specialNames2, for other names, e.g. 'wxGrid.wxGrid': 'wx.grid.Grid.wxGrid'
# 
# This file currently munges the 
# - EVT_xxx change from wxPython 2.4 style to 2.5 style
# - .Append for menu, changes 'helpString' to 'help', 'item' to 'text' and
#   wxITEM to wx.ITEM
# - changes the 'map(lambda _init_whatever: wxNewId()' to the new format
# - changes 'wxID_WX' to the new format
# - changes the classes from wxName to wx.Name
#   check "self.specialNames" to see which special cases are handled
# - changes the 'init' from wxName.__init to wx.Name.__init
#   check "self.importNames" to see which imports are handled
# - true and false to True and False
# - SetStatusText "(i=" keyword to "(number="
# - AddSpacer "n, n" to wx.Size(n, n)
# - flag= i.e. flag=wxALL
# - style= i.e. style=wxDEFAULT_DIALOG_STYLE
# - wxInitAllImageHandlers to wx.InitAllImageHandlers
# - orient=wx to orient=wx.
# - kind=wx to kind=wx.
# - Following changes are handled, see self.specialNames2
#   - wxIcon( to wx.Icon(
#   - wxBITMAP to wx.BITMAP
#   - wxBitmap( to wx.Bitmap(
#   - wxSize( to wx.Size(
#   - wxNullBitmap to wx.NullBitmap
#   - wxPoint( to wx.Point(
#   - wxNewID to wx.NewID (if used in user code)
#   - wxColour to wx.Colour
#   - wxOPEN to wx.OPEN
#   - wxID_OK to wx.ID_OK
#   - wxRED to wx.RED
#   - wxGREEN to wx.GREEN
#   - wxBLUE to wx.BLUE
#   - wxGrid.wxGrid to wx.grid.Grid.wxGrid
# - wxFont(8,wxSWISS,wxNORMAL,wxNORMAL to wx.Font(8,wx.SWISS,wx.NORMAL,wx.NORMAL
# - wxACCEL to wx.ACCEL
# - wxAcceleratorTable to wx.AcceleratorTable
# - wxTheClipboard to wx.TheClipboard
# - wxID_YES to wx.ID_YES
# - wxOK to wx.OK
# - wxICON_QUESTION to wx.ICON_QUESTION
# - wxICON_EXCLAMATION wx.ICON_EXCLAMATION
#
#
# A lot is converted however manual inspection and correction of code
# IS STILL REQUIRED!

from pyparsing import *
import string

def lit(text):
    '''For when you want to return a literal value independent of the input'''
    def _lit(s, l, t):
        return text
    return _lit


class Upgrade:
    def __init__(self):
        # Set to True if you want to convert non Boa generated events
        # which contain "control.GetId()"
        specialEventCode = True
        self.specialNames = {'GenButton': 'wx.lib.buttons.GenButton',
                             'StyledTextCtrl': 'wx.stc.StyledTextCtrl',
                             'GenStaticText': 'wx.lib.stattext.GenStaticText',
                             'MaskedComboBox': 'wx.lib.masked.combobox.ComboBox',
                             'MaskedTextCtrl': 'wx.lib.masked.textctrl.TextCtrl',
                             'IpAddrCtrl': 'wx.lib.masked.ipaddrctrl.IpAddrCtrl',
                             'MaskedNumCtrl': 'wx.lib.masked.numctrl.NumCtrl',
                             'TimeCtrl': 'wx.lib.masked.timectrl.TimeCtrl',
                             'IntCtrl': 'wx.lib.intctrl.IntCtrl',
                             'Grid': 'wx.grid.Grid',                             
                             'EditableListBox': 'wx.gizmos.EditableListBox',
                             'TreeListCtrl': 'wx.gizmos.TreeListCtrl'
                             }

        self.specialNames2 = {'wxInitAllImageHandlers' : 'wx.InitAllImageHandlers',
                              'wxIcon' : 'wx.Icon',
                              'wxBITMAP' : 'wx.BITMAP',
                              'wxBitmap' : 'wx.Bitmap',
                              'wxSize' : 'wx.Size',
                              'wxNullBitmap': 'wx.NullBitmap',
                              'wxPoint': 'wx.Point',
                              'wxNewId': 'wx.NewId',
                              'wxColour': 'wx.Colour',
                              'wxOPEN': 'wx.OPEN',
                              'wxID_OK': 'wx.ID_OK',
                              'wxRED': 'wx.RED',
                              'wxBLUE': 'wx.BLUE',
                              'wxGREEN': 'wx.GREEN',
                              'wxGrid.wxGrid': 'wx.grid.Grid.wxGrid',
                              'wxACCEL':'wx.ACCEL',
                              'wxAcceleratorTable':'wx.AcceleratorTable',
                              'wxTheClipboard':'wx.TheClipboard',
                              'wxID_YES':'wx.ID_YES',
                              'wxOK':'wx.OK',
                              'wxICON_QUESTION':'wx.ICON_QUESTION',
                              'wxICON_EXCLAMATION':'wx.ICON_EXCLAMATION',
                              'wxPySimpleApp' : 'wx.PySimpleApp'
                              }

        self.importNames = {'.wx import *': 'import wx',
                            '.stc import *': 'import wx.stc',
                            '.gizmos import *': 'import wx.gizmos',
                            '.grid import *': 'import wx.grid',
                            '.lib.buttons import *': 'import wx.lib.buttons',
                            '.lib.stattext import wxGenStaticText': 'import wx.lib.stattext.GenStaticText',
                            '.lib.maskededit import *': 'import wx.lib.masked.maskededit',
                            '.lib.maskededit import wxMaskedComboBox': 'import wx.lib.masked.maskededit',
                            '.lib.maskednumctrl import *': 'import wx.lib.masked.maskednumctrl',
                            '.lib.timectrl import *': 'import wx.lib.timectrl',
                            '.lib.intctrl import *': 'import wx.lib.intctrl',
                            '.html import *': 'import wx.html',
                            '.intctrl import *': 'import wx.lib.intctrl'}

        COMMA = Literal(',').suppress()
        LPAREN = Literal('(').suppress()
        RPAREN = Literal(')').suppress()
        EQ = Literal('=').suppress()
        ident = Word(alphanums+"_")
        uident = Word(string.ascii_uppercase+"_")        
        qualIdent = Word(alphanums+"_.")
        qualIdent2 = Word(alphanums+"_.()")
        qualIdent3 = Word(alphanums+"_. *")
        intOnly = Word(nums)
        uident2 = Word(string.ascii_uppercase+"_123456789")
        wxExp = Literal("wx").suppress()
        flagExp = (wxExp+uident)
        flags = delimitedList(flagExp, delim='|')
        
        # 2 Parameter evt macros.
        evt_P2 = Literal("EVT_") + uident + LPAREN +\
            qualIdent + COMMA +\
            qualIdent +\
            RPAREN
        evt_P2.setParseAction(self.evt_P2Action)

        # 3 Parameter evt macros.
        evt_P3 = Literal("EVT_") + uident + LPAREN +\
            qualIdent + COMMA +\
            qualIdent + COMMA +\
            qualIdent +\
            RPAREN
        evt_P3.setParseAction(self.evt_P3Action)

        # 3 Parameter evt macros.
        #   specialEventCode = True required
        #   event codes containing "control.GetId()" in code
        evt_P3a = Literal("EVT_") + uident + LPAREN +\
            qualIdent + COMMA +\
            qualIdent2 + COMMA +\
            qualIdent +\
            RPAREN
        evt_P3a.setParseAction(self.evt_P3aAction)

        # Append keyword args
        karg = ident + EQ + (quotedString ^ ident)
        append = Literal(".Append").suppress() \
            + LPAREN + karg + COMMA + karg + COMMA \
            + karg + COMMA + karg + RPAREN
        append.setParseAction(self.appendAction)

        # wxFont
        wxfont = Literal("wxFont").suppress() + LPAREN + \
                        intOnly + COMMA + ident + COMMA + ident + COMMA + \
                        ident
        wxfont.setParseAction(self.wxfontAction)

        # SetStatusText keyword args
        setStatusText = Literal(".SetStatusText").suppress() \
            + LPAREN + ident + EQ + intOnly
        setStatusText.setParseAction(self.setStatusTextAction)

        # AddSpacer keyword args
        addSpacer = Literal(".AddSpacer").suppress() \
            + LPAREN + intOnly + COMMA + intOnly
        addSpacer.setParseAction(self.addSpacerAction)

        # Flags
        flags = Or(map(Literal, ["flag=", "style=", "orient=", "kind=",])) + flags
        flags.setParseAction(self.flagsAction)

        # map(lambda... to wx.NewId() for etc
        RANGE = Literal('range(').suppress()
        COL = Literal(':').suppress()
        repId1 = Literal("map(lambda ").suppress() + qualIdent2 + COL \
                + qualIdent2 + COMMA + RANGE + intOnly + RPAREN + RPAREN
        repId1.setParseAction(self.repId1Action)
        
        # import
        imp = Literal("from wxPython") + qualIdent3
        imp.setParseAction(self.impAction)

        # Specific name space changes
        repWXSpec = Or(map(Literal, self.specialNames2.keys()))
        repWXSpec.setParseAction(self.repNamespace)

        # wx to wx. e.g. wxFrame1(wxFrame)to wxFrame1(wx.Frame)
        repWX = Literal("(wx") + ident + ")"
        repWX.setParseAction(self.repWXAction)
        
        # wx to wx. e.g. self.panel1 = wxPanel to self.Panel1 = wx.Panel
        repWX2 = Literal("= wx") + ident + "("
        repWX2.setParseAction(self.repWX2Action)
        
        # init wx to wx.
        repWX3 = Literal("wx") + ident + ".__"
        repWX3.setParseAction(self.repWX3Action)

        # true to True
        repTrue = Literal("true")
        repTrue.setParseAction(lit('True'))

        # false to False
        repFalse = Literal("false")
        repFalse.setParseAction(lit('False'))

        self.grammar = evt_P2 ^ evt_P3 ^ append ^ wxfont\
            ^ setStatusText ^ addSpacer ^ flags ^ repId1 ^ imp\
            ^ repWXSpec ^ repWX ^ repWX2 ^ repWX3\
            ^ repTrue ^ repFalse\
             
        if specialEventCode:
            self.grammar ^= evt_P3a 

    def evt_P2Action(self, s, l, t):
        ev, evname, win, fn = t
        module = 'wx'
        if evname.find("GRID") != -1:
            module += ".grid"
        return '%s.Bind(%s.%s%s, %s)' % (win, module, ev, evname, fn)

    def evt_P3Action(self, s, l, t):
        ev, evname, win, id, fn = t
        return '%s.Bind(wx.%s%s, %s, id=%s)' % (win, ev, evname, fn, id)

    def evt_P3aAction(self, s, l, t):
        ev, evname, win, id, fn = t
        return '%s.Bind(wx.%s%s, %s, id=%s)' % (win, ev, evname, fn, id)

    def appendAction(self, s, l, t):
        # tokens assumed to be in keyword, arg pairs in sequence
        subs = {'helpString': 'help', 'item': 'text'}
        arglist = []
        for i in range(0, len(t), 2):
            kw, arg = t[i:i+2]
            try:
                kw = subs[kw]
            except:
                pass
            if kw == 'kind':
                arg = arg.replace('wx', 'wx.')
            arglist.append("%s=%s" % (kw, arg))
        return '.Append(' + string.join(arglist, ', ') + ')'

    def wxfontAction(self, s, l, t):
        a, b, c, d = t
        b = b.replace('wx', 'wx.')
        c = c.replace('wx', 'wx.')
        d = d.replace('wx', 'wx.')
        return 'wx.Font('+a+','+b+','+c+','+d

    def setStatusTextAction(self, s, l, t):
        a, b = t
        return '.SetStatusText(' + "number" + "=" + b

    def addSpacerAction(self, s, l, t):
        a, b = t
        return ".AddSpacer(wx.Size("+a+","+b+")"
    
    def flagsAction(self, s, l, t):
        return t[0] + "wx." + string.join(t[1:], '|wx.')

    def repId1Action(self, s, l, t):
        a, b, c = t
        return "[wx.NewId() for "+a+" in range("+c+")]"

    def impAction(self, s, l, t):
        a, b = t
        try:
            newImport = self.importNames[b]
            return newImport
        except KeyError:
            return a+b

    def repNamespace(self, s, l, t):
        return self.specialNames2[t[0]]

    def repWXAction(self, s, l, t):
        if len(t) == 1:
            return
        else:
            a, b, c = t
            return "(wx."+b+c

    def repWX2Action(self, s, l, t):
        a, b, c = t
        try:
            newWX = self.specialNames[b]
            return "= "+newWX+c
        except KeyError:
            return "= wx."+b+c

    def repWX3Action(self, s, l, t):
        a, b, c = t
        return "wx."+b+c

    def scanner(self, text):
        '''
        Scan text, replacing grammar as we go.
        '''
        pos = 0
        for t, s, e in self.grammar.scanString(text):
            yield text[pos:s], t[0]
            pos = e
        if pos < len(text):
            yield text[pos:], ''

    def upgrade(self, intext):
        '''Upgrade the text from wx2.4 style to wx2.5'''
        frag = []
        for non, replacement in self.scanner(intext):
            frag.append(non)
            frag.append(replacement)
        return string.join(frag, '')

if __name__ == "__main__":
    import sys
    u = Upgrade()
    if len(sys.argv) < 2:
        print 'usage: python wx25update.py <boafile>'
        sys.exit(1)
    filename = sys.argv[1]
    fin = file(filename, 'r')
    try:
        print u.upgrade(fin.read())
    finally:
        fin.close()