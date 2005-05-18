#----------------------------------------------------------------------
# Name:        EventCollections.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2005 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
# XXX Add another type of event:
# XXX   Old style method overriding
# XXX   These methods would be picked up from the methods of the class in module
# XXX   and not connected to an EVT_*.
# XXX   At first this is only practical with frames as frames are the only
# XXX   design time overrideable control.

# Miscellaneous

##def EVT_ACTIVATE(win, func):
##def EVT_ACTIVATE_APP(win, func):

##def EVT_END_SESSION(win, func):
##def EVT_QUERY_END_SESSION(win, func):
##def EVT_DROP_FILES(win, func):

##def EVT_INIT_DIALOG(win, func):
##def EVT_SYS_COLOUR_CHANGED(win, func):

##def EVT_SHOW(win, func):
##def EVT_MAXIMIZE(win, func):
##def EVT_ICONIZE(win, func):
##def EVT_NAVIGATION_KEY(win, func):
##def EVT_IDLE(win, func):
##def EVT_UPDATE_UI(win, id, func):

### Mouse Events

### EVT_COMMAND
##def EVT_COMMAND(win, id, cmd, func):
##def EVT_COMMAND_RANGE(win, id1, id2, cmd, func):

### Scrolling

### Scrolling, with an id
##def EVT_COMMAND_SCROLL(win, id, func):
##def EVT_COMMAND_SCROLL_TOP(win, id, func):
##def EVT_COMMAND_SCROLL_BOTTOM(win, id, func):
##def EVT_COMMAND_SCROLL_LINEUP(win, id, func):
##def EVT_COMMAND_SCROLL_LINEDOWN(win, id, func):
##def EVT_COMMAND_SCROLL_PAGEUP(win, id, func):
##def EVT_COMMAND_SCROLL_PAGEDOWN(win, id, func):
##def EVT_COMMAND_SCROLL_THUMBTRACK(win, id, func):

###---
##def EVT_SCROLLWIN(win, func):
##def EVT_SCROLLWIN_TOP(win, func):
##def EVT_SCROLLWIN_BOTTOM(win, func):
##def EVT_SCROLLWIN_LINEUP(win, func):
##def EVT_SCROLLWIN_LINEDOWN(win, func):
##def EVT_SCROLLWIN_PAGEUP(win, func):
##def EVT_SCROLLWIN_PAGEDOWN(win, func):
##def EVT_SCROLLWIN_THUMBTRACK(win, func):

### Scrolling, with an id
##def EVT_COMMAND_SCROLLWIN(win, id, func):
##def EVT_COMMAND_SCROLLWIN_TOP(win, id, func):
##def EVT_COMMAND_SCROLLWIN_BOTTOM(win, id, func):
##def EVT_COMMAND_SCROLLWIN_LINEUP(win, id, func):
##def EVT_COMMAND_SCROLLWIN_LINEDOWN(win, id, func):
##def EVT_COMMAND_SCROLLWIN_PAGEUP(win, id, func):
##def EVT_COMMAND_SCROLLWIN_PAGEDOWN(win, id, func):
##def EVT_COMMAND_SCROLLWIN_THUMBTRACK(win, id, func):

### Convenience commands
##def EVT_BUTTON(win, id, func):
##def EVT_CHECKBOX(win, id, func):
##def EVT_CHOICE(win, id, func):
##def EVT_LISTBOX(win, id, func):
##def EVT_LISTBOX_DCLICK(win, id, func):
##def EVT_TEXT(win, id, func):
##def EVT_TEXT_ENTER(win, id, func):
##def EVT_MENU(win, id, func):
##def EVT_MENU_RANGE(win, id1, id2, func):
##def EVT_SLIDER(win, id, func):
##def EVT_RADIOBOX(win, id, func):
##def EVT_RADIOBUTTON(win, id, func):
##def EVT_VLBOX(win, id, func):
##def EVT_COMBOBOX(win, id, func):
##def EVT_TOOL(win, id, func):
##def EVT_TOOL_RCLICKED(win, id, func):
##def EVT_TOOL_ENTER(win, id, func):
##def EVT_CHECKLISTBOX(win, id, func):

### Generic command events

##def EVT_COMMAND_LEFT_CLICK(win, id, func):
##def EVT_COMMAND_LEFT_DCLICK(win, id, func):
##def EVT_COMMAND_RIGHT_CLICK(win, id, func):
##def EVT_COMMAND_RIGHT_DCLICK(win, id, func):
##def EVT_COMMAND_SET_FOCUS(win, id, func):
##def EVT_COMMAND_KILL_FOCUS(win, id, func):
##def EVT_COMMAND_ENTER(win, id, func):

### wxNotebook events
##def EVT_NOTEBOOK_PAGE_CHANGED(win, id, func):
##def EVT_NOTEBOOK_PAGE_CHANGING(win, id, func):

### wxTreeCtrl events

### wxSpinButton

### wxTaskBarIcon
##def EVT_TASKBAR_MOVE(win, func):
##def EVT_TASKBAR_LEFT_DOWN(win, func):
##def EVT_TASKBAR_LEFT_UP(win, func):
##def EVT_TASKBAR_RIGHT_DOWN(win, func):
##def EVT_TASKBAR_RIGHT_UP(win, func):
##def EVT_TASKBAR_LEFT_DCLICK(win, func):
##def EVT_TASKBAR_RIGHT_DCLICK(win, func):

### wxGrid
##def EVT_GRID_SELECT_CELL(win, fn):
##def EVT_GRID_CREATE_CELL(win, fn):
##def EVT_GRID_CHANGE_LABELS(win, fn):
##def EVT_GRID_CHANGE_SEL_LABEL(win, fn):
##def EVT_GRID_CELL_CHANGE(win, fn):
##def EVT_GRID_CELL_LCLICK(win, fn):
##def EVT_GRID_CELL_RCLICK(win, fn):
##def EVT_GRID_LABEL_LCLICK(win, fn):
##def EVT_GRID_LABEL_RCLICK(win, fn):

### wxSashWindow
##def EVT_SASH_DRAGGED(win, id, func):
##def EVT_SASH_DRAGGED_RANGE(win, id1, id2, func):
##def EVT_QUERY_LAYOUT_INFO(win, func):
##def EVT_CALCULATE_LAYOUT(win, func):

### wxListCtrl

###wxSplitterWindow
##def EVT_SPLITTER_SASH_POS_CHANGING(win, id, func):
##def EVT_SPLITTER_SASH_POS_CHANGED(win, id, func):
##def EVT_SPLITTER_UNSPLIT(win, id, func):
##def EVT_SPLITTER_DOUBLECLICKED(win, id, func):


class wxMiscEvent :
    pass

""" Collections of event class macros """
EventCategories = {'ActivateEvent': ('wx.EVT_ACTIVATE', 'wx.EVT_ACTIVATE_APP'),
'MiscEvent':   ('wx.EVT_SIZE',
                'wx.EVT_MOVE',
                'wx.EVT_PAINT',
                'wx.EVT_ERASE_BACKGROUND'),

'FocusEvent' : ('wx.EVT_SET_FOCUS',
                'wx.EVT_KILL_FOCUS'),

'KeyEvent' : (  'wx.EVT_CHAR',
                'wx.EVT_CHAR_HOOK',
                'wx.EVT_KEY_DOWN',
                'wx.EVT_KEY_UP'),

'MouseEvent' : ('wx.EVT_LEFT_DOWN',
                'wx.EVT_LEFT_UP',
                'wx.EVT_MIDDLE_DOWN',
                'wx.EVT_MIDDLE_UP',
                'wx.EVT_RIGHT_UP',
                'wx.EVT_RIGHT_DOWN',
                'wx.EVT_MOTION',
                'wx.EVT_LEFT_DCLICK',
                'wx.EVT_MIDDLE_DCLICK',
                'wx.EVT_RIGHT_DCLICK',
                'wx.EVT_LEAVE_WINDOW',
                'wx.EVT_ENTER_WINDOW',
                'wx.EVT_MOUSEWHEEL',
                'wx.EVT_MOUSE_EVENTS'),

'ScrollEvent' :('wx.EVT_SCROLL',
                'wx.EVT_SCROLL_TOP',
                'wx.EVT_SCROLL_BOTTOM',
                'wx.EVT_SCROLL_LINEUP',
                'wx.EVT_SCROLL_LINEDOWN',
                'wx.EVT_SCROLL_PAGEUP',
                'wx.EVT_SCROLL_PAGEDOWN',
                'wx.EVT_SCROLL_THUMBTRACK',
                'wx.EVT_SCROLL_THUMBRELEASE'),

'CmdScrollEvent' : ('wx.EVT_COMMAND_SCROLL',
                    'wx.EVT_COMMAND_SCROLL_TOP',
                    'wx.EVT_COMMAND_SCROLL_BOTTOM',
                    'wx.EVT_COMMAND_SCROLL_LINEUP',
                    'wx.EVT_COMMAND_SCROLL_LINEDOWN',
                    'wx.EVT_COMMAND_SCROLL_PAGEUP',
                    'wx.EVT_COMMAND_SCROLL_PAGEDOWN',
                    'wx.EVT_COMMAND_SCROLL_THUMBTRACK',
                    'wx.EVT_COMMAND_SCROLL_THUMBRELEASE'),

'ScrollWinEvent' :('wx.EVT_SCROLLWIN',
                   'wx.EVT_SCROLLWIN_TOP',
                   'wx.EVT_SCROLLWIN_BOTTOM',
                   'wx.EVT_SCROLLWIN_LINEUP',
                   'wx.EVT_SCROLLWIN_LINEDOWN',
                   'wx.EVT_SCROLLWIN_PAGEUP',
                   'wx.EVT_SCROLLWIN_PAGEDOWN',
                   'wx.EVT_SCROLLWIN_THUMBTRACK',
                   'wx.EVT_SCROLLWIN_THUMBRELEASE'),

'FrameEvent' : ('wx.EVT_ACTIVATE',
                'wx.EVT_CLOSE',
                'wx.EVT_DROP_FILES',
                'wx.EVT_MAXIMIZE',
                'wx.EVT_ICONIZE',
                'wx.EVT_NAVIGATION_KEY',
                'wx.EVT_IDLE'),

'ListEvent' : ( 'wx.EVT_LIST_BEGIN_DRAG',
                'wx.EVT_LIST_BEGIN_RDRAG',
                'wx.EVT_LIST_BEGIN_LABEL_EDIT',
                'wx.EVT_LIST_END_LABEL_EDIT',
                'wx.EVT_LIST_DELETE_ITEM',
                'wx.EVT_LIST_DELETE_ALL_ITEMS',
                'wx.EVT_LIST_ITEM_SELECTED',
                'wx.EVT_LIST_ITEM_ACTIVATED',
                'wx.EVT_LIST_ITEM_DESELECTED',
                'wx.EVT_LIST_KEY_DOWN',
                'wx.EVT_LIST_INSERT_ITEM',
                'wx.EVT_LIST_ITEM_RIGHT_CLICK',
                'wx.EVT_LIST_COL_CLICK',
                'wx.EVT_LIST_COL_RIGHT_CLICK',
                'wx.EVT_LIST_COL_BEGIN_DRAG',
                'wx.EVT_LIST_COL_DRAGGING',
                'wx.EVT_LIST_COL_END_DRAG',
                'wx.EVT_LIST_CACHE_HINT',),

'TreeEvent' : ( 'wx.EVT_TREE_BEGIN_DRAG',
                'wx.EVT_TREE_BEGIN_RDRAG',
                'wx.EVT_TREE_BEGIN_LABEL_EDIT',
                'wx.EVT_TREE_END_LABEL_EDIT',
                'wx.EVT_TREE_GET_INFO',
                'wx.EVT_TREE_SET_INFO',
                'wx.EVT_TREE_ITEM_EXPANDED',
                'wx.EVT_TREE_ITEM_EXPANDING',
                'wx.EVT_TREE_ITEM_COLLAPSED',
                'wx.EVT_TREE_ITEM_COLLAPSING',
                'wx.EVT_TREE_ITEM_ACTIVATED',
                'wx.EVT_TREE_SEL_CHANGED',
                'wx.EVT_TREE_SEL_CHANGING',
                'wx.EVT_TREE_KEY_DOWN',
                'wx.EVT_TREE_DELETE_ITEM'),

'AppEvent' : (  'wx.EVT_ACTIVATE_APP',
                'wx.EVT_END_SESSION',
                'wx.EVT_QUERY_END_SESSION',
                'wx.EVT_IDLE',
                'wx.EVT_UPDATE_UI'),

'SpinEvent' : ( 'wx.EVT_SPIN_UP',
                'wx.EVT_SPIN_DOWN',
                'wx.EVT_SPIN'),

'HelpEvent': (  'wx.EVT_HELP', ),

}

##EventCategoryNames = {
##    'ActivateEvent': ('Activate', 
##                      'ActivateApp'),
##    'MiscEvent':   ('Size', 'Move', 'Paint', 'EraseBackground'),
##    'FocusEvent' : ('SetFocus', 'KillFocus'),
##    'KeyEvent' : ('Char', 'CharHook', 'KeyDown', 'KeyUp'),
##    'MouseEvent' : ('LeftDown', 'LeftUp', 'MiddleDown',
##                    'MiddleUp',

normalCategories = ['MiscEvent','FocusEvent','KeyEvent','MouseEvent','AppEvent',
'FrameEvent', 'ScrollEvent']
commandCategories = ['ListEvent', 'TreeEvent', 'CmdScrollEvent', 'SpinEvent',
'HelpEvent']

reservedWxIds = [
 # std ids
 'wx.ID_SEPARATOR',
 'wx.ID_OK', 'wx.ID_CANCEL', 'wx.ID_APPLY', 'wx.ID_YES', 'wx.ID_NO', 'wx.ID_STATIC',
 'wx.ID_CUT', 'wx.ID_COPY', 'wx.ID_PASTE', 'wx.ID_CLEAR', 'wx.ID_FIND',
 'wx.ID_DUPLICATE', 'wx.ID_SELECTALL',
 # help ids
 'wx.ID_CONTEXT_HELP', # this name is from wxPython.help
 'wx.ID_HELP_COMMANDS', 'wxID_HELP_CONTENTS', 'wxID_HELP_CONTEXT', 'wxID_HELP_PROCEDURES',
 # doc view ids
 'wx.ID_OPEN', 'wx.ID_CLOSE', 'wx.ID_NEW', 'wx.ID_SAVE', 'wx.ID_SAVEAS',
 'wx.ID_REVERT', 'wx.ID_EXIT', 'wx.ID_UNDO', 'wx.ID_REDO', 'wx.ID_HELP', 'wx.ID_PRINT',
 'wx.ID_PRINT_SETUP', 'wx.ID_PREVIEW', 'wx.ID_ABOUT',
 # misc ids
 'wx.ID_BACKWARD', 'wx.ID_FORWARD', 'wx.ID_SETUP', 'wx.ID_MORE',
]

# Other names that may clash in the 'id' namespace ;)
## copy of UtilCompanions.stockCursorIds

# >>> print "reservedCursors = ['"+"', '".join([k for k in wx.__dict__ if k.startswith('wxCURSOR_')])+"']"

reservedCursors = ['wx.CURSOR_LEFT_BUTTON', 'wx.CURSOR_PAINT_BRUSH', 
 'wx.CURSOR_WATCH', 'wx.CURSOR_CROSS', 'wx.CURSOR_BLANK', 'wx.CURSOR_MAX',
 'wx.CURSOR_CHAR', 'wx.CURSOR_RIGHT_ARROW', 'wx.CURSOR_POINT_RIGHT',
 'wx.CURSOR_SIZENESW', 'wx.CURSOR_MIDDLE_BUTTON', 'wx.CURSOR_WAIT',
 'wx.CURSOR_BULLSEYE', 'wx.CURSOR_SIZING', 'wx.CURSOR_POINT_LEFT',
 'wx.CURSOR_IBEAM', 'wx.CURSOR_SIZENWSE', 'wx.CURSOR_MAGNIFIER',
 'wx.CURSOR_SPRAYCAN', 'wx.CURSOR_SIZEWE',  'wx.CURSOR_RIGHT_BUTTON',
 'wx.CURSOR_ARROWWAIT', 'wx.CURSOR_DEFAULT', 'wx.CURSOR_PENCIL',
 'wx.CURSOR_NONE', 'wx.CURSOR_QUESTION_ARROW', 'wx.CURSOR_HAND',
 'wx.CURSOR_ARROW', 'wx.CURSOR_NO_ENTRY', 'wx.CURSOR_SIZENS']

reservedWxNames = reservedWxIds + reservedCursors

def renameCmdIdInDict(dct, name, newId):
    if dct[name] in reservedWxNames:
        return
    dct[name] = newId
