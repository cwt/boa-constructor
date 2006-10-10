import wx

import Plugins

try:
    import wx.lib.dragscroller
except ImportError:
    raise Plugins.SkipPlugin, 'Module wx.lib.dragscroller not found'

from Companions import UtilCompanions
from PropEdit import PropertyEditors

#-------------------------------------------------------------------------------
# DragScroller
# wx.lib.dragscroller.DragScroller

class DragScrollerDTC(UtilCompanions.UtilityDTC):
    handledConstrParams = ('id',)
    def __init__(self, name, designer, objClass):
        UtilCompanions.UtilityDTC.__init__(self, name, designer, objClass)
        self.editors['Sensitivity'] = PropertyEditors.BITPropEditor

    def constructor(self):
        return {'ScrollWindow': 'scrollwin', 'UpdateRate': 'rate'}

    def designTimeSource(self):
        return {'scrollwin': 'None', 'rate': '35'}

    def writeImports(self):
        return 'import wx.lib.dragscroller'

#-------------------------------------------------------------------------------

Plugins.registerComponents('Library',
 (wx.lib.dragscroller.DragScroller, 'wx.lib.dragscroller.DragScroller', DragScrollerDTC))

