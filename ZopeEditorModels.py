#-----------------------------------------------------------------------------
# Name:        ZopeEditorModels.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001/06/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001
# Licence:     GPL
#-----------------------------------------------------------------------------
import string, os

from wxPython import wx

import EditorModels, Utils, EditorHelper
from PrefsKeys import keyDefs
import moduleparse

true = 1; false = 0

# Indexes for the ZOA relevant imagelist
ZOAImages = [\
 ('root', 'Images/ZOA/Zope.bmp'),
 ('Folder', 'Images/ZOA/Folder.bmp'),
 ('directory', 'Images/ZOA/Folder.bmp'),
 ('Local Directory', 'Images/ZOA/Folder.bmp'),
 ('DTML Document', 'Images/ZOA/dtmldoc.bmp'),
 ('Image', 'Images/ZOA/Image.bmp'),
 ('File', 'Images/ZOA/File.bmp'),
 ('User Folder', 'Images/ZOA/UserFolder_icon.bmp'),
 ('Version', 'Images/ZOA/version.bmp'),
 ('Control Panel', 'Images/ZOA/ControlPanel_icon.bmp'),
 ('Debug Information', 'Images/ZOA/DebugManager_icon.bmp'),
 ('Version Management', 'Images/ZOA/VersionManagement_icon.bmp'),
 ('Database Management', 'Images/ZOA/DatabaseManagement_icon.bmp'),
 ('Product Help', 'Images/ZOA/ProductHelp_icon.bmp'),
 ('Product Management', 'Images/ZOA/ProductFolder_icon.bmp'),
 ('Product', 'Images/ZOA/InstalledProduct_icon.bmp'),
 ('Z Class', 'Images/ZOA/ZClass_Icon.bmp'),
 ('Zope Factory', 'Images/ZOA/Factory_icon.bmp'),
 ('Zope Permission', 'Images/ZOA/Permission_icon.bmp'),
 ('Base Class', 'Images/ZOA/BaseClass.bmp'),
 ('Aggregation', 'Images/ZOA/attribute.bmp'),
 ('Broken Because Product is Gone', 'Images/ZOA/broken.bmp'),
 ('unknown', 'Images/ZOA/unknown.bmp'),
 ('Python Method', 'Images/ZOA/pymethod.bmp'),
 ('Script (Python)', 'Images/ZOA/PythonScript.bmp'),
 ('External Method', 'Images/ZOA/extmethod.bmp'),
 ('DTML Method', 'Images/ZOA/dtmlmethod.bmp'),
 ('Z SQL Method', 'Images/ZOA/sqlmethod.bmp'),
 ('common', 'Images/ZOA/common.bmp'),
 ('Z Gadfly Database Connection', 'Images/ZOA/db.bmp'),
 ('Z ODBC Database Connection', 'Images/ZOA/db.bmp'),
 ('Local File System', 'Images/ZOA/fs.bmp'),
 ('ZCatalog', 'Images/ZOA/ZCatalog.bmp'),
 ('Vocabulary', 'Images/ZOA/Vocabulary.bmp'),
]

imgCounter = EditorHelper.imgCounter

ZOAIcons = {}
for m_type, file in ZOAImages:
    ZOAIcons[m_type] = imgCounter
    imgCounter = imgCounter + 1


class ZopeEditorModel(EditorModels.BasePersistentModel):
    modelIdentifier = 'Zope'
    def __init__(self, name, data, editor, saved, zopeObject):
        EditorModels.BasePersistentModel.__init__(self, name, data, editor, saved)
        self.zopeObj = zopeObject  #this is the instance of our node now

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
    bitmap = 'Package_s.bmp'

    saveBmp = 'Images/Editor/Save.bmp'

    def __init__(self, name, data, editor, saved, zopeObject):
        ZopeEditorModel.__init__(self, name, data, editor, saved, zopeObject)
        self.savedAs = true

##    def addTools(self, toolbar):
##        ZopeEditorModel.addTools(self, toolbar)
##        Utils.AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save',
##              self.editor.OnSave)

##    def addMenus(self, menu):
##        accls = ZopeEditorModel.addMenus(self, menu)
##        self.addMenu(menu, EditorHelper.wxID_EDITORSAVE, 'Save', accls,
##              (keyDefs['Save']))
##        self.addMenu(menu, EditorHelper.wxID_EDITORCLOSEPAGE, 'Close', accls,
##              (keyDefs['Close']))
##        return accls

    def saveAs(self, filename):
        """ Saves contents of data to file specified by filename.
        Override this to catch name changes. """

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
    bitmap = 'Package_s.bmp'
    imgIdx = ZOAIcons['Script (Python)']

class ZopePythonMethodModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopePythonMethod'
    defaultName = 'zopepythonmethod'
    bitmap = 'Package_s.bmp'
    imgIdx = ZOAIcons['Python Method']

class ZopeExternalMethodModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopeExternalMethod'
    defaultName = 'zopeexternalmethod'
    bitmap = 'Package_s.bmp'
    imgIdx = ZOAIcons['External Method']

    def getModule(self):
        if self._module is None:
            self.moduleName = self.transport.resourcepath
        return ZopePythonSourceModel.getModule(self)

class ZopeExportFileModel(EditorModels.EditorModel):
    modelIdentifier = 'ZopeExport'
    defaultName = 'zexp'
    bitmap = 'ZopeExport_s.bmp'
    imgIdx = EditorModels.imgZopeExportFileModel
    ext = '.zexp'

EditorHelper.modelReg[ZopeExportFileModel.modelIdentifier] = ZopeExportFileModel
EditorHelper.extMap[ZopeExportFileModel.ext] = ZopeExportFileModel
