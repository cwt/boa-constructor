import os

import ExplorerNodes, EditorHelper

true=1;false=0

class OpenModelsNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.openeditormodels'
    def __init__(self, editor, parent):
        ExplorerNodes.ExplorerNode.__init__(self, 'Editor', '', None, 
              EditorHelper.imgFolder, parent, {})
        self.editor = editor
        self.bold = true

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return true

    def createChildNode(self, name, model):
        return OpenModelItemNode(os.path.basename(name), name, model, self)

    def openList(self):
        res = []
        for name, modPage in self.editor.modules.items():
            res.append(self.createChildNode(name, modPage.model))
        return res


class OpenModelItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.model'
    def __init__(self, name, resourcepath, model, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, 
              model.imgIdx, parent, {})
        self.model = model

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return true
    
    def openList(self):
        res = []
        for view in self.model.views.keys():
            if self.model.views[view].canExplore:
                res.append(self.createChildNode(view, self.model))
        return res

    def createChildNode(self, name, model):
        return ModelViewItemNode(name, model, self)

class ModelViewItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.view'
    def __init__(self, name, model, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, '', None, 
              EditorHelper.imgFolder, parent, {})
        self.model = model
        
    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return true
    
    def openList(self):
        res = []
        for item in self.model.views[self.name].explore():
            res.append(ViewItemNode(item, '', None, -1, self, {}))
        return res

class ViewItemNode(ExplorerNodes.ExplorerNode):
    def open(self, editor):
        pass