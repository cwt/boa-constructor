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

import os, glob

import Preferences, Utils
from Preferences import IS
import PaletteStore

from wxPython.wx import *

if Preferences.suWxPythonSupport:
    # This should be the first time the Companion classes are imported
    # As the modules are imported they add themselves to the PaletteStore
    from Companions.Companions import *
    
    from Companions.GizmoCompanions import *
    
    if Utils.IsComEnabled():
        from Companions.ComCompanions import *
    
    from Companions.UtilCompanions import *
    
    from Companions.DialogCompanions import *

if Utils.createAndReadConfig('Explorer').has_option('explorer', 'zope'):
    from ZopeLib.ZopeCompanions import *

#-Controller imports which auto-regisers themselves on the Palette--------------
from Models import Controllers

if Preferences.suWxPythonSupport:
    from Models import wxPythonControllers

from Models import PythonControllers, EditorHelper

if not Preferences.suWxPythonSupport:
    # useful hack to alias wxApp modules to PyApp modules
    EditorHelper.modelReg['App'] = PythonControllers.PythonEditorModels.PyAppModel
    
# The text and makepy controllers are registered outside the Controllers
# module so that their palette order can be fine tuned
PaletteStore.newControllers['Text'] = Controllers.TextController
PaletteStore.paletteLists['New'].append('Text')

#-Registration of other built in support---------------------------------------
from Models import ConfigSupport
from Models import HTMLSupport
from Models import XMLSupport
from Models import CPPSupport

if Utils.createAndReadConfig('Explorer').has_option('explorer', 'zope'):
    import ZopeLib.ZopeEditorModels

if Utils.IsComEnabled():
    PaletteStore.newControllers['MakePy-Dialog'] = Controllers.MakePyController
    PaletteStore.paletteLists['New'].append('MakePy-Dialog')

#-Plug-ins initialisation-------------------------------------------------------
if Preferences.pluginPaths:
    pluginPathGlobs = []
    for ppth in Preferences.pluginPaths:
        pluginPathGlobs.append(ppth+'/*.plug-in.py')

    print 'executing plug-ins...'
    for globpath in pluginPathGlobs:
        for pluginFilename in glob.glob(globpath):
            try:
                execfile(pluginFilename)
            except Exception, error:
                wxLogError('Problem executing plug-in %s:\n%s' %\
                    (os.path.basename(pluginFilename), str(error)) )

#-------------------------------------------------------------------------------
# called after all models have been imported
EditorHelper.initExtMap()
#-------------------------------------------------------------------------------

palette = PaletteStore.palette
newPalette = PaletteStore.newPalette
dialogPalette = PaletteStore.dialogPalette
zopePalette = PaletteStore.zopePalette
helperClasses = PaletteStore.helperClasses
compInfo = PaletteStore.compInfo

def compInfoByName(name):
    for comp in compInfo.keys():
        if comp.__name__ == name: return comp
    raise name+' not found'

def loadBitmap(name):
    """ Loads bitmap if it exists, else loads default bitmap """
    imgPath = 'Images/Palette/' + name+'.png'
    if IS.canLoad(imgPath):
        return IS.load(imgPath)
    else:
        return IS.load('Images/Palette/Component.png')


def bitmapForComponent(wxClass, wxBase='None'):
    """ Returns a bitmap for given comonent class.

    "Aquires" bitmap by traversing inheritance thru if necessary.
    """
    if wxBase != 'None': return loadBitmap(wxBase)
    else:
        cls = wxClass
        try: bse = wxClass.__bases__[0]
        except:
            if compInfo.has_key(wxClass):
                return loadBitmap(compInfo[wxClass][0])
            else:
                return loadBitmap('Component')
        try:
            while not compInfo.has_key(cls):
                cls = bse
                bse = cls.__bases__[0]

            return loadBitmap(compInfo[cls][0])
        except:
            print 'not found!'
            return loadBitmap('Component')

def _(gtstr): return gtstr

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
        wxNullBitmap = _NB
        localsDct = locals()
    else:
        localsDct['wxNullBitmap'] = _NB

    try:
        return eval(expr, globals(), localsDct)
    except:
        ##e, v, t = sys.exc_info()
        ##print str(e), str(v), str(t)
        raise
