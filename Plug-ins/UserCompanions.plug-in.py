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

from Companions import BaseCompanions, BasicCompanions, EventCollections, Constructors
from PropEdit import PropertyEditors
import PaletteStore

try:
    import wxPython.lib.bcrtl
except ImportError:
    raise ImportError, 'The "bcrtl" package is not installed, turn on "installBCRTL" under Preferences'

#-------------------------------------------------------------------------------

# Objects which Boa will need at design-time needs to be imported into the
# Companion module's namespace
from wxPython.lib.bcrtl.user.ExampleST import *

# Silly barebones example of a companion for a new component that is not
# available in the wxPython distribution
class ExampleSTDTC(BasicCompanions.StaticTextDTC):
    def writeImports(self):
        return 'from wxPython.lib.bcrtl.user.ExampleST import *'

#-------------------------------------------------------------------------------
# Example of a composite control, control itself, implemented in
# wxPython.lib.bcrtl.user.StaticTextCtrl

from wxPython.lib.bcrtl.user.StaticTextCtrl import wxStaticTextCtrl

class StaticTextCtrlDTC(BasicCompanions.TextCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BasicCompanions.TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['CaptionAlignment'] = PropertyEditors.EnumPropEdit
        self.options['CaptionAlignment'] = [wx.wxTOP, wx.wxLEFT]
        self.names['CaptionAlignment'] = {'wx.TOP': wx.wxTOP, 'wx.LEFT': wx.wxLEFT}

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name',
                'Caption': 'caption'}

    def writeImports(self):
        return 'from wxPython.lib.bcrtl.user.StaticTextCtrl import *'

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = BasicCompanions.TextCtrlDTC.designTimeSource(self, position, size)
        dts['caption'] = `self.name`
        return dts


# Add the component's class to this list
PaletteStore.paletteLists['User'].extend([wxExampleStaticText, wxStaticTextCtrl])

# Add an entry to this dict with the following structure:
# <component class>: ['Palette tip name and bitmap file', <companion>]
PaletteStore.compInfo.update({wxExampleStaticText: ['wxExampleStaticText', ExampleSTDTC],
                              wxStaticTextCtrl: ['wxStaticTextCtrl', StaticTextCtrlDTC]})

#-------------------------------------------------------------------------------

# Example wrapping of a wxPython control which covers most of the aspects of
# integrating controls

from wxPython.calendar import *
from wxPython.utils import *

class CalendarConstr:
    def constructor(self):
        return {'Date': 'date', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

EventCollections.EventCategories['CalendarEvent'] = ('wx.calendar.EVT_CALENDAR',
      'wx.calendar.EVT_CALENDAR_SEL_CHANGED', 
      'wx.calendar.EVT_CALENDAR_DAY, EVT_CALENDAR_MONTH',
      'wx.calendar.EVT_CALENDAR_YEAR', 'wx.calendar.EVT_CALENDAR_WEEKDAY_CLICKED')
EventCollections.commandCategories.append('CalendarEvent')

class CalendarDTC(CalendarConstr, BaseCompanions.WindowDTC):
    #wxDocs = HelpCompanions.wxCalendarCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.calendar.CAL_SUNDAY_FIRST', 'wx.calendar.CAL_MONDAY_FIRST',
              'wx.calendar.CAL_SHOW_HOLIDAYS', 'wx.calendar.CAL_NO_YEAR_CHANGE',
              'wx.calendar.CAL_NO_MONTH_CHANGE'] + self.windowStyles

        self.compositeCtrl = true

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'date': 'wx.calendar.DateTime_Now()',
                'pos': position,
                'size': size,
                'style': 'wx.calendar.CAL_SHOW_HOLIDAYS',
                'name': `self.name`}

    def events(self):
        return BaseCompanions.WindowDTC.events(self) + ['CalendarEvent']

    def writeImports(self):
        return 'import wx.calendar'

PaletteStore.paletteLists['BasicControls'].append(wxCalendarCtrl)
PaletteStore.compInfo[wxCalendarCtrl] = ['wxCalendarCtrl', CalendarDTC]

class DateTimePropEditor(PropertyEditors.BITPropEditor):
    def getDisplayValue(self):
        if self.value.IsValid():
            return '<%s>' % self.value.Format()
        else:
            return '<Invalid date>'
            
    def valueAsExpr(self):
        if self.value.IsValid():
            v = self.value
            return 'wx.calendar.DateTimeFromDMY(%d, %d, %d, %d, %d, %d)'%(
               v.GetDay(), v.GetMonth(), v.GetYear(), 
               v.GetHour(), v.GetMinute(), v.GetSecond()) 
        else:
            return '<Invalid date>'
        
    def valueToIECValue(self):
        return self.valueAsExpr()

    def inspectorEdit(self):
        if self.value.IsValid():
            PropertyEditors.BITPropEditor.inspectorEdit(self)
        

PropertyEditors.registeredTypes.extend( [
    ('Class', wxDateTimePtr, [DateTimePropEditor]),
    ('Class', wxDateTime, [DateTimePropEditor]),
])

#-------------------------------------------------------------------------------
