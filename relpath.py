#----------------------------------------------------------------------
# Name:        relpath.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

##b = 'c:\\a\\b\\f\\d'
##d = 'c:\\a\\b\\f\\h.txt'
##d = 'c:\\a\\b\\h\\i\\j.txt'
##e = 'd:\\z\\x\\y\\j\\k.txt'

import os
from os import path

def splitpath(apath):
    """ Splits a path into a list of directory names """
    path_list = []
    head, tail = path.split(apath)
    while tail:
        path_list.insert(0, tail)
        head, tail = path.split(head)
    return path_list
        

def relpath(base, comp):
    """ Return a path to file comp relative to path base. """
    base_drive, base_path = path.splitdrive(base)
    comp_drive, comp_path = path.splitdrive(comp)
    base_path_list = splitpath(base_path)
    comp_path_list = splitpath(comp_path)

    if base_drive != comp_drive:
        return comp
    
    # relative path defaults to the list of files with
    # a greater index then the entire base
    rel_path = comp_path_list[len(base_path_list):]
    # find the first directory for which the 2 paths differ 
    found = -1
    for idx in range(len(base_path_list)):
        if base_path_list[idx] != comp_path_list[idx]:
            rel_path = comp_path_list[idx:]
            found = 0
            break
    for cnt in range(max(len(base_path_list) - idx + found, 0)):
        rel_path.insert(0, os.pardir) 
#    for cnt in range(max(1 + len(base_path_list) - len(comp_path_list), 0)):
#        rel_path.insert(0, os.pardir)
            
    return apply(path.join, rel_path)
        
#print relpath(b, d)        
