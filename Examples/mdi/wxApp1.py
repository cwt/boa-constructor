#!/usr/bin/env python
#Boa:App:BoaApp

from wxPython.wx import *

import wxMDIParentFrame1

modules ={'wxMDIChildFrame1': [0, '', 'wxMDIChildFrame1.py'],
 'wxMDIParentFrame1': [1, '', 'wxMDIParentFrame1.py']}

class BoaApp(wxApp):
    def OnInit(self):
        self.main = wxMDIParentFrame1.create(None)
        self.main.Show(true)
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
