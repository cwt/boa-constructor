#----------------------------------------------------------------------
# Name:        ImageStore.py
# Purpose:     Cache images used in a central place.
#
# Author:      Riaan Booysen
#
# Created:     2000/03/15
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from os import path
import sys, os, string, pprint

from wxPython import wx

class InvalidImgPathError(Exception): pass

class ImageStore:
    def __init__(self, rootpaths, images = None, cache = 1):
        if not images: images = {}
        if type(rootpaths) == type(''):
            self.rootpaths = [rootpaths]
        else:
            self.rootpaths = rootpaths
        self.images = images
        self.useCache = cache

    def cleanup(self):
        self.images = {}

    def createImage(self, filename, ext):
        if ext == '.bmp':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_BMP).ConvertToBitmap()
        elif ext == '.png':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_PNG).ConvertToBitmap()
        elif ext == '.jpg':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_JPEG).ConvertToBitmap()
        elif ext == '.gif':
            return wx.wxImage(filename, wx.wxBITMAP_TYPE_GIF).ConvertToBitmap()
        elif ext == '.ico':
            return wx.wxIcon(filename, wx.wxBITMAP_TYPE_ICO)
        else:
            raise 'Extension not handled '+ext

    def pathExtFromName(self, root, name):
        imgPath = string.replace(path.normpath(path.join(root, name)), '\\', '/')
        ext = path.splitext(name)[1]
        self.checkPath(imgPath)
        return imgPath, ext

    def load(self, name):
        for rootpath in self.rootpaths:
            try:
                imgpath, ext = self.pathExtFromName(rootpath, name)
            except InvalidImgPathError, err:
                continue

            if self.useCache:
                if not self.images.has_key(name):
                    self.images[name] = self.createImage(imgpath, ext)
                return self.images[name]
            else:
                return self.createImage(imgpath, ext)
        raise InvalidImgPathError, '%s not found in image paths' %name

    def canLoad(self, name):
        for rootpath in self.rootpaths:
            try:
                imgpath, ext = self.pathExtFromName(rootpath, name)
            except InvalidImgPathError, err:
                continue
            else:
                return 1
        return 0
##        name, ext = self.pathExtFromName(name)
##        return os.path.isfile(name)

    def checkPath(self, imgPath):
        if not path.isfile(imgPath):
            raise InvalidImgPathError, '%s not valid' %imgPath

class ZippedImageStore(ImageStore):
    def __init__(self, rootpaths, defaultArchive, images = None):
        ImageStore.__init__(self, rootpaths, images)
        self.archives = {}
        self.addArchive(defaultArchive)
        # XXX do not erase tempfiles until app exits, but then crashes will leak
        #self.tempfiles = {}

    def cleanup(self):
        #ImageStore.cleanup(self)
        self.zipfile.close()

    def addArchive(self, defaultArchive):
        import zipfile
        zf = zipfile.ZipFile(path.join(self.rootpath, defaultArchive))
        self.archives[defaultArchive] = map(lambda fl: fl.filename, zf.filelist)

        for img in self.archives[defaultArchive]:
            if img[-1] == '/':
                continue

            imgExt = path.splitext(img)[1]
            bmpPath = string.replace(path.join(path.splitext(defaultArchive)[0],
                  os.path.normpath(img)), '\\', '/')

            self.images[bmpPath] = (img, imgExt)

        self.zipfile = zf

    def load(self, name):
        import tempfile
        name = string.replace(path.normpath(name), '\\', '/')
        try:
            img, imgExt = self.images[name]
        except KeyError:
            print name, 'not found by zipped image store'
            return wx.wxNullBitmap
        else:
            tmpname = tempfile.mktemp()
            open(tmpname, 'wb').write(self.zipfile.read(img))
            try:
                try:
                    return self.createImage(tmpname, imgExt)
                except Exception, error:
                    print 'Image creation failed', name, str(error)
                    return wx.wxNullBitmap
            finally:
                os.remove(tmpname)

    def canLoad(self, name):
        name = string.replace(path.normpath(name), '\\', '/')
        return self.images.has_key(name)

