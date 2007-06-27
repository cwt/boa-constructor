#-----------------------------------------------------------------------------
# Name:        PyInterpreterChooser.plug-in.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2003/07/20
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2006
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:PyInterpreterChooserDlg
import os, sys

import wx

from Utils import _

PyCoreRegPath = 'SOFTWARE\\Python\\Pythoncore'

[wxID_PYINTERPRETERCHOOSERDLG, wxID_PYINTERPRETERCHOOSERDLGBTNCANCEL, 
 wxID_PYINTERPRETERCHOOSERDLGBTNOK, 
 wxID_PYINTERPRETERCHOOSERDLGGDCINSTALLPATH, 
 wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS, 
 wxID_PYINTERPRETERCHOOSERDLGPANEL1, wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT1, 
 wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT2, 
 wxID_PYINTERPRETERCHOOSERDLGTXTPYINTPPATH, 
] = [wx.NewId() for _init_ctrls in range(9)]

class PyInterpreterChooserDlg(wx.Dialog):
    def _init_coll_boxSizer3_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panel1, 1, border=0, flag=wx.GROW)
        parent.AddWindow(self.btnOK, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)
        parent.AddWindow(self.btnCancel, 0, border=10,
              flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=10, flag=wx.ALL)
        parent.AddSizer(self.boxSizer2, 1, border=0, flag=wx.GROW)
        parent.AddWindow(self.staticText2, 0, border=10, flag=wx.ALL)
        parent.AddWindow(self.txtPyIntpPath, 0, border=10,
              flag=wx.GROW | wx.ALL)
        parent.AddSizer(self.boxSizer3, 0, border=0,
              flag=wx.ALIGN_RIGHT | wx.GROW | wx.ALL)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.lcInstallations, 1, border=10,
              flag=wx.GROW | wx.ALL)
        parent.AddWindow(self.gdcInstallPath, 1, border=10,
              flag=wx.GROW | wx.ALL)

    def _init_coll_lcInstallations_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
              heading=_('Version'), width=50)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT,
              heading=_('Install Path'), width=170)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer3 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)
        self._init_coll_boxSizer3_Items(self.boxSizer3)

        self.SetSizer(self.boxSizer1)

    def _init_utils(self):
        # generated method, don't edit
        self.images = wx.ImageList(height=16, width=16)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_PYINTERPRETERCHOOSERDLG,
              name='PyInterpreterChooserDlg', parent=prnt, pos=wx.Point(548,
              346), size=wx.Size(532, 358),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Python Interpreter Chooser'))
        self._init_utils()
        self.SetClientSize(wx.Size(524, 331))
        self.Center(wx.BOTH)

        self.staticText1 = wx.StaticText(id=wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT1,
              label=_('Found installations: (double click to select)'),
              name='staticText1', parent=self, pos=wx.Point(10, 10),
              size=wx.Size(256, 22), style=0)

        self.gdcInstallPath = wx.GenericDirCtrl(defaultFilter=0, dir='.',
              filter=self.installPathFilter,
              id=wxID_PYINTERPRETERCHOOSERDLGGDCINSTALLPATH,
              name='gdcInstallPath', parent=self, pos=wx.Point(272, 52),
              size=wx.Size(242, 146),
              style=wx.DIRCTRL_SHOW_FILTERS | wx.DIRCTRL_3D_INTERNAL | wx.NO_BORDER)

        self.lcInstallations = wx.ListView(id=wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS,
              name='lcInstallations', parent=self, pos=wx.Point(10, 52),
              size=wx.Size(242, 146), style=wx.LC_REPORT,
              validator=wx.DefaultValidator)
        self._init_coll_lcInstallations_Columns(self.lcInstallations)
        self.lcInstallations.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
              self.OnLcinstallationsListItemActivated,
              id=wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS)

        self.staticText2 = wx.StaticText(id=wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT2,
              label=_('Current interpreter path (Blank means sys.executable will be used.)'),
              name='staticText2', parent=self, pos=wx.Point(10, 218),
              size=wx.Size(502, 19), style=0)

        self.txtPyIntpPath = wx.TextCtrl(id=wxID_PYINTERPRETERCHOOSERDLGTXTPYINTPPATH,
              name='txtPyIntpPath', parent=self, pos=wx.Point(10, 257),
              size=wx.Size(504, 21), style=0, value=self.pythonInterpreterPath)

        self.btnOK = wx.Button(id=wx.ID_OK, label=_('OK'), name='btnOK',
              parent=self, pos=wx.Point(287, 298), size=wx.Size(101, 23),
              style=0)

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='btnCancel', parent=self, pos=wx.Point(408, 298),
              size=wx.Size(106, 23), style=0)

        self.panel1 = wx.Panel(id=wxID_PYINTERPRETERCHOOSERDLGPANEL1,
              name='panel1', parent=self, pos=wx.Point(0, 288),
              size=wx.Size(277, 43), style=wx.TAB_TRAVERSAL)

        self._init_sizers()

    def __init__(self, parent, currentPyIntpPath=''):
        self.pythonInterpreterPath = ''
        self.pythonInterpreterPath = currentPyIntpPath
        self.installPathFilter = '(*.exe)|*.exe)'
        self.installPathFilter = self.getInstallPathFilter()

        self._init_ctrls(parent)

        self.populateFoundInstallations()

        self.gdcInstallPath.GetChildren()[0].Bind(wx.EVT_LEFT_DCLICK,
             self.OnGdcinstallpathLeftDclick)

    def populateFoundInstallations(self):
        paths = self.installedPaths = self.getInstallations()
        for idx, (version, path) in zip(range(len(paths)), paths):
            self.lcInstallations.InsertStringItem(idx, version)
            self.lcInstallations.SetStringItem(idx, 1, path)

        # Bold the current installation
        li = self.lcInstallations.GetItem(0)
        f = li.GetFont()
        f.SetWeight(wx.BOLD)
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
            try:
                pyIntpPath = os.path.join(winreg.QueryValue(reg, 'InstallPath'),
                                      self.sysBinName)
            except WindowsError:
                continue
            
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
    app = wx.PySimpleApp()
    dlg = PyInterpreterChooserDlg(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()

#-------------------------------------------------------------------------------

import Preferences, Utils, Plugins

def openPyInterpChooser(editor):
    dlg = PyInterpreterChooserDlg(editor, Preferences.pythonInterpreterPath)
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return

        pyIntpPath = dlg.txtPyIntpPath.GetValue()

        if pyIntpPath != Preferences.pythonInterpreterPath:
            Plugins.updateRcFile('prefs.rc.py', 'pythonInterpreterPath', `pyIntpPath`)

            for ver, path in dlg.installedPaths:
                if path == pyIntpPath:
                    break
            else:
                for path in Preferences.picExtraPaths:
                    if path == pyIntpPath:
                        break
                else:
                    Plugins.updateRcFile('prefs.plug-ins.rc.py', 'picExtraPaths',
                        `Preferences.picExtraPaths+[pyIntpPath]`)
    finally:
        dlg.Destroy()

_('Additional locations to choose the Python Interpreter Path from.')

Plugins.registerPreference('PyInterpreterChooser', 'picExtraPaths', '[]',
                           ['Additional locations to choose the Python '
                            'Interpreter Path from.'])
Plugins.registerTool(_('Python interpreter chooser'), openPyInterpChooser)

# warn the user if the Preferences.pythonInterpreterPath is not valid
def checkInterpreter():
    if hasattr(sys, 'frozen') and not Preferences.pythonInterpreterPath:
        wx.LogWarning(_('No interpreter set to run programs with.\n'
                      'Please set it up as soon as possible via:\n'
                      'Tools->Python interpreter chooser'))
wx.CallAfter(checkInterpreter)
    