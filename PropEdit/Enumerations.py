#----------------------------------------------------------------------
# Name:        Enumerations.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from wxPython.wx import *

def reverseDict(dict):
    rev = {}
    for k in dict.keys():
        rev[dict[k]] = k
    return rev
        
windowStyles =[wxCAPTION, wxMINIMIZE_BOX, wxMAXIMIZE_BOX, wxTHICK_FRAME, 
wxSIMPLE_BORDER, wxDOUBLE_BORDER, wxSUNKEN_BORDER, wxRAISED_BORDER, 
wxSTATIC_BORDER, wxTRANSPARENT_WINDOW, wxNO_3D, wxTAB_TRAVERSAL, wxVSCROLL,
wxHSCROLL, wxCLIP_CHILDREN]

windowNameStyles = {'wxCAPTION':wxCAPTION, 'wxMINIMIZE_BOX':wxMINIMIZE_BOX, 
'wxMAXIMIZE_BOX':wxMAXIMIZE_BOX, 'wxTHICK_FRAME':wxTHICK_FRAME, 
'wxSIMPLE_BORDER':wxSIMPLE_BORDER, 'wxDOUBLE_BORDER':wxDOUBLE_BORDER, 
'wxSUNKEN_BORDER':wxSUNKEN_BORDER, 'wxRAISED_BORDER':wxRAISED_BORDER, 
'wxSTATIC_BORDER':wxSTATIC_BORDER, 'wxTRANSPARENT_WINDOW':wxTRANSPARENT_WINDOW, 
'wxNO_3D':wxNO_3D, 'wxTAB_TRAVERSAL':wxTAB_TRAVERSAL, 'wxVSCROLL':wxVSCROLL,
'wxHSCROLL':wxHSCROLL, 'wxCLIP_CHILDREN':wxCLIP_CHILDREN}

##windowStyleNames = {wxCAPTION:'wxCAPTION', wxMINIMIZE_BOX:'wxMINIMIZE_BOX', 
##wxMAXIMIZE_BOX:'wxMAXIMIZE_BOX', wxTHICK_FRAME:'wxTHICK_FRAME', 
##wxSIMPLE_BORDER:'wxSIMPLE_BORDER', wxDOUBLE_BORDER:'wxDOUBLE_BORDER', 
##wxSUNKEN_BORDER:'wxSUNKEN_BORDER', wxRAISED_BORDER:'wxRAISED_BORDER', 
##wxSTATIC_BORDER:'wxSTATIC_BORDER', wxTRANSPARENT_WINDOW:'wxTRANSPARENT_WINDOW', 
##wxNO_3D:'wxNO_3D', wxTAB_TRAVERSAL:'wxTAB_TRAVERSAL', wxVSCROLL:'wxVSCROLL',
##wxHSCROLL:'wxHSCROLL', wxCLIP_CHILDREN:'wxCLIP_CHILDREN'}

# Fonts
fontFamily = [wxDEFAULT, wxDECORATIVE, wxROMAN, wxSCRIPT, wxSWISS, wxMODERN]
fontFamilyNames = {'wxDEFAULT':wxDEFAULT, 'wxDECORATIVE':wxDECORATIVE, 'wxROMAN':wxROMAN, 
		   'wxSCRIPT':wxSCRIPT, 'wxSWISS':wxSWISS, 'wxMODERN':wxMODERN}
fontStyle = [wxNORMAL, wxSLANT, wxITALIC]
fontStyleNames = {'wxNORMAL':wxNORMAL, 'wxSLANT':wxSLANT, 'wxITALIC':wxITALIC}
fontWeight = [wxNORMAL, wxLIGHT, wxBOLD]
fontWeightNames = {'wxNORMAL':wxNORMAL, 'wxLIGHT':wxLIGHT, 'wxBOLD':wxBOLD}

splitterWindowSplitMode = [1, 2]
splitterWindowSplitModeNames = {'wxSPLIT_HORIZONTAL': 1, 
                                'wxSPLIT_VERTICAL': 2}

constraintEdges = ['wxLeft', 'wxRight', 'wxTop', 'wxBottom', 'wxHeight',
                   'wxWidht', 'wxCentreX', 'wxCentreY']
constraintRelationships = ['wxUnconstrained', 'wxAsIs', 'wxAbove', 'wxBelow',
                           'wxLeftOf', 'wxRightOf', 'wxSameAs', 'wxPercentOf',
                           'wxAbsolute']

formatStyle = ['wxLIST_FORMAT_LEFT', 'wxLIST_FORMAT_RIGHT','wxLIST_FORMAT_CENTRE',
               'wxLIST_FORMAT_CENTER']

sashLayoutOrientation = [wxLAYOUT_HORIZONTAL, wxLAYOUT_VERTICAL]
sashLayoutOrientationNames = {'wxLAYOUT_HORIZONTAL' : wxLAYOUT_HORIZONTAL, 
                              'wxLAYOUT_VERTICAL' : wxLAYOUT_VERTICAL}

sashLayoutAlignment = [wxLAYOUT_NONE, wxLAYOUT_TOP, wxLAYOUT_LEFT, wxLAYOUT_RIGHT, 
                       wxLAYOUT_BOTTOM]
sashLayoutAlignmentNames = {'wxLAYOUT_NONE' : wxLAYOUT_NONE,
                            'wxLAYOUT_TOP' : wxLAYOUT_TOP,
                            'wxLAYOUT_LEFT' : wxLAYOUT_LEFT, 
                            'wxLAYOUT_RIGHT' : wxLAYOUT_RIGHT,
                            'wxLAYOUT_BOTTOM' : wxLAYOUT_BOTTOM}
class BinarySet:
    def __init__(self, elements, names, set):
        self.elements = elements
        self.names = names
        self.revNames = reverseDict(names)

        self.set = set
    
    def getBinaryValue(self):
        v = 0
        for i in self.set:
            v = v + i
        return v

    def setBinaryValue(self, value):
        self.set = []
        for i in self.elements:
            if i & value:
                self.set.append(i)
    
    def add(self, elementName):
        element = self.names[elementName]
        self.remove(element)
        self.set.append(element)
        
    def remove(self, elementName):
        element = self.names[elementName]
        try:
            self.set.remove(element)
        except:
            pass

    def has_element(self, elementName):
        element = self.names[elementName]
        for i in self.set:
            if i == element:
                return true
        return false
        
    def values(self):
        v = []
        for i in self.elements:
            v.append([self.names[i], self.has_element(self.revNames[i])])
        return v
        
