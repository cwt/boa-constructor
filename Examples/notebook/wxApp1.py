#Boa:App:BoaApp
from wxPython.wx import *

import wxFrame1

modules ={'wxDialog1': [0, '', 'wxDialog1.py'],
 'wxFrame1': [1, 'Main frame of Application', 'wxFrame1.py']}

class BoaApp(wxApp):
    """Documentation String"""
    def OnInit(self):
        wxInitAllImageHandlers()
        self.main = wxFrame1.create(None)
        self.main.Show(true)
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    # XXX Test ToDo on line 24
    main()
