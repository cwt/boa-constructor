#-----------------------------------------------------------------------------
# Name:        GizmoCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.GizmoCompanion'

from wxPython.wx import *

import Preferences, Utils
import BaseCompanions, Companions, EventCollections, Constructors
from PropEdit import PropertyEditors
import PaletteStore

#-------------------------------------------------------------------------------
from wxPython.gizmos import *

class GizmoDTCMix:
    def writeImports(self):
        return 'from wxPython.gizmos import *'

EventCollections.EventCategories['DynamicSashEvent'] = (EVT_DYNAMIC_SASH_SPLIT, EVT_DYNAMIC_SASH_UNIFY)
EventCollections.commandCategories.append('DynamicSashEvent')

# Derives from Window instead of Container because children must be added in
# the OnSplit event, not at design-time (crashes if children not added in event)
class DynamicSashWindowDTC(GizmoDTCMix, Constructors.WindowConstr, BaseCompanions.WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxDS_MANAGE_SCROLLBARS', 'wxDS_DRAG_CORNER'] + self.windowStyles
        self.ctrlDisabled = true

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size':  'wxSize(100, 100)',
                'style': 'wxCLIP_CHILDREN',
                'name':  `self.name`}

    def events(self):
        return BaseCompanions.WindowDTC.events(self) + ['DynamicSashEvent']

PaletteStore.paletteLists['ContainersLayout'].append(wxDynamicSashWindow)
PaletteStore.compInfo[wxDynamicSashWindow] = ['wxDynamicSashWindow', DynamicSashWindowDTC]

#-------------------------------------------------------------------------------

LEDNumberCtrlAlignment = [wxLED_ALIGN_LEFT, wxLED_ALIGN_RIGHT,
                          wxLED_ALIGN_CENTER, wxLED_ALIGN_MASK]
LEDNumberCtrlAlignmentNames = {'wxLED_ALIGN_LEFT': wxLED_ALIGN_LEFT,
                               'wxLED_ALIGN_RIGHT': wxLED_ALIGN_RIGHT,
                               'wxLED_ALIGN_CENTER': wxLED_ALIGN_CENTER,
                               'wxLED_ALIGN_MASK': wxLED_ALIGN_MASK}

class LEDNumberCtrlDTC(GizmoDTCMix, BaseCompanions.WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Alignment'   : PropertyEditors.EnumPropEdit,
                             'DrawFaded' : PropertyEditors.BoolPropEdit})
        self.windowStyles = ['wxLED_ALIGN_LEFT', 'wxLED_ALIGN_RIGHT',
                             'wxLED_ALIGN_CENTER', 'wxLED_ALIGN_MASK',
                             'wxLED_DRAW_FADED'] + self.windowStyles
        self.options['Alignment'] = LEDNumberCtrlAlignment
        self.names['Alignment'] = LEDNumberCtrlAlignmentNames

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size':  'wxSize(%d, %d)'%(Preferences.dsDefaultControlSize.x,
                                           Preferences.dsDefaultControlSize.y),
                'style': 'wxLED_ALIGN_LEFT'}

PaletteStore.paletteLists['BasicControls'].append(wxLEDNumberCtrl)
PaletteStore.compInfo[wxLEDNumberCtrl] = ['wxLEDNumberCtrl', LEDNumberCtrlDTC]


#-------------------------------------------------------------------------------

class EditableListBoxDTC(GizmoDTCMix, Companions.PanelDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        Companions.PanelDTC.__init__(self, name, designer, parent, ctrlClass)
        self.ctrlDisabled = true

    def constructor(self):
        return {'Label': 'label', 'Position': 'pos', 'Size': 'size', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos':   position,
                'size':  self.getDefCtrlSize(),
                'name': `self.name`}

PaletteStore.paletteLists['ListControls'].append(wxEditableListBox)
PaletteStore.compInfo[wxEditableListBox] = ['wxEditableListBox', EditableListBoxDTC]
