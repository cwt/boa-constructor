import os, sys

#---Model-----------------------------------------------------------------------

# Define new zope image and a Model for opening in the Editor
from ZopeLib.ZopeEditorModels import addZOAImage, ZOAIcons, ZopeDocumentModel, ZopeController
from Models import Controllers

addZOAImage('Page Template', 'Images/ZOA/ZopePageTemplate.png')

class ZopePageTemplateModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['Page Template']

#---Controller------------------------------------------------------------------
class PageTemplateZopeController(ZopeController):
    def OnSave(self, event):
        ZopeController.OnSave(self, event)
        # trigger a reload after saving so that errors saved as comments in the
        # source are displayed
        self.OnReload(event)

# Connect controller to the model
Controllers.modelControllerReg[ZopePageTemplateModel] = PageTemplateZopeController

#---Views-----------------------------------------------------------------------

from ZopeLib import ZopeViews
class ZopePTHTMLView(ZopeViews.ZopeHTMLView):
    viewName = 'Source.html'
    def generatePage(self):
        import urllib
        url = 'http://%s:%d/%s/source.html'%(self.model.zopeObj.properties['host'],
              self.model.zopeObj.properties['httpport'],
              self.model.zopeObj.whole_name())
        f = urllib.urlopen(url)
        return f.read()

#---Explorer--------------------------------------------------------------------

# Node in the explorer
from ZopeLib.ZopeExplorer import ZopeNode, zopeClassMap
from Models import HTMLSupport
class PageTemplateNode(ZopeNode):
    Model = ZopePageTemplateModel
    defaultViews = (HTMLSupport.HTMLSourceView,)
    additionalViews = (ZopeViews.ZopeUndoView,
          ZopeViews.ZopeSecurityView, ZopePTHTMLView, ZopeViews.ZopeHTMLView)
    def save(self, filename, data, mode='wb'):
        self.getResource().pt_upload('', data)

zopeClassMap['Page Template'] = PageTemplateNode

#---Companion-------------------------------------------------------------------

# Companion used for creation from palette and inspection/posting of props
from ZopeLib.ZopeCompanions import CustomZopePropsMixIn, ZopeCompanion
class PageTemplateZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/PageTemplates/'
        mime, res = self.call(self.objPath, prodPath+'manage_addPageTemplate',
              id = self.name, title = '')

    def getProps(self):
        path, name = os.path.split(self.objPath)
        mime, res = self.call(path, 'zoa/props/PageTemplate', name=name)
        return eval(res)

    def SetProp(self, name, value):
        props = self.getProps()
        props[name] = value
        path, name = os.path.split(self.objPath)

        mime, res = self.call(self.objPath, 'pt_editAction',
            title = props['title'],
            text = self.call(self.objPath, 'document_src'),
            content_type = props['content_type'],
            expand = props['expand'])

    propOrder = ('title', 'content_type', 'expand')
    propTypeMap = {'title':       ('string', 'title'),
                   'content_type':('string', 'content_type'),
                   'expand':      ('boolean', 'expand'),
                  }

# Add to the Zope palette
import PaletteStore
PaletteStore.paletteLists['Zope'].append('Page Template')
PaletteStore.compInfo['Page Template'] = ['ZopePageTemplate', PageTemplateZC]
