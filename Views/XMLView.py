#-----------------------------------------------------------------------------
# Name:        XMLView.py
# Purpose:
#
# Author:      Riaan Booysen
#              Based on xml tree example in wxPython demo
#
# Created:     2001/01/06
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2004
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
from EditorViews import EditorView

from wxPython.wx import *

from xml.parsers import expat
parsermodule = expat

class XMLTreeView(wxTreeCtrl, EditorView):
    viewName = 'XMLTree'
    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        id = wxNewId()
        wxTreeCtrl.__init__(self, parent, id)#, style = wxTR_HAS_BUTTONS | wxSUNKEN_BORDER)
        EditorView.__init__(self, model,
          (('Goto line', self.OnGoto, self.gotoLineBmp, ''),), 0)

        self.nodeStack = []

        EVT_KEY_UP(self, self.OnKeyPressed)

        self.active = true

    def buildTree(self, parent, dict):
        for item in dict.keys():
            child = self.AppendItem(parent, item, 0)
            if len(dict[item].keys()):
                self.buildTree(child, dict[item])
            self.Expand(child)

    def refreshCtrl(self):
        self.nodeStack = [self.AddRoot('Root')]
        self.loadTree(self.model.filename)
        self.Expand(self.nodeStack[0])
        return

    # Define a handler for start element events
    def startElement(self, name, attrs ):
        name = name.encode()
        if attrs:
            if attrs.has_key('class'):
                if attrs.has_key('name'):
                    name = '%s (%s:%s)' % (name, attrs['name'], attrs['class'])
                else:
                    name = '%s (%s)' % (name, attrs['class'])
            else:
                if attrs.has_key('name'):
                    name = '%s :%s' % (name, attrs['name'])

        id = self.AppendItem(self.nodeStack[-1], name)
        self.nodeStack.append(id)

    def endElement(self,  name ):
        self.nodeStack = self.nodeStack[:-1]

    def characterData(self, data ):
        if data.strip():
            data = data.encode()
            self.AppendItem(self.nodeStack[-1], data)


    def loadTree(self, filename):
        # Create a parser
        Parser = parsermodule.ParserCreate()

        # Tell the parser what the start element handler is
        Parser.StartElementHandler = self.startElement
        Parser.EndElementHandler = self.endElement
        Parser.CharacterDataHandler = self.characterData

        # Parse the XML File
        ParserStatus = Parser.Parse(self.model.data, 1)

    def OnGoto(self, event):
        idx  = self.GetSelection()
        if idx.IsOk():
            name = self.GetItemText(idx)
            if self.model.views.has_key('Source') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Source']
                srcView.focus()
                module = self.model.getModule()
                srcView.gotoLine(int(module.classes[name].block.start) -1)

    def OnKeyPressed(self, event):
        key = event.KeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)

class XMLTree(wxTreeCtrl):
    def __init__(self, parent, ID):
        wxTreeCtrl.__init__(self, parent, ID)
        self.nodeStack = [self.AddRoot(Root)]

    # Define a handler for start element events
    def StartElement(self, name, attrs ):
        if py2:
            name = name.encode()
        id = self.AppendItem(self.nodeStack[-1], name)
        self.nodeStack.append(id)

    def EndElement(self,  name ):
        self.nodeStack = self.nodeStack[:-1]

    def CharacterData(self, data ):
        if data.strip():
            if py2:
                data = data.encode()
            self.AppendItem(self.nodeStack[-1], data)


    def LoadTree(self, filename):
        # Create a parser
        Parser = parsermodule.ParserCreate()

        # Tell the parser what the start element handler is
        Parser.StartElementHandler = self.StartElement
        Parser.EndElementHandler = self.EndElement
        Parser.CharacterDataHandler = self.CharacterData

        # Parse the XML File
        ParserStatus = Parser.Parse(open(filename,'r').read(), 1)
