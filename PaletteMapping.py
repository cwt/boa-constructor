#----------------------------------------------------------------------
# Name:        PaletteMapping.py
# Purpose:     Module that initialises the Palette's data and provides
#              the namespace in which design time code is evaluated
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import Preferences, Utils
from Preferences import IS
from os import path

import PaletteStore

from wxPython.wx import *

# This should be the first time the Companion classes are imported
# As the modules are imported they add themselves to the PaletteStore
##print 'importing Companions.Companions'
from Companions.Companions import *

if Utils.IsComEnabled():
    ##print 'importing Companions.ComCompanions'
    from Companions.ComCompanions import *

##print 'importing Companions.UserCompanions'
try:
    from Companions.UserCompanions import *
except Exception, error:
    wxLogError('Problem importing User companions: '+str(error))

##print 'importing Companions.UtilCompanions'
from Companions.UtilCompanions import *

##print 'importing Companions.DialogCompanions'
from Companions.DialogCompanions import *

##print 'importing Companions.ZopeCompanions'
from Companions.ZopeCompanions import *

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

def loadBitmap(name, subfold=''):
    """ Loads bitmap if it exists, else loads default bitmap """
    filepath = Preferences.pyPath+ '/Images/Palette/' + subfold + name+'.bmp'
    if path.exists(filepath):
        return IS.load('Images/Palette/' + subfold + name+'.bmp')
    else:
        return IS.load('Images/Palette/Component.bmp')


def bitmapForComponent(wxClass, wxBase='None', gray=false):
    """ Returns a bitmap for given comonent class.
    
    "Aquires" bitmap by traversing inheritance thru if necessary.
    """
    if gray: sf = 'Gray/'
    else: sf = ''
    if wxBase != 'None': return loadBitmap(wxBase, sf)
    else:
        cls = wxClass
        try: bse = wxClass.__bases__[0]
        except:
            if compInfo.has_key(wxClass):
                return loadBitmap(compInfo[wxClass][0], sf)
            else:
                return loadBitmap('Component')
        try:
            while not compInfo.has_key(cls):
                cls = bse
                bse = cls.__bases__[0]

            return loadBitmap(compInfo[cls][0], sf)
        except:
            print 'not found!'
            return loadBitmap('Component')

_NB = None
def evalCtrl(expr, localsDct=None):
    """ Function usually used to evaluate source snippets.
    
    Uses the namespace of this module which contain all the wxPython libs
    and also adds param localDct.
    """
    global _NB
    if not _NB:
        _NB = IS.load('Images/Inspector/wxNullBitmap.bmp')
    if not localsDct:
        wxNullBitmap = _NB
        localsDct = locals()
    else:
        localsDct['wxNullBitmap'] = _NB

    return eval(expr, globals(), localsDct)
