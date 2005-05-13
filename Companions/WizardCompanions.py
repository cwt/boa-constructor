#-----------------------------------------------------------------------------
# Name:        WizardCompanions.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing Companions.WizardCompanions'

from wxPython.wx import *
from wxPython.wizard import *

from Preferences import wxDefaultFrameSize, wxDefaultFramePos
from FrameCompanions import DialogDTC, FramePanelDTC
from PropEdit.PropertyEditors import BitmapConstrPropEdit, StrConstrPropEdit

import EventCollections
import sourceconst

##defWizardImport = 'from wxPython.wizard import *'

wizardSize = (400, 370)
wizardPageSize = (270, 300)
wizardFrameStyle = wxMINIMIZE_BOX | wxSYSTEM_MENU | wxCAPTION #wxMAXIMIZE_BOX

EventCollections.EventCategories['WizardEvent'] = (
      'wx.wizard.EVT_WIZARD_PAGE_CHANGED', 'wx.wizard.EVT_WIZARD_PAGE_CHANGING', 
      'wx.wizard.EVT_WIZARD_CANCEL', 'wx.wizard.EVT_WIZARD_HELP', 
      'wx.wizard.EVT_WIZARD_FINISHED')
      
EventCollections.commandCategories.append('WizardEvent')

class WizardDTC(DialogDTC): 
    defFrameSize = wxSize(*wizardSize)
    defFrameStyle = wizardFrameStyle

    def __init__(self, name, designer, frameCtrl):
        DialogDTC.__init__(self, name, designer, frameCtrl)
        self.editors['Bitmap'] = BitmapConstrPropEdit
        self.index = 0

    def constructor(self):
        return {'Title': 'title', 'Position': 'pos', 'Bitmap': 'bitmap'}

    def designTimeSource(self):
        return {'title': `self.name`,
                'pos':   `wxDefaultFramePos`,
                'bitmap': 'wx.NullBitmap'}

    def hideDesignTime(self):
        return DialogDTC.hideDesignTime(self) + ['Size', 'ClientSize']

    def events(self):
        return DialogDTC.events(self) + ['WizardEvent']


class PyWizardPageDTC(FramePanelDTC):
    defFrameSize = wxSize(*wizardPageSize)
    defFrameStyle = wizardFrameStyle
    suppressWindowId = true
    def __init__(self, name, designer, frameCtrl):
        FramePanelDTC.__init__(self, name, designer, frameCtrl)
        self.editors['Bitmap'] = BitmapConstrPropEdit
        self.editors['Resource'] = StrConstrPropEdit
        self.index = 0

    def constructor(self):
        return {'Bitmap': 'bitmap', 'Resource': 'resource'}

    def designTimeSource(self):
        return {'bitmap': 'wx.NullBitmap', 'resource': "''"}

    def hideDesignTime(self):
        return FramePanelDTC.hideDesignTime(self) + ['Position', 'Size', 'ClientSize']

    
class WizardPageSimpleDTC(FramePanelDTC):
    defFrameSize = wxSize(*wizardPageSize)
    defFrameStyle = wizardFrameStyle
    suppressWindowId = true
    def __init__(self, name, designer, frameCtrl):
        FramePanelDTC.__init__(self, name, designer, frameCtrl)

    def constructor(self):
        return {'Previous': 'prev', 'Next': 'next'}

    def designTimeSource(self):
        return {'prev': 'None', 'next': 'None'}

    def hideDesignTime(self):
        return FramePanelDTC.hideDesignTime(self) + ['Position', 'Size', 'ClientSize']


#-------------------------------------------------------------------------------
import Plugins

Plugins.registerComponents(None,
      (wxWizard, 'wx.wizard.Wizard', WizardDTC),
      (wxPyWizardPage, 'wx.wizard.PyWizardPage', PyWizardPageDTC),
      (wxWizardPageSimple, 'wx.wizard.WizardPageSimple', WizardPageSimpleDTC),
    )
