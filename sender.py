#----------------------------------------------------------------------
# Name:        sender.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import string

class SenderMapper:
    def __init__(self):
        self.objectDict = {}

    def stripThis(self, eventObject):
        return eventObject[1:string.find(eventObject, '_', 1)]

    def addObject(self, obj):
        self.objectDict[self.stripThis(obj.this)] = obj

    def getObject(self, eventObject):
        evtObj = eventObject.GetEventObject()
        if evtObj:
            return self.objectDict[self.stripThis(eventObject.GetEventObject())]
        else:
            print 'no evt obj'

    def getBtnObject(self, eventObject):
        return eventObject.theButton

    def __repr__(self):
        return `self.objectDict`
