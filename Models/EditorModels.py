#----------------------------------------------------------------------
# Name:        EditorModels.py
# Purpose:     Model classes usually representing different types of
#              source code
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

# Behind the screen
# beyond interpretation
# essence

""" The model classes represent different types of source code files,
    Different views can be connected to a model  """

# XXX form inheritance

print 'importing Models.EditorModels'

import string, os, sys

from wxPython import wx

# XXX
#import PaletteMapping
import Preferences, Utils, EditorHelper
from Preferences import keyDefs

from sourceconst import *

true = 1;false = 0

_vc_hook = None

class EditorModel:
    defaultName = 'abstract'
    bitmap = 'None'
    imgIdx = -1
    closeBmp = 'Images/Editor/Close.png'
    objCnt = 0
    def __init__(self, name, data, editor, saved):
        self.active = false
        self.data = data
        self.savedAs = saved
        self.filename = name
        self.editor = editor
        self.transport = None
        self.prevSwitch = None

        self.views = {}
        self.modified = not saved
        self.viewsModified = []

##        self.objCnt = self.objCnt + 1

##    def __del__(self):
##        self.objCnt = self.objCnt - 1
##        print '__del__', self.__class__.__name__

    def destroy(self):
#        print 'destroy', self.__class__.__name__
#        for i in self.views.values():
#            print sys.getrefcount(i)

        del self.views
        del self.viewsModified
        del self.editor

    def reorderFollowingViewIdxs(self, idx):
        for view in self.views.values():
            if view.pageIdx > idx:
                view.pageIdx = view.pageIdx - 1

    def getDataAsLines(self):
        return string.split(self.data, '\012')

    def setDataFromLines(self, lines):
        data = self.data
        self.data = string.join(lines, '\012')
        self.modified = self.modified or self.data != data

    def hasUnsavedChanges(self):
        return self.modified or len(self.viewsModified)

    def notify(self):
        """ Update all views connected to this model.
            This method must be called after changes were made to the model """
        for view in self.views.values():
            view.update()

    def update(self):
        """ Rebuild additional derived structure, called when data is changed """

    def refreshFromViews(self):
        for view in self.viewsModified:
            self.views[view].refreshModel()

    def getPageName(self):
        return os.path.splitext(os.path.basename(self.filename))[0]

    def getSourceView(self):
        views = self.views
        if views.has_key('Source'):
            return views['Source']
        elif views.has_key('HTML'):
            return views['HTML']
        return None


class FolderModel(EditorModel):
    modelIdentifier = 'Folder'
    defaultName = 'folder'
    bitmap = 'Folder_s.png'
    imgIdx = EditorHelper.imgFolder

    def __init__(self, data, name, editor, filepath):
        EditorModel.__init__(self, name, data, editor, true)
        self.filepath = filepath

class SysPathFolderModel(FolderModel):
    modelIdentifier = 'SysPathFolder'
    defaultName = 'syspathfolder'
    bitmap = 'Folder_green.png'
    imgIdx = EditorHelper.imgPathFolder

class CVSFolderModel(FolderModel):
    modelIdentifier = 'CVS Folder'
    defaultName = 'cvsfolder'
    bitmap = 'Folder_cyan_s.png'
    imgIdx = EditorHelper.imgCVSFolder

    def __init__(self, data, name, editor, filepath):
        FolderModel.__init__(self, data, name, editor, filepath)
        self.readFiles()

    def readFile(self, filename):
        f = open(filename, 'r')
        try: return string.strip(f.read())
        finally: f.close()

    def readFiles(self):
        self.root = self.readFile(os.path.join(self.filepath, 'Root'))
        self.repository = self.readFile(os.path.join(self.filepath, 'Repository'))
        self.entries = []

        f = open(os.path.join(self.filepath, 'Entries'), 'r')
        dirpos = 0
        try:
            txtEntries = f.readlines()
            for txtEntry in txtEntries:
                txtEntry = string.strip(txtEntry)
                if txtEntry:
                    if txtEntry == 'D':
                        pass
                        # maybe add all dirs?
                    elif txtEntry[0] == 'D':
                        self.entries.insert(dirpos, CVSDir(txtEntry))
                        dirpos = dirpos + 1
                    else:
                        try:
                            self.entries.append(CVSFile(txtEntry, self.filepath))
                        except IOError: pass
        finally:
            f.close()

class BitmapFileModel(EditorModel):
    modelIdentifier = 'Bitmap'
    defaultName = 'bmp'
    bitmap = 'Bitmap_s.png'
    imgIdx = EditorHelper.imgBitmapFileModel
    ext = '.bmp'

class ZipFileModel(EditorModel):
    modelIdentifier = 'ZipFile'
    defaultName = 'zip'
    bitmap = 'ZipFile_s.png'
    imgIdx = EditorHelper.imgZipFileModel
    ext = '.zip'

class BasePersistentModel(EditorModel):
    fileModes = ('r', 'w')
    saveBmp = 'Images/Editor/Save.png'
    saveAsBmp = 'Images/Editor/SaveAs.png'

    def load(self, notify = true):
        """ Loads contents of data from file specified by self.filename.
            Note: Load's not really used much currently cause objects are
                  constructed with their data as parameter """
        if not self.transport:
            raise 'No transport for loading'

        self.data = self.transport.load(mode=self.fileModes[0])
        self.modified = false
        self.saved = false
        self.update()
        if notify: self.notify()

    def save(self, overwriteNewer=false):
        """ Saves contents of data to file specified by self.filename. """
        if not self.transport:
            raise 'No transport for saving'

        if self.filename:
            filename = self.transport.assertFilename(self.filename)
            # this check is to minimise interface change.
            if overwriteNewer:
                self.transport.save(filename, self.data, mode=self.fileModes[1], 
                      overwriteNewer=true)
            else:
                self.transport.save(filename, self.data, mode=self.fileModes[1])
            self.modified = false
            self.saved = true

            for view in self.views.values():
                view.saveNotification()

            if _vc_hook:
                _vc_hook.save(filename, self.data, mode=self.fileModes[1])
        else:
            raise 'No filename'

    def saveAs(self, filename):
        """ Saves contents of data to file specified by filename.
            Override this to catch name changes. """
        # Catch transport changes
        from Explorers.Explorer import splitURI, getTransport
        protO, catO, resO, uriO = splitURI(self.filename)
        protN, catN, resN, uriN = splitURI(filename)

        if protO != protN:
            self.transport = getTransport(protN, catN, resN,
                  self.editor.explorer.tree.transports)

        # Rename and save
        self.filename = filename
        self.save()
        self.savedAs = true

    def localFilename(self, filename=None):
        if filename is None: filename = self.filename
        from Explorers.Explorer import splitURI
        return splitURI(filename)[2]
        
    def assertLocalFile(self, filename=None):
        if filename is None:
            filename = self.filename
        from Explorers.Explorer import splitURI
        prot, cat, filename, uri = splitURI(filename)
        assert prot=='file', 'Operation only supported on the filesystem.'
        return filename

    def new(self):
        self.data = ''
        self.savedAs = false
        self.modified = true
        self.update()
        self.notify()

class PersistentModel(BasePersistentModel):
    def __init__(self, data, name, editor, saved):
        BasePersistentModel.__init__(self, name, data, editor, saved)
        if data: self.update()

    def load(self, notify=true):
        BasePersistentModel.load(self, false)
        self.update()
        if notify: self.notify()

class SourceModel(BasePersistentModel):
    modelIdentifier = 'Source'
    def __init__(self, data, name, editor, saved):
        BasePersistentModel.__init__(self, name, data, editor, saved)

    def getCVSConflicts(self):
        # needless obscurity
        # numedLines = apply(map, (None,) + (lines, range(len(lines))) )

        # use model.module.source
        conflictStart = -1
        confCnt = 0
        lineNo = 0
        conflicts =[]
        for line in self.getDataAsLines():
            if line[:8] == '<<<<<<< ' and \
                  string.strip(line[8:]) == os.path.basename(self.filename):
                conflictStart = lineNo
            if line[:8] == '>>>>>>> ':
                rev = line[8:]
                conflicts.append( (rev, conflictStart, lineNo - conflictStart) )
                confCnt = confCnt + 1
            lineNo = lineNo + 1
        return conflicts

    def applyChangeBlock(self, conflict, blockIdx):
        rev, start, size = conflict
        lines = self.getDataAsLines()

        blocks = Utils.split_seq(lines[start+1 : start+size], '=======')
        lines[start:start+size+1] = blocks[blockIdx]
        self.setDataFromLines(lines)

        self.update()
        self.notify()

        self.editor.updateModuleState(self)

    def acceptConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 1)

    def rejectConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 0)

#class DiffModel(PersistentModel):
#    modelIdentifier = 'Diff'
#    defaultName = 'diff'
#    bitmap = 'Diff_s.png'
#    imgIdx = EditorHelper.imgDiffModel
#    ext = '.diff'

class TextModel(PersistentModel):
    modelIdentifier = 'Text'
    defaultName = 'text'
    bitmap = 'Text_s.png'
    imgIdx = EditorHelper.imgTextModel
    ext = '.txt'
    
class UnknownFileModel(TextModel):
    modelIdentifier = 'Unknown'
    defaultName = '*'
    bitmap = 'Unknown_s.png'
    imgIdx = EditorHelper.imgUnknownFileModel
    ext = '.*'

class InternalFileModel(TextModel):
    modelIdentifier = 'Internal'
    defaultName = ''
    bitmap = 'InternalFile_s.png'
    imgIdx = EditorHelper.imgInternalFileModel
    ext = '.intfile'

#-------------------------------------------------------------------------------

modelReg = EditorHelper.modelReg
extMap = EditorHelper.extMap

# model registry: add to this dict to register a Model (needed for explorer images)
modelReg.update({
            TextModel.modelIdentifier: TextModel,
            ZipFileModel.modelIdentifier: ZipFileModel,
            UnknownFileModel.modelIdentifier: UnknownFileModel,
            BitmapFileModel.modelIdentifier: BitmapFileModel,
            InternalFileModel.modelIdentifier: InternalFileModel,
            })

extMap[''] = TextModel
extMap['.jpg'] = extMap['.gif'] = extMap['.png'] = BitmapFileModel

EditorHelper.imageExtReg.extend(['.bmp', '.jpg', '.gif', '.png'])
EditorHelper.internalFilesReg.extend(['.umllay', '.implay', '.brk', '.trace', '.stack', '.cycles', '.prof', '.cached'])
EditorHelper.pythonBinaryFilesReg.extend(['.pyc', '.pyo', '.pyd'])
EditorHelper.binaryFilesReg.extend(['.zip', '.zexp', '.prof'])
