#Boa:Frame:AddressEntry

import wx

def create(parent):
    return AddressEntry(parent)

[wxID_ADDRESSENTRY, wxID_ADDRESSENTRYADDRESS, wxID_ADDRESSENTRYCITY, 
 wxID_ADDRESSENTRYCOUNTRY, wxID_ADDRESSENTRYFIRSTNAME, 
 wxID_ADDRESSENTRYLASTNAME, wxID_ADDRESSENTRYNOTES, wxID_ADDRESSENTRYPANEL1, 
 wxID_ADDRESSENTRYPOSTAL, wxID_ADDRESSENTRYSTADDRESS, wxID_ADDRESSENTRYSTCITY, 
 wxID_ADDRESSENTRYSTCOUNTRY, wxID_ADDRESSENTRYSTFIRSTNAME, 
 wxID_ADDRESSENTRYSTLASTNAME, wxID_ADDRESSENTRYSTNOTES, 
 wxID_ADDRESSENTRYSTPOSTAL, 
] = [wx.NewId() for _init_ctrls in range(16)]

class AddressEntry(wx.Frame):
    def _init_coll_flexGridSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stFirstName, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.firstName, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stLastName, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.lastName, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stAddress, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.address, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stPostal, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.postal, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stCity, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.city, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stCountry, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.country, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stNotes, 0, border=4,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.notes, 1, border=4, flag=wx.ALL | wx.EXPAND)

    def _init_coll_flexGridSizer1_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableRow(6)
        parent.AddGrowableCol(1)

    def _init_sizers(self):
        # generated method, don't edit
        self.flexGridSizer1 = wx.FlexGridSizer(cols=2, hgap=0, rows=0, vgap=0)

        self._init_coll_flexGridSizer1_Items(self.flexGridSizer1)
        self._init_coll_flexGridSizer1_Growables(self.flexGridSizer1)

        self.panel1.SetSizer(self.flexGridSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_ADDRESSENTRY, name='AddressEntry',
              parent=prnt, pos=wx.Point(533, 250), size=wx.Size(453, 371),
              style=wx.DEFAULT_FRAME_STYLE, title='Address entry form')
        self.SetClientSize(wx.Size(445, 337))

        self.panel1 = wx.Panel(id=wxID_ADDRESSENTRYPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(445, 337),
              style=wx.TAB_TRAVERSAL)

        self.stFirstName = wx.StaticText(id=wxID_ADDRESSENTRYSTFIRSTNAME,
              label='First name', name='stFirstName', parent=self.panel1,
              pos=wx.Point(4, 8), size=wx.Size(54, 13), style=0)

        self.firstName = wx.TextCtrl(id=wxID_ADDRESSENTRYFIRSTNAME,
              name='firstName', parent=self.panel1, pos=wx.Point(66, 4),
              size=wx.Size(166, 21), style=0, value='')

        self.stLastName = wx.StaticText(id=wxID_ADDRESSENTRYSTLASTNAME,
              label='Last Name', name='stLastName', parent=self.panel1,
              pos=wx.Point(4, 37), size=wx.Size(54, 13), style=0)

        self.lastName = wx.TextCtrl(id=wxID_ADDRESSENTRYLASTNAME,
              name='lastName', parent=self.panel1, pos=wx.Point(66, 33),
              size=wx.Size(166, 21), style=0, value='')

        self.stAddress = wx.StaticText(id=wxID_ADDRESSENTRYSTADDRESS,
              label='Address', name='stAddress', parent=self.panel1,
              pos=wx.Point(4, 88), size=wx.Size(54, 13), style=0)

        self.address = wx.TextCtrl(id=wxID_ADDRESSENTRYADDRESS, name='address',
              parent=self.panel1, pos=wx.Point(66, 62), size=wx.Size(166, 66),
              style=wx.TE_MULTILINE, value='')

        self.stPostal = wx.StaticText(id=wxID_ADDRESSENTRYSTPOSTAL,
              label='Postal', name='stPostal', parent=self.panel1,
              pos=wx.Point(4, 140), size=wx.Size(54, 13), style=0)

        self.postal = wx.TextCtrl(id=wxID_ADDRESSENTRYPOSTAL, name='postal',
              parent=self.panel1, pos=wx.Point(66, 136), size=wx.Size(100, 21),
              style=0, value='')

        self.stCity = wx.StaticText(id=wxID_ADDRESSENTRYSTCITY, label='City',
              name='stCity', parent=self.panel1, pos=wx.Point(4, 169),
              size=wx.Size(54, 13), style=0)

        self.city = wx.TextCtrl(id=wxID_ADDRESSENTRYCITY, name='city',
              parent=self.panel1, pos=wx.Point(66, 165), size=wx.Size(166, 21),
              style=0, value='')

        self.stCountry = wx.StaticText(id=wxID_ADDRESSENTRYSTCOUNTRY,
              label='Country', name='stCountry', parent=self.panel1,
              pos=wx.Point(4, 198), size=wx.Size(54, 13), style=0)

        self.country = wx.TextCtrl(id=wxID_ADDRESSENTRYCOUNTRY, name='country',
              parent=self.panel1, pos=wx.Point(66, 194), size=wx.Size(168, 21),
              style=0, value='')

        self.stNotes = wx.StaticText(id=wxID_ADDRESSENTRYSTNOTES, label='Notes',
              name='stNotes', parent=self.panel1, pos=wx.Point(4, 271),
              size=wx.Size(54, 13), style=0)

        self.notes = wx.TextCtrl(id=wxID_ADDRESSENTRYNOTES, name='notes',
              parent=self.panel1, pos=wx.Point(66, 223), size=wx.Size(375, 110),
              style=wx.TE_RICH2 | wx.TE_MULTILINE, value='')

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop()
