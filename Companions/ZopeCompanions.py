from BaseCompanions import Companion
from ZopeLib import Client, ExtMethDlg
from ZopeLib.DateTime import DateTime
import RTTI
import moduleparse
import string
from wxPython import wx
from PropEdit.PropertyEditors import StrZopePropEdit, BoolZopePropEdit, EvalZopePropEdit
import PaletteStore

# XXX This creation logic should be in the model, the companions should only
# XXX manage prperties

class ZopeConnection:
    def connect(self, host, port, user, password):
#        self.svr = rpc.rpc_server(host, port, user, password)
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def parseInstanceListToTypeLst(self, instLstStr):
        instLstStr = instLstStr[1:-1]
        instLst = methodparse.safesplitfields(instLstStr, ',')
        tpeLst = []
        for inst in instLst:
            key, val = string.split(inst[1:-1], ', ')
            val = string.split(val[1:], ' ')[0]
            tpeLst.append( (key, val) )
        return tpeLst

    def call(self, objPath, method, **kw):
        try:
            wx.wxBeginBusyCursor()
            try:
                url = 'http://%s:%d/%s/%s' % (self.host, self.port, objPath, method)
                return apply(Client.call, (url, self.user, self.password), kw)
            finally:
                wx.wxEndBusyCursor()
        except Client.ServerError, rex:
            return None, rex

    def callkw(self, objPath, method, kw):
        try:
            wx.wxBeginBusyCursor()
            try:
                url = 'http://%s:%d/%s/%s' % (self.host, self.port, objPath, method)
                return apply(Client.call, (url, self.user, self.password), kw)
            finally:
                wx.wxEndBusyCursor()
        except Client.ServerError, rex:
            return None, rex

class ZopeCompanion(Companion, ZopeConnection):
    propMapping = {'string': StrZopePropEdit,
                   'boolean': BoolZopePropEdit,
                   'default': EvalZopePropEdit}
    def __init__(self, name, objPath, localPath = ''):
        Companion.__init__(self, name)
        self.objPath = objPath
#        self.propMap = []
        self.propItems = []
        self.designer = None
        self.control = None
        self.localPath = localPath

    def constructor(self):
        return {}
    def events(self):
        return []
    def getEvents(self):
        return []
    def getPropEditor(self, prop):
        return self.propMapping.get(self.getPropertyType(prop), self.propMapping['default'])
    def getPropOptions(self, prop):
        return []
    def getPropNames(self, prop):
        return []
    def checkTriggers(self, name, oldValue, value):
        pass
    def persistProp(self, name, setterName, value):
        pass
    def propIsDefault(self, name, setterName):
        return 1
    def propRevertToDefault(self, name, setterName):
        pass

    def updateZopeProps(self):
        self.propItems = self.getPropertyItems()
        self.propMap = self.getPropertyMap()

    def getPropList(self):
        propLst = []
        for prop in self.propItems:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        return {'constructor':[], 'properties': propLst}

    def getObjectItems(self):
        mime, res = self.call(self.objPath, 'objectItems')
        return self.parseInstanceToTypeList(res)

    def getPropertyMap(self):
##        # [ {'id': <prop name>, 'type': <prop type>}, ... ]
        # This is a workaround for zope returning 2 prop map items incorrectly
        if len(self.propItems) == 2:
            mime, tpe1 = self.call(self.objPath, 'getPropertyType', id=self.propItems[0][0])
            mime, tpe2 = self.call(self.objPath, 'getPropertyType', id=self.propItems[1][0])
            return [ {'id': self.propItems[0][0], 'type': tpe1},
                     {'id': self.propItems[1][0], 'type': tpe2} ]
        else:
            mime, res = self.call(self.objPath, 'propertyMap')
            return eval(res)

    def getPropertyItems(self):
        # [ (<prop name>, <prop value>), ...]
        mime, res = self.call(self.objPath, 'propertyItems')
        return eval(res)

    def getPropertyType(self, name):
        for p in self.propMap:
            if p['id'] == name:
                if name == 'passwd':
                    return 'passwd'
                return p['type']
        return 'string'

    def setZopeProp(self, name, value):
        mime, res = self.callkw(self.objPath, 'manage_changeProperties', {name: value})#'id=name, value=value, type = tpe)

    def addProperty(self, name, value, tpe):
        mime, res = self.call(self.objPath, 'manage_addProperty', id=name, value=value, type = tpe)

    def delProperty(self, name):
        mime, res = self.call(self.objPath, 'manage_delProperties', ids=[name])

    def GetProp(self, name):
        for prop in self.propItems:
            if prop[0] == name: return prop[1]

    def SetProp(self, name, value):
        for idx in range(len(self.propItems)):
            if self.propItems[idx][0] == name:
                self.setZopeProp(name, value)
                self.propItems[idx] = (name, value)
                break

class DTMLDocumentZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addDTMLDocument', id = self.name)

class DTMLMethodZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addDTMLMethod', id = self.name)

class FolderZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addFolder', id = self.name)

class FileZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addFile', id = self.name, file = '')

class ImageZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addImage', id = self.name, file = '')

class ExternalMethodZC(ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/ExternalMethod/'
        dlg = ExtMethDlg.ExtMethDlg(None, self.localPath)
        try:
            if dlg.ShowModal() == wx.wxID_OK:
                mime, res = self.call(self.objPath, prodPath+'manage_addExternalMethod',
                      id = self.name, title = '',
                      function = dlg.chFunction.GetValue(),
                      module = dlg.cbModule.GetValue())
        finally:
            dlg.Destroy()

class PythonMethodZC(ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/PythonMethod/'
        mime, res = self.call(self.objPath, prodPath+'manage_addPythonMethod',
              id = self.name, title = '', params = '', body = 'pass')

class MailHostZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addMailHost', id = self.name)

class ZCatalogZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addProduct/ZCatalog/manage_addZCatalog',
              id = self.name, title = '')

##class SQLMethodZC(ZopeCompanion):
##    zMeth = 'manage_addProduct.ZSQLMethods.add'

class UserFolderZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addUserFolder')

PaletteStore.paletteLists['Zope'].extend(['DTML Document', 'DTML Method', 
      'Folder', 'File', 'Image', 'External Method', 'Python Method', 
      'Mail Host', 'ZCatalog', 'User Folder'] )#'SQL Method',

PaletteStore.compInfo.update({'DTML Document': ['DTMLDocument', DTMLDocumentZC],
    'DTML Method': ['DTMLMethod', DTMLMethodZC],
    'Folder': ['Folder', FolderZC],
    'File': ['File', FileZC],
    'Image': ['Image', ImageZC],
    'External Method': ['ExternalMethod', ExternalMethodZC],
    'Python Method': ['PythonMethod', PythonMethodZC],
    'Mail Host': ['MailHost', MailHostZC],
    'ZCatalog': ['ZCatalog', ZCatalogZC],
#    'SQL Method': ['SQLMethod', SQLMethodZC],
    'User Folder': ['UserFolder', UserFolderZC],

})
