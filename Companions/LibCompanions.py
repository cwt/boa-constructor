#-----------------------------------------------------------------------------
# Name:        LibCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.LibCompanions'

from wxPython.wx import *

##from wxPython.lib.colourselect import ColourSelect, EVT_COLOURSELECT
from wxPython.lib.stattext import wxGenStaticText

from BaseCompanions import WindowDTC
from BasicCompanions import StaticTextDTC

##class ColourSelectDTC(ButtonDTC):
##    def __init__(self, name, designer, parent, ctrlClass):
##        ButtonDTC.__init__(self, name, designer, parent, ctrlClass)
##
##    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
##        return {'label': `self.name`,
##                'bcolour': `(0, 0, 0)`,
##                'pos': position,
##                'size': size,
##                'name': `self.name`,
##                'style': '0'}
##
##    def events(self):
##        return WindowDTC.events(self) + ['ButtonEvent']
##
##    def defaultAction(self):
##        insp = self.designer.inspector
##        insp.pages.SetSelection(2)
##        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')


class GenStaticTextDTC(StaticTextDTC):
    handledConstrParams = ('parent', 'ID')
    windowIdName = 'ID'

    def writeImports(self):
        return 'from wxPython.lib.stattext import wxGenStaticText'

#-------------------------------------------------------------------------------
import PaletteStore

PaletteStore.paletteLists['wxPython.lib'] = []
PaletteStore.palette.append(['wxPython.lib', 'Editor/Tabs/Basic',
                             PaletteStore.paletteLists['wxPython.lib']])
PaletteStore.paletteLists['wxPython.lib'].extend([
      wxGenStaticText,
])

PaletteStore.compInfo.update({
    wxGenStaticText: ['wxGenStaticText', GenStaticTextDTC],
})

