#----------------------------------------------------------------------
# Name:        ImageStore.py
# Purpose:     Cache images used in a central place.
#
# Author:      Riaan Booysen
#
# Created:     2000/03/15
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2003 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import os

from wxPython import wx

class InvalidImgPathError(Exception): pass

class ImageStore:
    def __init__(self, rootpaths, images=None, cache=1):
        if not images: images = {}
        self.rootpaths = []
        self.images = images
        self.useCache = cache

        for rootpath in rootpaths:
            self.addRootPath(rootpath)

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
        imgPath = self.canonizePath(os.path.join(root, name))
        ext = os.path.splitext(name)[1]
        self.checkPath(imgPath)
        return imgPath, ext

    def load(self, name):
        for rootpath in self.rootpaths:
            try:
                imgpath, ext = self.pathExtFromName(rootpath, name)
            except InvalidImgPathError:
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
            except InvalidImgPathError:
                continue
            else:
                return 1
        return 0

    def canonizePath(self, imgPath):
        return os.path.normpath(imgPath).replace('\\', '/')

    def checkPath(self, imgPath):
        if not os.path.isfile(imgPath):
            raise InvalidImgPathError, '%s not valid' %imgPath

    def addRootPath(self, rootPath):
        self.rootpaths.append(rootPath)

class ZippedImageStore(ImageStore):
    def __init__(self, rootpaths, images=None, cache=1):
        self.archives = {}
        ImageStore.__init__(self, rootpaths, images, cache)

    def cleanup(self):
        ImageStore.cleanup(self)

    def addRootPath(self, rootPath):
        ImageStore.addRootPath(self, rootPath)

        archive = os.path.join(rootPath, 'Images.archive.zip')
        if os.path.exists(archive):
            print 'reading Image archive...'
            import zipfile
            zf = zipfile.ZipFile(archive)
            self.archives[archive] = [fl.filename for fl in zf.filelist]
                                    #map(lambda fl: fl.filename, zf.filelist)

            for img in self.archives[archive]:
                if img[-1] == '/':
                    continue

                imgData = zf.read(img)
                imgExt = os.path.splitext(img)[1]
                bmpPath = img#self.canonizePath(path.join(path.splitext(archive)[0], img))
                self.images[bmpPath] = (imgData, imgExt)
            zf.close()

    def load(self, name):
        import tempfile
        name = self.canonizePath(name)
        try:
            imgData, imgExt = self.images[name]
        except KeyError:
            #print name, 'not found by zipped image store'
            return ImageStore.load(self, name)
        else:
            tmpname = tempfile.mktemp()
            open(tmpname, 'wb').write(imgData)
            try:
                try:
                    return self.createImage(tmpname, imgExt)
                except Exception, error:
                    #print 'Image creation failed', name, str(error)
                    return ImageStore.load(self, name)
            finally:
                os.remove(tmpname)

    def canLoad(self, name):
        name = self.canonizePath(name)
        if not self.images.has_key(name):
            return ImageStore.canLoad(self, name)
