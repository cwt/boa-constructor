#-----------------------------------------------------------------------------
# Name:        wx25upgradeDialog.py
# Purpose:     Dialog to select a folder to upgrade
#
#              Inspired by paul sorenson's upgrade.py, which is required
#
# Author:      Werner F. Bruhin
#
# Created:     2005/07/03
# RCS-ID:      $Id$
# Licence:     very simple, any one may use and/or change it.
#-----------------------------------------------------------------------------
#Boa:Dialog:Wx25CodeUpgradeDlg

import wx
import os
import sys
import string

from ExternalLib import wx25upgrade

def createWx25CodeUpgradeDlg(parent):
    return Wx25CodeUpgradeDlg(parent)

[wxID_WX25CODEUPGRADEDLG, wxID_WX25CODEUPGRADEDLGSETSOURCE, 
 wxID_WX25CODEUPGRADEDLGSETTARGET, wxID_WX25CODEUPGRADEDLGSOURCEFOLDER, 
 wxID_WX25CODEUPGRADEDLGSTART, wxID_WX25CODEUPGRADEDLGSTATICTEXT1, 
 wxID_WX25CODEUPGRADEDLGSTSOURCEFOLDER, wxID_WX25CODEUPGRADEDLGSTTARGETFOLDER, 
 wxID_WX25CODEUPGRADEDLGTARGETFOLDER, wxID_WX25CODEUPGRADEDLGUPGRADEGUIDE, 
] = [wx.NewId() for _init_ctrls in range(10)]

class Wx25CodeUpgradeDlg(wx.Dialog):
    def _init_coll_bsDialog_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.flexGridSizer1, 1, border=2, flag=wx.ALL)
        parent.AddSizer(self.fgsButtons, 0, border=2, flag=wx.ALL)

    def _init_coll_fgsButtons_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.setSource, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.setTarget, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.start, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.upgradeGuide, 1, border=2, flag=wx.ALL)

    def _init_coll_flexGridSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stSourceFolder, 1, border=2,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.sourceFolder, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.stTargetFolder, 1, border=2,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.targetFolder, 1, border=2, flag=wx.ALL)

    def _init_sizers(self):
        # generated method, don't edit
        self.flexGridSizer1 = wx.FlexGridSizer(cols=2, hgap=0, rows=0, vgap=0)

        self.fgsButtons = wx.FlexGridSizer(cols=4, hgap=0, rows=0, vgap=0)

        self.bsDialog = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_flexGridSizer1_Items(self.flexGridSizer1)
        self._init_coll_fgsButtons_Items(self.fgsButtons)
        self._init_coll_bsDialog_Items(self.bsDialog)

        self.SetSizer(self.bsDialog)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WX25CODEUPGRADEDLG,
              name='Wx25CodeUpgradeDlg', parent=prnt, pos=wx.Point(167, 443),
              size=wx.Size(543, 150), style=wx.DEFAULT_DIALOG_STYLE,
              title='Upgrade Boa code to 0.4 style')
        self.SetClientSize(wx.Size(535, 123))

        self.sourceFolder = wx.TextCtrl(id=wxID_WX25CODEUPGRADEDLGSOURCEFOLDER,
              name='sourceFolder', parent=self, pos=wx.Point(77, 4),
              size=wx.Size(435, 21), style=0, value='textCtrl1')

        self.targetFolder = wx.TextCtrl(id=wxID_WX25CODEUPGRADEDLGTARGETFOLDER,
              name='targetFolder', parent=self, pos=wx.Point(77, 29),
              size=wx.Size(435, 21), style=0, value='textCtrl2')

        self.stSourceFolder = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTSOURCEFOLDER,
              label='Source Folder:', name='stSourceFolder', parent=self,
              pos=wx.Point(4, 8), size=wx.Size(69, 13), style=0)

        self.stTargetFolder = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTTARGETFOLDER,
              label='Target Folder', name='stTargetFolder', parent=self,
              pos=wx.Point(4, 33), size=wx.Size(63, 13), style=0)

        self.setSource = wx.Button(id=wxID_WX25CODEUPGRADEDLGSETSOURCE,
              label='Set Source Folder', name='setSource', parent=self,
              pos=wx.Point(4, 96), size=wx.Size(100, 23), style=0)
        self.setSource.Bind(wx.EVT_BUTTON, self.OnSetSourceButton,
              id=wxID_WX25CODEUPGRADEDLGSETSOURCE)

        self.setTarget = wx.Button(id=wxID_WX25CODEUPGRADEDLGSETTARGET,
              label='Set Target Folder', name='setTarget', parent=self,
              pos=wx.Point(108, 96), size=wx.Size(97, 23), style=0)
        self.setTarget.Bind(wx.EVT_BUTTON, self.OnSetTargetButton,
              id=wxID_WX25CODEUPGRADEDLGSETTARGET)

        self.start = wx.Button(id=wxID_WX25CODEUPGRADEDLGSTART,
              label='Start conversion', name='start', parent=self,
              pos=wx.Point(209, 96), size=wx.Size(92, 23), style=0)
        self.start.Bind(wx.EVT_BUTTON, self.OnStartButton,
              id=wxID_WX25CODEUPGRADEDLGSTART)

        self.staticText1 = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTATICTEXT1,
              label='It is strongly recommended NOT to set the "Target Folder" to the same name as "Source Folder"!',
              name='staticText1', parent=self, pos=wx.Point(16, 56),
              size=wx.Size(457, 13), style=0)
        self.staticText1.SetForegroundColour(wx.Colour(255, 0, 0))

        self.upgradeGuide = wx.Button(id=wxID_WX25CODEUPGRADEDLGUPGRADEGUIDE,
              label='Upgrade Guide', name='upgradeGuide', parent=self,
              pos=wx.Point(305, 96), size=wx.Size(103, 23), style=0)
        self.upgradeGuide.Bind(wx.EVT_BUTTON, self.OnUpgradeGuideButton,
              id=wxID_WX25CODEUPGRADEDLGUPGRADEGUIDE)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.sourceFolderName = os.getcwd()
        self.targetFolderName = self.sourceFolderName + 'Upgraded'
        self.sourceFolder.SetValue(self.sourceFolderName)
        self.targetFolder.SetValue(self.targetFolderName)

    def OnSetSourceButton(self, event):
        dlg = wx.DirDialog(self, defaultPath=self.sourceFolderName,
              style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.sourceFolder.SetValue(dir)
                self.targetFolder.SetValue(self.sourceFolder.GetValue()+'Upgraded')
        finally:
            dlg.Destroy()

    def OnSetTargetButton(self, event):
        dlg = wx.DirDialog(self, defaultPath=self.targetFolderName, 
              style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON )
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.targetFolder.SetValue(dir)
        finally:
            dlg.Destroy()

    def OnStartButton(self, event):
        targetFolder = self.targetFolder.GetValue()
        if not os.path.isdir(targetFolder):
            if wx.MessageBox('Target folder does not exist, create it?', 
                  'Create folder', wx.YES_NO | wx.ICON_QUESTION) == wx.NO:
                return
            os.mkdir(targetFolder)
            
        u = wx25upgrade.Upgrade()
        try:
            files = os.listdir(self.sourceFolder.GetValue())
            max = len(files)
            dlg = wx.ProgressDialog("Converting source files",
                                   "Starting conversion of source files",
                                   maximum = max,
                                   parent=self)
    
            keepGoing = True
            count = 0
       
            for name in files:
                count = count +1
                root, ext = os.path.splitext(name)
                if ext == '.py':
                    temp = 'Converting: %s' % name
                    keepGoing = dlg.Update(count, temp)
                    
                    fInput = file(os.path.join(self.sourceFolder.GetValue(), name), 'r')
                    fOutput = file(os.path.join(self.targetFolder.GetValue(), name), 'w')
                    try:
                        frag = []
                        for non, rep in u.scanner(fInput.read()):
                            frag.append(non)
                            frag.append(rep)
                        newtext = string.join(frag, '')
                        fOutput.write(newtext)
                    finally:
                        fInput.close()
                        fOutput.close()
                        temp = 'Done converting: %s' % name
                        keepGoing = dlg.Update(count, temp)
                        print 'Converted: %s' % name

            keepGoing = dlg.Update(count, "We are all done")
        finally:
            dlg.Destroy()
        
    def OnUpgradeGuideButton(self, event):
        import webbrowser
        webbrowser.open('http://wiki.wxpython.org/index.cgi/Boa040Upgrade')


#-------------------------------------------------------------------------------


def showWx25CodeUpgradeDlg(editor):
    dlg = createWx25CodeUpgradeDlg(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    
from Models import EditorHelper
EditorHelper.editorToolsReg.append( ('wxPython 2.4 to 2.5 code upgrader', showWx25CodeUpgradeDlg) )
