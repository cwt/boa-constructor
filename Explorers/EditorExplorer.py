import os, string

from wxPython import wx

import ExplorerNodes, EditorHelper, Utils

true=1;false=0

[wxID_EDTGOTO, wxID_EDTRELOAD, wxID_EDTCLOSE, wxID_EDTMOVEUP, wxID_EDTMOVEDOWN, 
 wxID_EDTCOPYPATH] =\
 map(lambda _init_ctrls: wx.wxNewId(), range(6))

class EditorController(ExplorerNodes.Controller):
    closeBmp = 'Images/Editor/Close.bmp'
    moveUpBmp = 'Images/Shared/up.bmp'
    moveDownBmp = 'Images/Shared/down.bmp'

    def __init__(self, editor, list):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.wxMenu()

        self.editorMenuDef = ( (wxID_EDTGOTO, 'Goto', self.OnGotoModel, '-'),
                               (-1, '-', None, ''),
                               (wxID_EDTRELOAD, 'Refresh', self.OnReloadItems, '-'),
                               (-1, '-', None, '-'),
                               (wxID_EDTCLOSE, 'Close', self.OnCloseModels, self.closeBmp),
                               (-1, '-', None, ''),
                               (wxID_EDTMOVEUP, 'Move up', self.OnMoveModelUp, self.moveUpBmp),
                               (wxID_EDTMOVEDOWN, 'Move down', self.OnMoveModelDown, self.moveDownBmp), 
                               (-1, '-', None, '-'),
                               (wxID_EDTCOPYPATH, 'Copy filepath(s) to clipboard', self.OnCopyPath, '-'),
                               )
    
        self.setupMenu(self.menu, self.list, self.editorMenuDef)
        self.toolbarMenus = [self.editorMenuDef]

    def destroy(self):
        self.editorMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def editorUpdateNotify(self, info=''):
        self.OnReloadItems(None)

    def OnReloadItems(self, event):
        if self.list.node:
            self.list.refreshCurrent()

    def OnCloseModels(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            for node in nodes:
                self.editor.closeModulePage(node.modulePage)
    
    def moveModel(self, node, idx, direc):
        page = self.editor.tabs.GetPage(idx)
        text = self.editor.tabs.GetPageText(idx)
        if wx.wxPlatform == '__WXMSW__':
            imgIdx = self.editor.tabs.GetPageImage(idx)
        self.editor.tabs.RemovePage(idx)
        if wx.wxPlatform == '__WXMSW__':
            self.editor.tabs.InsertPage(idx+direc, page, text, false, imgIdx)
        else:
            self.editor.tabs.InsertPage(idx+direc, page, text, false)

        # swap the two tIdx's
        for modPage in self.editor.modules.values():
            if modPage.tIdx == idx:
                modPage.tIdx = idx + direc
            elif modPage.tIdx == idx + direc:
                modPage.tIdx = idx

        self.list.refreshCurrent()
        self.list.selectItemByIdx(idx+direc-1)

    def OnMoveModelUp(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.wxLogError('Can only move 1 at a time')
            else:
                node = nodes[0]
                idx = node.modulePage.tIdx
                if idx == 2:
                    wx.wxLogError('Already at the beginning')
                else:
                    self.moveModel(node, idx, -1)
                            
    def OnMoveModelDown(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.wxLogError('Can only move 1 at a time')
            else:
                node = nodes[0]
                idx = node.modulePage.tIdx
                if idx == self.editor.tabs.GetPageCount() -1:
                    wx.wxLogError('Already at the end')
                else:
                    self.moveModel(node, idx, 1)

    def OnGotoModel(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.wxLogError('Can only goto 1 at a time')
            else:
                nodes[0].open(self.editor)

    def OnCopyPath(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            paths = []
            for node in nodes:
                paths.append(node.resourcepath)
            Utils.writeTextToClipboard(string.join(paths, os.linesep))
            
class OpenModelsNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.open-models'
    def __init__(self, editor, parent):
        ExplorerNodes.ExplorerNode.__init__(self, 'Editor', '', None, 
              EditorHelper.imgOpenEditorModels, parent, {})
        self.editor = editor
        self.bold = true
        self.vetoSort = true

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return true

    def createChildNode(self, name, modulePage):
        return OpenModelItemNode(os.path.basename(name), name, modulePage, self)

    def openList(self):
        res = []
        mods = []
        for name, modPage in self.editor.modules.items():
            mods.append( (modPage.tIdx, name, modPage) )
        
        mods.sort()
        for idx, name, modPage in mods:
            res.append(self.createChildNode(name, modPage))
        return res


class OpenModelItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.model'
    def __init__(self, name, resourcepath, modulePage, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, 
              modulePage.model.imgIdx, parent, {})
        self.modulePage = modulePage
        self.model = modulePage.model

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return false
    
    def open(self, editor):
        editor.openOrGotoModule(self.resourcepath)
    
##    def openList(self):
##        res = []
##        for view in self.model.views.keys():
##            if self.model.views[view].canExplore:
##                res.append(self.createChildNode(view, self.model))
##        return res
##
##    def createChildNode(self, name, model):
##        return ModelViewItemNode(name, model, self)

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