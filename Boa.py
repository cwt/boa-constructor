#!/usr/bin/env python  
#----------------------------------------------------------------------
# Name:        Boa.py
# Purpose:     The main file for Boa.
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:App:BoaApp

# Once upon a time
# the story starts
# in a few files far away

""" The __main__ file for Boa.

Handles creation/initialisation of main objects and commandline arguments """

import sys, os, string

# should Boa run as a 'server' and receive and open modules from other Boas 
# started with module command line arguments
server_mode = 1

def trace_func(frame, event, arg):
    """ Callback function when Boa runs in tracing mode"""
    if frame:
        info = '%s|%d|%d|%s|%s\n' % (frame.f_code.co_filename, frame.f_lineno, 
              id(frame), event, `arg`)
        tracefile.write(info)
        tracefile.flush()
    return trace_func

def get_current_frame():
    try: 1 + ''  # raise an exception
    except: return sys.exc_info()[2].tb_frame

def sendToRunningBoa(names, host='127.0.0.1', port=50007):
    import socket
    try:
        for name in names:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            # do not change files of form [prot]://[path]
            if string.find(name, '://') == -1:
                name = os.path.abspath(name)
            s.send(name)
            s.close()    
    except socket.error: return 0
    else: return 1
        
startupErrors = []

# Command line options
doDebug = constricted = 0
startupfile = ''
startupModules = ()

def processArgs(argv):
    _doDebug = _constricted = 0
    _startupfile = ''
    _startupModules = ()
    import getopt
    optlist, args = getopt.getopt(argv, 'CDTs', ['Constricted', 'Debug', 'Trace', 
          'startupscript'])
    if (('-D', '') in optlist or ('--Debug', '') in optlist) and len(args):
        # XXX should be able to 'debug in running Boa'
        _doDebug = 1
    elif ('-T', '') in optlist or ('--Trace', '') in optlist:
        global tracefile
        tracefile = open('Boa.trace', 'wt')
        tracefile.write(os.getcwd()+'\n')
        trace_func(get_current_frame(), 'call', None)
        sys.setprofile(trace_func)

    if len(args):
        # XXX Only the first file appears in the list when multiple files
        # XXX are drag/dropped on a Boa shortcut, why?
        _startupModules = args

    if ('-s', '') in optlist or ('--startupfile', '') in optlist:
        _startupfile = os.environ.get('BOASTARTUP') or \
                       os.environ.get('PYTHONSTARTUP')

    if ('-C', '') in optlist or ('--Constricted', '') in optlist:
        _constricted = 1

    return _doDebug, _startupfile, _startupModules, _constricted

# This happens as early as possible (before wxPython loads) to make filename
# transfer to a running Boa as quick as possible
if __name__ == '__main__' and len(sys.argv) > 1:
    doDebug, startupfile, startupModules, constricted = processArgs(sys.argv[1:])
    # Try connect to running Boa using sockets, tnx to Tim Hochberg
    if startupModules and server_mode:
        if sendToRunningBoa(startupModules):
            print 'Transfered arguments to running Boa, exiting.'
            sys.exit()

from __version__ import ver
print 'Starting Boa Constructor v%s'%ver

from wxPython.wx import *

if (wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_NUMBER) != (2, 3, 0):
    wxPySimpleApp()
    wxMessageBox('Sorry! This version of Boa requires wxPython 2.3.0', 
          'Version error', wxOK | wxICON_ERROR)
    raise 'wxPython 2.3.0 required'

import Preferences, About, Utils

# XXX auto created frames (main frame handled currently)
# XXX More property editors!
# XXX More companion classes! $

# XXX Find: Exceptions should not cancel the search

# XXX Mechanism to detect file date changes external of boa
# XXX Possibly on Explorer level, checking before saving on systems where
# XXX getting a time stamp makes sense and is available

# XXX Refactor PropertyEditor/Companion/Inspector interfaces

# XXX Support IDLE extensions

# XXX Code completion
# XXX     self.qwerty = qwerty
# XXX     wipes '= qwerty' when qwerty is selected

# XXX Renaming Boa.jpg in root fails

# XXX Save as after app is closed

# XXX Add wxImageBitmap, delete (prints class link error)


modules ={'About': [0, 'About box and Splash screen', 'About.py'],
 'AppViews': [0, 'Views for the AppModel', 'Views/AppViews.py'],
 'BaseCompanions': [0, '', 'Companions/BaseCompanions.py'],
 'Breakpoint': [0, '', 'Debugger/Breakpoint.py'],
 'Browse': [0, 'History for navigation through the IDE', 'Browse.py'],
 'CVSExplorer': [0, '', 'Explorers/CVSExplorer.py'],
 'CVSResults': [0, '', 'Explorers/CVSResults.py'],
 'ChildProcessClient': [0, '', 'Debugger/ChildProcessClient.py'],
 'ChildProcessServer': [0, '', 'Debugger/ChildProcessServer.py'],
 'ChildProcessServerStart': [0, '', 'Debugger/ChildProcessServerStart.py'],
 'ClassBrowser': [0,
                  'Frame that displays the wxPython object hierarchy by Class and Module',
                  'ClassBrowser.py'],
 'CollectionEdit': [0, '', 'Views/CollectionEdit.py'],
 'ComCompanions': [0,
                   'Companion classes for COM (win32 only)',
                   'Companions/ComCompanions.py'],
 'Companions': [0,
                'Most visual wxPython class companions ',
                'Companions/Companions.py'],
 'Constructors': [0,
                  'Constructor signature mixin classes',
                  'Companions/Constructors.py'],
 'Controllers': [0, 'Controllers for the Models and Views', 'Controllers.py'],
 'CtrlAlign': [0, 'Aligns a group of controls', 'CtrlAlign.py'],
 'CtrlSize': [0, 'Sizes a group of controls', 'CtrlSize.py'],
 'Cyclops': [0, '', 'ExternalLib/Cyclops.py'],
 'DAVExplorer': [0, '', 'Explorers/DAVExplorer.py'],
 'DataView': [0,
              'View to manage non visual frame objects',
              'Views/DataView.py'],
 'DebugClient': [0, '', 'Debugger/DebugClient.py'],
 'Debugger': [0,
              'Module for in-process debugging of wxPython and Python apps',
              'Debugger/Debugger.py'],
 'Designer': [0, 'View to visually design frames', 'Views/Designer.py'],
 'DialogCompanions': [0, '', 'Companions/DialogCompanions.py'],
 'DiffView': [0, '', 'Views/DiffView.py'],
 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'],
 'EditorExplorer': [0, '', 'Explorers/EditorExplorer.py'],
 'EditorHelper': [0, 'Module defining Editor constants', 'EditorHelper.py'],
 'EditorModels': [0,
                  'Model classes. Models loosely represent source types.',
                  'EditorModels.py'],
 'EditorUtils': [0,
                 'Specialised ToolBar and StatusBar controls for the Editor',
                 'EditorUtils.py'],
 'EditorViews': [0,
                 'Main module for View classes that work with Models',
                 'Views/EditorViews.py'],
 'Enumerations': [0, '', 'PropEdit/Enumerations.py'],
 'ErrorStack': [0, 'Various forms of error parsers', 'ErrorStack.py'],
 'ErrorStackFrm': [0, '', 'ErrorStackFrm.py'],
 'EventCollections': [0, '', 'Companions/EventCollections.py'],
 'Explorer': [0,
              'Specialised visual controls for the Explorer (Tree, list and splitter)',
              'Explorers/Explorer.py'],
 'ExplorerNodes': [0, '', 'Explorers/ExplorerNodes.py'],
 'ExtMethDlg': [0, 'Dialog for ExternalMethods', 'ZopeLib/ExtMethDlg.py'],
 'FTPExplorer': [0, '', 'Explorers/FTPExplorer.py'],
 'FileDlg': [0, 'Replacement for the standard file dialog. ', 'FileDlg.py'],
 'FileExplorer': [0, '', 'Explorers/FileExplorer.py'],
 'FindReplaceDlg': [0, '', 'FindReplaceDlg.py'],
 'FindReplaceEngine': [0, '', 'FindReplaceEngine.py'],
 'FindResults': [0, '', 'FindResults.py'],
 'GCFrame': [0, '', 'GCFrame.py'],
 'HTMLCyclops': [0, '', 'HTMLCyclops.py'],
 'HTMLResponse': [0, '', 'HTMLResponse.py'],
 'Help': [0, 'Interactive help frame', 'Help.py'],
 'ImageStore': [0,
                'Centralised point to load images (cached/zipped/etc)',
                'ImageStore.py'],
 'ImageViewer': [0, '', 'ZopeLib/ImageViewer.py'],
 'InProcessClient': [0, '', 'Debugger/InProcessClient.py'],
 'Infofields': [0, '', 'Infofields.py'],
 'InspectableViews': [0, '', 'Views/InspectableViews.py'],
 'Inspector': [0,
               "Inspects object's constructor/properties/events/parents",
               'Inspector.py'],
 'InspectorEditorControls': [0, '', 'PropEdit/InspectorEditorControls.py'],
 'IsolatedDebugger': [0, '', 'Debugger/IsolatedDebugger.py'],
 'LoginDialog': [0, '', 'ZopeLib/LoginDialog.py'],
 'ModRunner': [0,
               'Module that runs processes in a variety of ways',
               'ModRunner.py'],
 'OGLViews': [0, '', 'Views/OGLViews.py'],
 'ObjCollection': [0, '', 'Views/ObjCollection.py'],
 'OldDebugger': [0, '', 'Debugger/OldDebugger.py'],
 'Palette': [1,
             'Top frame which hosts the component palette and help options',
             'Palette.py'],
 'PaletteMapping': [0, '', 'PaletteMapping.py'],
 'PaletteStore': [0,
                  'Storage for variables defining the palette organisation',
                  'PaletteStore.py'],
 'PhonyApp': [0, '', 'PhonyApp.py'],
 'Preferences': [0,
                 'Central store of customiseable properties',
                 'Preferences.py'],
 'PrefsExplorer': [0, '', 'Explorers/PrefsExplorer.py'],
 'ProcessProgressDlg': [0, '', 'ProcessProgressDlg.py'],
 'ProfileView': [0, '', 'Views/ProfileView.py'],
 'PropDlg': [0, '', 'ZopeLib/PropDlg.py'],
 'PropertyEditors': [0,
                     'Module defining property editors used in the Inspector',
                     'PropEdit/PropertyEditors.py'],
 'PySourceView': [0, '', 'Views/PySourceView.py'],
 'PythonInterpreter': [0, '', 'ExternalLib/PythonInterpreter.py'],
 'RTTI': [0, 'Introspection code. Run time type info', 'RTTI.py'],
 'RemoteClient': [0, '', 'Debugger/RemoteClient.py'],
 'RemoteDialog': [0, '', 'Debugger/RemoteDialog.py'],
 'RunCyclops': [0, '', 'RunCyclops.py'],
 'SSHExplorer': [0, '', 'Explorers/SSHExplorer.py'],
 'STCStyleEditor': [0, '', 'Views/STCStyleEditor.py'],
 'Search': [0, '', 'Search.py'],
 'SelectionTags': [0,
                   'Controls and objects that manage the visual selection in the Designer',
                   'Views/SelectionTags.py'],
 'ShellEditor': [0, 'Python Interpreter Shell window', 'ShellEditor.py'],
 'Signature': [0, '', 'ExternalLib/Signature.py'],
 'SourceViews': [0, '', 'Views/SourceViews.py'],
 'StyledTextCtrls': [0,
                     'Mixin classes to use features of Scintilla',
                     'Views/StyledTextCtrls.py'],
 'Tasks': [0, '', 'Debugger/Tasks.py'],
 'Tests': [0, '', 'Tests.py'],
 'UserCompanions': [0, '', 'Companions/UserCompanions.py'],
 'UtilCompanions': [0, '', 'Companions/UtilCompanions.py'],
 'Utils': [0, 'General utility routines and classes', 'Utils.py'],
 'XMLView': [0, '', 'Views/XMLView.py'],
 'ZipExplorer': [0, '', 'Explorers/ZipExplorer.py'],
 'ZopeCompanions': [0, '', 'Companions/ZopeCompanions.py'],
 'ZopeEditorModels': [0,
                      'Editor models for Zope objects',
                      'ZopeEditorModels.py'],
 'ZopeExplorer': [0, '', 'Explorers/ZopeExplorer.py'],
 'ZopeFTP': [0, '', 'ZopeLib/ZopeFTP.py'],
 'ZopeViews': [0, '', 'Views/ZopeViews.py'],
 'babeliser': [0, '', 'ExternalLib/babeliser.py'],
 'methodparse': [0,
                 'Module responsible for parsing code inside generated methods',
                 'methodparse.py'],
 'moduleparse': [0,
                 'For parsing a whole module into Module, classes and functions',
                 'moduleparse.py'],
 'ndiff': [0, '', 'ExternalLib/ndiff.py'],
 'popen2import': [0, '', 'popen2import.py'],
 'reindent': [0, '', 'ExternalLib/reindent.py'],
 'relpath': [0, '', 'relpath.py'],
 'sender': [0, '', 'sender.py'],
 'sourceconst': [0, 'Source generation constants', 'sourceconst.py'],
 'xmlrpclib': [0, '', 'ExternalLib/xmlrpclib.py']}

class BoaApp(wxApp):
    """ Application object, responsible for the Splash screen, applying command 
        line switches, optional logging and creation of the main frames. """

    def __init__(self):
        wxApp.__init__(self, false)

    def OnInit(self):
        wxInitAllImageHandlers()

        wxToolTip_Enable(true)

        abt = About.createSplash(None)
        abt.Show(true)
        try:
            # Let the splash screen repaint
            #wxYield()

            print 'creating Palette'
            import Palette
            self.main = Palette.BoaFrame(None, -1, self)

            print 'creating Inspector'
            import Inspector
            inspector = Inspector.InspectorFrame(self.main)
    
            print 'creating Editor'
            import Editor
            editor = Editor.EditorFrame(self.main, -1, inspector, wxMenu(), 
                self.main.componentSB, self, self.main)

            self.main.initPalette(inspector, editor)
            
            editor.setupToolBar()

            import Help
            print 'attaching wxPython doc strings'
            Help.initWxPyDocStrs()
            if not Preferences.delayInitHelp:
                print 'initialising Help'
                Help.initHelp()

            print 'showing main frames'
            if constricted:
                pos = self.main.GetPosition()
                self.main.Center()
                editor.Center()
                self.main.SetPosition(pos)
                #editor.SetIcon(self.main.GetIcon())
            else:
                self.main.Show(true)
                inspector.Show(true)
                # For some reason the splitters have to be visible on GTK before they
                # can be sized.
                inspector.initSashes()

            editor.Show(true)
            self.SetTopWindow(editor)

            # Call startup files after complete editor initialisation
            editor.shell.execStartupScript(startupfile)            
        finally:
            abt.Destroy()
            del abt

        # Open info text files if run for the first time
        if os.path.exists('1stTime'):
            try:
                editor.openOrGotoModule('README.txt')
                editor.openOrGotoModule('Changes.txt')
                os.remove('1stTime')
            except:
                print 'Could not load intro text files'

        # Apply command line switches
        if doDebug and startupModules:
            mod = editor.openModule(startupModules[0])
            mod.debug()
        elif startupModules:
            for mod in startupModules:
                editor.openOrGotoModule(mod)
            editor.setupToolBar()

        Utils.showTip(self.main.editor)

        if Preferences.logStdStreams:
            sys.stderr = Utils.ErrorLoggerPF()
            sys.stdout = Utils.OutputLoggerPF()

        if startupErrors:
            for error in startupErrors:
                wxLogError(error)
            wxLogError('There were errors during startup, please click "Details"')

        if wxPlatform == '__WXMSW__':
            self.tbicon = wxTaskBarIcon()
            self.tbicon.SetIcon(self.main.GetIcon(), 'Boa Constructor')
            EVT_TASKBAR_LEFT_DCLICK(self.tbicon, self.OnTaskBarActivate)
            EVT_TASKBAR_RIGHT_UP(self.tbicon, self.OnTaskBarMenu)
            EVT_MENU(self.tbicon, self.TBMENU_RESTORE, self.OnTaskBarActivate)
            EVT_MENU(self.tbicon, self.TBMENU_CLOSE, self.OnTaskBarClose)
            EVT_MENU(self.tbicon, self.TBMENU_ABOUT, self.OnTaskBarAbout)

        return true

    [TBMENU_RESTORE, TBMENU_CLOSE, TBMENU_ABOUT] = Utils.wxNewIds(3)

    def OnTaskBarMenu(self, event):
        menu = wxMenu()
        menu.Append(self.TBMENU_RESTORE, 'Restore Boa Constructor')
        menu.Append(self.TBMENU_CLOSE,   'Exit')
        menu.Append(-1, '')
        menu.Append(self.TBMENU_ABOUT,   'About')
        self.tbicon.PopupMenu(menu)
        menu.Destroy()

    def OnTaskBarActivate(self, event):
        if self.main.IsIconized():
            self.main.Iconize(false)
        if not self.main.IsShown():
            self.main.Show(true)
        self.main.Raise()

    def OnTaskBarClose(self, event):
        self.main.Close()
        self.ProcessIdle()
    
    def OnTaskBarAbout(self, event):
        self.main.editor.OnHelpAbout(event)

def main(argv=None):
    # Custom installations
    # Only install if it's not a 'binary' distribution
    if Preferences.installBCRTL and hasattr(wx, '__file__'):
        wxPythonLibPath = os.path.join(os.path.dirname(wx.__file__), 'lib')
        try:
            # Install/update run time libs if necessary
            Utils.updateDir(os.path.join(Preferences.pyPath, 'bcrtl'),
                 os.path.join(wxPythonLibPath, 'bcrtl'))
        except Exception, error:
            startupErrors.extend(['Error while installing Run Time Libs:',
            '    '+str(error), 
            'Make sure you have sufficient rights to copy these files, and that ',
            'the files are not read only. You may turn off this attempted ',
            'installation in prefs.rc.py : installBCRTL'])

    if argv is not None:
        global doDebug, startupfile, startupModules
        doDebug, startupfile, startupModules, constricted = processArgs(argv)
    try:
        app = BoaApp()
    except Exception, error:
        wxMessageBox(str(error), 'Error on startup')
        raise
    # This looping over the MainLoop is needed by the old debugger
    app.quit = false
    while not app.quit:
        app.MainLoop()
    # Clean up (less warnings)
    if hasattr(app, 'tbicon'):
        del app.tbicon
    if Preferences.logStdStreams:
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__
    Preferences.IS.cleanup()

if __name__ == '__main__' or hasattr(wxApp, 'debugger'):
    main()
