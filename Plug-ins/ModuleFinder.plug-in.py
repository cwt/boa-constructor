#Boa:Dialog:ModuleFinderDlg

import sys, imp

from wxPython.wx import *

from Preferences import IS
import Utils

#-------------------------------------------------------------------------------

[wxID_MODULEFINDERDLG, wxID_MODULEFINDERDLGCANCELBTN, 
 wxID_MODULEFINDERDLGOKBTN, wxID_MODULEFINDERDLGSTATICTEXT1, 
 wxID_MODULEFINDERDLGTXTMODULENAME, 
] = map(lambda _init_ctrls: wxNewId(), range(5))

class ModuleFinderDlg(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_MODULEFINDERDLG, name='ModuleFinderDlg',
              parent=prnt, pos=wxPoint(676, 466), size=wxSize(275, 133),
              style=wxDEFAULT_DIALOG_STYLE, title='Module finder for sys.path')
        self.SetClientSize(wxSize(267, 106))
        self.Center(wxBOTH)

        self.staticText1 = wxStaticText(id=wxID_MODULEFINDERDLGSTATICTEXT1,
              label='Module name:', name='staticText1', parent=self,
              pos=wxPoint(8, 8), size=wxSize(104, 16), style=0)

        self.txtModuleName = wxTextCtrl(id=wxID_MODULEFINDERDLGTXTMODULENAME,
              name='txtModuleName', parent=self, pos=wxPoint(8, 32),
              size=wxSize(248, 21), style=0, value='')

        self.okBtn = wxButton(id=wxID_OK, label='OK', name='okBtn', parent=self,
              pos=wxPoint(103, 72), size=wxSize(75, 23), style=0)
        self.okBtn.SetDefault()

        self.cancelBtn = wxButton(id=wxID_CANCEL, label='Cancel',
              name='cancelBtn', parent=self, pos=wxPoint(183, 72),
              size=wxSize(75, 23), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
        
        icon = wxEmptyIcon()
        icon.CopyFromBitmap(IS.load('Images/ModuleFinder.png'))
        self.SetIcon(icon)

#-------------------------------------------------------------------------------

def openModuleFinder(editor):
    dlg = ModuleFinderDlg(editor)
    try:
        while dlg.ShowModal() == wxID_OK:
            modName = dlg.txtModuleName.GetValue()
            try:
                f, filename, (ext, mode, type) = \
                      Utils.find_dotted_module(modName, sys.path)
            except ImportError, err:
                wxLogError('%s not found on sys.path.'%modName)
            else:
                if f is not None:
                    f.close()
                if filename:
                    if type == imp.PKG_DIRECTORY:
                        editor.openOrGotoModule(os.path.join(filename, '__init__.py'))
                    elif type in (imp.PY_SOURCE, imp.C_EXTENSION):
                        editor.openOrGotoModule(filename)
                return
    finally:
        dlg.Destroy()
    
from Models import EditorHelper
if wxPlatform == '__WXMSW__':
    keyIdent = 'ModuleFinder'
    Preferences.keyDefs[keyIdent] = (wxACCEL_ALT, ord('M'), 'Alt-M')
else:
    keyIdent = ''
    
EditorHelper.editorToolsReg.append( 
      ('Module finder', openModuleFinder, 
       'Images/ModuleFinder.png', keyIdent) )

#-------------------------------------------------------------------------------

def getModuleFinderImgData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x1aIDATx\x9c\xa5\x93]j\xc30\x10\x84?\x95\x1c@\xd7\xf1\x12\x08\xd5\
\x89J\xf0[J\x7f\xc2\xe6-\x94\x9eH\x10\x12\xd6\xd7\xc9\x01\n\xdb\x07[\x8a\x9d\
\xba$\xa5\x0bb\xd7\x1efX\xcd\xa0\x10c\xe4?\xb5(C\xbbn\xfd\x1a\xdc\x7f\xec\
\xc3]\x02\xed\xba\xf5\xf4\x98\x90\xa5`\'\xab\x1d\xf0["\x8b\xdf\xc8\xb2\x14\
\x8c^d\x8eX\x85u\xab>.;\x9a\xab\xaa\xab\xaa\x03\xae:\xc5\xdd\xddu\xdbc1\xc6\
\x8b\x00N%\xfb\xf0\xc7\xdd\xabH\xc1q&\x02\xd5D;\x19\xf9\x90\xd9l6@\x00\x9c\
\x00\x98\x19"\x82\xad.\xd7\xcb\xe4z\x95\x872\xc8R\x86\xa9\x90\x03\xd6uH\xd3T\
\xbcx3\xae*0\xb8>"\x1b\xd24X\xd7U|\x94\xce\xfc\x06i\x95\xd8\xedv\x13\xb2\x88\
\xa0\xaa\xe4\xc3\xfc\x06\x13\x0fJt9g\x10A\x00U%\xa5D#\x00\x82\x1d\xa7\x1e\
\xfcHa\xae\xbfA\x9f\n\xfd\x19\xa7\x10\x86\x8f\x9b\xf5\xf5\xf2\xcc\xab\x0f\
\x1e\x0f-\xc6\x18\x18\x1e\x93\xdfs\xae7\x891\x12\xfe\xfa\x1a\x9f\xceg/\x9b\
\xbc\x8fM\xbc\xb7>c\x0c\x84\xb3\x97\xf9\x1b\xa7\x9e\xfe\x8e\xda\xadz\x91\x00\
\x00\x00\x00IEND\xaeB`\x82' 

IS.registerImage('Images/ModuleFinder.png', getModuleFinderImgData())
