import Preferences, Utils

(wxID_EDITOROPEN, wxID_EDITORSAVE, wxID_EDITORSAVEAS, wxID_EDITORCLOSEPAGE,
 wxID_EDITORREFRESH, wxID_EDITORDESIGNER, wxID_EDITORDEBUG, wxID_EDITORHELP,
 wxID_DEFAULTVIEWS, wxID_EDITORSWITCHTO, wxID_EDITORDIFF, wxID_EDITORPATCH,
 wxID_EDITORTOGGLEVIEW, wxID_EDITORSWITCHEXPLORER, wxID_EDITORSWITCHSHELL,
 wxID_EDITORSWITCHPALETTE, wxID_EDITORSWITCHINSPECTOR,
 wxID_EDITORTOGGLERO, wxID_EDITORHELPFIND, wxID_EDITORRELOAD,
 wxID_EDITORHELPABOUT, wxID_EDITORHELPGUIDE, wxID_EDITORHELPTIPS,
 wxID_EDITORPREVPAGE, wxID_EDITORNEXTPAGE,
 wxID_EDITORBROWSEFORW, wxID_EDITORBROWSEBACK,
 wxID_EDITOREXITBOA, wxID_EDITOROPENRECENT,
 wxID_EDITORHIDEPALETTE, wxID_EDITORWINDIMS, wxID_EDITORWINDIMSLOAD,
 wxID_EDITORWINDIMSSAVE, wxID_EDITORWINDIMSRESDEFS,
 wxID_EDITORSWITCHPREFS,
) = Utils.wxNewIds(35)

builtinImgs =('Images/Modules/FolderUp_s.png',
              'Images/Modules/Folder_s.png',
              'Images/Modules/Folder_green_s.png',
              'Images/Modules/Folder_cyan_s.png',
              'Images/Shared/SystemObj.png',
              'Images/Modules/ZopeConn_s.png',
              'Images/Shared/BoaLogo.png',
              'Images/Modules/Drive_s.png',
              'Images/Modules/NetDrive_s.png',
              'Images/Modules/FolderBookmark_s.png',
              'Images/Modules/OpenEditorModels_s.png',
              'Images/Modules/PrefsFolder_s.png',
              'Images/Shared/PrefsSTCStyles.png',
              'Images/Editor/RecentFiles.png')

imgCounter=0
def imgIdxRange(cnt):
    global imgCounter
    rng = range(imgCounter, imgCounter + cnt)
    imgCounter = imgCounter + cnt
    return rng

# Indexes for the imagelist
(imgFolderUp, imgFolder, imgPathFolder, imgCVSFolder, imgSystemObj,
 imgZopeConnection, imgBoaLogo, imgFSDrive, imgNetDrive, imgFolderBookmark,
 imgOpenEditorModels, imgPrefsFolder, imgPrefsSTCStyles, imgRecentFiles,

 imgTextModel, imgBitmapFileModel, imgZipFileModel,
 imgUnknownFileModel, imgInternalFileModel,
) = imgIdxRange(19)

# Registry of all modules {modelIdentifier : Model} (populated by EditorModels)
# Used for images and header identifier
modelReg = {}
# Mapping of file extension to model (populated by EditorModels)
extMap = {}
# List of image file extensions
imageExtReg = []
# List of extensions for internal filetypes created by Boa
internalFilesReg = []
# List of files which can be further identified by reading a header from the source
inspectableFilesReg = []
# List of extensions used by Python
pythonBinaryFilesReg = []
# List of extensions for additional binary files (will not be searched)
binaryFilesReg = []
def getBinaryFiles():
    return imageExtReg + binaryFilesReg + pythonBinaryFilesReg

def initExtMap():
    # All non python files identified by extension
    for mod in modelReg.values():
        if mod.ext not in inspectableFilesReg + ['.*', '.intfile', '.pybin']:
            extMap[mod.ext] = mod
