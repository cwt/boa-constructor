#----------------------------------------------------------------------
# Name:        PaletteMapping.py
# Purpose:     Module that initialises the Palette's data and provides
#              the namespace in which design time code is evaluated
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

""" Based on core support preferences this module initialises Companion, Model,
View and Controller classes. It also executes all active Plug-ins.

The namespace of this module is used to evalute code at Design-Time with evalCtrl.
Hence the needed import * and execfile.

"""

# XXX This module should be renamed it's function has changed over time
# XXX Maybe: BoaNamespace/DesignTimeNamespace

import os

import Preferences, Utils
from Preferences import IS
import PaletteStore

from wxPython.wx import *

if Preferences.csWxPythonSupport:
    # This should be the first time the Companion classes are imported
    # As the modules are imported they add themselves to the PaletteStore
    from Companions.Companions import *

    from Companions.FrameCompanions import *
    from Companions.ContainerCompanions import *
    from Companions.BasicCompanions import *
    from Companions.ButtonCompanions import *
    from Companions.ListCompanions import *
    from Companions.GizmoCompanions import *
    if Utils.IsComEnabled():
        from Companions.ComCompanions import *
    from Companions.UtilCompanions import *
    from Companions.DialogCompanions import *

# Zope requires spesific support
if Utils.transportInstalled('ZopeLib.ZopeExplorer'):
    from ZopeLib.ZopeCompanions import *

#-Controller imports which auto-regisers themselves on the Palette--------------

from Models import EditorHelper

if Preferences.csPythonSupport:
    import Models.PythonControllers

if Preferences.csWxPythonSupport:
    import Models.wxPythonControllers

if Preferences.csPythonSupport and not Preferences.csWxPythonSupport:
    # useful hack to alias wxApp modules to PyApp modules when wxPython support
    # is not loaded
    from Models.PythonEditorModels import PyAppModel
    EditorHelper.modelReg['App'] = PyAppModel

# The text and makepy controllers are registered outside the Controllers
# module so that their palette order can be fine tuned
from Models import Controllers
PaletteStore.newControllers['Text'] = Controllers.TextController
PaletteStore.paletteLists['New'].append('Text')

#-Registration of other built in support---------------------------------------
if Preferences.csConfigSupport: from Models import ConfigSupport
if Preferences.csCppSupport: from Models import CPPSupport
if Preferences.csHtmlSupport: from Models import HTMLSupport
if Preferences.csXmlSupport: from Models import XMLSupport

if Utils.transportInstalled('ZopeLib.ZopeExplorer'):
    import ZopeLib.ZopeEditorModels

if Utils.IsComEnabled():
    PaletteStore.newControllers['MakePy-Dialog'] = Controllers.MakePyController
    PaletteStore.paletteLists['New'].append('MakePy-Dialog')

#-Plug-ins initialisation-------------------------------------------------------
if Preferences.pluginPaths:
    print 'executing plug-ins...'
    fails = Preferences.failedPlugins
    succeeded = Preferences.installedPlugins

    for pluginFilename, ordered, enabled in Utils.buildPluginExecList():
        if not enabled:
            continue

        pluginBasename = os.path.basename(pluginFilename)
        filename = string.lower(pluginFilename)
        try:
            execfile(pluginFilename)
            succeeded.append(filename)
        except Utils.SkipPluginSilently, msg:
            fails[filename] = ('Skipped', msg)
        except Utils.SkipPlugin, msg:
            fails[filename] = ('Skipped', msg)
            wxLogWarning('Plugin skipped: %s, %s'%(pluginBasename, msg))
        except Exception, error:
            fails[filename] = ('Error', str(error))
            if Preferences.pluginErrorHandling == 'raise':
                raise
            elif Preferences.pluginErrorHandling == 'report':
                wxLogError('Problem executing plug-in %s:\n%s' %\
                    (pluginBasename, str(error)) )
            # else ignore

#-------------------------------------------------------------------------------
# called after all models have been imported and plugins executed
EditorHelper.initExtMap()
#-------------------------------------------------------------------------------

# XXX legacy references
palette = PaletteStore.palette
newPalette = PaletteStore.newPalette
dialogPalette = PaletteStore.dialogPalette
zopePalette = PaletteStore.zopePalette
helperClasses = PaletteStore.helperClasses
compInfo = PaletteStore.compInfo

_NB = None
def evalCtrl(expr, localsDct=None):
    """ Function usually used to evaluate source snippets.

    Uses the namespace of this module which contain all the wxPython libs
    and also adds param localDct.
    """
    global _NB
    if not _NB:
        _NB = IS.load('Images/Inspector/wxNullBitmap.png')
    if not localsDct:
        localsDct = {'wxNullBitmap': _NB}
    else:
        localsDct['wxNullBitmap'] = _NB
    localsDct['_'] = str

    return eval(expr, globals(), localsDct)
