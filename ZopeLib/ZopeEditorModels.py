#-----------------------------------------------------------------------------
# Name:        ZopeEditorModels.py
# Purpose:     Models for Zope objects that can be opened in the Editor
#
# Author:      Riaan Booysen
#
# Created:     2001/06/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing ZopeLib.ZopeEditorModels'

import string, os

from wxPython import wx

import Preferences, Utils
from Preferences import keyDefs

from Models import EditorModels, EditorHelper, HTMLSupport

true=1; false=0

def addZOAIcon(metatype):
    ZOAIcons[metatype] = EditorHelper.imgCounter
    EditorHelper.imgCounter = EditorHelper.imgCounter + 1
def addZOAImage(metatype, filepath):
    ZOAImages.append( (metatype, filepath) )
    addZOAIcon(metatype)

# meta-type to image index mapping
ZOAIcons = {}
# meta-type: filename mapping for ZOA imagelist
ZOAImages = [\
 ('root', 'Images/ZOA/Zope.png'),
 ('Folder', 'Images/ZOA/Folder.png'),
 ('DTML Document', 'Images/ZOA/dtmldoc.png'),
 ('Image', 'Images/ZOA/Image.png'),
 ('File', 'Images/ZOA/File.png'),
 ('Mail Host', 'Images/ZOA/MailHost.png'),
 ('User Folder', 'Images/ZOA/UserFolder_icon.png'),
 ('User', 'Images/ZOA/User_icon.png'),
 ('Version', 'Images/ZOA/version.png'),
 ('Control Panel', 'Images/ZOA/ControlPanel_icon.png'),
 ('Debug Information', 'Images/ZOA/DebugManager_icon.png'),
 ('Version Management', 'Images/ZOA/VersionManagement_icon.png'),
 ('Database Management', 'Images/ZOA/DatabaseManagement_icon.png'),
 ('Product Help', 'Images/ZOA/ProductHelp_icon.png'),
 ('Product Management', 'Images/ZOA/ProductFolder_icon.png'),
 ('Product', 'Images/ZOA/InstalledProduct_icon.png'),
 ('Z Class', 'Images/ZOA/ZClass_Icon.png'),
 ('Zope Factory', 'Images/ZOA/Factory_icon.png'),
 ('Zope Permission', 'Images/ZOA/Permission_icon.png'),
 ('Base Class', 'Images/ZOA/BaseClass.png'),
 ('Aggregation', 'Images/ZOA/attribute.png'),
 ('Broken Because Product is Gone', 'Images/ZOA/broken.png'),
 ('unknown', 'Images/ZOA/unknown.png'),
 ('Script (Python)', 'Images/ZOA/PythonScript.png'),
 ('External Method', 'Images/ZOA/extmethod.png'),
 ('DTML Method', 'Images/ZOA/dtmlmethod.png'),
 ('Z SQL Method', 'Images/ZOA/sqlmethod.png'),
 ('common', 'Images/ZOA/common.png'),
 ('Z Gadfly Database Connection', 'Images/ZOA/db.png'),
 ('ZCatalog', 'Images/ZOA/ZCatalog.png'),
 ('Vocabulary', 'Images/ZOA/Vocabulary.png'),
 ('WebDAV Lock Manager', 'Images/ZOA/davlocked.png'),
]

EditorHelper.imgZopeExportFileModel = EditorHelper.imgCounter
EditorHelper.imgCounter = EditorHelper.imgCounter + 1

for m_type, file in ZOAImages:
    addZOAIcon(m_type)

class ZopeEditorModel(EditorModels.BasePersistentModel):
    modelIdentifier = 'Zope'
    def __init__(self, name, data, editor, saved, zopeObject):
        EditorModels.BasePersistentModel.__init__(self, name, data, editor, saved)
        self.zopeObj = zopeObject  #this is the instance of our node now

    def load(self, notify = true):
        EditorModels.BasePersistentModel.load(self, notify)

        self.modified = false
        self.savedAs = true
        self.saved = true

    def save(self):
        """ This is perhaps not the best style, but here all exceptions
            on saving are caught and transformed to TransportSaveErrors.
            To much maintenance for every Node type to add exceptions
        """
        from ExternalLib.xmlrpclib import Fault
        try:
            EditorModels.BasePersistentModel.save(self)
        except Fault, err:
            from Explorers import ExplorerNodes
            raise ExplorerNodes.TransportSaveError(Utils.html2txt(err.faultString),
                self.zopeObj.resourcepath)

class ZopeBlankEditorModel(ZopeEditorModel):
    """ Objects which are's loaded and saved and does not have a 'Main' view,
        but which should still be able to host views """
    def load(self, notify = true):
        self.modified = false
        self.savedAs = true
        self.saved = true
    def getPageName(self):
        if self.filename[-1] == '/':
            return os.path.basename(self.filename[:-1])
        else:
            return ZopeEditorModel.getPageName(self)


class ZopeDocumentModel(ZopeEditorModel):
    modelIdentifier = 'ZopeDocument'
    defaultName = 'zopedoc'
    bitmap = 'Package_s.png'

    saveBmp = 'Images/Editor/Save.png'

    def __init__(self, name, data, editor, saved, zopeObject):
        ZopeEditorModel.__init__(self, name, data, editor, saved, zopeObject)
        self.savedAs = true

    def saveAs(self, filename):
        raise 'Save as not supported'

    def getPageName(self):
        if self.zopeObj.name == 'index_html':
            return '%s (%s)' % (self.zopeObj.name,
                  string.split(self.zopeObj.resourcepath, '/')[-2])
        else:
            return self.zopeObj.name

class ZopeDTMLDocumentModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['DTML Document']

class ZopeDTMLMethodModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['DTML Method']

class ZopeSQLMethodModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['Z SQL Method']

class ZopePythonSourceModel(ZopeDocumentModel):
    modelIdentifier = 'ZopePythonSource'
    def __init__(self, name, data, editor, saved,  zopeObject):
        ZopeDocumentModel.__init__(self, name, data, editor, saved,  zopeObject)
        self._module = None

    def getModule(self):
        if self._module is None:
            import moduleparse
            wx.wxBeginBusyCursor()
            try:
                self._module = moduleparse.Module(
                    self.zopeObj.whole_name, string.split(self.data, '\012'))
            finally:
                wx.wxEndBusyCursor()
        return self._module

class ZopePythonScriptModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopePythonScript'
    defaultName = 'zopepythonscript'
    bitmap = 'Package_s.png'
    imgIdx = ZOAIcons['Script (Python)']

class ZopeExternalMethodModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopeExternalMethod'
    defaultName = 'zopeexternalmethod'
    bitmap = 'Package_s.png'
    imgIdx = ZOAIcons['External Method']

    def getModule(self):
        if self._module is None:
            self.moduleName = self.transport.resourcepath
        return ZopePythonSourceModel.getModule(self)

#class ZopeLocalFSFileModel(ZopeEditorModel):


class ZopeExportFileModel(EditorModels.BasePersistentModel):
    modelIdentifier = 'ZopeExport'
    defaultName = 'zexp'
    bitmap = 'ZopeExport_s.png'
    imgIdx = EditorHelper.imgZopeExportFileModel
    ext = '.zexp'
    fileModes = ('rb', 'wb')

EditorHelper.modelReg[ZopeExportFileModel.modelIdentifier] = ZopeExportFileModel
EditorHelper.extMap[ZopeExportFileModel.ext] = ZopeExportFileModel
EditorHelper.extMap['.dtml'] = HTMLSupport.HTMLFileModel

#-Controllers------------------------------------------------------------------
from Models import Controllers

class ZopeExportFileController(Controllers.UndockedController):
    Model = ZopeExportFileModel
    DefaultViews = []
    AdditionalViews = []
    def __init__(self, editor):
        Controllers.UndockedController.__init__(self, editor)

    def display(self, model):
        from Explorers import Explorer
        transports = Explorer.all_transports
        for cat in transports.entries:
            if cat.itemProtocol == 'zope':
                itms = cat.openList()
                localZopes = {}
                for itm in itms:
                    lp = itm.properties['localpath']
                    if lp: localZopes[itm.treename] = itm.properties
                if not localZopes:
                    wx.wxMessageBox('''No locally reachable Zopes found.
(Hint: Set the localpath property of the Zope connection)''')
                else:
                    dlg = wx.wxSingleChoiceDialog(self.editor,
                        "To which Zope's import directory should this file be copied?",
                        'Choose Zope instance', localZopes.keys())
                    try:
                        if dlg.ShowModal() == wx.wxID_OK:
                            selected = dlg.GetStringSelection()
                            props = localZopes[selected]
                            zexppath = string.replace(\
                                props['localpath'] +'/import/' +\
                                os.path.basename(model.transport.resourcepath),
                                '<LocalFS::directory>', '<LocalFS::file>')

                            model.load()
                            model.saveAs(zexppath)

                            self.editor.setStatus(\
                                  '.zexp file copied. Ready to import in Zope.')
                    finally:
                        dlg.Destroy()


# XXX Zope Controllers should create from the palette, Zope Companions should
# XXX manage only inspection

wxID_ZOPEINSPECT = wx.wxNewId()

class ZopeController(Controllers.PersistentController):
    inspectBmp = 'Images/Shared/Inspector.png'
    DefaultViews = []
    AdditionalViews = []
    def __init__(self, editor, Model):
        Controllers.PersistentController.__init__(self, editor)
        self.Model = Model

    def addEvts(self):
        Controllers.PersistentController.addEvts(self)
        self.addEvt(wxID_ZOPEINSPECT, self.OnInspect)

    def addTools(self, toolbar, model):
        Controllers.PersistentController.addTools(self, toolbar, model)
        Controllers.addTool(self.editor, toolbar, self.inspectBmp, 'Inspect', self.OnInspect)

    def addMenus(self, menu, model):
        accls = Controllers.PersistentController.addMenus(self, menu, model)
        menu.Append(-1, '-')
        self.addMenu(menu, wxID_ZOPEINSPECT, 'Inspect', accls, ())
        return accls

    def createModel(self, source, filename, main, saved, transport):
        return self.Model(filename, main, self.editor, saved, transport)

    def createNewModel(self, modelParent=None):
        pass

    def OnInspect(self, event):
        model = self.getModel()
        model.editor.explorer.controllers['zope'].doInspectZopeItem(model.transport)

Controllers.modelControllerReg.update( {ZopeExportFileModel: ZopeExportFileController,
    ZopeBlankEditorModel: ZopeController,
    ZopeDocumentModel: ZopeController,
    ZopeDTMLDocumentModel: ZopeController,
    ZopeDTMLMethodModel: ZopeController,
    ZopeSQLMethodModel: ZopeController,
    ZopePythonSourceModel: ZopeController,
    ZopePythonScriptModel: ZopeController,
    ZopeExternalMethodModel: ZopeController,
    ZopeEditorModel: ZopeController})
