#----------------------------------------------------------------------
# Name:        HelpScrpt.py
# Purpose:     To generate HelpCompanions.py
#
# Author:      Riaan Booysen
#
# Created:     2000/04/03
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import string
import os
import pprint
from time import time, gmtime, strftime

header = '''#----------------------------------------------------------------------
# Name:        HelpCompanions.py
# Purpose:     Generated file used by companions to link to help files
#
# Author:      Riaan Booysen & Boa Constructor
#
# Created:     %s
# RCS-ID:      %sId: HelpCompanions.py %s
#----------------------------------------------------------------------

'''

# Copy the the files declared below into this script's directory and
# execute the script. Copy HelpCompanions to the Companions directory

# Currently set for 2.2.1's help

# Search for htm file containing: 
#   <title>wxWindows classes implemented in wxPython</title>
wxPythonClasses = 'wx477.htm'

# Search for htm file containing: 
#   <title>Miscellaneous functions</title>
wxPythonFuncs = 'wx400.htm'

pythonLibRef = 'genindex.html'
pythonLibDir = 'lib/'
pythonModRef = 'modindex.html'

helpFileDef = "%sDocs = '%s'\n"

def ripPythonDocs(splLst, dir, name_term):
    dict = {}
    for line in splLst:
        if line[:8]=='<a href=':
            idx = string.find(line, '>')
            if idx != -1:
                href = line[9:idx-1]
                name = line[idx+1:]

                idx = string.find(name, name_term)
                if idx != -1:
                    name = string.strip(name[:idx])
                    dict[name] = dir+href
    return dict


fileClss = open(wxPythonClasses, 'r')
clssHtmlLines = map(lambda a: string.strip(a), fileClss.readlines())
fileClss.close()

fileFncs = open(wxPythonFuncs, 'r')
fncsHtmlLines = map(lambda a: string.strip(a), fileFncs.readlines())
fileFncs.close()

fileLibRef = open(pythonLibRef, 'r')
libRefHtml = fileLibRef.read()
fileLibRef.close()

fileModRef = open(pythonModRef, 'r')
libModHtml = fileModRef.read()
fileModRef.close()

output = open('HelpCompanions.py', 'w')
output.write(header % (strftime('%Y/%d/%m', gmtime(time())), '$', '$'))

clssHelpItems = clssHtmlLines[clssHtmlLines.index('<UL>')+1: clssHtmlLines.index('</UL>')]

try:
    startIdx = fncsHtmlLines.index('<H2>Miscellaneous functions</H2>') + 2
except:
    print 'No function list found'
    fncsHelpItems = []
else:
    try:
        endIdx = fncsHtmlLines[startIdx:].index('<P>')
    except:
        print 'Function list terminator <P> not found'
        fncsHelpItems = []
    else:
        fncsHelpItems = fncsHtmlLines[startIdx:endIdx]
                
output.write(helpFileDef % ('wxDefault', wxPythonClasses))

output.write('\n# Classes\n')
for item in clssHelpItems:
    if item and item[5] == '<':
        qte = string.find(item, '">')
        output.write(helpFileDef % (item[qte+2:-4], item[14:qte]))

output.write('\n# Functions\n')
for item in fncsHelpItems:
    href, name = string.split(item, '">::')
    output.write(helpFileDef % (name[:-8], wxPythonFuncs+href[9:]))

#libRefHelpItems = []
splLst = string.split(libRefHtml, '<dt>')

libRefDict = ripPythonDocs(string.split(libRefHtml, '<dt>'), pythonLibDir, '()')

##for line in splLst:
##    if line[:9]=='<a href="':
##        idx = string.find(line, '">')
##        if idx != -1:
##            href = line[9:idx]
##            name = line[idx+2:]
##
##            idx = string.find(name, '()')
##            if idx != -1:
##                name = name[:idx]
##                libRefDict[name] = pythonLibRefDir+href
###                print 'adding', href, 'to', name

output.write('\n# Library reference index\n')
output.write('libRefDocs = ')                  
pprint.pprint(libRefDict, output) 

modRefDict = ripPythonDocs(string.split(libModHtml, '<dt>'), pythonLibDir, '<')

output.write('\n# Module index\n')
output.write('modRefDocs = ')                  
pprint.pprint(modRefDict, output) 

#filter(lambda x: x[:9]=='<a href="', sgs)
#libRefHelpItems


output.close()

print 'fin'





