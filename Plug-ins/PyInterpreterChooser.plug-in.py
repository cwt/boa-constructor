#-----------------------------------------------------------------------------
# Name:        PyInterpreterChooser.plug-in.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2003/07/20
# RCS-ID:      $Id$
# Copyright:   (c) 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:PyInterpreterChooserDlg
import os, sys

from wxPython.wx import *

PyCoreRegPath = 'SOFTWARE\\Python\\Pythoncore'

[wxID_PYINTERPRETERCHOOSERDLG, wxID_PYINTERPRETERCHOOSERDLGBTNCANCEL, 
 wxID_PYINTERPRETERCHOOSERDLGBTNOK, 
 wxID_PYINTERPRETERCHOOSERDLGGDCINSTALLPATH, 
 wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS, 
 wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT1, 
 wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT2, 
 wxID_PYINTERPRETERCHOOSERDLGTXTPYINTPPATH, 
] = map(lambda _init_ctrls: wxNewId(), range(8))

class PyInterpreterChooserDlg(wxDialog):
    def _init_coll_lcInstallations_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wxLIST_FORMAT_LEFT, heading='Version',
              width=50)
        parent.InsertColumn(col=1, format=wxLIST_FORMAT_LEFT,
              heading='Install Path', width=170)

    def _init_utils(self):
        # generated method, don't edit
        self.images = wxImageList(height=16, width=16)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_PYINTERPRETERCHOOSERDLG,
              name='PyInterpreterChooserDlg', parent=prnt, pos=wxPoint(566,
              355), size=wxSize(495, 330), style=wxDEFAULT_DIALOG_STYLE,
              title='Python Interpreter Chooser')
        self._init_utils()
        self.SetClientSize(wxSize(487, 303))
        self.Center(wxBOTH)

        self.staticText1 = wxStaticText(id=wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT1,
              label='Found installations:', name='staticText1', parent=self,
              pos=wxPoint(8, 8), size=wxSize(136, 16), style=0)

        self.gdcInstallPath = wxGenericDirCtrl(defaultFilter=0, dir='.',
              filter=self.installPathFilter,
              id=wxID_PYINTERPRETERCHOOSERDLGGDCINSTALLPATH,
              name='gdcInstallPath', parent=self, pos=wxPoint(248, 32),
              size=wxSize(224, 160),
              style=wxDIRCTRL_SHOW_FILTERS | wxDIRCTRL_3D_INTERNAL | wxNO_BORDER)

        self.lcInstallations = wxListView(id=wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS,
              name='lcInstallations', parent=self, pos=wxPoint(8, 32),
              size=wxSize(224, 160), style=wxLC_REPORT,
              validator=wxDefaultValidator)
        self._init_coll_lcInstallations_Columns(self.lcInstallations)
        EVT_LIST_ITEM_ACTIVATED(self.lcInstallations,
              wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS,
              self.OnLcinstallationsListItemActivated)

        self.staticText2 = wxStaticText(id=wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT2,
              label='Current interpreter path (Blank means sys.executable will be used.)',
              name='staticText2', parent=self, pos=wxPoint(8, 208),
              size=wxSize(376, 16), style=0)

        self.txtPyIntpPath = wxTextCtrl(id=wxID_PYINTERPRETERCHOOSERDLGTXTPYINTPPATH,
              name='txtPyIntpPath', parent=self, pos=wxPoint(8, 232),
              size=wxSize(464, 21), style=0, value=self.pythonInterpreterPath)

        self.btnOK = wxButton(id=wxID_OK, label='OK', name='btnOK', parent=self,
              pos=wxPoint(312, 264), size=wxSize(75, 23), style=0)

        self.btnCancel = wxButton(id=wxID_CANCEL, label='Cancel',
              name='btnCancel', parent=self, pos=wxPoint(397, 264),
              size=wxSize(75, 23), style=0)

    def __init__(self, parent, currentPyIntpPath=''):
        self.pythonInterpreterPath = ''
        self.pythonInterpreterPath = currentPyIntpPath
        self.installPathFilter = '(*.exe)|*.exe)'
        self.installPathFilter = self.getInstallPathFilter()
        
        self._init_ctrls(parent)

        self.populateFoundInstallations()
        
        EVT_LEFT_DCLICK(self.gdcInstallPath.GetChildren()[0],
             self.OnGdcinstallpathLeftDclick)

    def populateFoundInstallations(self):
        paths = self.installedPaths = self.getInstallations()
        for idx, (version, path) in zip(range(len(paths)), paths):
            self.lcInstallations.InsertStringItem(idx, version)
            self.lcInstallations.SetStringItem(idx, 1, path)
        
        # Bold the current installation
        li = self.lcInstallations.GetItem(0)
        f = li.GetFont()
        f.SetWeight(wxBOLD)
        li.SetFont(f)
        self.lcInstallations.SetItem(li)

    def getInstallations(self):
        res = [(self.sysBinVer, sys.executable)]

        import Preferences
        for path in Preferences.picExtraPaths:
            if os.path.exists(path):
                res.append( ('?', path) )

        # XXX search common locations on Linux?

        try:
            import _winreg as winreg
        except ImportError:
            return res

        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, PyCoreRegPath)
        except EnvironmentError:
            return res

        idx = 0
        versions = []
        try:
            while 1:
                versions.append(winreg.EnumKey(reg, idx))
                idx += 1
        except EnvironmentError: 
            pass
        
        try: versions.remove(self.sysBinVer)
        except ValueError: pass
        
        for version in versions:
            try:
                reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                     '%s\\%s'%(PyCoreRegPath, version))
            except EnvironmentError:
                continue
            pyIntpPath = os.path.join(winreg.QueryValue(reg, 'InstallPath'), 
                                      self.sysBinName)
            if os.path.exists(pyIntpPath):
                try: 
                    res.index( (version, pyIntpPath) )
                except ValueError:
                    res.append( (version, pyIntpPath) )

        return res

    def OnGdcinstallpathLeftDclick(self, event):
        event.Skip()
        currPath = self.gdcInstallPath.GetFilePath()
        self.updatePyIntpPath(currPath)

    def OnLcinstallationsListItemActivated(self, event):
        idx = self.lcInstallations.GetFirstSelected()
        path = self.lcInstallations.GetItem(idx, 1).GetText()
        self.updatePyIntpPath(path)

    def getInstallPathFilter(self):
        self.sysBinDir, self.sysBinName = os.path.split(sys.executable)
        self.sysBinVer = '%d.%d'%sys.version_info[:2]

        ext = '*%s'%os.path.splitext(self.sysBinName)[1]
        if ext == '*':
            return ''
        else:
            return '(%s)|%s'%(ext, ext)

    def updatePyIntpPath(self, path):
        if path == sys.executable:
            path = ''
        
        self.txtPyIntpPath.SetValue(path)




if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    dlg = PyInterpreterChooserDlg(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()

#-------------------------------------------------------------------------------

import Preferences, Utils, Plugins
from Explorers.PrefsExplorer import UsedModuleSrcBsdPrefColNode
import moduleparse

def updateRcFile(rcFile, propName, propSrcValue):
    prefsRcFile = os.path.join(Preferences.rcPath, rcFile)
    m = moduleparse.Module(rcFile, open(prefsRcFile).readlines())
    prefsRcNode = UsedModuleSrcBsdPrefColNode('', ('*',), prefsRcFile, -1, None, 
                                              Preferences, true)
    newProp = (propName, propSrcValue, m.globals[propName])
    prefsRcNode.save(propName, newProp)
    

def openPyInterpChooser(editor):
    dlg = PyInterpreterChooserDlg(editor, Preferences.pythonInterpreterPath)
    try:
        if dlg.ShowModal() != wxID_OK:
            return
    
        pyIntpPath = dlg.txtPyIntpPath.GetValue()

        if pyIntpPath != Preferences.pythonInterpreterPath:
            updateRcFile('prefs.rc.py', 'pythonInterpreterPath', `pyIntpPath`)
        
            for ver, path in dlg.installedPaths:
                if path == pyIntpPath:
                    break
            else:
                for path in Preferences.picExtraPaths:
                    if path == pyIntpPath:
                        break
                else:
                    updateRcFile('prefs.plug-ins.rc.py', 'picExtraPaths', 
                        `Preferences.picExtraPaths+[pyIntpPath]`)
    finally:
        dlg.Destroy()

Plugins.registerPreference('PyInterpreterChooser', 'picExtraPaths', '[]', 
                           ['Additional locations to choose the Python '
                            'Interpreter Path from.'])
    
from Models import EditorHelper
EditorHelper.editorToolsReg.append( ('Python interpreter chooser', openPyInterpChooser) )
        
