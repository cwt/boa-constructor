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

import string
import Preferences, Utils

idnt = Utils.getIndentBlock()

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
code_gen_warning = "generated method, don't edit"

defCreateClass = string.replace('''def create(parent):
\treturn %s(parent)

''', '\t', idnt)

wid = '[A-Za-z0-9_, ]*'
srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = '+\
'map\(lambda %s: [wx]*NewId\(\), range\((?P<count>\d+)\)\)'
defWindowIds = '''[%s] = map(lambda %s: wxNewId(), range(%d))\n'''

defClass = string.replace('''
class %s(%s):
\tdef '''+init_utils+'''(self):
\t\tpass

\tdef '''+init_ctrls+'''(self, prnt):
\t\t%s.__init__(%s)
\t\tself.'''+init_utils+'''()

\tdef __init__(self, parent):
\t\tself.'''+init_ctrls+'''(parent)
''', '\t', idnt)

defApp = string.replace('''import %s

modules = {'%s' : [1, 'Main frame of Application', '%s.py']}

class BoaApp(wxApp):
\tdef OnInit(self):
\t\twxInitAllImageHandlers()
\t\tself.main = %s.create(None)
\t\t#workaround for running in wxProcess
\t\tself.main.Show();self.main.Hide();self.main.Show()
\t\tself.SetTopWindow(self.main)
\t\treturn true

def main():
\tapplication = BoaApp(0)
\tapplication.MainLoop()

if __name__ == '__main__':
\tmain()
''', '\t', idnt)

defInfoBlock = '''#-----------------------------------------------------------------------------
# Name:        %(Name)s
# Purpose:     %(Purpose)s
#
# Author:      %(Author)s
#
# Created:     %(Created)s
# RCS-ID:      %(RCS-ID)s
# Copyright:   %(Copyright)s
# Licence:     %(Licence)s
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

defPyApp = string.replace('''modules = {}

def main():
\tpass

if __name__ == '__main__':
\tmain()
''', '\t', idnt)

simpleModuleRunSrc = string.replace('''

if __name__ == '__main__':
\tpass # add a call to run your script here
''', '\t', idnt)

simpleAppFrameRunSrc = string.replace('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tframe = create(None)
\tframe.Show();frame.Hide();frame.Show() #workaround for running in wxProcess
\tapp.MainLoop()
''', '\t', idnt)

simpleAppDialogRunSrc = string.replace('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tdlg = create(None)
\ttry:
\t\tdlg.ShowModal()
\tfinally:
\t\tdlg.Destroy()
''', '\t', idnt)

simpleAppPopupRunSrc = string.replace('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tframe = wxFrame(None, -1, 'Parent')
\tframe.SetAutoLayout(true)
\tframe.Show();frame.Hide();frame.Show() #workaround for running in wxProcess
\tpopup = create(frame)
\tpopup.Show(true)
\tapp.MainLoop()
''', '\t', idnt)
