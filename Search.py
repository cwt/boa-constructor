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
import string, time
from wxPython.wx import wxProgressDialog, wxPD_CAN_ABORT, wxPD_APP_MODAL, wxPD_AUTO_HIDE, true, false

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

def findInText(sourcelines, pattern, caseSensitive, includeLine = 0):
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
            else:
               result = [sourceIdx, idx]
               if includeLine:
                   result.append(line)
               results.append(tuple(result))
    return results

def findInFile(filename, pattern, caseSensitive, includeLine = 0):
    results = []
    try: f = open(filename, 'r')
    except IOError: return results
    try:
        sourcelines = f.readlines()
        return findInText(sourcelines, pattern, caseSensitive, includeLine)
    finally:
        f.close()

def defaultProgressCallback(dlg, count, file, msg):
    dlg.Update(count, msg +' '+ file)
                
def findInFiles(parent, srchPath, pattern, callback = defaultProgressCallback, deeperPath = '', filemask = ('.htm', '.html', '.txt'), progressMsg = 'Search help files...', dlg = None, joiner = '/'):
    results = []
    names = os.listdir(srchPath)
    cnt = 0   

    owndlg = false
    max = len(names)
    if not dlg:
    	dlg = wxProgressDialog(progressMsg,
                           'Searching...',
                           max,
                           parent,
                           wxPD_CAN_ABORT | wxPD_APP_MODAL | wxPD_AUTO_HIDE)
        owndlg = true
    try:
        for file in names:
            filePath = path.join(srchPath, file)
            ext = path.splitext(file)[1]
            if ext in filemask or ('.*' in filemask and ext):
                callback(dlg, cnt, file, 'Searching')
                ocs = count(filePath, pattern, 0)
     	        if ocs:
                    results.append((ocs, deeperPath+file))
            else:
                if path.isdir(filePath):
                    results.extend(findInFiles(parent, filePath, pattern, 
                      callback, file+joiner, filemask, dlg = dlg, joiner = joiner))
                else:
                    callback(dlg, cnt, file, 'Skipping')
            cnt = cnt + 1
        return results
    finally:
        if owndlg:
            dlg.Destroy()

