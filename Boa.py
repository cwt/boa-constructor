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

import Preferences
print 'importing wxPython...' 
from wxPython.wx import *
print 'imported Prefs'
import Palette
print 'imported Palette'
import Editor
print 'imported Editor'
import sys, os

currentMouseOverTip = ''

# Remaining milestones before alpha
# XXX auto created frames
# XXX sub-properties apply changes
# XXX More property editors!
# XXX More companion classes! $
# XXX OGL Views show content bug

# Milestones before beta
# XXX Cut, Copy, Paste
# XXX Multiple component selection
# XXX Templates
# XXX Comment/Licence block creation & maintenance

modules ={'EditorViews': [0, '', 'Views/EditorViews.py'], 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'], 'Inspector': [0, "Inspects object's constructor/properties/events/parents", 'Inspector.py'], 'Infofields': [0, '', 'Infofields.py'], 'ErrorStack': [0, '', 'ErrorStack.py'], 'AppModuleProps': [0, '', 'AppModuleProps.py'], 'UtilCompanions': [0, '', 'Companions/UtilCompanions.py'], 'HTMLCyclops': [0, '', 'HTMLCyclops.py'], 'ZopeFTP': [0, '', 'ZopeLib/ZopeFTP.py'], 'CtrlAlign': [0, '', 'CtrlAlign.py'], 'FileDlg': [0, '', 'FileDlg.py'], 'Constructors': [0, '', 'Companions/Constructors.py'], 'Utils': [0, '', 'Utils.py'], 'ExtMethDlg': [0, '', 'ZopeLib/ExtMethDlg.py'], 'CollectionEdit': [0, '', 'Views/CollectionEdit.py'], 'sender': [0, '', 'sender.py'], 'PrefsKeys': [0, '', 'PrefsKeys.py'], 'RunCyclops': [0, '', 'RunCyclops.py'], 'popen2import': [0, '', 'popen2import.py'], 'ClassBrowser': [0, '', 'ClassBrowser.py'], 'RTTI': [0, '', 'RTTI.py'], 'PySourceView': [0, '', 'Views/PySourceView.py'], 'EventCollections': [0, '', 'Companions/EventCollections.py'], 'PythonInterpreter': [0, '', 'ExternalLib/PythonInterpreter.py'], 'PhonyApp': [0, '', 'PhonyApp.py'], 'SSHExplorer': [0, '', 'Explorers/SSHExplorer.py'], 'SelectionTags': [0, '', 'Views/SelectionTags.py'], 'DiffView': [0, '', 'Views/DiffView.py'], 'PrefsGTK': [0, '', 'PrefsGTK.py'], 'About': [0, '', 'About.py'], 'PropDlg': [0, '', 'ZopeLib/PropDlg.py'], 'InspectorEditorControls': [0, '', 'PropEdit/InspectorEditorControls.py'], 'methodparse': [0, '', 'methodparse.py'], 'Search': [0, '', 'Search.py'], 'StyledTextCtrls': [0, '', 'Views/StyledTextCtrls.py'], 'relpath': [0, '', 'relpath.py'], 'Debugger': [0, '', 'Debugger/Debugger.py'], 'OGLViews': [0, '', 'Views/OGLViews.py'], 'EditorModels': [0, '', 'EditorModels.py'], 'PropertyEditors': [0, '', 'PropEdit/PropertyEditors.py'], 'ndiff': [0, '', 'ExternalLib/ndiff.py'], 'HelpCompanions': [0, '', 'Companions/HelpCompanions.py'], 'ZopeCompanions': [0, '', 'Companions/ZopeCompanions.py'], 'DataView': [0, '', 'Views/DataView.py'], 'moduleparse': [0, '', 'moduleparse.py'], 'Explorer': [0, '', 'Explorers/Explorer.py'], 'CtrlSize': [0, '', 'CtrlSize.py'], 'Designer': [0, '', 'Views/Designer.py'], 'ErrorStackFrm': [0, '', 'ErrorStackFrm.py'], 'ZipExplorer': [0, '', 'Explorers/ZipExplorer.py'], 'LoginDialog': [0, '', 'ZopeLib/LoginDialog.py'], 'PaletteMapping': [0, '', 'PaletteMapping.py'], 'ZopeExplorer': [0, '', 'Explorers/ZopeExplorer.py'], 'ShellEditor': [0, '', 'ShellEditor.py'], 'ExplorerNodes': [0, '', 'Explorers/ExplorerNodes.py'], 'BaseCompanions': [0, '', 'Companions/BaseCompanions.py'], 'AppViews': [0, '', 'Views/AppViews.py'], 'Help': [0, '', 'Help.py'], 'ProfileView': [0, '', 'Views/ProfileView.py'], 'FileExplorer': [0, '', 'Explorers/FileExplorer.py'], 'CVSExplorer': [0, '', 'Explorers/CVSExplorer.py'], 'Companions': [0, '', 'Companions/Companions.py'], 'Enumerations': [0, '', 'PropEdit/Enumerations.py'], 'Browse': [0, '', 'Browse.py'], 'PrefsMSW': [0, '', 'PrefsMSW.py'], 'Preferences': [0, '', 'Preferences.py'], 'Palette': [0, '', 'Palette.py'], 'DialogCompanions': [0, '', 'Companions/DialogCompanions.py']}
        
class BoaApp(wxApp):
    def __init__(self, redirect=false):
        wxApp.__init__(self, redirect)
        
    def OnInit(self):
        wxImage_AddHandler(wxJPEGHandler())
        wxImage_AddHandler(wxPNGHandler())
        wxImage_AddHandler(wxGIFHandler())
        
#        EVT_ACTIVATE_APP(self, self.OnActivate)
        wxToolTip_Enable(TRUE) 

        self.main = Palette.BoaFrame(None, -1, self)
        
#        sys.stdout = Editor.PseudoFileOut(self.main.log)
#        sys.stderr = Editor.PseudoFileErr(self.main.log)
                                      
        self.main.Show(true)
        self.SetTopWindow(self.main)

        self.main.inspector.Show(true)
        # For some reason the splitters have to be visible on GTK before they
        # can be sized.
        self.main.inspector.initSashes()
        self.main.editor.Show(true)
        
        if os.path.exists('1stTime'):
            try:
                self.main.editor.openOrGotoModule('README.txt')
                self.main.editor.openOrGotoModule('Changes.txt')
                os.remove('1stTime')
            except:
                print 'Could not load intro text files'
        
        if len(sys.argv) > 1:
            import getopt
            #import methodparse
            optlist, args = getopt.getopt(sys.argv[1:], 'D')
            if len(args):
                if ('-D', '') in optlist:
                    mod = self.main.editor.openModule(args[0])
                    mod.debug()
                else:
                    self.main.editor.openModule(args[0])

        self.ShowTip(self.main.editor)

        return true

    def ShowTip(self, frame):
        try:
            showTipsFile = Preferences.toPyPath('data/showTips')
            showTipText = open(showTipsFile).read()
            showTip, index = eval(showTipText)
        except IOError:
            showTip, index = (1, 0)
        if showTip:
            tp = wxCreateFileTipProvider(Preferences.toPyPath('data/tips.txt'), index)
            showTip = wxShowTip(frame, tp)
            index = tp.GetCurrentTip()
            try:
                open(showTipsFile, 'w').write(str( (showTip, index) ))
            except IOError:
                print 'Could not update tips file', showTipsFile, '(check permissions)'
    
    def OnActivate(self, event):
        # XXX this event does not fire (supposed to fire on wxMSW)
        print 'App activate'
        self.main.Raise()
        self.main.inspector.Raise()
        self.main.editor.Raise()
        self.Skip()

def main():
    app = BoaApp(0)
    app.quit = false
    while not app.quit:
        app.MainLoop()

if __name__ == '__main__' or hasattr(wxApp, 'debugger'):
    main()
