#----------------------------------------------------------------------
# Name:        ImageStore.py                                           
# Purpose:     Cache images used in a central place.                   
#                                                                      
# Author:      Riaan Booysen                                           
#                                                                      
# Created:     2000/03/15                                              
# RCS-ID:      $Id$                                     
# Copyright:   (c) 1999, 2000 Riaan Booysen                            
# Licence:     GPL                                                     
#----------------------------------------------------------------------

from os import path
import sys, os
from wxPython import wx

class ImageStore:
    def __init__(self, rootpath, images = {}):
        self.rootpath = rootpath
        self.images = images
##    def __del__(self):
##        print 'deleting image store1'
###        f = open('isb', 'w')
###        for i in self.images.items(): f.write(`i`+'\n')
###        f.close()
##        import sys
##        for i in self.images.values():
##            print sys.getrefcount(i),
##        print '', len(self.images)
##        del self.images
###        print 'deleting image store2'
###        raw_input() 

    def load(self, name):
        name = path.normpath(name)
        if not self.images.has_key(name): 
            self.images[name] = wx.wxBitmap(path.join(self.rootpath, name), 
              wx.wxBITMAP_TYPE_BMP)

        return self.images[name]
        
        
        
        
        
        
       