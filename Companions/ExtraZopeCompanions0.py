from ZopeCompanions import ZopeCompanion
import PaletteStore

class PythonMethodZC(ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/PythonMethod/'
        mime, res = self.call(self.objPath, prodPath+'manage_addPythonMethod',
              id = self.name, title = '', params = '', body = 'pass')

class TransparentFolderZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addProduct/TransparentFolder/manage_addTransparentFolder',
              id = self.name, title = '')

class LocalFSZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addProduct/LocalFS/manage_addLocalFS',
              id = self.name, title = '', basepath = '')

class PyGreSQLDAZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addProduct/ZCatalog/manage_addZCatalog',
              id = self.name, title = '')

PaletteStore.paletteLists['Zope'].extend(['Python Method', 
      'LocalFS', 'Transparent Folder', 'PyGreSQLDA'] )

PaletteStore.compInfo.update({'Python Method': ['PythonMethod', PythonMethodZC],
    'LocalFS': ['LocalFS', LocalFSZC],
    'Transparent Folder': ['TransparentFolder', TransparentFolderZC],
    'PyGreSQLDA': ['PyGreSQLDA', PyGreSQLDAZC], })


from ZopeLib import ProdPageTemplates