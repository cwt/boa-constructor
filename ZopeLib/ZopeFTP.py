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
             
class ZopeFTPItem:
    def __init__(self, path = '', name = '', perms = '----------', id = 0, size = 0, date = ''):
        self.path = path
        self.name = name
        self.perms = perms
        self.id = id
        self.size = size
        self.date = date
        self.lines = []
    
    def __repr__(self):
        return '<%s %s, %s>' % (`self.__class__`, self.whole_name(), self.date)

    def read(self, line):
        try: 
            self.perms = line[:10]
            entries = filter(None, string.split(line[10:42], ' '))
            self.size = int(entries[3])
            self.date = line[43:55]
            self.name = string.strip(line[55:]) 
        except Exception, message:
            print 'Could not read:', line, message
#        print line
#        print self

    def prepareAsFile(self, data):
        self.lines = string.split(data, '\n')
        self.lines.reverse()
 
    def readline(self):
        try: return self.lines.pop()+'\n'
        except IndexError: return ''

    def isFolder(self):
        return self.perms[0] == 'd'

    def isSysObj(self):
        return (self.size == 0) and (self.perms == '----------')

    def whole_name(self):
        if self.path == '/': return '/%s' % self.name
        else: return '%s/%s' % (self.path, self.name)

    def obj_path(self):
        return string.join(string.split(self.path, '/') + [self.name], '.')

    def cmd(self, cmd):
        return '%s %s' % (cmd, self.whole_name())

class ZopeFTP:
    def __init__(self):
        self.ftp = None
        self.host = ''
        self.port = 21
        self.username = ''
        self.connected = false
        self.http_port = 8080
    
    def __del__(self):
        self.disconnect()

    def connect(self, username, password, host, port = 21):
        self.ftp = ftplib.FTP('')

        self.host = host
        self.port = port
        self.username = username

        res = []
        res.append(self.ftp.connect(host, port))

        # Zope returns 'Login successful' even on wrong passwords :(
        res.append(self.ftp.login(username, password))
            
        return string.join(res, '\n') 

        self.connected = true

    def disconnect(self):
        if self.ftp: self.ftp.quit()
        self.ftp = None
        self.connected = false

    def add_doc(self, name, path):
        return ZopeFTPItem(path, name, '-rw-rw----', 0, '')

    def folder_item(self, name, path):
        return ZopeFTPItem(path, name, 'drw-rw----', 0, '')

    def add_folder(self, name, path):
        self.ftp.mkd('%s/%s' % (path, name))

    def dir(self, path):
        res = []
        lst = []
        self.ftp.dir(path, lst.append)
        for line in lst:
            zftpi = ZopeFTPItem()
            zftpi.read(line)
            zftpi.path = path
            res.append(zftpi)
        return res

    def download(self, server_filename, local_filename):
        f = open(local_filename, 'wb')
        self.ftp.retrbinary('RETR %s' % server_filename, f.write)
        f.close()
     
    def load(self, item):
        res = []
        self.ftp.retrlines(item.cmd('RETR'), res.append)
        return string.join(res, '\n') 

    def save(self, item, data):
        item.prepareAsFile(data) 
        self.ftp.storlines(item.cmd('STOR'), item)

    def upload(self, filename, dest_path):
        f = open(filename, 'rb')
        data = f.read()
        f.close()
        self.save(ZopeFTPItem(dest_path, os.path.basename(filename)), data)

    def delete(self, item):
        if item.isFolder():
            self.ftp.rmd(item.whole_name())
            return true
        else:
            self.ftp.delete(item.whole_name())
            return false
    
    def rename(self, item, new_name):
        old_path = item.whole_name()
        new_path = os.path.dirname(old_path)+'/'+new_name
        self.ftp.rename(old_path, new_path)
        