#!/usr/bin/env python
#Boa:App:BoaApp

from wxPython.wx import *

import wxFrame1

modules ={'wxFrame1': [1, 'Main frame of Application', 'wxFrame1.py'],
 'wxPanel1': [0, '', 'wxPanel1.py'],
 'wxPanel2': [0, '', 'wxPanel2.py'],
 'wxPanel3': [0, '', 'wxPanel3.py']}

class BoaApp(wxApp):
    def OnInit(self):
        wxInitAllImageHandlers()
        self.main = wxFrame1.create(None)
        #workaround for running in wxProcess
        self.main.Show();self.main.Hide();self.main.Show()
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
