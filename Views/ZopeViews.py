from EditorViews import HTMLView, ListCtrlView
from ExternalLib import xmlrpclib
import HTMLResponse
from wxPython import wx

true=1; false=0

# XXX This is expensive and will really need to delay generatePage until View
# XXX is focused (like ExploreView)
# XXX The HTML control does not interact well with Zope.

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
        print url, s
        return s#f.read()

class ZopeUndoView(ListCtrlView):
    viewName = 'Undo'
    undoBmp = 'Images/Shared/Undo.bmp'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.wxLC_REPORT,
          (('Undo', self.OnUndo, self.undoBmp, ()),), -1)
        self.addReportColumns( (('Action', 300), ('User', 75), ('Date', 130)) )

        self.active = true

        self.undoIds = []

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        try:
            undos = self.model.zopeObj.getUndoableTransactions()
        except xmlrpclib.Fault, error:
            frm = HTMLResponse.create(None, error.faultString)
            frm.Show(true)
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
                frm = HTMLResponse.create(None, error.faultString)
                frm.Show(true)
            except xmlrpclib.ProtocolError, error:
                if error.errmsg == 'Moved Temporarily':
                    # This is actually a successful move
                    self.refreshCtrl()
                else:
                    frm = HTMLResponse.create(None, error.errmsg)
                    frm.Show(true)
            else:
                self.refreshCtrl()

class ZopeSecurityView(ListCtrlView):
    viewName = 'Security'
    undoBmp = 'Images/Shared/Undo.bmp'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.wxLC_REPORT,
          (('Edit', self.OnEdit, self.undoBmp, ()),), -1)
        self.active = true

        #self.undoIds = []

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        perms = self.model.zopeObj.getPermissions()
        roles = self.model.zopeObj.getRoles()

        colls = [('Acquired', 40), ('Permission', 275)]
        for role in roles:
            colls.append( (role, 75) )

        self.addReportColumns( colls )

        i = 0
        #self.undoIds = []
        for perm in perms:
            apply(self.addReportItems,
                  (i, ((perm['acquire'] == 'CHECKED' and '*' or '',
                  perm['name']) + tuple(map( lambda x: x['checked'] == 'CHECKED' and '*' or '',
                  perm['roles'])) )))
            #self.undoIds.append(undo['id'])
            i = i + 1

        self.pastelise()

    def OnEdit(self, event):
        if self.selected != -1:
            pass
            #from ExternalLib import xmlrpclib

##            try:
##                self.model.zopeObj.undoTransaction([self.undoIds[self.selected]])
##            except xmlrpclib.Fault, error:
##                import HTMLResponse
##                frm = HTMLResponse.create(None, error.faultString)
##                frm.Show(true)
##            except xmlrpclib.ProtocolError, error:
##                if error.errmsg == 'Moved Temporarily':
##                    # This is actually a succesful move
##                    self.refreshCtrl()
##                else:
##                    import HTMLResponse
##                    frm = HTMLResponse.create(None, error.errmsg)
##                    frm.Show(true)
##            else:
##                self.refreshCtrl()
