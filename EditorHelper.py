from wxPython.wx import wxNewId

[wxID_EDITOROPEN, wxID_EDITORSAVE, wxID_EDITORSAVEAS, wxID_EDITORCLOSEPAGE,
 wxID_EDITORREFRESH, wxID_EDITORDESIGNER, wxID_EDITORDEBUG, wxID_EDITORHELP,
 wxID_EDITORSWITCHAPP, wxID_DEFAULTVIEWS, wxID_EDITORSWITCHTO,
 wxID_EDITORTOGGLEVIEW, wxID_EDITORSWITCHEXPLORER, wxID_EDITORSWITCHSHELL,
 wxID_EDITORSWITCHPALETTE, wxID_EDITORSWITCHINSPECTOR, wxID_EDITORDIFF,
 wxID_EDITORCMPAPPS, wxID_EDITORHELPABOUT, wxID_EDITORPREVPAGE,
 wxID_EDITORNEXTPAGE, wxID_EDITORBROWSEFORW, wxID_EDITORBROWSEBACK,
 wxID_EDITORHELPGUIDE, wxID_EDITORHELPTIPS,
 wxID_EDITORPYCHECK, wxID_EDITORCONFPYCHECK,
 wxID_EDITORRELOAD,
 wxID_SETUPINSTALL, wxID_SETUPCLEAN, wxID_SETUPBUILD,
 wxID_SETUPSDIST, wxID_SETUPBDIST, wxID_SETUPBDIST_WININST, wxID_SETUPPY2EXE,
] = map(lambda _editor_menus: wxNewId(), range(35))

# Indexes for the imagelist
imgCounter=27
[imgFolder, imgPathFolder, imgCVSFolder, imgZopeSystemObj, imgZopeConnection,
 imgBoaLogo, imgFolderUp, imgFSDrive, imgFolderBookmark,

 imgAppModel, imgFrameModel, imgDialogModel, imgMiniFrameModel,
 imgMDIParentModel, imgMDIChildModel, imgModuleModel, imgPackageModel,
 imgTextModel, imgConfigFileModel, imgZopeExportFileModel, imgBitmapFileModel,
 imgZipFileModel, imgCPPModel, imgUnknownFileModel, imgHTMLFileModel,
 imgXMLFileModel, imgSetupModel,
 
] = range(imgCounter)

# Registry of all modules {modelIdentifier : Model} (populated by EditorModels)
modelReg = {}

# Mapping of file extension to model (populated by EditorModels)
extMap = {}
