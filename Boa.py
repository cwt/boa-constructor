#----------------------------------------------------------------------
# Name:        Boa.py
# Purpose:     The main file for Boa.
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:App:BoaApp

# Once upon a time
# in a few files far away
# the story starts

import sys, os

def trace_func(frame, event, arg):
    """ Callback function when Boa runs in tracing mode"""
    if frame:
        info = '%s|%d|%d|%s|%s\n' % (frame.f_code.co_filename, frame.f_lineno, id(frame), event, `arg`)
        tracefile.write(info)
        tracefile.flush()
    return trace_func

def get_current_frame():
    try:
        1 + ''  # raise an exception
    except:
        return sys.exc_info()[2].tb_frame

# Command line options
doDebug = 0
startupModules = ()
if len(sys.argv) > 1:
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'DT')
    if ('-D', '') in optlist and len(args):
        doDebug = 1
    elif ('-T', '') in optlist:
        tracefile = open('Boa.trace', 'wt')
        tracefile.write(os.getcwd()+'\n')
        trace_func(get_current_frame(), 'call', None)
        sys.setprofile(trace_func)
    elif len(args):
        # XXX Only the first file appears in the list when multiple files
        # XXX are drag/dropped on a Boa shortcut, why?
        startupModules = args

startupErrors = []

# Custom installations

# Only install if it's not a 'binary' distribution
import wxPython
if hasattr(wxPython, '__file__'):
    boaPath = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))
    wxPythonLibPath = os.path.join(os.path.dirname(wxPython.__file__), 'lib')
    # Install anchors if necessary
    try:
        import wxPython.lib.anchors
    except ImportError:
        print 'installing Anchors'
        import shutil
        shutil.copy(os.path.join(boaPath, 'anchors.py'), wxPythonLibPath)
        import wxPython.lib.anchors

print 'importing Preferences'
import Preferences
from wxPython.wx import *
import About
import Utils

if hasattr(wxPython, '__file__'):
    try:
        # Install/update run time libs if necessary
        Utils.updateDir(os.path.join(boaPath, 'bcrtl'),
             os.path.join(wxPythonLibPath, 'bcrtl'))
    except Exception, error:
        startupErrors.extend(['Error while installing Run Time Libs:', 
                              '    '+str(error)])

# XXX Remaining milestones before alpha
# XXX auto created frames (main frame handled currently)
# XXX More property editors!
# XXX More companion classes! $

pad = 80*' '

modules ={'About': [0, '', 'About.py'],
 'AppModuleProps': [0, '', 'AppModuleProps.py'],
 'AppViews': [0, '', 'Views/AppViews.py'],
 'BaseCompanions': [0, '', 'Companions/BaseCompanions.py'],
 'Browse': [0, '', 'Browse.py'],
 'CVSExplorer': [0, '', 'Explorers/CVSExplorer.py'],
 'CVSResults': [0, '', 'Explorers/CVSResults.py'],
 'ClassBrowser': [0, '', 'ClassBrowser.py'],
 'CollectionEdit': [0, '', 'Views/CollectionEdit.py'],
 'ComCompanions': [0, '', 'Companions/ComCompanions.py'],
 'Companions': [0, '', 'Companions/Companions.py'],
 'Constructors': [0, '', 'Companions/Constructors.py'],
 'CtrlAlign': [0, '', 'CtrlAlign.py'],
 'CtrlSize': [0, '', 'CtrlSize.py'],
 'DataView': [0, '', 'Views/DataView.py'],
 'Debugger': [0, '', 'Debugger/Debugger.py'],
 'Designer': [0, '', 'Views/Designer.py'],
 'DialogCompanions': [0, '', 'Companions/DialogCompanions.py'],
 'DiffView': [0, '', 'Views/DiffView.py'],
 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'],
 'EditorModels': [0, '', 'EditorModels.py'],
 'EditorViews': [0, '', 'Views/EditorViews.py'],
 'Enumerations': [0, '', 'PropEdit/Enumerations.py'],
 'ErrorStack': [0, '', 'ErrorStack.py'],
 'ErrorStackFrm': [0, '', 'ErrorStackFrm.py'],
 'EventCollections': [0, '', 'Companions/EventCollections.py'],
 'Explorer': [0, '', 'Explorers/Explorer.py'],
 'ExplorerNodes': [0, '', 'Explorers/ExplorerNodes.py'],
 'ExtMethDlg': [0, '', 'ZopeLib/ExtMethDlg.py'],
 'FTPExplorer': [0, '', 'Explorers/FTPExplorer.py'],
 'FileDlg': [0, '', 'FileDlg.py'],
 'FileExplorer': [0, '', 'Explorers/FileExplorer.py'],
 'GCFrame': [0, '', 'GCFrame.py'],
 'HTMLCyclops': [0, '', 'HTMLCyclops.py'],
 'Help': [0, '', 'Help.py'],
 'HelpCompanions': [0, '', 'Companions/HelpCompanions.py'],
 'ImageStore': [0, '', 'ImageStore.py'],
 'ImageViewer': [0, '', 'ZopeLib/ImageViewer.py'],
 'Infofields': [0, '', 'Infofields.py'],
 'InspectableViews': [0, '', 'Views/InspectableViews.py'],
 'Inspector': [0,
               "Inspects object's constructor/properties/events/parents",
               'Inspector.py'],
 'InspectorEditorControls': [0, '', 'PropEdit/InspectorEditorControls.py'],
 'LoginDialog': [0, '', 'ZopeLib/LoginDialog.py'],
 'ModRunner': [0, '', 'ModRunner.py'],
 'OGLViews': [0, '', 'Views/OGLViews.py'],
 'ObjCollection': [0, '', 'Views/ObjCollection.py'],
 'Palette': [1, '', 'Palette.py'],
 'PaletteMapping': [0, '', 'PaletteMapping.py'],
 'PhonyApp': [0, '', 'PhonyApp.py'],
 'Preferences': [0, '', 'Preferences.py'],
 'PrefsGTK': [0, '', 'PrefsGTK.py'],
 'PrefsKeys': [0, '', 'PrefsKeys.py'],
 'PrefsMSW': [0, '', 'PrefsMSW.py'],
 'ProcessProgressDlg': [0, '', 'ProcessProgressDlg.py'],
 'ProfileView': [0, '', 'Views/ProfileView.py'],
 'PropDlg': [0, '', 'ZopeLib/PropDlg.py'],
 'PropertyEditors': [0, '', 'PropEdit/PropertyEditors.py'],
 'PySourceView': [0, '', 'Views/PySourceView.py'],
 'PythonInterpreter': [0, '', 'ExternalLib/PythonInterpreter.py'],
 'RTTI': [0, '', 'RTTI.py'],
 'RunCyclops': [0, '', 'RunCyclops.py'],
 'SSHExplorer': [0, '', 'Explorers/SSHExplorer.py'],
 'Search': [0, '', 'Search.py'],
 'SelectionTags': [0, '', 'Views/SelectionTags.py'],
 'ShellEditor': [0, '', 'ShellEditor.py'],
 'StyledTextCtrls': [0, '', 'Views/StyledTextCtrls.py'],
 'Tests': [0, '', 'Tests.py'],
 'UserCompanions': [0, '', 'Companions/UserCompanions.py'],
 'UtilCompanions': [0, '', 'Companions/UtilCompanions.py'],
 'Utils': [0, '', 'Utils.py'],
 'ZipExplorer': [0, '', 'Explorers/ZipExplorer.py'],
 'ZopeCompanions': [0, '', 'Companions/ZopeCompanions.py'],
 'ZopeExplorer': [0, '', 'Explorers/ZopeExplorer.py'],
 'ZopeFTP': [0, '', 'ZopeLib/ZopeFTP.py'],
 'curry': [0, '', 'curry.py'],
 'methodparse': [0, '', 'methodparse.py'],
 'moduleparse': [0, '', 'moduleparse.py'],
 'ndiff': [0, '', 'ExternalLib/ndiff.py'],
 'popen2import': [0, '', 'popen2import.py'],
 'relpath': [0, '', 'relpath.py'],
 'sender': [0, '', 'sender.py'],
 'sourceconst': [0, '', 'sourceconst.py']}

class BoaApp(wxApp):
    def __init__(self, redirect=false):
        wxApp.__init__(self, redirect)

    def OnInit(self):
        wxInitAllImageHandlers()

        wxToolTip_Enable(true)

        abt = About.createSplash(None)
        abt.Show(true)
        try:
            # Let the splash screen repaint
            wxYield()
            import Palette

            print 'creating Palette'
            self.main = Palette.BoaFrame(None, -1, self)

            self.main.Show(true)
            self.SetTopWindow(self.main)

            self.main.inspector.Show(true)
            # For some reason the splitters have to be visible on GTK before they
            # can be sized.
            self.main.inspector.initSashes()
            self.main.editor.Show(true)
            
        finally:
            abt.Show(false)
            abt.Destroy()
        # Open info text files if run for the first time
        if os.path.exists('1stTime'):
            try:
                self.main.editor.openOrGotoModule('README.txt')
                self.main.editor.openOrGotoModule('Changes.txt')
                os.remove('1stTime')
            except:
                print 'Could not load intro text files'

        # Apply command line switches
        if doDebug:
            mod = self.main.editor.openModule(args[0])
            mod.debug()
        elif startupModules:
            for mod in startupModules:
                self.main.editor.openModule(mod)

        Utils.showTip(self.main.editor)

        if Preferences.logStdStreams:
            from ShellEditor import PseudoFile
            class LoggerPF(PseudoFile):
                def __init__(self, logFunc, realStdStream, mayDoRecord = true):
                    self.logFunc = logFunc
                    self.realStrm = realStdStream
                    self.mayDoRecord = mayDoRecord
                def write(self, s):
                    ss = string.rstrip(s)
                    if ss:
                        if self.mayDoRecord and Preferences.recordModuleCallPoint:
                            frame = get_current_frame()
                            ss = '%s : <<%s, %d>>' % \
                                (ss,
                                 frame.f_back.f_back.f_code.co_filename,
                                 frame.f_back.f_back.f_lineno)
                        self.logFunc((ss+pad)[:80]+string.strip((ss+pad)[80:]))
                        if not self.mayDoRecord:
                            s = s + '\n'
                        self.realStrm.write(s)

            sys.stderr = LoggerPF(wxLogError, sys.__stderr__, false)
            sys.stdout = LoggerPF(wxLogMessage, sys.__stdout__)
        
        if startupErrors:
            for error in startupErrors:
                wxLogError(error)

        return true


def main():
    app = BoaApp(0)
    app.quit = false
    while not app.quit:
        app.MainLoop()

if __name__ == '__main__' or hasattr(wxApp, 'debugger'):
    main()
