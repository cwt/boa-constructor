#----------------------------------------------------------------------
# Name:        Constructors.py
# Purpose:     Definitions mapping property names to constructor
#              keyword arguments
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2003 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

class PropertyKeywordConstructor:
    """ The base class for all constructor definitions mapping property
        names to constructor keyword arguments
    """

class EmptyConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {}

class ChoicesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Name': 'name', 'Entries': 'choices'}

class AcceleratorTableEntriesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Name': 'name', 'Flags': 'flags', 'KeyCode': 'keyCode',
                'Command': 'cmd'}

class WindowConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style', 'Name': 'name'}
##wxNotebook(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize&
##size, long style = 0, const wxString& name = "notebook")

##wxPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size =
##wxDefaultSize, long style = wxTAB_TRAVERSAL, const wxString& name = "panel")

##wxGrid(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style=0, const
##wxString& name="grid")

##wxStatusBar(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize&
##size = wxDefaultSize, long style = 0, const wxString& name = "statusBar")

##wxToolBar(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxTB_HORIZONTAL | wxNO_BORDER, const wxString& name =
##wxPanelNameStr)

##wxScrolledWindow(wxWindow* parent, wxWindowID id = -1, const wxPoint& pos = wxDefaultPosition,
##const wxSize& size = wxDefaultSize long, style = wxHSCROLL | wxVSCROLL, const wxString& name = "scrolledWindow")

class MenuBarConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Style': 'style', 'Name': 'name'}

class MenuBarMenusConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Menu': 'menu', 'Title': 'title'}

class BitmapButtonConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Bitmap': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}
##wxBitmapButton(wxWindow* parent, wxWindowID id, const wxBitmap& bitmap, const wxPoint& pos, const
##wxSize& size = wxDefaultSize, long style = wxBU_AUTODRAW, const wxValidator& validator, const
##wxString& name = "button")


class LabeledInputConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Label': 'label',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}
##wxButton(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos, const wxSize& size
##= wxDefaultSize, long style = 0, const wxValidator& validator, const wxString& name = "button")

##wxCheckBox(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = 0, const wxValidator& val, const
##wxString& name = "checkBox")

##wxRadioButton(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = 0, const wxValidator& validator =
##wxDefaultValidator, const wxString& name = "radioButton")


class LabeledNonInputConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Label': 'label',
                'Style': 'style', 'Name': 'name'}
##wxStaticBox(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = 0, const wxString& name = "staticBox")

##wxStaticText(wxWindow* parent, wxWindowID id, const wxString& label = "", const wxPoint& pos, const
##wxSize& size = wxDefaultSize, long style = 0, const wxString& name = "staticText")


class ListConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'Style': 'style', 'Validator': 'validator',
                'Name': 'name'}
##wxChoice(wxWindow *parent, wxWindowID id, const wxPoint& pos, const wxSize& size, int n, const wxString
##choices[], long style = 0, const wxValidator& validator = wxDefaultValidator, const wxString& name =
##"choice")

##wxListBox(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, int n, const wxString choices[] = NULL, long style = 0, const wxValidator& validator =
##wxDefaultValidator, const wxString& name = "listBox")

##wxCheckListBox(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const
##wxSize& size = wxDefaultSize, int n, const wxString choices[] = NULL, long style = 0, const wxValidator&
##validator = wxDefaultValidator, const wxString& name = "listBox")

##wxSpinButton(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxDefaultSize, long style =
##wxSP_HORIZONTAL, const wxValidator& validator = wxDefaultValidator, const wxString& name = "spinButton")

class MultiItemCtrlsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}
##wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxLC_ICON, const wxValidator& validator = wxDefaultValidator, const
##wxString& name = "listCtrl")

##wxTreeCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxTR_HAS_BUTTONS, const wxValidator& validator = wxDefaultValidator,
##const wxString& name = "listCtrl")

##wxScrollBar(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size
##= wxDefaultSize, long style = wxSB_HORIZONTAL, const wxValidator& validator = wxDefaultValidator,
##const wxString& name = "scrollBar")


class HtmlWindowConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Name': 'name'}

##wxHtmlWindow(wxWindow *parent, wxWindowID id = -1, const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxDefaultSize,
##long style = wxHW_SCROLLBAR_AUTO, const wxString& name = "htmlWindow")

class RadioBoxConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Label': 'label', 'Position': 'point', 'Size': 'size',
                'Choices': 'choices', 'MajorDimension': 'majorDimension',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}
##wxRadioBox(wxWindow* parent, wxWindowID id, const wxString& label, const wxPoint& point =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, int n = 0, const wxString choices[] = NULL, int
##majorDimension = 0, long style = wxRA_SPECIFY_COLS, const wxValidator& validator =
##wxDefaultValidator, const wxString& name = "radioBox")


class StaticBitmapConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Bitmap': 'bitmap', 'Label': 'label', 'Position': 'pos',
                'Size': 'size', 'Style': 'style', 'Name': 'name'}
##wxStaticBitmap(wxWindow* parent, wxWindowID id, const wxBitmap& label = "", const wxPoint& pos, const
##wxSize& size = wxDefaultSize, long style = 0, const wxString& name = "staticBitmap")

class TextCtrlConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}
##wxTextCtrl(wxWindow* parent, wxWindowID id, const wxString& value = "", const wxPoint& pos, const
##wxSize& size = wxDefaultSize, long style = 0, const wxValidator& validator, const wxString& name = "text")

class ImageListConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Name': 'name', 'Width': 'width', 'Height': 'height'}
##, 'Masked': 'mask',
##                'InitialCount': 'initialCount'}

class MenuConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Name': 'name', 'Title': 'title'}

class ListCtrlColumnsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Column': 'col', 'Heading': 'heading', 'Format': 'format',
                'Width': 'width'}

class ImageListImagesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Bitmap': 'bitmap', 'Mask': 'mask'}

class StatusBarFieldsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Index': 'i', 'Text': 'text', 'Width': 'width'}

class NotebookPageConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Page': 'page', 'Text': 'text',
                'Selected' : 'select', 'ImageId': 'imageId'}

class AcceleratorTableEntriesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Entries': 'choices'}

class LayoutConstraintsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Relationship': 'rel', 'Edge': 'edge', 'OtherEdge': 'otherEdge',
                'OtherWindow' : 'otherWin', 'Value': 'value', 'Margin': 'margin'}

class SizerControlsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Window': 'window', 'Option': 'option', 'Flag': 'flag', 'Border': 'border'}
