#----------------------------------------------------------------------
# Name:        Search.py
# Purpose:     Searching html/txt file
#
# Author:      Riaan Booysen
#
# Created:     2000/01/08
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from os import path
import os
import string
from wxPython.wx import wxProgressDialog, wxPD_CAN_ABORT, wxPD_APP_MODAL

##def visit(info, dirname, names):
##    pattern = info[0]
##    results = info[1]
##        
##    for file in names:
##        if find(path.join(dirname, file), pattern):
##            results.append(file)
    
def count(filename, pattern, caseSensitive):
    try: f = open(filename, 'r')
    except IOError: return 0
    try:
        data = f.read()
        if not caseSensitive:
            data = string.lower(data)
            pattern = string.lower(pattern)

        return string.count(data, pattern)
    finally:
        f.close()

def findInText(sourcelines, pattern, caseSensitive):
    results = []
    if not caseSensitive:
        sourcelines = map(lambda sourceline: string.lower(sourceline), sourcelines) 
        pattern = string.lower(pattern)
        
    matches = map(lambda x, y: (x, y), sourcelines, range(len(sourcelines)))
    for line, sourceIdx in matches:
        idx = -1
        while 1:
            idx = string.find(line, pattern, idx + 1)
            if idx == -1: break
            else: results.append((sourceIdx, idx))
    return results

def findInFile(filename, pattern, caseSensitive):
    results = []
    try: f = open(filename, 'r')
    except IOError: return results
    try:
        sourcelines = f.readlines()
        print 'len data', len(sourcelines)
        return findInText(sourcelines, pattern, caseSensitive)
    finally:
        f.close()
        
def findInFiles(parent, srchPath, pattern, callback, deeperPath = '', filemask = ('.htm', '.html', '.txt')):
    results = []
    names = os.listdir(srchPath)
    cnt = 0   

    max = len(names)
    dlg = wxProgressDialog('Search help files...',
                           'Searching...',
                           max,
                           parent,
                           wxPD_CAN_ABORT | wxPD_APP_MODAL)
    try:
        for file in names:
            filePath = path.join(srchPath, file)
            dummy, ext = path.splitext(file)
            if ext in filemask:
                callback(dlg, cnt, file, 'Searching')
                ocs = count(filePath, pattern, 0)
     	        if ocs:
                    results.append((ocs, deeperPath+file))
            else:
                if path.isdir(filePath):
                    results.extend(findInFiles(parent, filePath, pattern, 
                      callback, file+'/'))
                else:
                    callback(dlg, cnt, file, 'Skipping')
            cnt = cnt + 1
        return results
    finally:
        dlg.Destroy()
