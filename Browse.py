#-----------------------------------------------------------------------------
# Name:        Browse.py
# Purpose:     
#                
# Author:      Riaan Booysen
#                
# Created:     2000/09/24
# RCS-ID:      $Id$
# Copyright:   (c) 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

class BrowsePage:
    def __init__(self, modulepage, marker):
        self.modulePage = modulepage
        self.marker = marker
    
    def goto(self):
        # XXX What if page has been closed, notification
        self.modulePage.focus()
        self.modulePage.model.views[view].goto(marker)

class Browser:
    def __init__(self):
        self.pages = []
        self.idx = 0

    def add(self, page):
        if self.idx == len(self.pages)-1:
            self.pages.append(page)
        else:
            self.pages[self.idx:] = [page]
        self.idx = len(self.pages)-1

    def step(self, dir):
        self.idx = self.idx + dir
        self.pages[self.idx].goto()
            
    def canForward(self):
        return self.idx < len(self.pages)-1
    
    def forward(self):
        if self.canForward():
            self.step(1)
            
    def canBack(self):
        return self.idx > 0

    def back(self):
        if self.canBack():
            self.step(-1)
    