#----------------------------------------------------------------------
# Name:        Enumerations.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2004 Riaan Booysen
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

windowNameStyles = {'wx.CAPTION':wxCAPTION, 'wx.MINIMIZE_BOX':wxMINIMIZE_BOX,
'wx.MAXIMIZE_BOX':wxMAXIMIZE_BOX, 'wx.THICK_FRAME':wxTHICK_FRAME,
'wx.SIMPLE_BORDER':wxSIMPLE_BORDER, 'wx.DOUBLE_BORDER':wxDOUBLE_BORDER,
'wx.SUNKEN_BORDER':wxSUNKEN_BORDER, 'wx.RAISED_BORDER':wxRAISED_BORDER,
'wx.STATIC_BORDER':wxSTATIC_BORDER, 'wx.TRANSPARENT_WINDOW':wxTRANSPARENT_WINDOW,
'wx.NO_3D':wxNO_3D, 'wx.TAB_TRAVERSAL':wxTAB_TRAVERSAL, 'wx.VSCROLL':wxVSCROLL,
'wx.HSCROLL':wxHSCROLL, 'wx.CLIP_CHILDREN':wxCLIP_CHILDREN}

# Fonts
fontFamily = [wxDEFAULT, wxDECORATIVE, wxROMAN, wxSCRIPT, wxSWISS, wxMODERN]
fontFamilyNames = {'wx.DEFAULT':wxDEFAULT, 'wx.DECORATIVE':wxDECORATIVE, 'wx.ROMAN':wxROMAN,
                   'wx.SCRIPT':wxSCRIPT, 'wx.SWISS':wxSWISS, 'wx.MODERN':wxMODERN}
fontStyle = [wxNORMAL, wxSLANT, wxITALIC]
fontStyleNames = {'wx.NORMAL':wxNORMAL, 'wx.SLANT':wxSLANT, 'wx.ITALIC':wxITALIC}
fontWeight = [wxNORMAL, wxLIGHT, wxBOLD]
fontWeightNames = {'wx.NORMAL':wxNORMAL, 'wx.LIGHT':wxLIGHT, 'wx.BOLD':wxBOLD}

splitterWindowSplitMode = [1, 2]
splitterWindowSplitModeNames = {'wx.SPLIT_HORIZONTAL': 1,
                                'wx.SPLIT_VERTICAL': 2}

constraintEdges = ['wx.Left', 'wx.Right', 'wx.Top', 'wx.Bottom', 'wx.Height',
                   'wx.Width', 'wx.CentreX', 'wx.CentreY']
constraintRelationships = ['wx.Unconstrained', 'wx.AsIs', 'wx.Above', 'wx.Below',
                           'wx.LeftOf', 'wx.RightOf', 'wx.SameAs', 'wx.PercentOf',
                           'wx.Absolute']

formatStyle = ['wx.LIST_FORMAT_LEFT', 'wx.LIST_FORMAT_RIGHT','wx.LIST_FORMAT_CENTRE',
               'wx.LIST_FORMAT_CENTER']

sashLayoutOrientation = [wxLAYOUT_HORIZONTAL, wxLAYOUT_VERTICAL]
sashLayoutOrientationNames = {'wx.LAYOUT_HORIZONTAL' : wxLAYOUT_HORIZONTAL,
                              'wx.LAYOUT_VERTICAL' : wxLAYOUT_VERTICAL}

sashLayoutAlignment = [wxLAYOUT_NONE, wxLAYOUT_TOP, wxLAYOUT_LEFT, wxLAYOUT_RIGHT,
                       wxLAYOUT_BOTTOM]
sashLayoutAlignmentNames = {'wx.LAYOUT_NONE' : wxLAYOUT_NONE,
                            'wx.LAYOUT_TOP' : wxLAYOUT_TOP,
                            'wx.LAYOUT_LEFT' : wxLAYOUT_LEFT,
                            'wx.LAYOUT_RIGHT' : wxLAYOUT_RIGHT,
                            'wx.LAYOUT_BOTTOM' : wxLAYOUT_BOTTOM}
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
