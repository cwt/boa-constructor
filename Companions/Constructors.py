#----------------------------------------------------------------------
# Name:        Constructors.py                                         
# Purpose:     Definitions mapping property names to constructor       
#              keyword arguments                                       
#                                                                      
# Author:      Riaan Booysen                                           
#                                                                      
# Created:     1999                                                    
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen                            
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

class SplitterWindowConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Position': 'point', 'Size': 'size', 'Style': 'style', 'Name': 'name'}


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

class ComboConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size', 
                'Choices': 'choices', 'Style': 'style', 'Validator': 'validator', 
                'Name': 'name'}
##wxComboBox(wxWindow* parent, wxWindowID id, const wxString& value = "", const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, int n, const wxString choices[], long style = 0, const
##wxValidator& validator = wxDefaultValidator, const wxString& name = "comboBox")



class FramesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Title': 'title', 'Position': 'pos', 'Size': 'size', 
                'Style': 'style', 'Name': 'name'}
##wxFrame(wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxDEFAULT_FRAME_STYLE, const
##wxString& name = "frame")

##wxDialog(wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxDEFAULT_DIALOG_STYLE, const
##wxString& name = "dialogBox")

##wxMiniFrame(wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxDEFAULT_FRAME_STYLE, const
##wxString& name = "frame")

##wxMDIChildFrame(wxMDIParentFrame* parent, wxWindowID id, const wxString& title, const wxPoint& pos
##= wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxDEFAULT_FRAME_STYLE, const
##wxString& name = "frame")

##wxMDIParentFrame(wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxDEFAULT_FRAME_STYLE |
##wxVSCROLL | wxHSCROLL, const wxString& name = "frame")


class GaugeConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Range': 'range', 'Position': 'pos', 'Size': 'size', 
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}
##wxGauge(wxWindow* parent, wxWindowID id, int range, const wxPoint& pos = wxDefaultPosition, const
##wxSize& size = wxDefaultSize, long style = wxGA_HORIZONTAL, const wxValidator& validator =
##wxDefaultValidator, const wxString& name = "gauge")


class SliderConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'MinValue': 'minValue', 'MaxValue': 'maxValue',
                'Position': 'point', 'Size': 'size', 'Style': 'style', 
                'Validator': 'validator', 'Name': 'name'}
##wxSlider(wxWindow* parent, wxWindowID id, int value , int minValue, int maxValue, const wxPoint& point =
##wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxSL_HORIZONTAL, const wxValidator&
##validator = wxDefaultValidator, const wxString& name = "slider")


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

class MenuItemsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Id': 'id', 'Label': 'item', 'HelpString': 'helpString',
                'Checkable': 'checkable'}
                
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
        return {'Page': 'pPage', 'Text': 'strText', 
                'Selected' : 'bSelect', 'ImageId': 'imageId'}

class AcceleratorTableEntriesConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Entries': 'choices'}

class LayoutConstraintsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Relationship': 'rel', 'Edge': 'edge', 'OtherEdge': 'otherEdge',
                'OtherWindow' : 'otherWin', 'Value': 'value', 'Margin': 'margin'}

class GenButtonConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Label': 'label', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

class GenBitmapButtonConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size', 
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}
                
class ToolBarToolsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Id': 'id', 'Bitmap': 'bitmap', 'PushedBitmap': 'pushedBitmap',
                'IsToggle': 'isToggle', 
#                'XPos': 'xPos', 'YPos': 'yPos',
                'ShortHelpString': 'shortHelpString', 
                'LongHelpString': 'longHelpString'}

class SizerControlsConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Window': 'window', 'Option': 'option', 'Flag': 'flag', 'Border': 'border'}