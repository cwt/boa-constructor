""" Boa plug-in which allows linking a sub application to a main application.

Add the main application as a file in the modules list.

When run application is performed on the linked application or any of it's
modules, the main application file is run.

Note, as running is always proxied to the main application, you won't be able
to run the link app module itself from the IDE!

Linked apps can be chained but beware of cycles! ;)
"""

import sourceconst
from Models import PythonEditorModels, PythonControllers, EditorHelper, Controllers

EditorHelper.imgLinkAppModel = EditorHelper.imgIdxRange()

class LinkAppModel(PythonEditorModels.BaseAppModel):
    modelIdentifier = 'LinkApp'
    defaultName = 'LinkApp'
    bitmap = 'LinkApp_s.png'
    imgIdx = EditorHelper.imgLinkAppModel

    def getDefaultData(self):
        return sourceconst.defSig %(self.modelIdentifier, '')

    def run(self, args = ''):
        # find app module
        for name, Model in self.moduleModels.items():
            if Model.modelIdentifier in Controllers.appModelIdReg:
                filepath = self.moduleFilename(name)
                if self.editor.modules.has_key(filepath):
                    model = self.editor.modules[filepath].model
                else:
                    model = Model('', filepath, '', self.editor, 0, {})
                model.run(args)
                return

        wxLogWarning('No Application module found in modules list to link to')

class LinkAppController(PythonControllers.BaseAppController):
    Model = LinkAppModel


#-------------------------------------------------------------------------------
modelId = LinkAppModel.modelIdentifier
EditorHelper.modelReg[modelId] = LinkAppModel
Controllers.modelControllerReg[LinkAppModel]=LinkAppController
Controllers.appModelIdReg.append(modelId)
PaletteStore.paletteLists['New'].append(modelId)
PaletteStore.newControllers[modelId] = LinkAppController
