#-----------------------------------------------------------------------------
# Name:        BicycleRepairMan.plug-in.py
# Purpose:     Integrating Boa Constructor and Bicycle Repair Man
#
# Author:      Riaan Booysen
#
# Created:     2003/04/26
# RCS-ID:      $Id$
# Copyright:   (c) 2003
# Licence:     BSD
#-----------------------------------------------------------------------------

""" A Boa Constructor Plug-in that integrates the Bicycle Repair Man into the IDE.

The refactoring actions are published under the Edit menu of Python Source Views,
this is also the source's context menu.

There is a global refactoring context shared between all open modules.
This is exposed as editor.brm_context.

When a python module is opened in the IDE, it is automatically added to the
context (and parsed). 
See Preferences->Plug-ins->Preferences->brmAddToContextOnOpen

When a Container type like Applications or Packages is opened in the IDE, 
it's contents (the list of files) not automatically added to the
context. 
See Preferences->Plug-ins->Preferences->brmAddContentsToContextOnOpen

To explicitly load an open file (and it's contents if any) into the context, 
select File->BRM - Import module(s)

Files and entire folders can also be added to the context thru the Explorer
interface while browsing over the FileSystem transport.
From the Edit menu choose BRM - Import selected.

Also clearing the current context can be called from the Explorer menu.

"""

print 'importing BicycleRepairMan'
 
import os, linecache

import bike

from wxPython import wx

import Preferences, Utils, Plugins

from Views import PySourceView
from Models import PythonEditorModels, PythonControllers
from Explorers import ExplorerNodes, FileExplorer
import ErrorStack, Editor

Editor.EditorFrame.brm_context = None

# Issues
# * On Windows filenames aren't guaranteed to always match those in the Editor
# * When the Boa IDE framework supports it, the BRM support should have 
#   it's own menu, e.g. Tools->BicycleRepairMan->[Actions]
#   or a submenu under Edit, e.g. Edit->BicycleRepairMan->[Actions]

# Notes
# * There is an off-by-one issue between BRM and Scintilla,
#       before passing a scintilla lineno to BRM, add 1
#       before passing a BRM lineno to Scintilla, minus 1
# Settings to control how the collection of files that BRM tracks is built up

Plugins.registerPreference('BicycleRepairMan', 'brmAddToContextOnOpen', 'True', 
                           ['When a python module is opened in the IDE, it is '
                            'automatically','added to the refactoring context.'])
Plugins.registerPreference('BicycleRepairMan', 'brmAddContentsToContextOnOpen', 
                           'False', ['When a container file is opened in the '
                           'IDE, it''s contents is automatically added to the ',
                           'refactoring context.'])
Plugins.registerPreference('BicycleRepairMan', 'brmProgressLogger', 
                           "'ProgressStatusLogger'", 
                           ['Destination for progress messages from BRM.'], 
                           "options: 'ProgressStatusLogger', 'ProgressErrOutLogger'")

#-Editor plugins----------------------------------------------------------------

class BRMViewPlugin:
    """ Plugin class for View classes that exposes the refactoring API.
    
    Handles """ 
    def __init__(self, model, view, actions):
        self.model = model
        self.view = view
        actions.extend( (
              ('-', None, '-', ''),
              ('BRM - Find references', self.OnFindReferences, '-', ''),
              ('BRM - Find definition', self.OnFindDefinition, '-', ''),
              ('-', None, '-', ''),
              ('BRM - Rename', self.OnRename, '-', ''),
              ('BRM - Extract method', self.OnExtractMethod, '-', ''),
              ('-', None, '-', ''),
              ('BRM - Extract local variable', self.OnExtractLocalVar, '-', ''),
              ('BRM - Inline local variable', self.OnInlineLocalVar, '-', ''),
              ('-', None, '-', ''),
              #('BRM - Get type of expression', self., '-', ''), # not useful currently
              ('BRM - Undo last', self.OnUndoLast, '-', ''),
        ) )

    def prepareForSelectOperation(self):
        selection = self.view.GetSelectedText().strip()
        if not selection:
            raise 'No text selected.'

        ctx = self.model.editor.brm_context
        filename = self.model.checkLocalFile()
        pos = self.view.GetSelectionStart()
        lineno = self.view.LineFromPosition(pos)+1
        column = self.view.GetColumn(pos)

        return ctx, selection, filename, lineno, column

    def prepareOutputDisplay(self, txt):
        errout = self.model.editor.erroutFrm
        errout.runningDir = ''
        errout.tracebackType = 'Info'

        tree = errout.errorStackTC
        tree.DeleteAllItems()
        root = tree.AddRoot(txt)
        errout.display()

        return errout, tree, root

    def saveAndRefresh(self):
        editor = self.model.editor
        savedfiles = editor.brm_context.save()

        for filename in savedfiles:
            editor.explorerModifyNotify('file://'+os.path.abspath(filename))


    def checkUnsavedChanges(self):
        model = self.model
        ctx = model.editor.brm_context

        for path in ctx.paths:
            uri = 'file://'+os.path.abspath(path)
            if uri in model.editor.modules:
                try:
                    model.editor.prepareForCloseModule(
                          model.editor.modules[uri], True,
                          'Save changes before Refactoring operation')
                except 'Cancelled':
                    wx.wxLogError('Operation aborted.')
                    return False
        return True

    def getExtractionInfo(self, xtype, caption):
        selection = self.view.GetSelectedText().strip()
        if not selection:
            raise 'No text selected. Highlight the region you want to extract.'

        filename = self.model.checkLocalFile()
        name = wx.wxGetTextFromUser('New %s name:'%xtype, caption)
        if not name:
            raise 'Empty names are invalid.'

        startpos, endpos = self.view.GetSelection()
        startline = self.view.LineFromPosition(startpos)
        startcol = self.view.GetColumn(startpos)
        endline = self.view.LineFromPosition(endpos)
        endcol = self.view.GetColumn(endpos)

        return filename, startline+1, startcol, endline+1, endcol, name

    def OnFindReferences(self, event):
        wx.wxBeginBusyCursor()
        try:
            ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

            errout, tree, root = self.prepareOutputDisplay(
                                 'BRM - References for %s'%sel)
            x = 0
            for ref in ctx.findReferencesByCoordinates(filename, lineno, column):
                entry = ReferencesMatcher([ref])
                x = errout.addTracebackNode(entry, x)

            tree.SetItemHasChildren(root, True)
            tree.Expand(root)

            if x:
                errout.notebook1.SetSelection(0)
                self.model.editor.setStatus('BRM - %s reference(s) found'%x)
        finally:
            wx.wxEndBusyCursor()

    def OnFindDefinition(self, event):
        wx.wxBeginBusyCursor()
        try:
            ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

            defs = ctx.findDefinitionByCoordinates(filename, lineno, column)
            try:
                first = defs.next()
            except StopIteration:
                wx.wxLogError("Couldn't find definition")
                return

            mod, ctr = self.model.editor.openOrGotoModule(first.filename)
            view = mod.getSourceView()
            view.GotoLine(first.lineno-1)
            view.setLinePtr(first.lineno-1)

            errout, tree, root = self.prepareOutputDisplay(
                                 'BRM - Definition for %s'%sel)
            x = 1
            x = errout.addTracebackNode(ReferencesMatcher([first]), x)
            for ref in defs:
                entry = ReferencesMatcher([ref])
                x = errout.addTracebackNode(entry, x)

            tree.SetItemHasChildren(root, true)
            tree.Expand(root)

            if x:
                errout.notebook1.SetSelection(0)
                self.model.editor.setStatus('BRM - %s matches(s) found'%x)
        finally:
            wx.wxEndBusyCursor()

    def OnRename(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        ctx.setRenameMethodPromptCallback(self.renameCallback)

        newname = wx.wxGetTextFromUser('Rename to:', 'Rename', sel)
        if not newname:
            return

        ctx.renameByCoordinates(filename, lineno, column, newname)
        self.saveAndRefresh()

    def renameCallback(self, filename, lineno, colbegin, colend):
        currfile = self.model.filename

        model, ctr = self.model.editor.openOrGotoModule(filename)
        view = model.getSourceView()
        edge = view.PositionFromLine(lineno-1)
        view.SetSelection(edge+colbegin, edge+colend)

        try:
            return wx.wxMessageBox('Cannot deduce the type of highlighted object'
                 ' reference.\nRename this declaration?', 'Rename?',
                 wx.wxYES_NO | wx.wxICON_QUESTION) == wx.wxYES
        finally:
            self.model.editor.openOrGotoModule(currfile)

    def OnExtractMethod(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx = self.model.editor.brm_context
        ctx.extractMethod(*self.getExtractionInfo('Method', 'Extract method'))
        self.saveAndRefresh()

    def OnUndoLast(self, event):
        try:
            self.model.editor.brm_context.undo()
        except bike.UndoStackEmptyException, msg:
            wx.wxLogWarning('Nothing to undo, the undo stack is empty.')
        else:
            self.saveAndRefresh()

    def OnExtractLocalVar(self, event):
        if not self.checkUnsavedChanges():
            return
        
        ctx = self.model.editor.brm_context
        filename, startline, startcol, endline, endcol, variablename = \
              self.getExtractionInfo('Variable', 'Extract variable')
        
        ctx.extractLocalVariable(filename, startline, startcol, endline, endcol, 
                                 variablename)
        self.saveAndRefresh()
        
    def OnInlineLocalVar(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        ctx.inlineLocalVariable(filename, lineno, column)
        
        self.saveAndRefresh()

    def OnGetExprType(self, event):
        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        wx.wxLogMessage(
           `ctx.getTypeOfExpression(filename, lineno, column, column+len(sel))`)
        
PySourceView.PythonSourceView.plugins += (BRMViewPlugin,)


class BRMControllerPlugin:
    """ Plugin class for Controller classes that plublishes the Model interface """
    def __init__(self, controller):
        self.controller = controller

    def actions(self, model):
        return [('-', None, '', ''),
                ('BRM - Import module(s)', self.OnImportModules, '-', ''),
               ]

    def OnImportModules(self, event):
        model = self.controller.getModel()
        cnt = model.plugins['BRM'].importModules()
        if cnt:
            model.editor.setStatus('BRM - Parsed %s modules'%cnt)

PythonControllers.ModuleController.plugins += (BRMControllerPlugin,)


class BRMModelPlugin:
    """ Plugin class for Model classes that creates the context and performs
        various ways importing into the refactoring context. """
    name = 'BRM'
    def __init__(self, model):
        self.model = model

        # the first one created starts the context
        #if not hasattr(model.editor, 'brm_context'):
        if not hasattr(model.editor, 'brm_context') or not model.editor.brm_context:
            model.editor.brm_context = context = bike.init()
            context.setProgressLogger(
                  globals()[Preferences.brmProgressLogger](model.editor))

        if Preferences.brmAddToContextOnOpen:
            self.importModule()
    
    def update(self):
        if Preferences.brmAddContentsToContextOnOpen:
            self.importModules()

    def importModule(self):
        context = self.model.editor.brm_context
        from Explorers.Explorer import TransportError
        try:
            context.load(self.model.checkLocalFile())
            return 1
        except TransportError:
            return 0
    
    def importModules(self):
        cnt = self.importModule()
        context = self.model.editor.brm_context
        if self.model.app == self.model and self.model.app.modules:
            lst = [self.model.checkLocalFile(self.model.moduleFilename(path))
                  for path in self.model.modules.keys()]
            for abspath in lst:
                context.load(abspath)
            cnt = len(lst)
        elif self.model.modelIdentifier == 'Package':
            context.load(os.path.dirname(self.model.checkLocalFile()))
            cnt = '???'
        return cnt

PythonEditorModels.ModuleModel.plugins += (BRMModelPlugin,)


#-------------------------------------------------------------------------------

class ProgressErrOutLogger:
    """ File like logger that uses the Output tab at the bottom of the Editor """
    def __init__(self, editor):
        self.errout = editor.erroutFrm

    def write(self, txt):
        self.errout.appendToOutput(txt)

class ProgressStatusLogger:
    """ File like logger that uses the Editor statusbar as output """
    def __init__(self, editor):
        self.editor = editor
        self._buffer = ''

    def write(self, txt):
        self._buffer += txt
        if txt.endswith('\n'):
            self.editor.setStatus(self._buffer.strip())
            self._buffer = ''

class ReferencesMatcher(ErrorStack.StackErrorParser):
    """ Needed to build "traceback objects" that appear on Find definition """
    def parse(self):
        for ref in self.lines:
            self.error = ['%s%% confidence for: %s:%s'% (
                          ref.confidence, ref.filename, ref.lineno)]
            self.stack.append(ErrorStack.StackEntry(ref.filename, ref.lineno,
                      linecache.getline(ref.filename, ref.lineno), self.error))

#-Explorer plugins--------------------------------------------------------------

class BRMTranspController:
    """ Transport Controller that extends the context menu of Filesystem objects """
    def __init__(self, controller, editor):
        self.controller = controller
        self.editor = editor
    
    def menuDefs(self):
        return [
         (-1, '-', None, '-'),
         (wx.wxNewId(), 'BRM - Import selection', self.OnImportItem, '-'),
         (wx.wxNewId(), 'BRM - Clear refactoring context', self.OnClearContext, '-'),
         (-1, '-', None, '-'),
        ]

    def OnImportItem(self, event):
        list = self.controller.list
        if list.node and self.editor.brm_context:
            nodes = self.controller.getNodesForSelection(list.getMultiSelection())
            for node in nodes:
                filename = node.resourcepath
                # only import dirs and modules
                if os.path.splitext(filename)[1] in ('', '.py'):
                    self.editor.brm_context.load(filename)

    def OnClearContext(self, event):
        self.editor.brm_context = context = bike.init()
        context.setProgressLogger(
              globals()[Preferences.brmProgressLogger](self.editor))

#-------------------------------------------------------------------------------
FileExplorer.FileSysController.plugins += (BRMTranspController,)

#-Preferences-------------------------------------------------------------------

### Current logger
##ProgressLogger = ProgressStatusLogger
