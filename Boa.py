#!/usr/bin/env python
#----------------------------------------------------------------------
# Name:        Boa.py
# Purpose:     The main file for Boa.
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:App:BoaApp

""" The __main__ file for Boa.

Handles creation/initialisation of main objects and commandline arguments """

import sys, os, string, time

t1 = time.time()

# This flag determines if Boa should try to send the filename via a socket to an
# already running instance of Boa. There is another flag under Preferences
# which determines if Boa should create and listen on the socket.
server_mode = 1

trace_mode = 'functions' # 'lines'
trace_save = 'all'#'lastline' # 'all'
def trace_func(frame, event, arg):
    """ Callback function when Boa runs in tracing mode"""
    if frame and tracefile:
        info = '%s|%d|%d|%s|\n' % (frame.f_code.co_filename, frame.f_lineno,
              id(frame), event)
        if trace_save == 'lastline':
            tracefile.seek(0)
        tracefile.write(info)
        tracefile.flush()
    return trace_func

def get_current_frame():
    try: raise 'get_exc_info'
    except: return sys.exc_info()[2].tb_frame.f_back

def sendToRunningBoa(names, host='127.0.0.1', port=50007):
    import socket
    try:
        if names:
            print 'Sent',
        for name in names:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            # do not change files of form [prot]://[path]
            if string.find(name, '://') == -1:
                name = os.path.abspath(name)
            s.send(name)
            print name,
            s.close()
        print
    except socket.error: return 0
    else: return 1

startupErrors = []

import __version__

# Command line options
doDebug = constricted = emptyEditor = 0
startupfile = ''
startupModules = ()
startupEnv = os.environ.get('BOASTARTUP') or os.environ.get('PYTHONSTARTUP')

def processArgs(argv):
    _doDebug = _doRemoteDebugSvr = _constricted = _emptyEditor = 0
    _startupfile = ''
    _startupModules = ()
    import getopt
    optlist, args = getopt.getopt(argv, 'CDTSBO:ERhv', ['Constricted', 'Debug',
          'Trace', 'StartupFile', 'BlockHomePrefs', 'OverridePrefsDirName',
          'EmptyEditor', 'RemoteDebugServer', 'help', 'version'])
    if (('-D', '') in optlist or ('--Debug', '') in optlist) and len(args):
        # XXX should be able to 'debug in running Boa'
        _doDebug = 1
    elif (('-R', '') in optlist or ('--RemoteDebugServer', '') in optlist) and len(args):
        _doRemoteDebugSvr = 1
    elif ('-T', '') in optlist or ('--Trace', '') in optlist:
        print 'Running in trace mode.'
        global tracefile
        tracefile = open('Boa.trace', 'wt')
        tracefile.write(os.getcwd()+'\n')
        trace_func(get_current_frame().f_back, 'call', None)
        trace_func(get_current_frame(), 'call', None)
        if trace_mode == 'functions':
            sys.setprofile(trace_func)
        elif trace_mode == 'lines':
            sys.settrace(trace_func)

    if len(args):
        # XXX Only the first file appears in the list when multiple files
        # XXX are drag/dropped on a Boa shortcut, why?
        _startupModules = args

    if ('-S', '') in optlist or ('--StartupFile', '') in optlist:
        _startupfile = startupEnv

    if ('-C', '') in optlist or ('--Constricted', '') in optlist:
        _constricted = 1

    if ('-E', '') in optlist or ('--EmptyEditor', '') in optlist:
        _emptyEditor = 1

    if ('-h', '') in optlist or ('--help', '') in optlist:
        print 'Version: %s'%__version__.version
        print 'Command-line usage: Boa.py [options] [file1] [file2] ...'
        print '-C, --Constricted:'
        print '\tRuns in constricted mode, overrides the Preference'
        print '-D, --Debug:'
        print '\tRuns the first filename passed on the command-line in the Debugger '
        print '\ton startup'
        print '-T, --Trace:'
        print '\tRuns in traceing mode. Used for tracking down core dumps. Every '
        print '\tfunction call is logged to a file which can later be parsed for '
        print '\ta traceback'
        print '-S, --StartupFile:'
        print '\tExecutes the script pointed to by $BOASTARTUP or '\
              '$PYTHONSTARTUP in'
        print '\tthe Shell namespace. The Editor object is available as sys.boa_ide.'
        print '\tOverrides the Preference'
        print '-B, --BlockHomePrefs:'
        print '\tPrevents the $HOME directory being used '
        print '-O dirname, --OverridePrefsDirName dirname:'
        print '\tSpecify a different directory to load Preferences from.'
        print '\tDefault is .boa and is used if it exists'
        print '\tDirectory will be created (and populated) if it does not exist'
        print '-E, --EmptyEditor:'
        print "\tDon't open the files that were open last time Boa was closed."
        print '-R, --RemoteDebugServer:'
        print "\tRuns the first filename passed on the command-line in a "
        print "\tRemote Debugger Server that can be connected to over a socket.'"

        sys.exit()
    if ('-v', '') in optlist or ('--version', '') in optlist:
        print 'Version: %s'%__version__.version
        sys.exit()

    return (_doDebug, _startupfile, _startupModules, _constricted, _emptyEditor,
            _doRemoteDebugSvr, optlist, args)

# This happens as early as possible (before wxPython loads) to make filename
# transfer to a running Boa as quick as possible and little NS pollution
if __name__ == '__main__' and len(sys.argv) > 1:
    (doDebug, startupfile, startupModules, constricted, emptyEditor, doDebugSvr,
     opts, args) = processArgs(sys.argv[1:])
    if doDebugSvr and startupModules:
        print 'Running as a Remote Debug Server'
        from Debugger.RemoteServer import start
        # XXX username, password optionally should be on the command-line
        start(username='', password='')

        # startupModules contain everything from the first filename and on
        sys.argv = startupModules
        execfile(sys.argv[0], {'__name__': '__main__',
                               '__builtins__': __builtins__})

        sys.exit()
    # Try connect to running Boa using sockets, tnx to Tim Hochberg
    if startupModules and server_mode:
        if sendToRunningBoa(startupModules):
            print 'Transfered arguments to running Boa, exiting.'
            sys.exit()

print 'Starting Boa Constructor v%s'%__version__.version
print 'importing wxPython'

# silence wxPython's bool deprecations
from wxPython import wx
try:
    # wxPy 2.4.0.4 and Py 2.2 and 2.3
    wx.true = True
    wx.false = False
except NameError:
    try:
        # wxPy 2.4.0.4 and Py 2.1
        wx.true = wx.True
        wx.false = wx.False
    except AttributeError:
        # earlier wxPys
        pass

from wxPython.wx import *
wxRegisterId(15999)

# Use package version string as it is the only one containing bugfix version number
import wxPython
# Remove non number/dot characters
wxVersion = wxPython.__version__
for c in wxVersion:
    if c not in string.digits+'.':
        wxVersion = string.replace(wxVersion, c, '')

wxVersion = tuple(map(lambda v: int(v),
                      (string.split(wxVersion, '.')+['0'])[:4]))

if wxVersion < __version__.wx_version:
    wxPySimpleApp()
    wxMessageBox('Sorry! This version of Boa requires at least '\
                 'wxPython %d.%d.%d.%d'%__version__.wx_version,
          'Version error', wxOK | wxICON_ERROR)
    raise 'wxPython >= %d.%d.%d.%d required'%__version__.wx_version

import Preferences, About, Utils
print 'running main...'
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
 'BasicCompanions': [0, '', 'Companions/BasicCompanions.py'],
 'Breakpoint': [0, '', 'Debugger/Breakpoint.py'],
 'Browse': [0, 'History for navigation through the IDE', 'Browse.py'],
 'ButtonCompanions': [0, '', 'Companions/ButtonCompanions.py'],
 'CPPSupport': [0, '', 'Models/CPPSupport.py'],
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
 'ConfigSupport': [0, '', 'Models/ConfigSupport.py'],
 'Constructors': [0,
                  'Constructor signature mixin classes',
                  'Companions/Constructors.py'],
 'ContainerCompanions': [0, '', 'Companions/ContainerCompanions.py'],
 'Controllers': [0, '', 'Models/Controllers.py'],
 'CtrlAlign': [0, '', 'Views/CtrlAlign.py'],
 'CtrlSize': [0, '', 'Views/CtrlSize.py'],
 'Cyclops': [0, '', 'ExternalLib/Cyclops.py'],
 'DAVExplorer': [0, '', 'Explorers/DAVExplorer.py'],
 'DataView': [0,
              'View to manage non visual frame objects',
              'Views/DataView.py'],
 'DebugClient': [0, '', 'Debugger/DebugClient.py'],
 'Debugger': [0,
              'Module for out-of-process debugging of Python apps',
              'Debugger/Debugger.py'],
 'DebuggerControls': [0, '', 'Debugger/DebuggerControls.py'],
 'Designer': [0, 'View to visually design frames', 'Views/Designer.py'],
 'DialogCompanions': [0, '', 'Companions/DialogCompanions.py'],
 'DiffView': [0, '', 'Views/DiffView.py'],
 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'],
 'EditorExplorer': [0, '', 'Explorers/EditorExplorer.py'],
 'EditorHelper': [0, '', 'Models/EditorHelper.py'],
 'EditorModels': [0, '', 'Models/EditorModels.py'],
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
 'FrameCompanions': [0, '', 'Companions/FrameCompanions.py'],
 'GCFrame': [0, '', 'GCFrame.py'],
 'GizmoCompanions': [0, '', 'Companions/GizmoCompanions.py'],
 'HTMLCyclops': [0, '', 'HTMLCyclops.py'],
 'HTMLResponse': [0, '', 'HTMLResponse.py'],
 'HTMLSupport': [0, '', 'Models/HTMLSupport.py'],
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
 'ListCompanions': [0, '', 'Companions/ListCompanions.py'],
 'LoginDialog': [0, '', 'ZopeLib/LoginDialog.py'],
 'ModRunner': [0,
               'Module that runs processes in a variety of ways',
               'ModRunner.py'],
 'OGLViews': [0, '', 'Views/OGLViews.py'],
 'ObjCollection': [0, '', 'Views/ObjCollection.py'],
 'Palette': [1,
             'Top frame which hosts the component palette and help options',
             'Palette.py'],
 'PaletteMapping': [0, '', 'PaletteMapping.py'],
 'PaletteStore': [0,
                  'Storage for variables defining the palette organisation',
                  'PaletteStore.py'],
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
 'PythonControllers': [0, '', 'Models/PythonControllers.py'],
 'PythonEditorModels': [0, '', 'Models/PythonEditorModels.py'],
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
 'UtilCompanions': [0, '', 'Companions/UtilCompanions.py'],
 'Utils': [0, 'General utility routines and classes', 'Utils.py'],
 'XMLSupport': [0, '', 'Models/XMLSupport.py'],
 'XMLView': [0, '', 'Views/XMLView.py'],
 'ZipExplorer': [0, '', 'Explorers/ZipExplorer.py'],
 'ZopeCompanions': [0, '', 'ZopeLib/ZopeCompanions.py'],
 'ZopeEditorModels': [0, '', 'ZopeLib/ZopeEditorModels.py'],
 'ZopeExplorer': [0, '', 'ZopeLib/ZopeExplorer.py'],
 'ZopeFTP': [0, '', 'ZopeLib/ZopeFTP.py'],
 'ZopeViews': [0, '', 'ZopeLib/ZopeViews.py'],
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
 'wxNamespace': [0, '', 'wxNamespace.py'],
 'wxPythonControllers': [0, '', 'Models/wxPythonControllers.py'],
 'wxPythonEditorModels': [0, '', 'Models/wxPythonEditorModels.py'],
 'xmlrpclib': [0, '', 'ExternalLib/xmlrpclib.py']}

class BoaApp(wxApp):
    """ Application object, responsible for the Splash screen, applying command
        line switches, optional logging and creation of the main frames. """

    def __init__(self):
        wxApp.__init__(self, false)

    def OnInit(self):
        wxInitAllImageHandlers()

        wxToolTip_Enable(true)
        try: self.SetAssertMode(wxPYAPP_ASSERT_SUPPRESS)
        except AttributeError: pass # < 2.3.4

        conf = Utils.createAndReadConfig('Explorer')
        modTot = conf.getint('splash', 'modulecount')
        fileTot = len(eval(conf.get('editor', 'openfiles')))

        abt = About.createSplash(None, modTot, fileTot)
        abt.Show()
        # Let the splash screen repaint
        wxYield()

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
        self.SetTopWindow(editor)

        inspector.editor = editor

        conf.set('splash', 'modulecount', `len(sys.modules)`)
        try:
            Utils.writeConfig(conf)
        except IOError, err:
            startupErrors.append('Error writing config file: %s\nPlease '
          'ensure that the Explorer.*.cfg file is not read only.'% str(err))

        if not emptyEditor:
            editor.restoreEditorState()

        self.main.initPalette(inspector, editor)

##            editor.setupToolBar()

        import Help
        print 'attaching wxPython doc strings'
        Help.initWxPyDocStrs()
        if not Preferences.delayInitHelp:
            print 'initialising Help'
            Help.initHelp()

        global constricted
        constricted = constricted or Preferences.suBoaConstricted

        print 'showing main frames <<100/100>>'
        if constricted:
            pos = self.main.GetPosition()
            self.main.Center()
            #editor.Center()
            self.main.SetPosition(pos)
            #editor.SetIcon(self.main.GetIcon())
        else:
            self.main.Show()
            inspector.Show(true)
            # For some reason the splitters have to be visible on GTK before they
            # can be sized.
            inspector.initSashes()

        editor.Show()
        editor.doAfterShownActions()

        # Call startup files after complete editor initialisation
        global startupfile
        if Preferences.suExecPythonStartup and startupEnv:
            startupfile = startupEnv

        editor.shell.execStartupScript(startupfile)

        abt.Destroy()
        del abt


        # Apply command line switches
        if doDebug and startupModules:
            mod = editor.openOrGotoModule(startupModules[0])
            mod.debug()
        elif startupModules:
            for mod in startupModules:
                editor.openOrGotoModule(mod)

        editor.setupToolBar()

        editor.setStatus('Startup time: %5.2f' % (time.time() - t1))

        Utils.showTip(self.main.editor)

        if Preferences.logStdStreams:
            sys.stderr = Utils.ErrorLoggerPF()
            sys.stdout = Utils.OutputLoggerPF()

        if startupErrors:
            for error in startupErrors:
                wxLogError(error)
            wxLogError('\nThere were errors during startup, please click "Details"')

        if wxPlatform == '__WXMSW__':
            self.tbicon = wxTaskBarIcon()
            self.tbicon.SetIcon(self.main.GetIcon(), 'Boa Constructor')
            EVT_TASKBAR_LEFT_DCLICK(self.tbicon, self.OnTaskBarActivate)
            EVT_TASKBAR_RIGHT_UP(self.tbicon, self.OnTaskBarMenu)
            EVT_MENU(self.tbicon, self.TBMENU_RESTORE, self.OnTaskBarActivate)
            EVT_MENU(self.tbicon, self.TBMENU_CLOSE, self.OnTaskBarClose)
            EVT_MENU(self.tbicon, self.TBMENU_ABOUT, self.OnTaskBarAbout)

        if Preferences.exWorkingDirectory:
            os.chdir(Preferences.exWorkingDirectory)

        editor.assureRefreshed()

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
        if not self.main.IsShown():
            self.main.editor.restore()
        else:
            self.main.restore()

    def OnTaskBarClose(self, event):
        self.main.Close()
        self.ProcessIdle()

    def OnTaskBarAbout(self, event):
        self.main.editor.OnHelpAbout(event)

def main(argv=None):
    # XXX Custom installations, should distutil libs be used for this ?
    # XXX Binary test is no longer valid, maybe type of __import__ function
    # Only install if it's not a 'binary' distribution
    if Preferences.installBCRTL and hasattr(wx, '__file__'):
        join, dirname = os.path.join, os.path.dirname
        wxPythonPath = dirname(wx.__file__)
        wxPythonLibPath = join(dirname(wx.__file__), 'lib')
        pythonLibPath = dirname(wxPythonPath)
        try:
            # Install/update run time libs if necessary
            Utils.updateDir(join(Preferences.pyPath, 'bcrtl'),
                  join(wxPythonLibPath, 'bcrtl'))
            ## Install debugger hard breakpoint hook
            ##Utils.updateFile(join(Preferences.pyPath, 'Debugger', 'bcdb.lib.py'),
            ##                 join(pythonLibPath, 'bcdb.py'))
        except Exception, error:
            startupErrors.extend(['Error while installing Run Time Libs:',
            '    '+str(error),
            '\nMake sure you have sufficient rights to copy these files, and that ',
            'the files are not read only. You may turn off this attempted ',
            'installation in prefs.rc.py : installBCRTL'])

    if argv is not None:
        global doDebug, startupfile, startupModules
        doDebug, startupfile, startupModules, constricted, opts, args = \
              processArgs(argv)
    try:
        app = BoaApp()
    except Exception, error:
        wxMessageBox(str(error), 'Error on startup')
        raise

    #if hasattr(sys, 'breakpoint'): sys.breakpoint()
    app.MainLoop()

    # Clean up (less warnings)
    if hasattr(app, 'tbicon'):
        del app.tbicon
    if not hasattr(sys, 'boa_debugger'):
        if Preferences.logStdStreams:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__
        Preferences.cleanup()
    del app

if __name__ == '__main__':
    main()
