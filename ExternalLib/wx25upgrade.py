# Boa file upgrade helper.
# paul sorenson Feb 2005
# WARNING - changes files, take care!

# requires: pyparsing
# usage: python wx25upgrade myFrame.py > myNewFrame.py
# Current status: concept demonstrator
# $Id$
#
# This file currently munges the 
# - EVT_xxx change from wxPython 2.4 style to 2.5 style
# - changes the 'helpString' to 'help' for .Append
# - changes the 'item' to 'text' for .Append
# - changes the 'map(lambda _init_ctrls: wxNewId()' to the new format
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
# - wxInitAllImageHandlers( to wx.InitAllImageHandlers(
# - orient=wx to orient=wx.
# - kind=wxITEM to kind=wx.ITEM
# - wxIcon( to wx.Icon(
# - wxBITMAP to wx.BITMAP
# - wxBitmap( to wx.Bitmap(
# - wxSize( to wx.Size(
# - wxNullBitmap to wx.NullBitmap
# - wxPoint( to wx.Point(
#
#
# A lot is converted however manual inspection and correction of code
# IS STILL REQUIRED!

from pyparsing import *
import string

def orLit(a, b): return a ^ b

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
                             'TreeListCtrl': 'wx.gizmos.TreeListCtrl',
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
        flagExp = (wxExp+uident2)
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

        # SetStatusText keyword args
        setStatusText = Literal(".SetStatusText").suppress() \
            + LPAREN + ident + EQ + intOnly
        setStatusText.setParseAction(self.setStatusTextAction)

        # AddSpacer keyword args
        addSpacer = Literal(".AddSpacer").suppress() \
            + LPAREN + intOnly + COMMA + intOnly
        addSpacer.setParseAction(self.addSpacerAction)

        # Flag
        flag = Literal("flag=").suppress() \
            + flags
        flag.setParseAction(self.flagAction)

        # Style
        style = Literal("style=").suppress() \
            + flags
        style.setParseAction(self.styleAction)

        # Orient
        orient = Literal("orient=").suppress() \
            + flags
        orient.setParseAction(self.orientAction)

        # kind
        kind = Literal("kind=").suppress() \
            + flags
        kind.setParseAction(self.kindAction)

        # wxNewId() to wx.NewId()
        repId1 = Literal("map(lambda _init_ctrls: wxNewId()") +\
                COMMA + "range(" + ident + RPAREN + RPAREN
        repId1.setParseAction(self.repId1Action)
        
        # wxID_WX to wxID_
        repId2 = Literal("wxID_WX") + ident
        repId2.setParseAction(self.repId2Action)
        
        # import
        imp = Literal("from wxPython") + qualIdent3
        imp.setParseAction(self.impAction)

        # wx to wx. e.g. wxFrame1(wxFrame)to wxFrame1(wx.Frame)
        repWX = Literal("(wx") + ident + ")"
        repWX.setParseAction(self.repWXAction)
        
        # wx to wx. e.g. self.panel1 = wxPanel to self.Panel1 = wx.Panel
        repWX2 = Literal("= wx") + ident + "("
        repWX2.setParseAction(self.repWX2Action)
        
        # init wx to wx.
        repWX3 = Literal("wx") + ident + ".__"
        repWX3.setParseAction(self.repWX3Action)

        # init wxInitAllImageHandlers( to wx.InitAllImageHandlers(
        repWX4 = Literal("wxInitAllImageHandlers(")
        repWX4.setParseAction(self.repWX4Action)

        # init wxIcon( to wx.Icon(
        repWX5 = Literal("wxIcon(")
        repWX5.setParseAction(self.repWX5Action)

        # init wxBITMAP to wx.BITMAP
        repWX6 = Literal("wxBITMAP")
        repWX6.setParseAction(self.repWX6Action)

        # init wxBitmap( to wx.Bitmap(
        repWX7 = Literal("wxBitmap(")
        repWX7.setParseAction(self.repWX7Action)

        # init wxSize( to wx.Size(
        repWX8 = Literal("wxSize(")
        repWX8.setParseAction(self.repWX8Action)

        # init wxNullBitmap to wx.NullBitmap
        repWX9 = Literal("wxNullBitmap")
        repWX9.setParseAction(self.repWX9Action)

        # init wxPoint( to wx.Point(
        repWX10 = Literal("wxPoint(")
        repWX10.setParseAction(self.repWX10Action)

        # true to True
        repTrue = Literal("true")
        repTrue.setParseAction(self.trueAction)

        # false to False
        repFalse = Literal("false")
        repFalse.setParseAction(self.falseAction)

        # changed from ^ to ^, i.e. instead of doing OR match it does MatchFirst
        # as the things we are looking to convert are unique that should do
        # maybe a bit faster, but I did not notice a difference 
        if specialEventCode == False:
            self.grammar = evt_P2 ^ evt_P3 ^ append ^ repId1 ^ repId2 ^ imp\
                ^ repWX ^ repWX2 ^ repWX3 ^ repTrue ^ repFalse ^ setStatusText\
                ^ addSpacer ^ flag ^ style ^ repWX4 ^ orient ^ orient ^ repWX5\
                ^ repWX6 ^ repWX7 ^ repWX8 ^ repWX9 ^ repWX10
        else:
            self.grammar = evt_P2 ^ evt_P3 ^ append ^ repId1 ^ repId2 ^ imp\
                ^ repWX ^ repWX2 ^ repWX3 ^ evt_P3a ^ repTrue ^ repFalse\
                ^ setStatusText ^ addSpacer ^ flag ^ style ^ repWX4 ^ orient\
                ^ kind ^ repWX5 ^ repWX6 ^ repWX7 ^ repWX8 ^ repWX9 ^ repWX10

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
            arglist.append("%s=%s" % (kw, arg))
        result = '.Append(' + string.join(arglist, ', ') + ')'
        return result

    def setStatusTextAction(self, s, l, t):
        a, b = t
        return '.SetStatusText(' + "number" + "=" + b

    def addSpacerAction(self, s, l, t):
        a, b = t
        return ".AddSpacer(wx.Size("+a+","+b+")"
    
    def flagAction(self, s, l, t):
        first = False
        temp = ""
        for flag in t:
            if first == True:
                temp = temp + "|"
            first = True
            temp = temp + "wx." +flag
        return "flag="+temp
    
    def styleAction(self, s, l, t):
        first = False
        temp = ""
        for flag in t:
            if first == True:
                temp = temp + "|"
            first = True
            temp = temp + "wx." +flag
        return "style="+temp

    def orientAction(self, s, l, t):
        first = False
        temp = ""
        for flag in t:
            if first == True:
                temp = temp + "|"
            first = True
            temp = temp + "wx." +flag
        return "orient="+temp

    def kindAction(self, s, l, t):
        first = False
        temp = ""
        for flag in t:
            if first == True:
                temp = temp + "|"
            first = True
            temp = temp + "wx." +flag
        return "kind="+temp

    def repId1Action(self, s, l, t):
        a, b, c = t
        return "[wx.NewId() for _init_ctrls in range("+c+")]"

    def repId2Action(self, s, l, t):
        a, b = t
        return "wxID_"+b
    
    def impAction(self, s, l, t):
        a, b = t
        try:
            newImport = self.importNames[b]
            return newImport
        except KeyError:
            return a+b
    
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

    def repWX4Action(self, s, l, t):
        return "wx.InitAllImageHandlers("

    def repWX5Action(self, s, l, t):
        return "wx.Icon("

    def repWX6Action(self, s, l, t):
        return "wx.BITMAP"

    def repWX7Action(self, s, l, t):
        return "wx.Bitmap("

    def repWX8Action(self, s, l, t):
        return "wx.Size("

    def repWX9Action(self, s, l, t):
        return "wx.NullBitmap"

    def repWX10Action(self, s, l, t):
        return "wx.Point("

    def trueAction(self, s, l, t):
        return "True"

    def falseAction(self, s, l, t):
        return "False"

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

if __name__ == "__main__":
    import sys
    u = Upgrade()
    if len(sys.argv) < 2:
        print 'usage: python wx25update.py <boafile>'
        sys.exit(1)
    filename = sys.argv[1]
    fin = file(filename, 'r')
    try:
        frag = []
        for non, rep in u.scanner(fin.read()):
            frag.append(non);
            frag.append(rep);
        newtext = string.join(frag, '')
        print newtext
    finally:
        fin.close()