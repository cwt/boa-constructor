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
    if frame:
        info = '%s|%d|%d|%s|%s\n' % (frame.f_code.co_filename, frame.f_lineno, id(frame), event, `arg`)
        tracefile.write(info)
        tracefile.flush()
    return trace_func

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
        try:
            1 + ''  # raise an exception
        except:
            frame = sys.exc_info()[2].tb_frame
            print frame
            trace_func(frame, 'call', None)#.f_back
        sys.setprofile(trace_func)
    elif len(args):
        # XXX Only the first file appears in the list when multiple files
        # XXX are drag/dropped on a Boa shortcut, why?
        startupModules = args

### Install anchors if necessary
##try:
##    import wxPython.lib.anchors
##except ImportError:
##    print 'installing Anchors'
##    import shutil, wxPython
##    shutil.copy(os.path.join(os.path.abspath(os.path.join(os.getcwd(), sys.path[0])), 
##                'anchors.py'), os.path.join(os.path.dirname(wxPython.__file__), 'lib'))
##    import wxPython.lib.anchors

print 'importing Prefs'
import Preferences
from wxPython.wx import *
import About
print 'importing Editor'
import Utils

#currentMouseOverTip = ''

# XXX Remaining milestones before alpha
# XXX auto created frames (main frame handled currently)
# XXX sub-properties apply changes
# XXX More property editors!
# XXX More companion classes! $
# XXX OGL Views show content bug

#import Palette

modules ={'ExplorerNodes': [0, '', 'Explorers/ExplorerNodes.py'], 'EditorViews': [0, '', 'Views/EditorViews.py'], 'Inspector': [0, "Inspects object's constructor/properties/events/parents", 'Inspector.py'], 'Infofields': [0, '', 'Infofields.py'], 'ErrorStack': [0, '', 'ErrorStack.py'], 'AppModuleProps': [0, '', 'AppModuleProps.py'], 'UtilCompanions': [0, '', 'Companions/UtilCompanions.py'], 'HTMLCyclops': [0, '', 'HTMLCyclops.py'], 'ZopeFTP': [0, '', 'ZopeLib/ZopeFTP.py'], 'CtrlAlign': [0, '', 'CtrlAlign.py'], 'FileDlg': [0, '', 'FileDlg.py'], 'Constructors': [0, '', 'Companions/Constructors.py'], 'Utils': [0, '', 'Utils.py'], 'ExtMethDlg': [0, '', 'ZopeLib/ExtMethDlg.py'], 'CollectionEdit': [0, '', 'Views/CollectionEdit.py'], 'sender': [0, '', 'sender.py'], 'ProcessProgressDlg': [0, '', 'ProcessProgressDlg.py'], 'ProfileView': [0, '', 'Views/ProfileView.py'], 'RunCyclops': [0, '', 'RunCyclops.py'], 'popen2import': [0, '', 'popen2import.py'], 'ClassBrowser': [0, '', 'ClassBrowser.py'], 'RTTI': [0, '', 'RTTI.py'], 'PySourceView': [0, '', 'Views/PySourceView.py'], 'EventCollections': [0, '', 'Companions/EventCollections.py'], 'GCFrame': [0, '', 'GCFrame.py'], 'PythonInterpreter': [0, '', 'ExternalLib/PythonInterpreter.py'], 'SSHExplorer': [0, '', 'Explorers/SSHExplorer.py'], 'ModRunner': [0, '', 'ModRunner.py'], 'SelectionTags': [0, '', 'Views/SelectionTags.py'], 'DiffView': [0, '', 'Views/DiffView.py'], 'PrefsGTK': [0, '', 'PrefsGTK.py'], 'About': [0, '', 'About.py'], 'PhonyApp': [0, '', 'PhonyApp.py'], 'InspectorEditorControls': [0, '', 'PropEdit/InspectorEditorControls.py'], 'methodparse': [0, '', 'methodparse.py'], 'Search': [0, '', 'Search.py'], 'StyledTextCtrls': [0, '', 'Views/StyledTextCtrls.py'], 'DialogCompanions': [0, '', 'Companions/DialogCompanions.py'], 'relpath': [0, '', 'relpath.py'], 'Browse': [0, '', 'Browse.py'], 'OGLViews': [0, '', 'Views/OGLViews.py'], 'ImageStore': [0, '', 'ImageStore.py'], 'FileExplorer': [0, '', 'Explorers/FileExplorer.py'], 'EditorModels': [0, '', 'EditorModels.py'], 'PropertyEditors': [0, '', 'PropEdit/PropertyEditors.py'], 'HelpCompanions': [0, '', 'Companions/HelpCompanions.py'], 'DataView': [0, '', 'Views/DataView.py'], 'moduleparse': [0, '', 'moduleparse.py'], 'Explorer': [0, '', 'Explorers/Explorer.py'], 'CtrlSize': [0, '', 'CtrlSize.py'], 'Designer': [0, '', 'Views/Designer.py'], 'ErrorStackFrm': [0, '', 'ErrorStackFrm.py'], 'Companions': [0, '', 'Companions/Companions.py'], 'LoginDialog': [0, '', 'ZopeLib/LoginDialog.py'], 'PaletteMapping': [0, '', 'PaletteMapping.py'], 'PrefsMSW': [0, '', 'PrefsMSW.py'], 'ZopeCompanions': [0, '', 'Companions/ZopeCompanions.py'], 'ShellEditor': [0, '', 'ShellEditor.py'], 'Client': [0, '', 'ZopeLib/Client.py'], 'PropDlg': [0, '', 'ZopeLib/PropDlg.py'], 'BaseCompanions': [0, '', 'Companions/BaseCompanions.py'], 'AppViews': [0, '', 'Views/AppViews.py'], 'Help': [0, '', 'Help.py'], 'Debugger': [0, '', 'Debugger/Debugger.py'], 'ndiff': [0, '', 'ExternalLib/ndiff.py'], 'ZopeExplorer': [0, '', 'Explorers/ZopeExplorer.py'], 'CVSExplorer': [0, '', 'Explorers/CVSExplorer.py'], 'ZipExplorer': [0, '', 'Explorers/ZipExplorer.py'], 'Enumerations': [0, '', 'PropEdit/Enumerations.py'], 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'], 'CVSResults': [0, '', 'Explorers/CVSResults.py'], 'ImageViewer': [0, '', 'ZopeLib/ImageViewer.py'], 'Preferences': [0, '', 'Preferences.py'], 'Palette': [1, '', 'Palette.py'], 'PrefsKeys': [0, '', 'PrefsKeys.py'], 'FTPExplorer': [0, '', 'Explorers/FTPExplorer.py']}
        
class BoaApp(wxApp):
    def __init__(self, redirect=false):
        wxApp.__init__(self, redirect)
        
    def OnInit(self):
        wxImage_AddHandler(wxJPEGHandler())
        wxImage_AddHandler(wxPNGHandler())
        wxImage_AddHandler(wxGIFHandler())

        abt = About.createSplash(None)
        abt.Show(true)
        try:
            # Let the splash screen repaint
            wxYield()
            import Palette
            
            self.main = Palette.BoaFrame(None, -1, self)
            
            self.main.Show(true)
            self.SetTopWindow(self.main)
    
            self.main.inspector.Show(true)
            # For some reason the splitters have to be visible on GTK before they
            # can be sized.
            self.main.inspector.initSashes()
            self.main.editor.Show(true)

            # Open info text files if run for the first time
            if os.path.exists('1stTime'):
                try:
                    self.main.editor.openOrGotoModule('README.txt')
                    self.main.editor.openOrGotoModule('Changes.txt')
                    os.remove('1stTime')
                except:
                    print 'Could not load intro text files'
    
            # Apply command line switches
            g = globals()
            if doDebug:
                mod = self.main.editor.openModule(args[0])
                mod.debug()
            elif startupModules:
                for mod in startupModules:
                    self.main.editor.openModule(mod)
    
            try:
                Utils.showTip(self.main.editor)
            except Exception, err:
                print 'Error showing tips:', str(eer)
                
        finally:    
            abt.Destroy()
        return true

    
def main():
    app = BoaApp(0)
    app.quit = false
    while not app.quit:
        app.MainLoop()

if __name__ == '__main__' or hasattr(wxApp, 'debugger'):
    main()
