#-----------------------------------------------------------------------------
# Name:        sourceconst.py
# Purpose:     Central place for constants, templates and snippets used by the
#              code generation process
#
# Author:      Riaan Booysen
#
# Created:     2001/19/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
boaIdent = '#Boa'
boaClass = 'BoaApp'

init_ctrls = '_init_ctrls'
init_coll = '_init_coll_'
init_utils = '_init_utils'
init_props = '_init_props'
init_events = '_init_events'
defEnvPython = '#!/usr/bin/env python\n'
defImport = 'from wxPython.wx import *\n\n'
defSig = boaIdent+':%s:%s\n\n'

defCreateClass = '''def create(parent):
    return %s(parent)
\n'''
wid = '[A-Za-z0-9_, ]*'
srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = '+\
'map\(lambda %s: [wx]*NewId\(\), range\((?P<count>\d+)\)\)'
defWindowIds = '''[%s] = map(lambda %s: wxNewId(), range(%d))\n'''

defClass = '''
class %s(%s):
    def '''+init_utils+'''(self):
        pass

    def '''+init_ctrls+'''(self, prnt):
        %s.__init__(%s)
        self.'''+init_utils+'''()

    def __init__(self, parent):
        self.'''+init_ctrls+'''(parent)
'''

# This the closest I get to destroying partially created
# frames without mucking up my indentation.
# This doesn't not handle the case where the constructor itself fails
# Replace defClass with this in line 412 if you feel the need

defSafeClass = '''
class %s(%s):
    def '''+init_utils+'''(self):
        pass

    def '''+init_ctrls+'''(self, prnt):
        %s.__init__(%s)

    def __init__(self, parent):
        self.'''+init_utils+'''()
        try:
            self.'''+init_ctrls+'''(parent)

            # Your code
        except:
            self.Destroy()
            import traceback
            traceback.print_exc()
            raise
'''

defApp = '''import %s

modules = {'%s' : [1, 'Main frame of Application', '%s.py']}

class BoaApp(wxApp):
    def OnInit(self):
        wxInitAllImageHandlers()
        self.main = %s.create(None)
        self.main.Show(true)
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
'''

defInfoBlock = '''#-----------------------------------------------------------------------------
# Name:        %s
# Purpose:     %s
#
# Author:      %s
#
# Created:     %s
# RCS-ID:      %s
# Copyright:   %s
# Licence:     %s
#-----------------------------------------------------------------------------
'''

defSetup_py = '''
from distutils.core import setup

setup(name = '%s',
      version = '%s',
      scripts = [%s],
)
'''

defPackageSrc = '''# Package initialisation
'''

defPyApp = '''modules = {}

def main():
    pass

if __name__ == '__main__':
    main()
'''

simpleModuleRunSrc = '''

if __name__ == '__main__':
    pass # add a call to run your script here
'''

simpleAppFrameRunSrc = '''

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()
'''

simpleAppDialogRunSrc = '''

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
'''

simpleAppPopupRunSrc = '''

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = wxFrame(None, -1, 'Parent')
    frame.SetAutoLayout(true)
    frame.Show(true)
    popup = create(frame)
    popup.Show(true)
    app.MainLoop()
'''
