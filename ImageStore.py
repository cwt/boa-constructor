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
import sys, os, string

from wxPython import wx

class ImageStore:
    def __init__(self, rootpath, images = None, cache = 1):
        if not images: images = {}
        self.rootpath = rootpath
        self.images = images
        self.useCache = cache
    
    def cleanup(self):
        del self.images

    def createImage(self, filename, ext):
        if ext == '.bmp':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_BMP).ConvertToBitmap()
        elif ext == '.jpg':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_JPEG).ConvertToBitmap()
        elif ext == '.gif':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_GIF).ConvertToBitmap()
        elif ext == '.ico':
            return wx.wxIcon(filename, wx.wxBITMAP_TYPE_ICO)
        else:
            raise 'Extension not handled '+ext

    def load(self, name):
        name = path.normpath(name)
        if self.useCache:
            if not self.images.has_key(name):
                self.images[name] = self.createImage(path.join(self.rootpath,
                    name), path.splitext(name)[1])
            #print '%s:%s'%(self.images[name].this, name)
            return self.images[name]
        else:
            return self.createImage(path.join(self.rootpath, name),
                  path.splitext(name)[1])


class ZippedImageStore(ImageStore):
    def __init__(self, rootpath, defaultArchive, images = None):
        ImageStore.__init__(self, rootpath, images)
        self.archives = {}
        self.addArchive(defaultArchive)

    def addArchive(self, defaultArchive):
        import zipfile, tempfile
        zf = zipfile.ZipFile(path.join(self.rootpath, defaultArchive))
        self.archives[defaultArchive] = map(lambda fl: fl.filename, zf.filelist)

        for img in self.archives[defaultArchive]:
            if img[-1] == '/':
                continue

            imgExt = path.splitext(img)[1]
            bmpPath = path.join(path.splitext(defaultArchive)[0],
                  os.path.normpath(img))

            tmpname = tempfile.mktemp()
            open(tmpname, 'w').write(zf.read(img))
            try:
                if not self.images.has_key(bmpPath):
                    try:
                        self.images[bmpPath] = self.createImage(tmpname, imgExt)
                    except Exception, error:
                        print 'Ext not handled', bmpPath, str(error)
            finally:
                os.remove(tmpname)

        zf.close()

    def load(self, name):
        name = path.normpath(name)
        try:
            return self.images[name]
        except KeyError:
            print name, 'not found by zipped image store'
            return wx.wxNullBitmap
     