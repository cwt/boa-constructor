#!python
# Boa file upgrade helper.
# paul sorenson Feb 2005
# WARNING - changes files, take care.
# requires: pyparsing
# usage: python upgrade myFrame.py > myNewFrame.py
# Current status: concept demonstrator
# $Id$
#
# This file currently munges the EVT_xxx macros from those used with
# wxPython 2.4 to the 2.5 style.  At the moment only EVT_'s found in my
# code are catered for, adding new ones is simple.
# The code could be made more general - that was not my initial design
# goal.


from pyparsing import *
import string

def orLit(a, b): return a ^ b

P2_EvtNames = [Literal("RIGHT_DOWN"), "GRID_CELL_CHANGE",
    "CHAR", "KEY_DOWN", "GRID_CELL_RIGHT_CLICK"]
P3_EvtNames = [Literal("MENU"), "TOOL", "NOTEBOOK_PAGE_CHANGED",
    "TREE_ITEM_ACTIVATED", "TEXT_ENTER", "RADIOBOX"]

class Upgrade:
    def __init__(self):
        COMMA = Literal(',').suppress()
        LPAREN = Literal('(').suppress()
        RPAREN = Literal(')').suppress()
        EQ = Literal('=').suppress()
        ident = Word(alphanums+"_")
        qualIdent = Word(alphanums+"_.")
        # 2 Parameter evt macros.
        evt_P2 = Literal("EVT_") + reduce(orLit, P2_EvtNames) + LPAREN +\
            qualIdent + COMMA +\
            qualIdent +\
            RPAREN
        evt_P2.setParseAction(self.evt_P2Action)
        # 3 Parameter evt macros.
        evt_P3 = Literal("EVT_") + reduce(orLit, P3_EvtNames) + LPAREN +\
            qualIdent + COMMA +\
            qualIdent + COMMA +\
            qualIdent +\
            RPAREN
        evt_P3.setParseAction(self.evt_P3Action)
        # Append keyword args
        karg = ident + EQ + (quotedString ^ ident)
        append = Literal(".Append").suppress() \
            + LPAREN + karg + COMMA + karg + COMMA \
            + karg + COMMA + karg + RPAREN
        append.setParseAction(self.appendAction)
        self.grammar = evt_P2 ^ evt_P3 ^ append

    def evt_P2Action(self, s, l, t):
        ev, evname, win, fn = t
        module = 'wx'
        if evname.find("GRID") != -1:
            module += ".grid"
        return '%s.Bind(%s.%s%s, %s)' % (win, module, ev, evname, fn)

    def evt_P3Action(self, s, l, t):
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
        print 'usage: python wx25upgrade.py <boafile>'
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