#-----------------------------------------------------------------------------
# Name:        ResourceSupport.py
# Purpose:     Management of modules that contain functions to create images
#
# Author:      Riaan Booysen
#
# Created:     2003/07/27
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2004
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ResourceSelectDlg

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

[wxID_RESOURCESELECTDLG, wxID_RESOURCESELECTDLGBTNCANCEL, 
 wxID_RESOURCESELECTDLGBTNFILEDLG, wxID_RESOURCESELECTDLGBTNOK, 
] = map(lambda _init_ctrls: wxNewId(), range(4))

class ResourceSelectDlg(wxDialog):
    def _init_coll_boxSizerButtons_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.btnOK, 0, border=15,
              flag=wxBOTTOM | wxTOP | wxLEFT | wxALIGN_RIGHT)
        parent.AddWindow(self.btnCancel, 0, border=15,
              flag=wxBOTTOM | wxTOP | wxLEFT | wxALIGN_RIGHT)
        parent.AddWindow(self.btnFileDlg, 0, border=15,
              flag=wxBOTTOM | wxTOP | wxLEFT | wxALIGN_RIGHT)

    def _init_coll_boxSizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizerButtons, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizerMain = wxBoxSizer(orient=wxVERTICAL)

        self.boxSizerButtons = wxBoxSizer(orient=wxHORIZONTAL)

        self._init_coll_boxSizerMain_Items(self.boxSizerMain)
        self._init_coll_boxSizerButtons_Items(self.boxSizerButtons)

        self.SetSizer(self.boxSizerMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_RESOURCESELECTDLG,
              name='ResourceSelectDlg', parent=prnt, pos=wxPoint(384, 293),
              size=wxSize(307, 359),
              style=wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE,
              title='Select Resource')
        self.SetClientSize(wxSize(299, 332))

        self.btnOK = wxButton(id=wxID_OK, label='OK', name='btnOK', parent=self,
              pos=wxPoint(15, 15), size=wxSize(75, 23), style=0)

        self.btnCancel = wxButton(id=wxID_CANCEL, label='Cancel',
              name='btnCancel', parent=self, pos=wxPoint(105, 15),
              size=wxSize(75, 23), style=0)

        self.btnFileDlg = wxButton(id=wxID_RESOURCESELECTDLGBTNFILEDLG,
              label='File Dialog...', name='btnFileDlg', parent=self,
              pos=wxPoint(195, 15), size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.btnFileDlg, wxID_RESOURCESELECTDLGBTNFILEDLG,
              self.OnBtnfiledlgButton)

        self._init_sizers()

    def __init__(self, parent, editor, resourceFilename, imageName='', 
          onlyIcons=false):
        self._init_ctrls(parent)
        
        from Explorers import Explorer
        
        model = PyResourceBitmapModel('', resourceFilename, editor, true)
        model.transport = Explorer.openEx(resourceFilename)
        model.load(notify=false)
        self.resources = PyResourceImagesSelectionView(self, model,
              listStyle=wxLC_SMALL_ICON | wxLC_ALIGN_TOP, 
              imgLstStyle=wxIMAGE_LIST_SMALL)
        self.resources.onlyIcons = onlyIcons
        
        self.boxSizerMain.Prepend(self.resources, 1, 
                                  wxLEFT|wxRIGHT|wxTOP|wxGROW, 15)
        self.resources.refreshCtrl()
        
        if imageName:
            sel = -1
            for idx, r in zip(range(len(self.resources.imageSrcInfo)), 
                              self.resources.imageSrcInfo):
                if r[0] == imageName:
                    sel = idx
                    break

            if sel != -1:
                self.resources.Select(sel)
                self.resources.EnsureVisible(sel)
        
        self.resources.SetFocus()

    def OnBtnfiledlgButton(self, event):
        self.EndModal(wxID_YES)


#-------------------------------------------------------------------------------

import os
from StringIO import StringIO

import Preferences, Utils

from Views import EditorViews
from Models import EditorHelper, Controllers, PythonEditorModels, PythonControllers

class PyResourceModuleExec:
    def __init__(self, pyResImgSrc):
        self.imageFunctions = {}
        src = Utils.toUnixEOLMode(pyResImgSrc)+'\n\n'
        exec src in self.imageFunctions

class PyResourceArtProvider(wxArtProvider):
    def __init__(self, pyResModExec):
        wxArtProvider.__init__(self)
        self.imageFunctions = pyResModExec.imageFunctions
        
    def CreateBitmap(self, artid, client, size):
        return self.imageFunctions[artid]()

class PyResourceImagesView(EditorViews.ListCtrlView):
    viewName = 'Images'

    gotoLineBmp = 'Images/Editor/GotoLine.png'
    
    imageSize = (32, 32)
    
    onlyIcons = false

    def __init__(self, parent, model, listStyle=wxLC_ICON | wxLC_ALIGN_TOP, 
                                      imgLstStyle=wxIMAGE_LIST_NORMAL):
        EditorViews.ListCtrlView.__init__(self, parent, model, listStyle,
          (('Goto line', self.OnGoto, self.gotoLineBmp, ''), ), 0) 
           ##('Add image', self.OnAddImage, '-', ''),
        
        self.images = wxImageList(*self.imageSize)
        self.AssignImageList(self.images, imgLstStyle)

        self.imageSrcInfo = []
        self.functions = None
        self.cataloged = false
        self.eol = os.linesep

        self.active = true
        
    def refreshCtrl(self):
        EditorViews.ListCtrlView.refreshCtrl(self)
        
        self.functions = PyResourceModuleExec(self.model.data)
        self.imageSrcInfo = []
        self.images.RemoveAll()
        artProv = PyResourceArtProvider(self.functions)
        wxArtProvider_PushProvider(artProv)
        try:
            m = self.model.getModule()
            self.cataloged = m.globals.has_key('catalog') and m.globals.has_key('index')
            self.eol = m.eol
            for f in m.function_order:
                if f.startswith('get') and f.endswith('Data'):
                    name = f[3:-4]
                    iconFunction = m.functions.has_key('get%sIcon'%name)
                    if self.onlyIcons and not iconFunction:
                        continue
                    bmpFunctionStart = m.functions['get%sBitmap'%name].start
                    firstDataLine = m.source[m.functions['get%sData'%name].start]
                    compressed = firstDataLine.strip().startswith('return zlib.decompress')
                    bmp = wxArtProvider_GetBitmap('get%sBitmap'%name, size=self.imageSize)
                    idx = self.images.Add(bmp)
                    self.InsertImageStringItem(idx, name, idx)
                    self.imageSrcInfo.append( 
                        (name, (m.functions[f].start, bmpFunctionStart),
                         compressed, iconFunction) )
        finally:
            wxArtProvider_PopProvider()
            
    def OnGoto(self, event):
        if self.selected != -1:
            srcView = self.model.getSourceView()
            srcView.focus()
            lineNo = self.imageSrcInfo[self.selected][1][0]
            srcView.gotoLine(lineNo-1)

##    def OnAddImage(self, event):
##        dlg = wxDirDialog(self.model.editor)
##        try:
##            if dlg.ShowModal() != wxID_OK:
##                return
##            dir = dlg.GetPath()
##            res = []
##            os.path.walk(dir, visitor, res)
##        finally:
##            dlg.Destroy()
##
##def visitor(files, dirname, names):
##    for name in names:
##        filename = os.path.join(dirname, name)
##        if os.path.isfile(filename):
##            files.append(filename)

class PyResourceImagesSelectionView(PyResourceImagesView):
    docked = false
    imageSize = (16, 16)
    def OnGoto(self, event):
        if self.selected != -1:
            self.GetParent().EndModal(wxID_OK)

class PyResourceBitmapModel(PythonEditorModels.ModuleModel):
    modelIdentifier = 'PyImgResource'
    bitmap = 'PyResBitmap.png'
    imgIdx = EditorHelper.imgPyResBitmap = EditorHelper.imgIdxRange()

    def updateData(self, data, subImage):
        from wxPython.tools import img2py
        crunched = StringIO(img2py.crunch_data(data, subImage['zip'])).readlines()
        if subImage['zip']:
            crunched[-1].rstrip()
            crunched[-1] += ' )'+subImage['eol']
        srcLines = self.getDataAsLines()
        srcLines[subImage['start']:subImage['end']] = crunched + [subImage['eol']]
        
        self.setDataFromLines(srcLines)
        self.modified = true
        
        subImage['data'] = data

class PyResourceBitmapController(PythonControllers.ModuleController):
    Model = PyResourceBitmapModel
    DefaultViews    = PythonControllers.ModuleController.DefaultViews + \
                      [PyResourceImagesView]


#-------------------------------------------------------------------------------

EditorHelper.modelReg[PyResourceBitmapModel.modelIdentifier] = PyResourceBitmapModel
Controllers.modelControllerReg[PyResourceBitmapModel] = PyResourceBitmapController

Controllers.resourceClasses.append(PyResourceBitmapModel)

EditorHelper.imageExtReg.append('.py')
if not EditorHelper.imageSubTypeExtReg.has_key('.py'):
    EditorHelper.imageSubTypeExtReg['.py'] = []
EditorHelper.imageSubTypeExtReg['.py'].append(PyResourceBitmapModel)
