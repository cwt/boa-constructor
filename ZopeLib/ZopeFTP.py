#-----------------------------------------------------------------------------
# Name:        ZopeFTP.py                                                     
# Purpose:     FTP interface into Zope                                        
#                                                                             
# Author:      Riaan Booysen                                                  
#                                                                             
# Created:     2000/05/08                                                     
# RCS-ID:      $Id$                                               
# Copyright:   (c) 1999, 2000 Riaan Booysen                                   
# Licence:     GPL                                                            
#-----------------------------------------------------------------------------

import string
import ftplib, os

true = 1
false = 0
             
class ZopeFTP:
    def __init__(self):
        
        self.ftp = None
        self.host = ''
        self.port = 21
        self.username = ''
        self.connected = false
        self.http_port = 80
    
    def __del__(self):
        self.disconnect()
        
    
        
    def connect(self, username, password, host, port = 21, passive = 0):
        self.ftp = ftplib.FTP('')

        self.host = host
        self.port = port
        self.username = username

        res = []
        res.append(self.ftp.connect(host, port))

        # Zope returns 'Login successful' even on wrong passwords :(
        res.append(self.ftp.login(username, password))
            
        self.connected = true
        
        self.ftp.set_pasv(passive)

        return string.join(res, '\n') 


    def disconnect(self):
        if self.ftp: self.ftp.quit()
        self.ftp = None
        self.connected = false

    def add_doc(self, name, path):
        #return ZopeFTPItem(path, name, '-rw-rw----', 0, '')
        pass
    def folder_item(self, name, path):
        #return ZopeFTPItem(path, name, 'drw-rw----', 0, '')
        pass
        
    def add_folder(self, name, path):
        self.ftp.mkd('%s/%s' % (path, name))

    def dir(self, path):
##        res = []
##        lst = []
##        self.ftp.dir(path, lst.append)
##        #print lst
##        for line in lst:
##            zftpi = ZopeFTPItem()
##            zftpi.read(line)
##            zftpi.path = path
##            res.append(zftpi)
##        return res
        pass
        
    def download(self, server_filename, local_filename):
        f = open(local_filename, 'wb')
        self.ftp.retrbinary('RETR %s' % server_filename, f.write)
        f.close()
     
    def load(self, item):
        res = []
        self.ftp.retrlines(item.cmd('RETR'), res.append)
        return string.join(res, '\n') 

    def save(self, node,data):
        node.prepareAsFile(data) 
        self.ftp.storlines(node.cmd('STOR'), node)

    def upload(self, filename, dest_path):
        f = open(filename, 'rb')
        data = f.read()
        f.close()
        #self.save(ZopeFTPItem(dest_path, os.path.basename(filename)), data)
        # XXX must handle this upload thing
        
    def delete(self,node):
        if node.isFolder():
            self.ftp.rmd(node.path)
            return true
        else:
            self.ftp.delete(node.path)
            return false
    
    def rename(self, node,new_name):
        old_path = node.path
        new_path = os.path.dirname(old_path)+'/'+new_name
        self.ftp.rename(old_path, new_path)
        