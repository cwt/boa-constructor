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
    def __init__(self, modulepage, view, marker):
        self.modulePage = modulepage
        self.view = view
        self.marker = marker
    
    def goto(self):
        # XXX What if page has been closed, notification
        self.modulePage.focus()
        self.modulePage.model.views[self.view].goto(self.marker)
        self.modulePage.model.views[self.view].focus()
        
class Browser:
    def __init__(self):
        self.pages = []
        self.idx = -1

    def add(self, page):
        if self.idx == len(self.pages)-1:
            self.pages.append(page)
        else:
            self.pages[self.idx:] = [page]
        self.idx = len(self.pages)-1
    
    def checkRemoval(self, modPage):
        for page in self.pages[:]:
            if page.modulePage == modPage:
                idx = self.pages.index(page)
                if idx < self.idx:
                    self.idx = self.idx - 1
                del self.pages[idx]

    def step(self, dir):
        self.pages[self.idx].goto()
        self.idx = self.idx + dir
            
    def canForward(self):
        return self.idx < len(self.pages)-1
    
    def forward(self):
        if self.canForward():
            self.step(1)
            
    def canBack(self):
        return self.idx >= 0

    def back(self):
        if self.canBack():
            self.step(-1)
    