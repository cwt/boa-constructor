#-----------------------------------------------------------------------------
# Name:        PrefsExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001/06/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001
# Licence:     GPL
#-----------------------------------------------------------------------------
import string, os, sys

from wxPython import wx
true=1;false=0

#sys.path.append('..')
import EditorHelper, ExplorerNodes, Preferences

class PreferenceGroupNode(ExplorerNodes.ExplorerNode):
    """ Represents a group of preference collections """
    defName = 'PrefsGroup'
    def __init__(self, name, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, name, None,
              EditorHelper.imgFolder, None)#parent)

        self.preferences = []

##    def destroy(self):
##        self.parent = None
##        self.preferences = ()

    def isFolderish(self):
        return true

    def openList(self):
        return self.preferences

    def notifyBeginLabelEdit(self, event):
        event.Veto()

class BoaPrefGroupNode(PreferenceGroupNode):
    """ The Preference node in the Explorer """
    def __init__(self, parent):
        PreferenceGroupNode.__init__(self, 'Preferences', parent)
        self.bold = true

        prefImgIdx = EditorHelper.imgZopeSystemObj

        self.source_pref = PreferenceGroupNode('Source', self)
        self.source_pref.preferences = [
            PreferenceCollectionNode('Python', {}, '', prefImgIdx, self),
            PreferenceCollectionNode('HTML', {}, '', prefImgIdx, self),
            PreferenceCollectionNode('XML', {}, '', prefImgIdx, self),
            PreferenceCollectionNode('CPP', {}, '', prefImgIdx, self),]
        self.preferences.append(self.source_pref)

        self.general_pref = UsedModuleSrcBsdPrefColNode('General',
            Preferences.exportedProperties,
            Preferences.pyPath+'/Preferences.py', prefImgIdx, self,
            Preferences)
        self.preferences.append(self.general_pref)

        if wx.wxPlatform == '__WXMSW__':
            file = 'PrefsMSW.py'
        else:
            file = 'PrefsGTK.py'
        self.general_pref = UsedModuleSrcBsdPrefColNode('Platform',
            Preferences.exportedProperties2,
            Preferences.pyPath+'/'+file, prefImgIdx, self, Preferences)
        self.preferences.append(self.general_pref)

        self.pychecker_pref = SourceBasedPrefColNode('PyChecker',
            ('*',), Preferences.pyPath+'/.pycheckrc', prefImgIdx, self)
        self.preferences.append(self.pychecker_pref)



class PreferenceCollectionNode(ExplorerNodes.ExplorerNode):
    """ Represents an inspectable preference collection """
    protocol = 'prefs'
    def __init__(self, name, props, resourcepath, imgIdx, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None,
              imgIdx, None, props)#parent, props)

    def open(self, editor):
        """ Populate inspector with preference items """
        comp = PreferenceCompanion(self.name, self)
        comp.updateProps()

        # Select in inspector
        editor.inspector.Raise()
        if editor.inspector.pages.GetSelection() != 1:
            editor.inspector.pages.SetSelection(1)
        editor.inspector.selectObject(comp, false)

    def isFolderish(self):
        return false

    def load(self):
        raise 'Not implemented'

    def save(self, filename, data):
        pass

    def notifyBeginLabelEdit(self, event):
        event.Veto()

import moduleparse

class SourceBasedPrefColNode(PreferenceCollectionNode):
    """ Preference collection represented by the global names in python module

    Only names which are also defined in properties are returned
    except when properties is a special match all tuple; ('*',)

    This only applies to names assigned to values ( x = 123 ) not to global
    names defined by classes functions and imports.
    """
    def __init__(self, name, props, resourcepath, imgIdx, parent):
        PreferenceCollectionNode.__init__(self, name, props, resourcepath,
              imgIdx, parent)

    def load(self):
        # XXX Fix when there is a generic factory to create nodes based on
        # XXX filename protocol
        module = moduleparse.Module(self.name,
              open(self.resourcepath).readlines())

        values = []
        comments = []
        # keep only names defined in the property list
        for name in module.global_order[:]:
            if self.properties != ('*',) and name[0] != '_' and \
                  name not in self.properties:
                module.global_order.remove(name)
                del module.globals[name]
            else:
                # XXX Should handle multiline assign
                code = string.join(module.source[\
                      module.globals[name].start-1 : \
                      module.globals[name].end], '\n')

                # Extract value
                s = string.find(code, '=')
                if s != -1:
                    values.append(string.strip(code[s+1:]))
                else:
                    values.append('')

                # Read possible comment/help
                comment = []
                idx = module.globals[name].start-2
                while idx >= 0:
                    line = string.strip(module.source[idx])
                    if line and line[0] == '#':
                        comment.append(string.lstrip(line[1:]))
                        idx = idx - 1
                    else:
                        break
                comment.reverse()
                comments.append(string.join(comment, '\n'))

        return module.global_order, values, module.globals, comments

    def save(self, filename, data):
        """ Updates one property """
        src = open(self.resourcepath).readlines()
        src[data[2].start-1] = '%s = %s\n' % (data[0], data[1])
        open(self.resourcepath, 'w').writelines(src)

class UsedModuleSrcBsdPrefColNode(SourceBasedPrefColNode):
    """ Also update the value of a global attribute of an imported module """
    def __init__(self, name, props, resourcepath, imgIdx, parent, module):
        SourceBasedPrefColNode.__init__(self, name, props, resourcepath, imgIdx,
              parent)
        self.module = module

    def save(self, filename, data):
        SourceBasedPrefColNode.save(self, filename, data)
        if hasattr(self.module, data[0]):
            setattr(self.module, data[0], eval(data[1]))

class ConfigBasedPrefsColNode(PreferenceCollectionNode):
    """ Preferences driven by config files """
    pass

class STCPrefsColNode(PreferenceCollectionNode):
    """ StyledTextControl preferences """
    pass

#---Companions------------------------------------------------------------------

from PropEdit import PropertyEditors
from wxPython import wx

class PreferenceCompanion(ExplorerNodes.ExplorerCompanion):
    def __init__(self, name, prefNode):
        ExplorerNodes.ExplorerCompanion.__init__(self, name)
        self.prefNode = prefNode

    def getPropEditor(self, prop):
        return PropertyEditors.StrConfPropEdit

    def getPropertyHelp(self, propName):
        for prop in self.propItems:
            if prop[0] == propName: return prop[3]
        else:
            return propName

    def getPropertyItems(self):
        order, vals, props, comments = self.prefNode.load()

        res = []
        for name, value, comment in map(None, order, vals, comments):
            res.append( (name, value, props[name], comment) )
        return res

    def setPropHook(self, name, value, oldProp):
        # XXX validate etc.
        try:
            eval(value)
        except Exception, error:
            wx.wxLogError('Error: '+str(error))
            return false
        else:
            newProp = (name, value) + oldProp[2:]
            self.prefNode.save(name, newProp)
            return true
