#Boa:App:BoaApp

#!/bin/env python
from wxPython.wx import *

import wxFrame1

modules ={'HelpCompanions': [0, '', 'HelpCompanions.py'], 'Constructors': [0, '', 'Constructors.py'], 'BaseCompanions': [0, '', 'BaseCompanions.py'], 'EventCollections': [0, '', 'EventCollections.py'], 'UtilCompanions': [0, '', 'UtilCompanions.py'], 'Companions': [0, '', 'Companions.py'], 'DialogCompanions': [0, '', 'DialogCompanions.py']}

class BoaApp(wxApp):
    def OnInit(self):
        self.main = wxFrame1.create(None)
        self.main.Show(true)
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()