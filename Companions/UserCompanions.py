#-----------------------------------------------------------------------------
# Name:        UserCompanions.py
# Purpose:     Add your own companion classes to this module
#              If you wish to define companion in separate modules, import
#              their contents into this module. Use from module import *
#
# Created:     2001/02/04
# RCS-ID:      $Id$
#-----------------------------------------------------------------------------

from wxPython.wx import *

import BaseCompanions, Companions, EventCollections, PropEdit
import PaletteStore

# Defines a new page for the palette
PaletteStore.paletteLists['User'] = []
# Adds the page to the palette
PaletteStore.palette.append(['User', 'Editor/Tabs/User',
                             PaletteStore.paletteLists['User']])

# Objects which Boa will need at design-time needs to be imported into the
# Companion module's namespace
from wxPython.lib.bcrtl.user.ExampleST import *
from wxPython.lib.bcrtl.user.StaticTextCtrl import wxStaticTextCtrl

# Silly barebones example of a companion for a new component that is not
# available in the wxPython distribution
class ExampleSTDTC(Companions.StaticTextDTC):
    def writeImports(self):
        return 'from wxPython.lib.bcrtl.user.ExampleST import *'


class StaticTextCtrlDTC(Companions.TextCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        Companions.TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['CaptionAlignment'] = PropEdit.PropertyEditors.EnumPropEdit
        self.options['CaptionAlignment'] = [wx.wxTOP, wx.wxLEFT]
        self.names['CaptionAlignment'] = {'wxTOP': wx.wxTOP, 'wxLEFT': wx.wxLEFT}
        
    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name',
                'Caption': 'caption'}

    def writeImports(self):
        return 'from wxPython.lib.bcrtl.user.StaticTextCtrl import *'

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        dts = Companions.TextCtrlDTC.designTimeSource(self, position, size)
        dts['caption'] = `self.name`
        return dts
    

# Add the component's class to this list
PaletteStore.paletteLists['User'].extend([wxExampleStaticText, wxStaticTextCtrl])

# Add an entry to this dict with the following structure:
# <component class>: ['Tip name and bitmap file', <companion>]
PaletteStore.compInfo.update({wxExampleStaticText: ['wxExampleStaticText', ExampleSTDTC],
                              wxStaticTextCtrl: ['wxStaticTextCtrl', StaticTextCtrlDTC]})


# Example wrapping of a wxPython control which covers most of the aspects of
# integrating controls

from wxPython.calendar import *
from wxPython.utils import *

class CalendarConstr:
    def constructor(self):
        return {'Date': 'date', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

EventCollections.EventCategories['CalendarEvent'] = (EVT_CALENDAR,
      EVT_CALENDAR_SEL_CHANGED, EVT_CALENDAR_DAY, EVT_CALENDAR_MONTH,
      EVT_CALENDAR_YEAR, EVT_CALENDAR_WEEKDAY_CLICKED)
EventCollections.commandCategories.append('CalendarEvent')

class CalendarDTC(CalendarConstr, BaseCompanions.WindowDTC):
    #wxDocs = HelpCompanions.wxCalendarCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxCAL_SUNDAY_FIRST', 'wxCAL_MONDAY_FIRST',
              'wxCAL_SHOW_HOLIDAYS', 'wxCAL_NO_YEAR_CHANGE',
              'wxCAL_NO_MONTH_CHANGE'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'date': 'wxDateTime_Now()',
                'pos': position,
                'size': size,
                'style': 'wxCAL_SHOW_HOLIDAYS',
                'name': `self.name`}

    def events(self):
        return BaseCompanions.WindowDTC.events(self) + ['CalendarEvent']

    def writeImports(self):
        return 'from wxPython.calendar import *\n'+\
               'from wxPython.utils import *'

#PaletteStore.paletteLists['BasicControls'].append(wxCalendarCtrl)
PaletteStore.compInfo[wxCalendarCtrl] = ['wxCalendarCtrl', CalendarDTC]

from PropEdit import PropertyEditors

class DateTimePropEditor(PropertyEditors.BITPropEditor):
    def getDisplayValue(self):
        return '<%s>' % self.value.Format()
    def valueAsExpr(self):
        return 'wxDateTimeFromTimeT(%d)' % self.value.GetTicks()
    def valueToIECValue(self):
        return self.valueAsExpr()

PropertyEditors.registeredTypes.append( ('Class', wxDateTimePtr,
                                         [DateTimePropEditor]) )
