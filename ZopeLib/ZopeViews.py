#-----------------------------------------------------------------------------
# Name:        ZopeViews.py
# Purpose:     Custom views for Zope models
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing ZopeLib.ZopeViews'

from wxPython import wx

##import sys
##sys.path.append('..')

from Views.EditorViews import HTMLView, ListCtrlView
from Views.SourceViews import EditorStyledTextCtrl
from Models.HTMLSupport import BaseHTMLStyledTextCtrlMix
import Utils

from ExternalLib import xmlrpclib

true=1; false=0

# XXX This is expensive and will really need to delay generatePage until View
# XXX is focused (like ExploreView)
# XXX The HTML control does not interact well with Zope.

class ZopeHTMLStyledTextCtrlMix(BaseHTMLStyledTextCtrlMix):
    def __init__(self, wId):
        BaseHTMLStyledTextCtrlMix.__init__(self, wId)

        zope_dtml_elements = 'dtml-var dtml-in dtml-if dtml-elif dtml-else dtml-unless '\
        'dtml-with dtml-let dtml-call dtml-comment dtml-tree dtml-try dtml-except '\
        'dtml-raise dtml-finally dtml-sqlvar '
        
        zope_zsql_tags = 'params '

        zope_attributes=\
        'sequence-key sequence-item sequence-start sequence-end sequence-odd '

        zope_pt_attributes=\
        'z tal tal:content tal:replace tal:condition tal:attributes tal:define '\
        'tal:repeat tales metal '

        self.keywords = self.keywords + ' public !doctype '+ zope_dtml_elements +\
              zope_zsql_tags + zope_attributes + zope_pt_attributes

        self.setStyles()

class ZopeHTMLSourceView(EditorStyledTextCtrl, ZopeHTMLStyledTextCtrlMix):
    viewName = 'ZopeHTML'
    def __init__(self, parent, model):
        wxID_ZOPEHTMLSOURCEVIEW = wx.wxNewId()
        EditorStyledTextCtrl.__init__(self, parent, wxID_ZOPEHTMLSOURCEVIEW,
          model, (('Refresh', self.OnRefresh, '-', 'Refresh'),), -1)
        ZopeHTMLStyledTextCtrlMix.__init__(self, wxID_ZOPEHTMLSOURCEVIEW)
        self.active = true

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

class ZopeHTMLView(HTMLView):
    viewName = 'View'
    def generatePage(self):
##        if hasattr(self, 'lastpage'):
##            if len(self.model.viewsModified):
##                return self.lastpage
        import urllib
        url = 'http://%s:%d/%s'%(self.model.zopeObj.properties['host'],
              self.model.zopeObj.properties['httpport'],
              self.model.zopeObj.whole_name())
        f = urllib.urlopen(url)
        s = f.read()
#        print url, s
        return s#f.read()

class ZopeUndoView(ListCtrlView):
    viewName = 'Undo'
    undoBmp = 'Images/Shared/Undo.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.wxLC_REPORT,
          (('Undo', self.OnUndo, self.undoBmp, ''),), -1)
        self.addReportColumns( (('Action', 300), ('User', 75), ('Date', 130)) )

        self.active = true

        self.undoIds = []

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        try:
            #print 'ZOPEOBJ '+repr(self.model.zopeObj)
            undos = self.model.zopeObj.getUndoableTransactions()
        except xmlrpclib.Fault, error:
            wx.wxLogError(Utils.html2txt(error.faultString))
        else:
            i = 0
            self.undoIds = []
            for undo in undos:
                self.addReportItems(i, (undo['description'], undo['user_name'], str(undo['time'])) )
                self.undoIds.append(undo['id'])
                i = i + 1

            self.pastelise()

    def OnUndo(self, event):
        if self.selected != -1:
            try:
                self.model.zopeObj.undoTransaction([self.undoIds[self.selected]])
            except xmlrpclib.Fault, error:
                wx.wxLogError(Utils.html2txt(error.faultString))
            except xmlrpclib.ProtocolError, error:
                if error.errmsg == 'Moved Temporarily':
                    # This is actually a successful move
                    self.refreshCtrl()
                else:
                    wx.wxLogError(Utils.html2txt(error.errmsg))
            else:
                self.refreshCtrl()

class ZopeSecurityView(ListCtrlView):
    viewName = 'Security'
    undoBmp = 'Images/Shared/Undo.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.wxLC_REPORT,
          (('Edit', self.OnEdit, self.undoBmp, ''),), -1)
        self.active = true

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        perms = self.model.zopeObj.getPermissions()
        roles = self.model.zopeObj.getRoles()

        colls = [('Acquired', 40), ('Permission', 275)]
        for role in roles:
            colls.append( (role, 75) )

        self.addReportColumns( colls )

        i = 0
        for perm in perms:
            apply(self.addReportItems,
                  (i, ((perm['acquire'] == 'CHECKED' and '*' or '',
                  perm['name']) + tuple(map( lambda x: x['checked'] == 'CHECKED' and '*' or '',
                  perm['roles'])) )))
            i = i + 1

        self.pastelise()

    def OnEdit(self, event):
        if self.selected != -1:
            pass
