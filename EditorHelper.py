import Preferences, Utils

(wxID_EDITOROPEN, wxID_EDITORSAVE, wxID_EDITORSAVEAS, wxID_EDITORCLOSEPAGE,
 wxID_EDITORREFRESH, wxID_EDITORDESIGNER, wxID_EDITORDEBUG, wxID_EDITORHELP,
 wxID_EDITORSWITCHAPP, wxID_DEFAULTVIEWS, wxID_EDITORSWITCHTO, wxID_EDITORADDTOAPP,
 wxID_EDITORTOGGLEVIEW, wxID_EDITORSWITCHEXPLORER, wxID_EDITORSWITCHSHELL,
 wxID_EDITORSWITCHPALETTE, wxID_EDITORSWITCHINSPECTOR, wxID_EDITORDIFF, wxID_EDITORTOGGLERO,
 wxID_EDITORHELPABOUT, wxID_EDITORHELPGUIDE, wxID_EDITORHELPTIPS, 
 wxID_EDITORHELPFIND,
 wxID_EDITORPREVPAGE, wxID_EDITORNEXTPAGE, 
 wxID_EDITORBROWSEFORW, wxID_EDITORBROWSEBACK,
 wxID_EDITORPYCHECK, wxID_EDITORCONFPYCHECK,
 wxID_EDITORRELOAD, wxID_EDITORATTACHTODEBUGGER, wxID_EDITOREXITBOA,
 wxID_EDITORHIDEPALETTE,
) = Utils.wxNewIds(33)

(wxID_SETUPINSTALL, wxID_SETUPCLEAN, wxID_SETUPBUILD,
 wxID_SETUPSDIST, wxID_SETUPBDIST, wxID_SETUPBDIST_WININST, wxID_SETUPPY2EXE,
) = Utils.wxNewIds(7)

(wxID_MODULEPROFILE, wxID_MODULECHECKSOURCE, wxID_MODULERUNAPP, wxID_MODULERUN,   
 wxID_MODULERUNPARAMS, wxID_MODULEDEBUG, wxID_MODULEDEBUGPARAMS, 
 wxID_MODULEDEBUGSTEPIN, wxID_MODULEDEBUGSTEPOVER, wxID_MODULEDEBUGSTEPOUT,
 wxID_MODULECYCLOPSE, wxID_MODULEREINDENT,
) = Utils.wxNewIds(12)

(wxID_APPSAVEALL, wxID_APPCMPAPPS, wxID_APPCRASHLOG) = Utils.wxNewIds(3)

# Indexes for the imagelist
imgCounter=32
(imgFolderUp, imgFolder, imgPathFolder, imgCVSFolder, imgZopeSystemObj, 
 imgZopeConnection, imgBoaLogo, imgFSDrive, imgNetDrive, imgFolderBookmark,
 imgOpenEditorModels, imgPrefsFolder, imgPrefsSTCStyles,

 imgAppModel, imgFrameModel, imgDialogModel, imgMiniFrameModel,
 imgMDIParentModel, imgMDIChildModel, imgPyAppModel, imgModuleModel, imgPackageModel,
 imgTextModel, imgConfigFileModel, imgZopeExportFileModel, imgBitmapFileModel,
 imgZipFileModel, imgCPPModel, imgUnknownFileModel, imgHTMLFileModel,
 imgXMLFileModel, imgSetupModel,
) = range(imgCounter)

# Registry of all modules {modelIdentifier : Model} (populated by EditorModels)
modelReg = {}

# Mapping of file extension to model (populated by EditorModels)
extMap = {}
