#----------------------------------------------------------------------
# Name:        ImageStore.py
# Purpose:     Cache images used in a central place.
#
# Author:      Riaan Booysen
#
# Created:     2000/03/15
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2003 Riaan Booysen
# Licence:     BSD
#----------------------------------------------------------------------

import os, cStringIO

from wxPython import wx

class ImageStoreError(Exception): pass
class InvalidImgPathError(ImageStoreError): pass
class UnhandledExtError(ImageStoreError): pass

class ImageStore:
    def __init__(self, rootpaths, images=None, cache=1):
        if not images: images = {}
        self.rootpaths = []
        self.images = images
        self.useCache = cache
        
        self.dataReg = {}

        for rootpath in rootpaths:
            self.addRootPath(rootpath)

    def cleanup(self):
        self.images = {}
        self.dataReg = {}

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
        elif ext == 'data':
            stream = cStringIO.StringIO(self.dataReg[filename])
            return wx.wxBitmapFromImage(wx.wxImageFromStream(stream))
        else:
            raise UnhandledExtError, 'Extension not handled: '+ext

    def pathExtFromName(self, root, name):
        imgPath = self.canonizePath(os.path.join(root, name))
        ext = os.path.splitext(name)[1]
        self.checkPath(imgPath)
        return imgPath, ext

    def load(self, name):
        if self.dataReg.has_key(name):
            return self.createImage(name, 'data')
            
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
        if self.dataReg.has_key(name):
            return 1

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
        if self.dataReg.has_key(imgPath):
            return

        if not os.path.isfile(imgPath):
            raise InvalidImgPathError, '%s not valid' %imgPath

    def addRootPath(self, rootPath):
        self.rootpaths.append(rootPath)

    def registerImage(self, name, data):
        self.dataReg[name] = data

class ZippedImageStore(ImageStore):
    def __init__(self, rootpaths, images=None, cache=1):
        self.archives = {}
        ImageStore.__init__(self, rootpaths, images, cache)

    def addRootPath(self, rootPath):
        ImageStore.addRootPath(self, rootPath)

        archive = os.path.join(rootPath, 'Images.archive.zip')
        if os.path.exists(archive):
            print 'reading Image archive...'
            import zipfile
            zf = zipfile.ZipFile(archive)
            self.archives[archive] = [fl.filename for fl in zf.filelist]

            for img in self.archives[archive]:
                if img[-1] == '/':
                    continue

                imgData = zf.read(img)
                imgExt = os.path.splitext(img)[1]
                bmpPath = img
                self.images[bmpPath] = (imgData, imgExt)
            zf.close()

    def load(self, name):
        import tempfile
        name = self.canonizePath(name)
        try:
            imgData, imgExt = self.images[name]
        except KeyError:
            return ImageStore.load(self, name)
        else:
            tmpname = tempfile.mktemp()
            open(tmpname, 'wb').write(imgData)
            try:
                try:
                    return self.createImage(tmpname, imgExt)
                except Exception, error:
                    return ImageStore.load(self, name)
            finally:
                os.remove(tmpname)

    def canLoad(self, name):
        name = self.canonizePath(name)
        if not self.images.has_key(name):
            return ImageStore.canLoad(self, name)
    

class ResourseImageStore(ImageStore):
    def __init__(self, rootpaths, images=None, cache=1):
        self.resources = {}
        ImageStore.__init__(self, rootpaths, images, cache)
        