#----------------------------------------------------------------------
# Name:        Boa.py
# Purpose:     The main file for Boa
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:App:BoaApp

print 'importing wxPython...' 
from wxPython.wx import *
print 'imported wxPython' 
import Editor
print 'imported Editor'
import Preferences, Palette
print 'imported Palette'

currentMouseOverTip = ''

# Remaining milestones before alpha
# XXX $Event separation 2, 3
# XXX Renaming of $classes, $controls and modules
# XXX Constructor params which aren't properties $
# XXX $Deletion of controls
# XXX $Frame models
# XXX $id allocation
# XXX auto created frames
# XXX sub-properties apply changes
# XXX More property editors!
# XXX More companion classes! $
# XXX Form selection(tags)/moving update
# XXX $Changing Editor.modules to access on filename, not modulename
# XXX $Imports view
# XXX OGL Views saving position and size and show content bug

# Milestones before beta
# XXX Invisible components
# XXX Cut, Copy, Paste
# XXX Multiple component selection
# XXX Composites
# XXX Templates
# XXX Comment/Licence block creation & maintenance

modules ={'relpath': [0, '', 'relpath.py'], 'EditorViews': [0, '', 'EditorViews.py'], 'Inspector': [0, "Inspects object's constructor/properties/events/parents", 'Inspector.py'], 'Infofields': [0, '', 'Infofields.py'], 'AppModuleProps': [0, '', 'AppModuleProps.py'], 'Palette': [0, '', 'Palette.py'], 'UtilCompanions': [0, '', 'UtilCompanions.py'], 'EditorModels': [0, '', 'EditorModels.py'], 'Enumerations': [0, '', 'Enumerations.py'], 'Preferences': [0, '', 'Preferences.py'], 'Constructors': [0, '', 'Constructors.py'], 'Utils': [0, '', 'Utils.py'], 'PhonyApp': [0, '', 'PhonyApp.py'], 'moduleparse': [0, '', 'moduleparse.py'], 'sender': [0, '', 'sender.py'], 'Explorer': [0, '', 'Explorer.py'], 'Designer': [0, '', 'Designer.py'], 'UMLView': [0, '', 'UMLView.py'], 'PaletteMapping': [0, '', 'PaletteMapping.py'], 'Debugger': [0, '', 'Debugger.py'], 'PrefsMSW': [0, '', 'PrefsMSW.py'], 'ClassBrowser': [0, '', 'ClassBrowser.py'], 'RTTI': [0, '', 'RTTI.py'], 'PropertyEditors': [0, '', 'PropertyEditors.py'], 'BaseCompanions': [0, '', 'BaseCompanions.py'], 'EventCollections': [0, '', 'EventCollections.py'], 'PythonInterpreter': [0, '', 'PythonInterpreter.py'], 'Help': [0, '', 'Help.py'], 'SelectionTags': [0, '', 'SelectionTags.py'], 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'], 'DataView': [0, '', 'DataView.py'], 'CollectionEdit': [0, '', 'CollectionEdit.py'], 'Companions': [0, '', 'Companions.py'], 'ImportView': [0, '', 'ImportView.py'], 'InspectorEditorControls': [0, '', 'InspectorEditorControls.py'], 'methodparse': [0, '', 'methodparse.py'], 'Search': [0, '', 'Search.py'], 'PrefsGTK': [0, '', 'PrefsGTK.py'], 'DialogCompanions': [0, '', 'DialogCompanions.py']}
        
class BoaApp(wxApp):
    def OnInit(self):
        wxImage_AddHandler(wxJPEGHandler())
        wxImage_AddHandler(wxPNGHandler())
        wxImage_AddHandler(wxGIFHandler())

        self.main = Palette.BoaFrame(None, -1, 
          'Boa Constructor - wxPython GUI Builder', self)
        
#        sys.stdout = Editor.PseudoFileOut(self.main.log)
#        sys.stderr = Editor.PseudoFileErr(self.main.log)
                                      
        self.main.Show(true)
        self.SetTopWindow(self.main)

	self.main.inspector.Show(true)
	self.main.editor.Show(true)
        
        return true

def main():
    app = BoaApp(0)
    app.quit = false
    while not app.quit:
        app.MainLoop()


#if __name__ == '__main__':
main()



 
