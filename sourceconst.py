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
code_gen_warning = "generated method, don't edit"

defEnvPython = '#!/usr/bin/env python\n'
defImport = 'from wxPython.wx import *\n\n'
defSig = boaIdent+':%(modelIdent)s:%(main)s\n\n'

methodIndent = idnt
bodyIndent = idnt*2

def tabfix(s):
    return string.replace(s, '\t', idnt)

defCreateClass = tabfix('''def create(parent):
\treturn %(main)s(parent)

''')

srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = '+\
'map\(lambda %s: (wx)*NewId\(\), range\((?P<count>\d+)\)\)'
srchWindowIdsCont = '(?P<any>.*)\] = map\(lambda %s: (wx)*NewId\(\), range\((?P<count>\d+)\)\)'
defWindowIds = '''[%(idNames)s] = map(lambda %(idIdent)s: wxNewId(), range(%(idCount)d))\n'''
defWindowIdsCont = '''] = map(lambda %(idIdent)s: wxNewId(), range(%(idCount)d))\n'''

defClass = tabfix('''
class %(main)s(%(defaultName)s):
\tdef '''+init_utils+'''(self):
\t\tpass

\tdef '''+init_ctrls+'''(self, prnt):
\t\t%(defaultName)s.__init__(%(params)s)
\t\tself.'''+init_utils+'''()

\tdef __init__(self, parent):
\t\tself.'''+init_ctrls+'''(parent)
''')

defApp = tabfix('''import %(mainModule)s

modules = {'%(mainModule)s' : [1, 'Main frame of Application', '%(mainModule)s.py']}

class BoaApp(wxApp):
\tdef OnInit(self):
\t\twxInitAllImageHandlers()
\t\tself.main = %(mainModule)s.create(None)
\t\t#workaround for running in wxProcess
\t\tself.main.Show()
\t\tself.SetTopWindow(self.main)
\t\treturn true

def main():
\tapplication = BoaApp(0)
\tapplication.MainLoop()

if __name__ == '__main__':
\tmain()
''')

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

setup(name = '%(name)s',
      version = '%(version)s',
      scripts = [%(scripts)s],
)
'''

defPackageSrc = '''# Package initialisation
'''

defPyApp = tabfix('''modules = {}

def main():
\tpass

if __name__ == '__main__':
\tmain()
''')

simpleModuleRunSrc = tabfix('''

if __name__ == '__main__':
\tpass # add a call to run your script here
''')

simpleAppFrameRunSrc = tabfix('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tframe = create(None)
\tframe.Show()
\tapp.MainLoop()
''')

simpleAppDialogRunSrc = tabfix('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tdlg = create(None)
\ttry:
\t\tdlg.ShowModal()
\tfinally:
\t\tdlg.Destroy()
\tapp.MainLoop()
''')

simpleAppPopupRunSrc = tabfix('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tframe = wxFrame(None, -1, 'Parent')
\tframe.SetAutoLayout(true)
\tframe.Show()
\tpopup = create(frame)
\tpopup.Show(true)
\tapp.MainLoop()
''')
